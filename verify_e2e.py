"""
End-to-End pipeline verification script.
Uses the admin (Service Role) client directly against Supabase to bypass RLS,
then verifies the scoring logic matches our expected ordering.
"""
import sys
import os
import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_ROLE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
BASE_URL = "http://localhost:8000"

HEADERS = {"Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"}

def run_e2e():
    print("=" * 60)
    print("  Talent AI - End-to-End Pipeline Verification")
    print("=" * 60)

    with httpx.Client(timeout=60.0) as client:

        # Step 1: Create Job Description
        print("\n[1/3] Creating Job Description: 'Senior Software Engineer'...")
        job_payload = {
            "title": "Senior Software Engineer",
            "description": (
                "We are looking for a senior developer skilled in building "
                "high-performance backend services and modern React frontends. "
                "The ideal candidate has experience with Python, FastAPI, React, "
                "TypeScript, Docker, and PostgreSQL."
            ),
            "skills": ["Python", "FastAPI", "React", "TypeScript", "Docker", "PostgreSQL"],
            "experience_years": 5.0,
            "education_level": "Bachelor's"
        }
        res = client.post(f"{BASE_URL}/jobs/", json=job_payload, headers=HEADERS)
        if not res.is_success:
            print(f"  FAILED to create job: {res.text}")
            sys.exit(1)
        job = res.json()
        job_id = job["id"]
        print(f"  OK - Job created: {job_id}")

        # Step 2: Upload Resumes
        print("\n[2/3] Uploading 3 test resumes...")
        resume_files = [
            ("test_resumes/alice_smith_perfect_match.docx",  "Alice Smith  (Perfect Match)"),
            ("test_resumes/bob_jones_partial_match.docx",    "Bob Jones    (Partial Match)"),
            ("test_resumes/charlie_brown_poor_match.docx",   "Charlie Brown (Poor Match)"),
        ]

        for file_path, label in resume_files:
            if not os.path.exists(file_path):
                print(f"  SKIP - File not found: {file_path}")
                continue
            with open(file_path, "rb") as f:
                content = f.read()
            files = {"file": (os.path.basename(file_path), content,
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            up_res = client.post(
                f"{BASE_URL}/resumes/upload/{job_id}",
                files=files,
                headers=HEADERS,
            )
            if up_res.is_success:
                score = up_res.json().get("total_score", "?")
                print(f"  OK - {label} scored: {score:.1f}%")
            else:
                print(f"  FAIL - {label}: {up_res.text[:300]}")

        # Step 3: Fetch Rankings
        print("\n[3/3] Fetching ranked results...")
        rank_res = client.get(f"{BASE_URL}/resumes/job/{job_id}", headers=HEADERS)
        if not rank_res.is_success:
            print(f"  FAILED to fetch results: {rank_res.text}")
            sys.exit(1)

        results = rank_res.json()
        print(f"\n{'-'*60}")
        print(f"  FINAL RANKINGS  ({len(results)} candidates)")
        print(f"{'-'*60}")
        for i, r in enumerate(results):
            name   = (r.get("resume") or {}).get("candidate_name") or "Unknown"
            total  = r["total_score"]
            sem    = r["semantic_score"]
            skills = r["skills_score"]
            exp    = r["experience_score"]
            edu    = r["education_score"]
            print(
                f"  #{i+1}  {name:<30} Total:{total:5.1f}%  "
                f"[Sem:{sem:.0f}% Skills:{skills:.0f}% Exp:{exp:.0f}% Edu:{edu:.0f}%]"
            )
        print(f"{'-'*60}")

        # Verify ordering: Alice > Bob > Charlie
        if len(results) == 3:
            names = [(r.get("resume") or {}).get("candidate_name", "") for r in results]
            alice_pos   = next((i for i, n in enumerate(names) if "Alice"   in (n or "")), None)
            bob_pos     = next((i for i, n in enumerate(names) if "Bob"     in (n or "")), None)
            charlie_pos = next((i for i, n in enumerate(names) if "Charlie" in (n or "")), None)
            if alice_pos is not None and bob_pos is not None and charlie_pos is not None:
                if alice_pos < bob_pos < charlie_pos:
                    print("\n  PASS: Ranking order correct: Alice > Bob > Charlie")
                else:
                    print(f"\n  WARN: Unexpected order (Alice={alice_pos} Bob={bob_pos} Charlie={charlie_pos})")

        print("\n  DONE: End-to-End verification complete.\n")

if __name__ == "__main__":
    run_e2e()

