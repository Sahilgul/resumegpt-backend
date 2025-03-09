from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from sqlalchemy.future import select
from .. import models, auth
from ..database import get_db
from ..resume_analyzer import ResumeAnalyzer
from pydantic import BaseModel
import json

router = APIRouter(
    prefix="/resume",
    tags=["resume"],
    responses={404: {"description": "Not found"}},
)

# Models
class ResumeBase(BaseModel):
    name: str

class ResumeCreate(ResumeBase):
    content: str

class Resume(ResumeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class AnalysisResult(BaseModel):
    id: int
    matched_tech_skills: List
    matched_soft_skills: List
    missing_tech_skills: List
    missing_soft_skills: List
    suggestions: str

    class Config:
        orm_mode = True

# Initialize resume analyzer
resume_analyzer = ResumeAnalyzer()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=Resume)
async def upload_resume(
    name: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    current_user = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if file is None and text_content is None:
        raise HTTPException(status_code=400, detail="Either file or text content must be provided")
    
    content = ""
    file_path = None
    
    if file:
        # Save the uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Extract text if it's a PDF
        if file_extension.lower() == ".pdf":
            content = resume_analyzer.extract_text_from_pdf(file_path)
        else:
            # For text files
            with open(file_path, "r") as f:
                content = f.read()
    else:
        content = text_content
    
    # Create new resume
    resume = models.Resume(
        name=name,
        content=content,
        file_path=file_path,
        user_id=current_user.id
    )
    
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    return resume

@router.post("/analyze/{resume_id}", response_model=AnalysisResult)
async def analyze_resume(
    resume_id: int,
    job_description: str = Form(...),
    current_user = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # # Get the resume
    # resume = await db.query(models.Resume).filter(
    #     models.Resume.id == resume_id,
    #     models.Resume.user_id == current_user.id
    # ).first()

    # resume = db.query(models.Resume).filter(
    #     models.Resume.id == resume_id,
    #     models.Resume.user_id == current_user.id
    # ).first()

    # result = await db.execute(
    #     models.Resume.__table__.select().where(
    #         models.Resume.id == resume_id, models.Resume.user_id == current_user.id
    #     )
    # )
    # resume = result.scalar_one_or_none()

    result = await db.execute(
        select(models.Resume).where(
            models.Resume.id == resume_id,
            models.Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()  # Fetch ORM object
    
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Analyze the resume
    analysis = await resume_analyzer.analyze_resume(
        resume.content,
        job_description,
        db,
        current_user.id,
        resume_id
    )
    
    # Parse JSON fields
    result = {
        "id": analysis.id,
        "matched_tech_skills": json.loads(analysis.matched_tech_skills),
        "matched_soft_skills": json.loads(analysis.matched_soft_skills),
        "missing_tech_skills": json.loads(analysis.missing_tech_skills),
        "missing_soft_skills": json.loads(analysis.missing_soft_skills),
        "suggestions": analysis.suggestions
    }
    
    return result

@router.post("/analyze-text", response_model=AnalysisResult)
def analyze_resume_text(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    current_user = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Analyze the resume text directly
    analysis = resume_analyzer.analyze_resume(
        resume_text,
        job_description,
        db,
        current_user.id
    )
    
    # Parse JSON fields
    result = {
        "id": analysis.id,
        "matched_tech_skills": json.loads(analysis.matched_tech_skills),
        "matched_soft_skills": json.loads(analysis.matched_soft_skills),
        "missing_tech_skills": json.loads(analysis.missing_tech_skills),
        "missing_soft_skills": json.loads(analysis.missing_soft_skills),
        "suggestions": analysis.suggestions
    }
    
    return result

@router.get("/history", response_model=List[AnalysisResult])
def get_analysis_history(
    current_user = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    analyses = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.user_id == current_user.id
    ).all()
    
    results = []
    for analysis in analyses:
        results.append({
            "id": analysis.id,
            "matched_tech_skills": json.loads(analysis.matched_tech_skills),
            "matched_soft_skills": json.loads(analysis.matched_soft_skills),
            "missing_tech_skills": json.loads(analysis.missing_tech_skills),
            "missing_soft_skills": json.loads(analysis.missing_soft_skills),
            "suggestions": analysis.suggestions
        })
    
    return results