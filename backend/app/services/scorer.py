from typing import Dict, Any, List, Tuple
from app.config import settings
from app.services.nlp import EDUCATION_LEVELS

def calculate_cosine_similarity(u: List[float], v: List[float]) -> float:
    """
    Computes cosine similarity between two vectors.
    Since embeddings are normalized, this is simply the dot product.
    """
    if not u or not v or len(u) != len(v):
        return 0.0
    return sum(x * y for x, y in zip(u, v))

def compute_match_score(
    job_desc: Dict[str, Any],
    resume_desc: Dict[str, Any],
    job_embedding: List[float],
    resume_embedding: List[float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Computes a hybrid match score out of 100 based on:
    - 50% Semantic similarity
    - 30% Explicit skills overlap
    - 10% Experience level match
    - 10% Education level match
    
    Weights are loaded from settings (defaulting to 0.50, 0.30, 0.10, 0.10).
    Returns total_score, score_breakdown, and a natural language explanation.
    """
    # 1. Semantic Similarity Score (0-100)
    raw_sim = calculate_cosine_similarity(job_embedding, resume_embedding)
    # Clamp cosine similarity between 0 and 1, then scale to 0-100
    semantic_score = max(0.0, min(1.0, raw_sim)) * 100.0
    
    # 2. Skills Overlap Score (0-100)
    req_skills = [s.strip().lower() for s in job_desc.get("skills", []) if s.strip()]
    cand_skills = [s.strip().lower() for s in resume_desc.get("skills", []) if s.strip()]
    
    matched_skills = []
    missing_skills = []
    
    if req_skills:
        for req in req_skills:
            # Case-insensitive match, but preserve the original requirement casing in output
            found = any(req.lower() == cand.lower() for cand in cand_skills)
            if found:
                matched_skills.append(req)   # preserve original casing
            else:
                missing_skills.append(req)   # preserve original casing
        
        skills_score = (len(matched_skills) / len(req_skills)) * 100.0
    else:
        # No skills required = full marks
        skills_score = 100.0
        
    # 3. Experience Match Score (0-100)
    req_exp = float(job_desc.get("experience_years", 0.0))
    cand_exp = float(resume_desc.get("experience_years", 0.0))
    
    if req_exp <= 0.0:
        experience_score = 100.0
        exp_gap_val = cand_exp
        exp_status = f"No experience required. Candidate has {cand_exp} years."
    else:
        exp_gap_val = cand_exp - req_exp
        if cand_exp >= req_exp:
            experience_score = 100.0
            exp_status = f"Meets or exceeds requirement (Candidate has {cand_exp} years, required: {req_exp} years)."
        else:
            # Gradual penalty
            experience_score = (cand_exp / req_exp) * 100.0
            exp_status = f"Missing {abs(exp_gap_val):.1f} years of experience (Candidate has {cand_exp} years, required: {req_exp} years)."
            
    # 4. Education Match Score (0-100)
    req_edu_str = (job_desc.get("education_level") or "Bachelor's").lower()
    cand_edu_str = (resume_desc.get("education_level") or "Bachelor's").lower()
    
    # Clean up string matching
    def get_edu_rank(edu_str: str) -> int:
        for key, rank in EDUCATION_LEVELS.items():
            if key in edu_str:
                return rank
        return 3 # Default to Bachelor's (rank 3)
        
    req_edu_rank = get_edu_rank(req_edu_str)
    cand_edu_rank = get_edu_rank(cand_edu_str)
    
    if cand_edu_rank >= req_edu_rank:
        education_score = 100.0
        edu_status = f"Meets or exceeds requirement (Candidate: {resume_desc.get('education_level') or "Bachelor's"}, Required: {job_desc.get('education_level') or "Bachelor's"})."
    elif cand_edu_rank == req_edu_rank - 1:
        education_score = 50.0
        edu_status = f"Below requirement by 1 level (Candidate: {resume_desc.get('education_level') or "Bachelor's"}, Required: {job_desc.get('education_level') or "Bachelor's"})."
    else:
        education_score = 0.0
        edu_status = f"Significantly below requirement (Candidate: {resume_desc.get('education_level') or "Bachelor's"}, Required: {job_desc.get('education_level') or "Bachelor's"})."
        
    # 5. Hybrid Weighted Score
    w_sem = settings.WEIGHT_SEMANTIC
    w_skills = settings.WEIGHT_SKILLS
    w_exp = settings.WEIGHT_EXPERIENCE
    w_edu = settings.WEIGHT_EDUCATION
    
    # Assert weights sum to 1.0 roughly
    total_weight = w_sem + w_skills + w_exp + w_edu
    if not (0.99 <= total_weight <= 1.01):
        # Normalize weights if they don't sum to 1.0
        w_sem /= total_weight
        w_skills /= total_weight
        w_exp /= total_weight
        w_edu /= total_weight
        
    total_score = (
        w_sem * semantic_score +
        w_skills * skills_score +
        w_exp * experience_score +
        w_edu * education_score
    )
    
    # Round scores to 2 decimal places
    total_score = round(total_score, 2)
    semantic_score = round(semantic_score, 2)
    skills_score = round(skills_score, 2)
    experience_score = round(experience_score, 2)
    education_score = round(education_score, 2)
    
    # 6. Generate Plain-Language Summary
    candidate_name = resume_desc.get("candidate_name", "The candidate")
    job_title = job_desc.get("title", "this position")
    
    summary_parts = []
    
    if total_score >= 85:
        summary_parts.append(f"{candidate_name} is an exceptional match for the {job_title} role with a total score of {total_score}%.")
    elif total_score >= 70:
        summary_parts.append(f"{candidate_name} is a strong candidate for the {job_title} role with a total score of {total_score}%.")
    elif total_score >= 50:
        summary_parts.append(f"{candidate_name} is a moderate match for the {job_title} role with a total score of {total_score}%.")
    else:
        summary_parts.append(f"{candidate_name} is a weak match for the {job_title} role with a total score of {total_score}%.")
        
    # Skills commentary
    if matched_skills:
        skill_comment = f"Demonstrates strong technical alignment with key matching skills including: {', '.join(matched_skills[:4])}."
        if missing_skills:
            skill_comment += f" However, they are missing some required skills: {', '.join(missing_skills[:3])}."
        summary_parts.append(skill_comment)
    elif req_skills:
        summary_parts.append(f"Does not list any of the explicitly required skills: {', '.join(req_skills[:3])}.")
        
    # Experience commentary
    if exp_gap_val >= 0:
        summary_parts.append(f"Meets the experience requirement with {cand_exp} years of relevant experience.")
    else:
        summary_parts.append(f"Has {cand_exp} years of experience, resulting in an experience gap of {abs(exp_gap_val):.1f} years.")
        
    # Education commentary
    if cand_edu_rank >= req_edu_rank:
        edu = resume_desc.get("education_level", "Bachelor's")
        if not edu: edu = "Bachelor's"
        summary_parts.append(f"Meets the education standard with a {edu} degree.")
    else:
        c_edu = resume_desc.get("education_level", "Bachelor's")
        j_edu = job_desc.get("education_level", "Bachelor's")
        if not c_edu: c_edu = "Bachelor's"
        if not j_edu: j_edu = "Bachelor's"
        summary_parts.append(f"Has a {c_edu} degree, which is below the requested {j_edu} degree.")
        
    summary = " ".join(summary_parts)
    
    explanation = {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_gap": round(exp_gap_val, 2),
        "experience_status": exp_status,
        "education_status": edu_status,
        "summary": summary
    }
    
    return total_score, {
        "total_score": total_score,
        "semantic_score": semantic_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "explanation": explanation
    }
