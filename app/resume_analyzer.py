from typing import Dict, Optional
from sqlalchemy.orm import Session
from .ml.skill_matcher import SkillMatcher

# import models
from app import models

import json
from pdfminer.high_level import extract_text

class ResumeAnalyzer:
    def __init__(self):
        self.skill_matcher = SkillMatcher()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        """
        try:
            return extract_text(file_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    async def analyze_resume(self, resume_text: str, job_description: str, 
                       db: Session, user_id: int, 
                       resume_id: Optional[int] = None) -> models.ResumeAnalysis:
        """
        Analyze a resume against a job description and save results to DB
        """
        # If resume_id is not provided, create a new resume
        if resume_id is None:
            resume = models.Resume(
                name="Uploaded Resume",
                content=resume_text,
                user_id=user_id
            )
            db.add(resume)
            await db.commit()
            await db.refresh(resume)
            resume_id = resume.id
        
        # Analyze the resume
        analysis_result = self.skill_matcher.analyze_resume(resume_text, job_description)
        
        # Create a new analysis record
        analysis = models.ResumeAnalysis(
            job_description=job_description,
            matched_tech_skills=json.dumps(analysis_result["matched_tech_skills"]),
            matched_soft_skills=json.dumps(analysis_result["matched_soft_skills"]),
            missing_tech_skills=json.dumps(analysis_result["missing_tech_skills"]),
            missing_soft_skills=json.dumps(analysis_result["missing_soft_skills"]),
            suggestions=analysis_result["suggestions"],
            user_id=user_id,
            resume_id=resume_id
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        return analysis