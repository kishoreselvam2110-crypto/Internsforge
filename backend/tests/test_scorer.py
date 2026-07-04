"""
Unit tests for the hybrid scorer.
Skills are stored lowercased by the NLP extractor, so assertions use .lower() comparisons.
"""
import pytest
from app.services.scorer import compute_match_score, calculate_cosine_similarity


def test_cosine_similarity():
    """Identical vectors → 1.0, orthogonal vectors → 0.0."""
    u = [1.0, 0.0, 0.0]
    v = [1.0, 0.0, 0.0]
    assert calculate_cosine_similarity(u, v) == 1.0

    w = [0.0, 1.0, 0.0]
    assert calculate_cosine_similarity(u, w) == 0.0


def test_compute_match_score_perfect():
    """
    Identical embeddings + full skill/exp/edu match → 100% on every component.
    Skill names in explanations may be lowercased by the NLP pipeline;
    assertions are therefore case-insensitive.
    """
    job_desc = {
        "title": "Senior Python Developer",
        "skills": ["Python", "FastAPI", "React"],
        "experience_years": 5.0,
        "education_level": "Master's",
    }

    resume_desc = {
        "candidate_name": "Alice Smith",
        "skills": ["Python", "FastAPI", "React", "Docker"],
        "experience_years": 6.0,
        "education_level": "Master's",
        "job_title": "Senior Python Developer",
    }

    # Identical embeddings → cosine similarity = 1.0 → semantic_score = 100
    embedding = [0.1] * 768

    total_score, breakdown = compute_match_score(job_desc, resume_desc, embedding, embedding)

    assert breakdown["semantic_score"] == 100.0
    assert breakdown["skills_score"] == 100.0
    assert breakdown["experience_score"] == 100.0
    assert breakdown["education_score"] == 100.0
    assert breakdown["total_score"] == 100.0
    assert total_score == 100.0

    # Case-insensitive skill checks
    matched_lower = [s.lower() for s in breakdown["explanation"]["matched_skills"]]
    assert "python" in matched_lower
    assert "fastapi" in matched_lower
    assert "react" in matched_lower
    assert breakdown["explanation"]["missing_skills"] == []


def test_compute_match_score_partial():
    """
    Partial skills + under-experienced + lower education → partial scores.
    """
    job_desc = {
        "title": "Data Scientist",
        "skills": ["Python", "Machine Learning", "AWS"],
        "experience_years": 3.0,
        "education_level": "Master's",
    }

    resume_desc = {
        "candidate_name": "Bob Jones",
        "skills": ["Python"],
        "experience_years": 1.5,
        "education_level": "Bachelor's",
        "job_title": "Junior Analyst",
    }

    # Partially overlapping embeddings
    job_emb = [0.5, 0.5] + [0.0] * 766
    res_emb = [0.0, 0.5] + [0.0] * 766

    total_score, breakdown = compute_match_score(job_desc, resume_desc, job_emb, res_emb)

    # 1 of 3 skills matched → 33.33%
    assert 33.0 <= breakdown["skills_score"] <= 34.0

    # 1.5 / 3.0 = 50% experience
    assert breakdown["experience_score"] == 50.0

    # 1 rank below Master's → 50%
    assert breakdown["education_score"] == 50.0

    # Missing skills include AWS and Machine Learning (case-insensitive)
    missing_lower = [s.lower() for s in breakdown["explanation"]["missing_skills"]]
    assert "aws" in missing_lower
    assert "machine learning" in missing_lower

    # Experience gap should be negative (candidate under-qualified)
    assert breakdown["explanation"]["experience_gap"] == -1.5
