from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobDescriptionCreate(BaseModel):
    title: str = Field(..., example="Senior Software Engineer")
    description: str = Field(..., example="Looking for a Python developer with FastAPI and React experience.")
    skills: List[str] = Field(default=[], example=["Python", "FastAPI", "React", "SQL"])
    experience_years: float = Field(default=0.0, example=3.5)
    education_level: Optional[str] = Field(default="Bachelor's", example="Bachelor's")

class JobDescriptionResponse(JobDescriptionCreate):
    id: str
    user_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    job_description_id: str
    file_name: str
    file_path: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0.0
    education_level: Optional[str] = None
    job_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreExplanation(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    experience_gap: float
    experience_status: str
    education_status: str
    summary: str

class MatchResultResponse(BaseModel):
    id: str
    resume_id: str
    job_description_id: str
    total_score: float
    semantic_score: float
    skills_score: float
    experience_score: float
    education_score: float
    explanation: ScoreExplanation
    created_at: datetime
    resume: Optional[ResumeResponse] = None

    class Config:
        from_attributes = True

class JobRankingResponse(BaseModel):
    rankings: List[MatchResultResponse]
