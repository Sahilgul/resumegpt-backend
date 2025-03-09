from typing import Dict, List, Tuple
from .llm_integration import extract_skills_from_text, calculate_skill_similarity, generate_resume_suggestions

class SkillMatcher:
    def __init__(self):
        self.similarity_threshold = 0.40  # Minimum similarity to consider a match
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Dict:
        """
        Main function to analyze a resume against a job description.
        """
        # Extract skills from resume and job description
        resume_tech, resume_soft = extract_skills_from_text(resume_text)
        job_tech, job_soft = extract_skills_from_text(job_description)
        
        # Calculate skill matches (technical)
        matched_tech, missing_tech = self._match_skills(resume_tech, job_tech)

        # Calculate skill matches (soft)
        matched_soft, missing_soft = self._match_skills(resume_soft, job_soft)

        # Generate suggestions
        suggestions = generate_resume_suggestions(
            resume_text, 
            job_description, 
            matched_tech, 
            matched_soft, 
            missing_tech, 
            missing_soft
        )
        
        return {
            "matched_tech_skills": matched_tech,
            "matched_soft_skills": matched_soft,
            "missing_tech_skills": missing_tech,
            "missing_soft_skills": missing_soft,
            "suggestions": suggestions
        }
    
    # def _match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Tuple[List[Dict], List[str]]:
    #     """
    #     Match skills based on similarity using Hugging Face API.
    #     """
    #     matched_skills = []
    #     missing_skills = []

    #     print(f"Matching Skills - Resume: {resume_skills}, Job: {job_skills}")  # Debugging

    #     if not resume_skills or not job_skills:
    #         print("No skills available for matching. All job skills are considered missing.")
    #         return matched_skills, job_skills  # All job skills are missing if resume has none

    #     similarity_results = calculate_skill_similarity(resume_skills, job_skills)

    #     for job_skill in job_skills:
    #         if job_skill in similarity_results:
    #             best_match = similarity_results[job_skill]
    #             if best_match["similarity"] >= self.similarity_threshold:
    #                 matched_skills.append({
    #                     "job_skill": job_skill,
    #                     "resume_skill": best_match["best_match"],
    #                     "similarity": best_match["similarity"]
    #                 })
    #             else:
    #                 missing_skills.append(job_skill)
    #         else:
    #             missing_skills.append(job_skill)

    #     print("Matched Skills:", matched_skills)  # Debugging
    #     print("Missing Skills:", missing_skills)  # Debugging

    #     return matched_skills, missing_skills


    def _match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Tuple[List[Dict], List[str]]:
        """
        Match skills based on similarity using Hugging Face API.
        """
        matched_skills = []
        missing_skills = job_skills.copy()  # Start with all job skills as missing

        print(f"Matching Skills - Resume: {resume_skills}, Job: {job_skills}")  # Debugging

        if not resume_skills or not job_skills:
            print("No skills available for matching. All job skills are considered missing.")
            return matched_skills, job_skills  # All job skills are missing if resume has none

        similarity_results = calculate_skill_similarity(resume_skills, job_skills)

        # Process the similarity results
        for resume_skill, match_info in similarity_results.items():
            job_skill = match_info["best_match"]
            similarity = match_info["similarity"]
            
            if similarity >= self.similarity_threshold:
                matched_skills.append({
                    "job_skill": job_skill,
                    "resume_skill": resume_skill,
                    "similarity": similarity
                })
                
                # Remove from missing skills if it's in there
                if job_skill in missing_skills:
                    missing_skills.remove(job_skill)

        print("Matched Skills:", matched_skills)  # Debugging
        print("Missing Skills:", missing_skills)  # Debugging

        return matched_skills, missing_skills