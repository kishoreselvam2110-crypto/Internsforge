import os
from dotenv import load_dotenv

# Load local .env if it exists
load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Weight settings for scoring (must sum to 1.0)
    WEIGHT_SEMANTIC: float = float(os.getenv("WEIGHT_SEMANTIC", 0.50))
    WEIGHT_SKILLS: float = float(os.getenv("WEIGHT_SKILLS", 0.30))
    WEIGHT_EXPERIENCE: float = float(os.getenv("WEIGHT_EXPERIENCE", 0.10))
    WEIGHT_EDUCATION: float = float(os.getenv("WEIGHT_EDUCATION", 0.10))

settings = Settings()
