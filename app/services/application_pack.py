from typing import Dict, Any

def generate_application_pack(job: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    company = job.get("company", "Company")
    title = job.get("title", "AI Specialist")
    url = job.get("url", "#")
    skills = ", ".join(user_profile.get("skills", ["Python", "Problem Solving", "AI Evaluation"]))
    name = user_profile.get("name", "Applicant")

    # Tailored Why Interested
    why_interested = (
        f"I am eager to contribute to {company}'s AI advancement as a {title}. "
        f"With hands-on experience in structured reasoning, prompt evaluation, and {skills}, "
        f"I focus on delivering rigorous, high-precision training data and ground-truth annotations "
        f"that prevent hallucinations and align model outputs with human intent."
    )

    # Relevant Experience
    relevant_experience = (
        f"Over the past several years, I have built and evaluated software systems and data workflows. "
        f"Key competencies include:\n"
        f"• Deep familiarity with {skills}\n"
        f"• Adherence to complex rubric guidelines, edge-case red-teaming, and model output ranking\n"
        f"• Experience diagnosing logic errors, verifying factual claims, and crafting adversarial test cases\n"
        f"• High output velocity while maintaining >98% accuracy and quality standards"
    )

    # Quality Assurance Strategy
    quality_assurance = (
        f"My workflow centers on a 3-pass verification system:\n"
        f"1. Instruction Verification: Cross-referencing prompt constraints (formatting, negative constraints, length).\n"
        f"2. Factual & Reasoning Audit: Independent verification of code logic, math derivations, and source citations.\n"
        f"3. Alignment & Safety Scoring: Ranking responses based on Helpfulness, Harmlessness, and Accuracy."
    )

    # Master Interview Prompt for external chat (Antigravity, ChatGPT, Claude)
    master_prompt = f"""# MASTER AI INTERVIEW PREPARATION PROMPT
ROLE: You are the Senior AI Technical Interviewer & Assessment Lead at {company}.
You are screening me for the role of: {title}.

COMPANY CONTEXT: {company} specializes in AI training data, RLHF, and frontier model evaluation.
JOB DETAILS: {title} | Compensation: {job.get('compensation', 'Standard rate')} | Platform: {job.get('platform', '')}

INSTRUCTIONS:
1. Act as a realistic, strict, yet fair interviewer evaluating whether to approve me for client projects.
2. Conduct a realistic 4-round simulation:
   - Round 1: Background & Communication Check (checking clarity and English fluency)
   - Round 2: Core Domain Assessment (e.g., coding, logic derivation, or structured evaluation)
   - Round 3: RLHF & Model Response Ranking (Present 2 candidate model outputs and have me rank them with justification)
   - Round 4: Edge Case & Adversarial Red-Teaming
3. Ask ONE question at a time. Do not dump all questions at once.
4. After each of my responses:
   - Provide a quick Score (1-10)
   - Give constructive feedback on what was strong and what red flags to avoid
   - Show how a "Top 1% Candidate" would have answered
   - Ask the next question.

To begin, introduce yourself as the interviewer from {company} and ask me Question 1 of Round 1.
"""

    # Combined 1-Click Clipboard Text
    one_click_bundle = f"""==================================================
APPLICATION & INTERVIEW PACK: {title} at {company}
==================================================
Apply URL: {url}
Platform: {job.get('platform', '')} | Compensation: {job.get('compensation', '')}

--- 1. CANDIDATE INTRODUCTION / COVER LETTER ---
Dear {company} Hiring Team,

{why_interested}

{relevant_experience}

{quality_assurance}

Sincerely,
{name}

--- 2. QUICK APPLICATION FORM ANSWERS ---
[Why are you interested in this project?]
{why_interested}

[Summarize your relevant domain & technical skills]
{relevant_experience}

[How do you maintain data accuracy under tight deadlines?]
{quality_assurance}

--- 3. MASTER INTERVIEW PREPARATION PROMPT ---
(Copy the text below into an AI chat to practice right away)
{master_prompt}
==================================================
"""

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
        "one_click_bundle": one_click_bundle
    }
