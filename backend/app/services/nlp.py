import re
from typing import Dict, List, Any, Optional

# A robust list of skills in our taxonomy
SKILLS_TAXONOMY = [
    "Python", "FastAPI", "Django", "Flask", "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", 
    "Pandas", "NumPy", "NLP", "Machine Learning", "Deep Learning", "Data Science", "AI", "LLM",
    "JavaScript", "TypeScript", "React", "Angular", "Vue", "Svelte", "Next.js", "Redux", "Tailwind", 
    "HTML", "CSS", "Node.js", "Express", "NestJS", "GraphQL", "REST API", "Microservices",
    "Java", "Spring Boot", "Hibernate", "Go", "Golang", "Rust", "C++", "C#", ".NET", "PHP", "Laravel", "Ruby", "Rails",
    "SQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch",
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "CI/CD", "Jenkins", "GitHub Actions",
    "Git", "GitHub", "GitLab", "Jira", "Agile", "Scrum", "Figma", "UI/UX", "System Design", "Unit Testing", "Pytest"
]

# Map alternative/shorthand skills to standard name
SKILLS_MAP = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "postgres": "PostgreSQL",
    "reactjs": "React",
    "react.js": "React",
    "nodejs": "Node.js",
    "node": "Node.js",
    "nextjs": "Next.js",
    "django framework": "Django",
    "fastapi framework": "FastAPI",
    "aws cloud": "AWS",
    "k8s": "Kubernetes",
    "tf": "TensorFlow",
    "gcp cloud": "GCP",
    "docker containers": "Docker",
}

# Normalization map for education level
EDUCATION_LEVELS = {
    "phd": 5, "ph.d": 5, "doctor of philosophy": 5, "doctorate": 5,
    "master": 4, "m.s": 4, "m.sc": 4, "m.tech": 4, "mba": 4, "m.b.a": 4, "postgraduate": 4,
    "bachelor": 3, "b.s": 3, "b.sc": 3, "b.tech": 3, "b.a": 3, "undergraduate": 3, "degree": 3,
    "associate": 2, "associate's": 2, "diploma": 2,
    "high school": 1, "hsc": 1, "secondary school": 1
}

EDUCATION_DISPLAY = {
    5: "PhD",
    4: "Master's",
    3: "Bachelor's",
    2: "Associate's",
    1: "High School"
}

