from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from sqlalchemy import select
from .. import models, auth
from ..database import get_db
from ..models import User
from ..resume_analyzer import ResumeAnalyzer
from pydantic import BaseModel
import json

router = APIRouter(
    prefix="/resume",
    tags=["resume"],
    responses={404: {"description": "Not found"}},
)


import logging

logger = logging.getLogger(__name__)


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
async def analyze_resume_text(
    job_description: str = Form(...),
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    current_user=Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Extract resume text from file if provided
    if resume_file:
        try:
            content = await resume_file.read()
            resume_text = content.decode("utf-8")  # Ensure proper decoding
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    if not resume_text:
        return {"error": "No resume text provided"}

    # Analyze the resume text
    analysis = await resume_analyzer.analyze_resume(
        resume_text,
        job_description,
        db,
        current_user.id
    )

    # Parse JSON fields safely
    result = {
        "id": analysis.id,
        "matched_tech_skills": json.loads(analysis.matched_tech_skills or "[]"),
        "matched_soft_skills": json.loads(analysis.matched_soft_skills or "[]"),
        "missing_tech_skills": json.loads(analysis.missing_tech_skills or "[]"),
        "missing_soft_skills": json.loads(analysis.missing_soft_skills or "[]"),
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





# backend/app/routers/resume.py
from app.auth import get_current_user

# backend/app/routers/resume.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@router.get("/recent")
async def get_recent_resumes(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent resume uploads for the current user
    """
    try:
        

        # Make sure we're using the correct async pattern
        stmt = select(models.Resume).where(
            models.Resume.user_id == current_user.id
        ).order_by(models.Resume.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        recent_resumes = result.scalars().all()

        query = text("""
            SELECT id, filename, created_at
            FROM resumes 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)


        result = await db.execute(query, {"user_id": current_user.id, "limit": limit})
        recent_resumes = result.mappings().all()

        
        result = []
        for resume in recent_resumes:
            result.append({
                "id": resume.id,
                "filename": resume.filename,
                "created_at": resume.created_at,
                "status": "analyzed" if hasattr(resume, "analyses") and resume.analyses else "uploaded"
            })
        
        return result
    except Exception as e:
        print('Recent Error')
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recent resumes: {str(e)}")
    

@router.get("/stats")
async def get_resume_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get statistics about resume analyses for the current user's dashboard
    """
    try:
        # Get all resume analyses for the current user
        # For async SQLAlchemy
        
        
        from sqlalchemy import text

        # Get all resume analyses for the current user (only fetch once)
        result = await db.execute(
            text("SELECT * FROM resumes WHERE user_id = :user_id"),
            {"user_id": current_user.id}
        )
        user_resumes = result.fetchall()

        
        # Calculate statistics
        total_resumes = len(user_resumes)
        
        # If there are no resumes, return empty stats
        if total_resumes == 0:
            return {
                "total_resumes": 0,
                "latest_analysis": None,
                "average_match_score": 0,
                "skill_gaps": [],
                "improvement_areas": []
            }
        
        # Get the latest analysis
        latest_resume = max(user_resumes, key=lambda x: x.created_at)
        latest_analysis = {
            "id": latest_resume.id,
            "filename": latest_resume.filename,
            "created_at": latest_resume.created_at,
            "match_score": latest_resume.match_score if hasattr(latest_resume, "match_score") else 0
        }
        
        # Calculate average match score if applicable
        resumes_with_scores = [r for r in user_resumes if hasattr(r, "match_score") and r.match_score is not None]
        average_match_score = sum(r.match_score for r in resumes_with_scores) / len(resumes_with_scores) if resumes_with_scores else 0
        
        # Get common skill gaps and improvement areas
        # This would ideally be calculated from analysis results stored in the database
        # For now, we'll return placeholder data
        skill_gaps = ["Python", "React", "FastAPI"] if total_resumes > 0 else []
        improvement_areas = ["Resume Structure", "Skills Section", "Experience Details"] if total_resumes > 0 else []
        
        return {
            "total_resumes": total_resumes,
            "latest_analysis": latest_analysis,
            "average_match_score": average_match_score,
            "skill_gaps": skill_gaps,
            "improvement_areas": improvement_areas
        }
    except Exception as e:
        print('Stats Error')
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard stats: {str(e)}")

# backend/app/routers/resume.py
from app.models import ResumeAnalysis

@router.get("/{resume_id}")
async def get_resume_details(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific resume
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get the latest analysis if it exists
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.resume_id == resume.id
    ).order_by(ResumeAnalysis.created_at.desc()).first()
    
    result = {
        "id": resume.id,
        "filename": resume.filename,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "has_analysis": bool(analysis),
        "file_path": resume.file_path
    }
    
    if analysis:
        result["analysis"] = {
            "id": analysis.id,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "match_score": analysis.match_score,
            "data": analysis.analysis_data or {}
        }
    
    return result


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_pasted_resume(
    resumeText: str = Form(...),
    job_description: str = Form(...),
    current_user = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Directly analyze the pasted resume without fetching from DB
    analysis = await resume_analyzer.analyze_resume(
        resumeText,
        job_description,
        db,
        current_user.id,
        resume_id=None  # No DB ID since it's pasted
    )
    
    result = {
        "id": analysis.id,
        "matched_tech_skills": json.loads(analysis.matched_tech_skills),
        "matched_soft_skills": json.loads(analysis.matched_soft_skills),
        "missing_tech_skills": json.loads(analysis.missing_tech_skills),
        "missing_soft_skills": json.loads(analysis.missing_soft_skills),
        "suggestions": analysis.suggestions
    }
    
    return result
