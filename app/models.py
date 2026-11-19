from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class JobItem(BaseModel):
    id: str
    platform: str
    title: str
    company: str
    url: str
    compensation: str = "Unspecified"
    comp_min: float = 0.0
    comp_max: float = 0.0
    comp_unit: str = "hr"  # 'hr', 'task', 'annual'
    tier: str = "Mid-Tier ($15-$30)" # 'Microtask ($2-$15)', 'Mid-Tier ($15-$30)', 'Expert ($30-$100+)'
    category: str = "Generalist" # 'Coding', 'Writing & RLHF', 'Math & Reasoning', 'Generalist', 'Multilingual'
    location: str = "Remote"
    requires_interview: str = "AI Interview" # 'No Interview / Direct', 'Automated Test', 'AI Interview', 'Human Interview'
    description: str = ""
    match_score: int = 0
    matching_skills: List[str] = []
    scraped_at: str = ""
    is_saved: bool = False
    application_status: str = "new" # 'new', 'applied', 'interviewing', 'offer', 'archived'

class UserProfile(BaseModel):
    name: str = "Candidate"
    email: Optional[str] = "candidate@example.com"
    phone: Optional[str] = "+91 XXXXX XXXXX"
    linkedin: Optional[str] = "linkedin.com/in/candidate"
    skills: List[str] = []
    resume_text: str = ""
    target_rate: float = 20.0
    experience_years: int = 2
    preferred_categories: List[str] = ["Coding", "Writing & RLHF", "Generalist"]

class ApplicationPack(BaseModel):
    job_id: str
    company: str
    role_title: str
    apply_url: str
    why_interested: str
    relevant_experience: str
    quality_assurance_strategy: str
    master_interview_prompt: str
    one_click_bundle: Optional[str] = None
    is_humanized: bool = True

class InterviewMessage(BaseModel):
    sender: str # 'ai' or 'user'
    message: str
    round_number: int = 1
    feedback: Optional[str] = None
    score: Optional[int] = None
    suggested_answer: Optional[str] = None

class InterviewSession(BaseModel):
    session_id: str
    job_id: str
    company: str
    role_title: str
    current_round: int = 1
    total_rounds: int = 4
    round_name: str = "Screening & Background"
    is_completed: bool = False
    overall_score: Optional[int] = None
    feedback_summary: str = ""
    messages: List[InterviewMessage] = []

class InterviewChatRequest(BaseModel):
    session_id: str
    job_id: str
    user_message: str

class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    groq_api_key: Optional[str] = None
    offline_mode: Optional[bool] = None
    minimum_rate: Optional[float] = None

class JobStatusUpdate(BaseModel):
    status: str
