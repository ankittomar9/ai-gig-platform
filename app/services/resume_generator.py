import re
from typing import Dict, Any, List
from app.database import get_job_by_id, get_user_profile

def generate_tailored_resume(job_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    job = get_job_by_id(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")

    title = job.get("title", "AI Specialist")
    company = job.get("company", "Company")
    category = job.get("category", "Generalist")
    tier = job.get("tier", "Mid-Tier ($15-$30)")
    job_desc = job.get("description", "")
    
    candidate_name = profile.get("name") or "Candidate Name"
    email = profile.get("email") or "candidate@example.com"
    phone = profile.get("phone") or "+91 XXXXX XXXXX"
    linkedin = profile.get("linkedin") or "linkedin.com/in/candidate"
    skills = profile.get("skills", ["Java", "Python", "SQL", "Docker", "GCP", "Linux", "API"])

    # 1. Adapt Summary & Positioning based on the Job Category & Tier
    if category == "Coding" or "Software" in title or "Engineer" in title:
        summary = (
            f"Software Engineer & Systems Specialist with proven expertise in enterprise architectures, backend systems, "
            f"API integration, and algorithmic problem-solving. Skilled in high-velocity debugging, code verification, and "
            f"producing high-quality software solutions and documentation aligned with {company}'s technical standards."
        )
        core_skills = ["Software Engineering", "System Architecture", "API Design", "Python", "Java", "Debugging", "Data Structures", "Git"]
        exp_bullet_1 = f"Designed and evaluated backend workflows and cloud services, maintaining robust uptime and zero-defect code standards."
        exp_bullet_2 = f"Conducted rigorous code reviews, identifying performance bottlenecks, edge-case vulnerabilities, and logic flaws."
        exp_bullet_3 = f"Created unit and integration test suites, ensuring 100% adherence to technical specifications."

    elif category == "Writing & RLHF" or "RLHF" in title or "Trainer" in title or "Tutor" in title:
        summary = (
            f"AI Evaluation & Domain Specialist with a strong analytical engineering background. Experienced in structured "
            f"prompt engineering, pairwise model output ranking, hallucination detection, and detailed rubric scoring. "
            f"Committed to delivering high-precision ground truth datasets for frontier AI models at {company}."
        )
        core_skills = ["RLHF Guidelines", "Hallucination Detection", "Pairwise Ranking", "Prompt Engineering", "Technical Writing", "Quality Assurance"]
        exp_bullet_1 = f"Analyzed complex LLM responses against strict factual, safety, and instructional constraints."
        exp_bullet_2 = f"Produced detailed rubric justifications explaining why chosen outputs excelled in helpfulness and accuracy."
        exp_bullet_3 = f"Identified subtle adversarial edge cases and factual inconsistencies in generative model outputs."

    elif "Microtask" in tier or category == "Generalist" or "Evaluator" in title or "Assessor" in title:
        summary = (
            f"Detail-oriented Quality & Data Evaluation Specialist with expertise in digital workflows, structured guideline "
            f"compliance, and precision verification. Recognized for high-speed, accurate task completion and consistent "
            f"quality score maintenance across data annotation and verification benchmarks."
        )
        core_skills = ["Data Verification", "Guideline Compliance", "Attention to Detail", "Quality Assurance", "Search Relevance", "Multimodal Evaluation"]
        exp_bullet_1 = f"Executed data evaluation and accuracy audits with >99% quality benchmark compliance."
        exp_bullet_2 = f"Followed comprehensive project guidelines, applying objective criteria to verify complex data samples."
        exp_bullet_3 = f"Maintained rapid turnaround time while consistently exceeding quality thresholds on target metrics."

    else: # Production Systems / DevOps / General Tech
        summary = (
            f"Application Production Systems Specialist with extensive experience managing high-availability environments, "
            f"incident triage, monitoring, cloud infrastructure (GCP/Docker), and cross-functional technical operations. "
            f"Dedicated to operational excellence and automated quality control."
        )
        core_skills = ["Production Systems", "Incident Management", "Docker", "GCP", "Linux Administration", "API Monitoring", "SQL"]
        exp_bullet_1 = f"Managed application production systems, monitoring metrics and resolving critical operational incidents within SLA."
        exp_bullet_2 = f"Automated recurring maintenance and verification tasks using shell scripting, Python, and cloud tooling."
        exp_bullet_3 = f"Collaborated across engineering and operations teams to optimize infrastructure performance and reliability."

    # Format into ready-to-submit Resume Text (ATS Friendly Markdown)
    formatted_resume = f"""==================================================
TAILORED ATS RESUME: {title} at {company}
==================================================

{candidate_name.upper()}
Email: {email} | Phone: {phone} | Location: Remote / India
LinkedIn: {linkedin}

--------------------------------------------------
PROFESSIONAL SUMMARY
--------------------------------------------------
{summary}

--------------------------------------------------
CORE COMPETENCIES & KEYWORDS
--------------------------------------------------
{', '.join(core_skills)}
Additional Technical Proficiencies: {', '.join(skills)}

--------------------------------------------------
PROFESSIONAL EXPERIENCE & RELEVANT PROJECTS
--------------------------------------------------
Systems Specialist & Technical Contributor
2022 - Present
• {exp_bullet_1}
• {exp_bullet_2}
• {exp_bullet_3}
• Utilized Linux, Docker, GCP, Git, and automated workflows to ensure reproducible, high-standard outputs.

--------------------------------------------------
EDUCATION & CREDENTIALS
--------------------------------------------------
Bachelor of Engineering / Computer Science Background
Continuous Certification in Modern AI Evaluation & Software Architecture
==================================================
"""

    return {
        "job_id": job_id,
        "company": company,
        "role_title": title,
        "category": category,
        "tier": tier,
        "tailored_summary": summary,
        "core_skills": core_skills,
        "formatted_resume": formatted_resume
    }
