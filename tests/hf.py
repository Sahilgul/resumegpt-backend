import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hugging Face Model ID
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

# Hugging Face API Token (store this in a .env file)
HF_TOKEN = os.getenv("HF_TOKEN")

# API Endpoint
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"

# Headers
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def get_hf_embedding(texts):
    """
    Fetches sentence embeddings using the Hugging Face Inference API.
    """
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": texts, "options": {"wait_for_model": True}})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

# Test embedding retrieval
if __name__ == "__main__":
    test_texts = [
        "Machine learning is transforming industries.",
        "Deep learning models require a lot of data."
    ]

    embeddings = get_hf_embedding(test_texts)

    if embeddings:
        print(f"Embedding for '{test_texts[0]}': {embeddings[0][:5]}")  # Print first 5 values
        print(f"Embedding for '{test_texts[1]}': {embeddings[1][:5]}")  # Print first 5 values



import sqlalchemy
print(sqlalchemy.__version__)
