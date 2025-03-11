import os
import json
import numpy as np
import requests
from typing import Dict, List, Tuple
from groq import Groq
from langchain_core.output_parsers import JsonOutputParser


from google.cloud import secretmanager
# Initialize Google Secret Manager client
def access_secret_version(secret_id: str, project_id="stalwart-star-448320-c8"):
    """
    Fetches a secret from Google Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    try:
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        return None
    
os.environ["GROQ_API_KEY"] = access_secret_version("GROQ_API_KEY") or ""
os.environ["HF_TOKEN"] = access_secret_version("HF_TOKEN") or ""

# Set GROQ_MODEL with a default value if not in secrets
os.environ["GROQ_MODEL"] = access_secret_version("GROQ_MODEL") or "gemma2-9b-it"


# Load secrets from Google Secret Manager
GCP_PROJECT_ID = "stalwart-star-448320-c8" 
# Load Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma2-9b-it")  # Default model
HF_TOKEN = os.getenv("HF_TOKEN")


# Hugging Face Model ID
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"
# Headers
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

output_parser = JsonOutputParser()

# Ensure API key is set
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def extract_skills_from_text(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract technical and soft skills from text using LLM (Groq - Gemma).
    """
    prompt = f"""
    Extract all technical skills and soft skills from the following text.
    Return the result as a JSON with two lists: "technical_skills" and "soft_skills".
    
    Text:
    {text}
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts skills from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
        )

        # Parse the response
        content = completion.choices[0].message.content
        print("Raw LLM Response:", content)  # Debugging

        try:
            # skills_data = json.loads(content)
            skills_data = output_parser.parse(content)
        except json.JSONDecodeError:
            print("Error: LLM response is not valid JSON")
            return [], []

        tech_skills = skills_data.get("technical_skills", [])
        soft_skills = skills_data.get("soft_skills", [])

        print("Extracted Technical Skills:", tech_skills)  # Debugging
        print("Extracted Soft Skills:", soft_skills)  # Debugging

        return tech_skills, soft_skills

    except Exception as e:
        print(f"Groq API Error: {e}")
        return [], []


def get_hf_embeddings(texts):
    """
    Fetches sentence embeddings using the Hugging Face Inference API.
    """
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": texts, "options": {"wait_for_model": True}})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None
    
def calculate_skill_similarity(resume_skills: List[str], job_skills: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Calculate similarity between resume skills and job skills using Hugging Face API embeddings.
    """
    result = {}

    if not resume_skills or not job_skills:
        print("No skills provided for similarity matching.")  # Debugging
        return result

    # Get embeddings from Hugging Face API
    resume_embeddings = get_hf_embeddings(resume_skills)
    job_embeddings = get_hf_embeddings(job_skills)

    if not resume_embeddings or not job_embeddings:
        print("Error: Embeddings could not be retrieved.")
        return result

    # Convert to NumPy arrays
    resume_embeddings = np.array(resume_embeddings)
    job_embeddings = np.array(job_embeddings)

    print(f"Resume Skills Embeddings Shape: {resume_embeddings.shape}")  # Debugging
    print(f"Job Skills Embeddings Shape: {job_embeddings.shape}")  # Debugging

    # Compute cosine similarity
    for i, resume_skill in enumerate(resume_skills):
        similarities = np.dot(job_embeddings, resume_embeddings[i]) / (
            np.linalg.norm(job_embeddings, axis=1) * np.linalg.norm(resume_embeddings[i])
        )

        # Find the best match
        best_match_idx = np.argmax(similarities)
        best_match_skill = job_skills[best_match_idx]
        best_match_score = similarities[best_match_idx]

        result[resume_skill] = {
            "best_match": best_match_skill,
            "similarity": round(best_match_score, 4)
        }

    print("Skill Similarity Results:", result)  # Debugging
    return result


def generate_resume_suggestions(resume_text: str, job_description: str,
                                matched_tech: List[Dict], matched_soft: List[Dict],
                                missing_tech: List[str], missing_soft: List[str]) -> str:
    """
    Generate personalized suggestions to improve the resume for the job.
    """
    prompt = f"""
    You are a career coach and resume expert. Based on the following information:
    
    Resume: {resume_text}
    
    Job Description: {job_description}
    
    Matched Technical Skills: {matched_tech}
    Matched Soft Skills: {matched_soft}
    Missing Technical Skills: {missing_tech}
    Missing Soft Skills: {missing_soft}
    
    Provide detailed suggestions on how to improve the resume, including:
    1. Which parts of the resume to improve
    2. How to address missing skills (both technical and soft)
    3. Specific wording or sections that could be enhanced
    4. Overall structure and presentation improvements
    
    Be specific, actionable, and constructive in your feedback.
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful career coach and resume expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Error: Unable to generate suggestions."
