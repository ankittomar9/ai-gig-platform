from typing import Dict, Any
from app.services.humanizer import generate_humanized_pack

def generate_application_pack(job: Dict[str, Any], user_profile: Dict[str, Any], humanize: bool = True) -> Dict[str, Any]:
    company = job.get("company", "Company")
    title = job.get("title", "AI Specialist")
    url = job.get("url", "#")
    skills = ", ".join(user_profile.get("skills", ["Python", "Problem Solving", "AI Evaluation"]))
    name = user_profile.get("name", "Applicant")

    if humanize:
        pack = generate_humanized_pack(job, user_profile)
        return {
            "job_id": job.get("id"),
            "company": company,
            "role_title": title,
            "apply_url": url,
            "cover_letter": pack["why_interested"],
            "why_interested": pack["why_interested"],
            "relevant_experience": pack["relevant_experience"],
            "quality_assurance_strategy": pack["quality_assurance_strategy"],
            "master_interview_prompt": pack["master_prompt"],
            "one_click_bundle": pack["one_click_bundle"],
            "is_humanized": True
        }

    # Standard fallback
    why_interested = (
        f"I am interested in contributing to {company}'s AI projects as a {title}. "
        f"With background in {skills}, I focus on structured reasoning and prompt evaluation."
    )
    relevant_experience = f"Experience with {skills}, guideline adherence, and data verification."
    quality_assurance = "3-pass review: instructions verification, factual check, rubric alignment."
    master_prompt = f"Conduct a 4-round interview simulation for {title} at {company}."

    return {
        "job_id": job.get("id"),
        "company": company,
        "role_title": title,
        "apply_url": url,
        "cover_letter": why_interested,
        "why_interested": why_interested,
        "relevant_experience": relevant_experience,
        "quality_assurance_strategy": quality_assurance,
        "master_interview_prompt": master_prompt,
        "one_click_bundle": f"Application for {title} at {company}\n{why_interested}",
        "is_humanized": False
    }
