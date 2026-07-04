from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import jobs, resumes

app = FastAPI(
    title="Talent AI API",
    description="API for the AI Resume Screening System",
    version="1.0.0"
)

# Allow requests from the Next.js frontend (e.g., localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
app.include_router(resumes.router)

@app.get("/")
def root():
    return {"message": "Talent AI API is running."}

@app.get("/health")
def health():
    return {"status": "ok"}
