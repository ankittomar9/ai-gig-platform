import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

COMMON_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "node.js",
    "sql", "postgresql", "mysql", "mongodb", "fastapi", "flask", "django", "spring boot",
    "machine learning", "deep learning", "nlp", "llm", "rlhf", "prompt engineering",
    "data annotation", "data labeling", "content moderation", "fact checking", "model evaluation",
    "mathematics", "calculus", "linear algebra", "statistics", "data analysis",
    "git", "docker", "kubernetes", "aws", "gcp", "azure", "linux", "api",
    "creative writing", "technical writing", "copywriting", "proofreading", "linguistics",
    "translation", "hindi", "spanish", "french", "german", "critical thinking", "reasoning"
]

def extract_text_from_file(file_path: Path) -> str:
    """Extract text from docx or txt. Raises ValueError on failure."""
    ext = file_path.suffix.lower()
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            if not text.strip():
                raise ValueError("The uploaded .docx document contains no extractable text.")
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from .docx file: {e}")
    elif ext in [".txt", ".md"]:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            if not text.strip():
                raise ValueError("The uploaded text document is empty.")
            return text
        except Exception as e:
            raise ValueError(f"Failed to read text file: {e}")
    raise ValueError(f"Unsupported file format '{ext}'. Only .docx, .txt, and .md files are supported.")

CANONICAL_SKILL_NAMES = {
    "sql": "SQL",
    "api": "API",
    "nlp": "NLP",
    "llm": "LLM",
    "rlhf": "RLHF",
    "aws": "AWS",
    "gcp": "GCP",
    "c++": "C++",
    "c#": "C#",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "spring boot": "Spring Boot",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
}

def format_skill_name(skill: str) -> str:
    s_lower = skill.lower()
    return CANONICAL_SKILL_NAMES.get(s_lower, skill.title())

def extract_skills_from_text(text: str) -> List[str]:
    """Identify matched skills in resume text"""
    text_lower = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        # Match word boundaries
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(format_skill_name(skill))
    return sorted(list(set(found)))

def calculate_match_score(job_title: str, job_desc: str, user_skills: List[str], user_resume: str) -> Tuple[int, List[str]]:
    """
    Computes a match score from 0 to 100 based on overlap
    between user skills/resume and job requirements.
    """
    job_content = f"{job_title} {job_desc}".lower()
    user_skills_lower = [s.lower() for s in user_skills]
    
    # 1. Direct skill overlap
    matching_skills = []
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, job_content):
            if skill in user_skills_lower or re.search(pattern, user_resume.lower()):
                matching_skills.append(format_skill_name(skill))

    # Base score
    score = 35 # baseline interest
    
    # Matching skills bonus (up to 40 pts)
    if matching_skills:
        score += min(45, len(matching_skills) * 9)

    # Title keyword match bonus (capped at 20 pts as documented)
    title_words = [w for w in re.findall(r'\w+', job_title.lower()) if len(w) > 3]
    title_bonus = 0
    for w in title_words:
        if w in user_resume.lower() or w in user_skills_lower:
            title_bonus += 6
    score += min(20, title_bonus)

    # Cap score
    score = max(20, min(98, score))
    return score, sorted(list(set(matching_skills)))
