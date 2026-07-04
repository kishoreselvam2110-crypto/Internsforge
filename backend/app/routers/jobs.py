from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client

from ..dependencies import get_db_client, get_user_id_from_token
from ..models.schemas import JobDescriptionCreate, JobDescriptionResponse
from ..services.embedding import embedding_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobDescriptionResponse)
def create_job(
    job: JobDescriptionCreate, 
    db: Client = Depends(get_db_client),
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Create a new job description. Generates a 768-d embedding for semantic search.
    """
    # Create text to embed
    text_to_embed = f"{job.title}. {job.description}. Skills required: {', '.join(job.skills)}."
    
    # Generate deterministic embedding
    embedding = embedding_service.generate_embedding(text_to_embed)
    
    # Prepare payload
    data = job.model_dump()
    data["embedding"] = embedding
    data["user_id"] = user_id
    
    try:
        response = db.table("job_descriptions").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to insert job description (empty response)")
            
        result = response.data[0]
        # Avoid sending back the heavy embedding vector
        if "embedding" in result:
            del result["embedding"]
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.get("/", response_model=List[JobDescriptionResponse])
def list_jobs(db: Client = Depends(get_db_client)):
    """
    List all job descriptions for the authenticated user.
    """
    try:
        # RLS restricts this to only the user's jobs
        response = db.table("job_descriptions").select("id, title, description, skills, experience_years, education_level, created_at, user_id").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.get("/{job_id}", response_model=JobDescriptionResponse)
def get_job(job_id: str, db: Client = Depends(get_db_client)):
    """
    Get a specific job description by ID.
    """
    try:
        response = db.table("job_descriptions").select("id, title, description, skills, experience_years, education_level, created_at, user_id").eq("id", job_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Job description not found")
        return response.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
