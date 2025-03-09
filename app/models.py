from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)  # Added length
    username = Column(String(150), unique=True, index=True)  # Added length
    hashed_password = Column(String(255))  # Added length
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    resumes = relationship("Resume", back_populates="owner")
    analyses = relationship("ResumeAnalysis", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # Added length
    content = Column(Text)
    file_path = Column(String(500), nullable=True)  # Added length
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  # Ensure foreign key constraints

    owner = relationship("User", back_populates="resumes")
    analyses = relationship("ResumeAnalysis", back_populates="resume")

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    job_description = Column(Text)
    matched_tech_skills = Column(JSON, nullable=True)
    matched_soft_skills = Column(JSON, nullable=True)
    missing_tech_skills = Column(JSON, nullable=True)
    missing_soft_skills = Column(JSON, nullable=True)
    suggestions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