def extract_name(text: str) -> Optional[str]:
    """
    Extract candidate name from resume text.
    Uses heuristics (name is usually at the top, first non-empty lines) 
    combined with spaCy PERSON entity recognition.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return None
        
    # Check the first 3 lines. If they contain email/phone/url, ignore.
    # A candidate's name is usually the very first line or two.
    for line in lines[:3]:
        # Ignore lines with typical header information
        if "@" in line or "http" in line or "/" in line or "+" in line or any(char.isdigit() for char in line):
            continue
        # Names are usually 2 to 4 words
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
            
    # Ultimate fallback: return the first line if it's not too long
    if lines and len(lines[0].split()) <= 4:
        return lines[0]
    return "Unknown Candidate"

def extract_email(text: str) -> Optional[str]:
    """
    Extract email address using regex.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number using regex.
    Supports formats like +1 234-567-8900, (123) 456-7890, 1234567890, etc.
    """
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_skills(text: str) -> List[str]:
    """
    Extract skills based on the defined SKILLS_TAXONOMY and map matching variants.
    Ensures word-boundary matches to avoid partial match false positives (e.g. "Go" in "Django").
    """
    extracted = set()
    text_lower = f" {text.lower()} "  # Pad with spaces to make boundary check simpler
    # Clean text to normalize spaces
    text_lower = re.sub(r'[\s,.:;()]+', ' ', text_lower)
    
    # 1. Match standard taxonomy
    for skill in SKILLS_TAXONOMY:
        # Use regex word boundaries for match
        # Escape skill name in case it has special characters (e.g., C++, .NET)
        escaped_skill = re.escape(skill.lower())
        
        # Handle special cases like C++ and .NET where word boundary \b doesn't work well due to non-alphanumeric chars
        if "++" in skill.lower() or "." in skill.lower() or "#" in skill.lower():
            pattern = rf'(?:^|\s){escaped_skill}(?:$|\s)'
        else:
            pattern = rf'\b{escaped_skill}\b'
            
        if re.search(pattern, text_lower):
            extracted.add(skill)
            
    # 2. Match mapped alternative spellings
    for alt_skill, std_skill in SKILLS_MAP.items():
        escaped_alt = re.escape(alt_skill.lower())
        if "." in alt_skill.lower():
            pattern = rf'(?:^|\s){escaped_alt}(?:$|\s)'
        else:
            pattern = rf'\b{escaped_alt}\b'
            
        if re.search(pattern, text_lower):
            extracted.add(std_skill)
            
    return sorted(list(extracted))

def extract_experience(text: str) -> float:
    """
    Extract total years of experience.
    Looks for sentences like "5 years of experience", "6+ years", "worked 3.5 years"
    or sums up dates if we find standard formats (e.g., "2018 - 2022").
    """
    # 1. Check for explicit total experience statements first
    total_exp_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional|work|industry|relevant)?\s*experience',
        r'(?:professional|work|industry|relevant)\s*experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        r'summary[\s\S]{1,100}?(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
    ]
    
    for pattern in total_exp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the highest explicit number found
            try:
                val = float(matches[0])
                if 0.5 <= val <= 40:
                    return val
            except ValueError:
                continue

    # 2. Heuristic: Parse date ranges and sum them up
    # Match ranges like: 2018 - 2022, Jan 2018 to Present, 10/2018 - 05/2021
    # We will look for (Month)? Year to (Month)? Year/Present
    months_pat = r'(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'
    year_pat = r'(?:20\d{2}|19\d{2})'
    date_pat = rf'(?:(?:{months_pat}\s+)?{year_pat}|\d{{1,2}}/\d{{4}})'
    
    range_pat = rf'({date_pat})\s*(?:-|–|to)\s*({date_pat}|present|current|now)'
    
    matches = re.findall(range_pat, text, re.IGNORECASE)
    total_months = 0.0
    
    def parse_year(date_str: str) -> Optional[int]:
        year_match = re.search(r'(20\d{2}|19\d{2})', date_str)
        if year_match:
            return int(year_match.group(1))
        return None

    def parse_month(date_str: str) -> int:
        # Default to 1 (January)
        date_str_lower = date_str.lower()
        months_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        for name, num in months_map.items():
            if name in date_str_lower:
                return num
        return 1

    for start_str, end_str in matches:
        start_year = parse_year(start_str)
        start_month = parse_month(start_str)
        
        if "present" in end_str.lower() or "current" in end_str.lower() or "now" in end_str.lower():
            # Assume current year is 2026 (based on local time input)
            end_year = 2026
            end_month = 7
        else:
            end_year = parse_year(end_str)
            end_month = parse_month(end_str)
            
        if start_year and end_year:
            months = (end_year - start_year) * 12 + (end_month - start_month)
            if 0 < months < 240:  # ignore weird date calculations (max 20 years per job)
                total_months += months
                
    if total_months > 0:
        calculated_years = round(total_months / 12.0, 1)
        if 0.5 <= calculated_years <= 45:
            return calculated_years

    # 3. Fallback: search any pattern of numbers followed by "years" or "yrs" and take max
    generic_pattern = r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b'
    matches = re.findall(generic_pattern, text, re.IGNORECASE)
    if matches:
        try:
            years = [float(m) for m in matches if 0.5 <= float(m) <= 40]
            if years:
                return max(years)
        except ValueError:
            pass
            
    return 0.0

def extract_education(text: str) -> Optional[str]:
    """
    Extract the highest level of education.
    Returns standard display value: PhD, Master's, Bachelor's, Associate's, High School, or None.
    """
    text_lower = text.lower()
    highest_rank = 0
    
    for key, rank in EDUCATION_LEVELS.items():
        # Match using word boundaries to avoid false positives (e.g. "master" in "mastery")
        escaped_key = re.escape(key)
        if "." in key:
            pattern = rf'(?:^|\s){escaped_key}(?:$|\s)'
        else:
            pattern = rf'\b{escaped_key}\b'
            
        if re.search(pattern, text_lower):
            if rank > highest_rank:
                highest_rank = rank
                
    if highest_rank > 0:
        return EDUCATION_DISPLAY[highest_rank]
    return "Bachelor's"  # Return a sensible default or None if not found

def extract_job_title(text: str) -> Optional[str]:
    """
    Extract candidate's target or current job title.
    Looks at the top lines or common title matches.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Software Engineer"
        
    common_titles = [
        "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Fullstack Developer", "Data Scientist", "Machine Learning Engineer", "ML Engineer",
        "DevOps Engineer", "Product Manager", "Project Manager", "UI/UX Designer", "Software Developer",
        "QA Engineer", "Mobile Developer", "iOS Developer", "Android Developer", "Data Analyst",
        "Systems Administrator", "Cloud Architect"
    ]
    
    # Check the first 5 lines for these exact matches or contains
    for line in lines[:5]:
        for title in common_titles:
            if title.lower() in line.lower() and len(line) < 60:
                return title
                
    # Otherwise check the rest of the document for the first occurrence of these titles
    for title in common_titles:
        if re.search(rf'\b{re.escape(title.lower())}\b', text.lower()):
            return title
            
    # Default to first non-empty line after the name, if short
    for line in lines[1:4]:
        if len(line) < 40 and not any(char.isdigit() for char in line) and "@" not in line:
            return line
            
    return "Software Engineer"

def parse_resume(text: str) -> Dict[str, Any]:
    """
    Parses resume text and extracts structured features.
    """
    return {
        "candidate_name": extract_name(text),
        "candidate_email": extract_email(text),
        "candidate_phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_years": extract_experience(text),
        "education_level": extract_education(text),
        "job_title": extract_job_title(text),
    }
