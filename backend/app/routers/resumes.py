from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from supabase import Client
import uuid

from ..dependencies import get_db_client, get_user_id_from_token
from ..models.schemas import MatchResultResponse, ResumeResponse
from ..services.embedding import embedding_service
from ..services.extractor import extract_text
from ..services.nlp import parse_resume
from ..services.scorer import compute_match_score

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload/{job_id}", response_model=MatchResultResponse)
async def upload_and_match_resume(
    job_id: str,
    file: UploadFile = File(...),
    db: Client = Depends(get_db_client),
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Uploads a resume (PDF/DOCX), extracts text and NLP features, generates embedding,
    computes a hybrid match score against the job description, and saves the results.
    """
    # 1. Fetch Job Description
    try:
        job_res = db.table("job_descriptions").select("*").eq("id", job_id).eq("user_id", user_id).execute()
        if not job_res.data:
            raise HTTPException(status_code=404, detail="Job description not found.")
        job_desc = job_res.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
        
    job_embedding = job_desc.get("embedding")
    if not job_embedding:
        raise HTTPException(status_code=500, detail="Job description is missing its vector embedding.")

    # 2. Extract Text
    try:
        file_bytes = await file.read()
        raw_text = extract_text(file_bytes, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
        
    # 3. NLP Parsing
    parsed_features = parse_resume(raw_text)
    
    # 4. Generate Resume Embedding
    text_to_embed = f"{parsed_features.get('job_title', '')}. {parsed_features.get('candidate_name', '')}. Skills: {', '.join(parsed_features.get('skills', []))}."
    # Mix some raw text to capture context if it's not too long (first 2000 chars)
    text_to_embed += f" Resume content: {raw_text[:2000]}"
    
    resume_embedding = embedding_service.generate_embedding(text_to_embed)
    
    # 5. Upload File to Supabase Storage
    # Path format: {user_id}/{job_id}/{uuid}_{filename}
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
    safe_filename = f"{uuid.uuid4().hex[:8]}.{file_ext}"
    storage_path = f"{user_id}/{job_id}/{safe_filename}"
    
    try:
        # Supabase python client doesn't fully support async file uploads natively yet, so we use sync
        db.storage.from_("resumes").upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        # If it fails, maybe it already exists, or RLS error.
        print(f"Storage upload error: {str(e)}")
        # We will continue even if storage fails for robustness, but ideally it shouldn't.

    # 6. Save Resume Record
    resume_data = {
        "user_id": user_id,
        "job_description_id": job_id,
        "file_name": file.filename,
        "file_path": storage_path,
        "raw_text": raw_text[:10000], # truncate to avoid massive payloads
        "candidate_name": parsed_features.get("candidate_name"),
        "candidate_email": parsed_features.get("candidate_email"),
        "candidate_phone": parsed_features.get("candidate_phone"),
        "skills": parsed_features.get("skills", []),
        "experience_years": parsed_features.get("experience_years", 0.0),
        "education_level": parsed_features.get("education_level"),
        "job_title": parsed_features.get("job_title"),
        "embedding": resume_embedding
    }
    
    try:
        resume_res = db.table("resumes").insert(resume_data).execute()
        resume_record = resume_res.data[0]
        resume_id = resume_record["id"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save resume: {str(e)}")

    # 7. Compute Match Score
    total_score, breakdown = compute_match_score(job_desc, resume_data, job_embedding, resume_embedding)
    
    # 8. Save Match Result
    match_data = {
        "user_id": user_id,
        "job_description_id": job_id,
        "resume_id": resume_id,
        "total_score": breakdown["total_score"],
        "semantic_score": breakdown["semantic_score"],
        "skills_score": breakdown["skills_score"],
        "experience_score": breakdown["experience_score"],
        "education_score": breakdown["education_score"],
        "explanation": breakdown["explanation"]
    }
    
    try:
        match_res = db.table("match_results").insert(match_data).execute()
        match_record = match_res.data[0]
        # Attach the resume payload for the frontend
        match_record["resume"] = resume_record
        return match_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save match result: {str(e)}")

@router.get("/job/{job_id}", response_model=List[MatchResultResponse])
def get_job_rankings(job_id: str, db: Client = Depends(get_db_client), user_id: str = Depends(get_user_id_from_token)):
    """
    Get all ranked resumes for a specific job description.
    """
    try:
        response = db.table("match_results").select("*, resume:resumes(*)").eq("job_description_id", job_id).eq("user_id", user_id).order("total_score", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
