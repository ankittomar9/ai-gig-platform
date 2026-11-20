import re
import random
from typing import Dict, Any, List

# Banned AI clichés that trigger GPTZero, CopyLeaks, and Turnitin
AI_CLICHES = {
    r"\bdelve\b": "dig",
    r"\bdelving\b": "digging",
    r"\btapestry\b": "mix",
    r"\btestament\b": "proof",
    r"\bspearheaded\b": "led",
    r"\bleveraged\b": "used",
    r"\bleveraging\b": "using",
    r"\bseamlessly\b": "directly",
    r"\bfoster\b": "encourage",
    r"\bfostering\b": "building",
    r"\bpivotal\b": "key",
    r"\bparamount\b": "critical",
    r"\bin today's fast-paced\b": "in fast-moving",
    r"\brobust\b": "solid",
    r"\bmultifaceted\b": "varied",
    r"\bholistic\b": "complete",
    r"\bmeticulous\b": "careful",
    r"\bmeticulously\b": "carefully",
    r"\bcornerstone\b": "foundation",
    r"\bindispensable\b": "necessary",
    r"\bmoreover\b": "also",
    r"\bfurthermore\b": "also",
    r"\bin conclusion\b": "overall"
}

def clean_ai_cliches(text: str) -> str:
    """Replaces dead-giveaway LLM words with natural, plain English words."""
    result = text
    for pattern, replacement in AI_CLICHES.items():
        result = re.sub(pattern, replacement, result, flags=re.I)
    return result

def generate_humanized_pack(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates application answers with HIGH BURSTINESS (mixed short/long sentences)
    and practical human phrasing designed to score 0% on AI detectors.
    """
    company = job.get("company", "the team")
    title = job.get("title", "AI Trainer")
    category = job.get("category", "Generalist")
    tier = job.get("tier", "Mid-Tier ($15-$30)")
    name = profile.get("name", "Applicant")
    skills = profile.get("skills", ["Linux", "Python", "SQL", "Docker", "Java"])

    # 1. Why Interested - Written in natural, grounded first-person voice
    if category == "Coding":
        why_interested = (
            f"I've spent the last couple of years troubleshooting real-world code and backend systems. "
            f"What caught my eye about this {title} role at {company} is the practical focus. "
            f"A lot of AI coding benchmarks look neat on paper, but break down when you throw edge cases, "
            f"weird input types, or performance constraints at them. I enjoy catching subtle off-by-one errors, "
            f"spotting bad time complexities early, and writing clean test cases that prove whether code actually works. "
            f"I want to help make sure the models you train produce dependable, production-ready code."
        )
    elif category == "Writing & RLHF":
        why_interested = (
            f"I'm applying because I genuinely enjoy analyzing text and picking apart arguments. "
            f"Working on {company}'s AI projects appeals to me because prompt evaluation isn't just about good grammar—it's "
            f"about checking whether the model actually followed instructions or quietly made things up. "
            f"I like reading complex guidelines, spotting where a response slips into vague filler, "
            f"and writing honest, constructive justifications for why one output beats another."
        )
    elif "Microtask" in tier:
        why_interested = (
            f"I'm looking for consistent, detail-oriented evaluation work where accuracy matters. "
            f"I have a reliable home setup, steady high-speed internet, and a daily habit of following instructions to the letter. "
            f"I don't rush through tasks or guess on ambiguous items; I check the project rubric, verify my work, and keep quality high."
        )
    else: # Production & Systems
        why_interested = (
            f"I come from a hands-on application support and production systems background. "
            f"I deal with live logs, cloud services, and incident triage every day. "
            f"When I saw {company} looking for a {title}, it made sense right away. "
            f"I understand what happens when instructions are misunderstood or systems fail in production, and I bring that same careful, "
            f"no-shortcuts approach to every dataset or technical project I handle."
        )

    # 2. Relevant Experience - Concrete, grounded anecdotes (bypasses AI detector pattern matching)
    if category == "Coding":
        relevant_experience = (
            f"Here is what I bring to the table:\n"
            f"• Solid coding foundation in {', '.join(skills[:4])}. I can trace execution paths in my head and write tests that catch edge cases.\n"
            f"• Debugging discipline: I don't just see that an answer is wrong; I pinpoint the exact line, explain why the logic breaks, and show the fix.\n"
            f"• Documentation: I write concise explanations that developers and reviewers can understand without having to re-read three times.\n"
            f"• Consistency: I'm comfortable working through dozens of technical prompts a day while keeping my review standards strict."
        )
    elif category == "Writing & RLHF":
        relevant_experience = (
            f"Key strengths I bring to this evaluation work:\n"
            f"• Close reading: I notice when a model skips negative constraints (like 'do not mention dates' or 'keep under 100 words').\n"
            f"• Fact verification: I always search and cross-verify dates, quotes, and technical assertions instead of assuming the model got it right.\n"
            f"• Rubric justification: When ranking Model A vs Model B, I write clear, bulleted reasons pointing to specific paragraphs, not generic praise.\n"
            f"• Comfort with complex rules: I'm used to adapting to multi-page style guides and guidelines that change between projects."
        )
    else:
        relevant_experience = (
            f"Practical experience highlights:\n"
            f"• Daily technical work in Linux, SQL, Docker, and enterprise application workflows.\n"
            f"• Zero tolerance for guesswork: If a guideline is ambiguous, I review project notes or ask for clarification rather than assuming.\n"
            f"• High focus over long sessions: Experienced with multi-hour evaluation and annotation tasks while maintaining >98% accuracy."
        )

    # 3. Quality Assurance Strategy - Realistic human workflow
    quality_assurance = (
        f"My daily quality routine is straightforward:\n"
        f"1. First pass: Check instructions. Did the response respect every formatting rule, word limit, and tone requirement?\n"
        f"2. Second pass: Check facts and logic. Run any code locally, verify formulas, and confirm external claims.\n"
        f"3. Final pass: Self-audit before submitting. Make sure my score and written comments align with the project rubric."
    )

    # Master prompt formatted for interview simulation
    master_prompt = (
        f"# AI TECHNICAL INTERVIEWER SIMULATOR FOR {company.upper()}\n"
        f"Role being interviewed for: {title}\n\n"
        f"You are the senior assessment reviewer at {company}. "
        f"Conduct a realistic, spoken-style 4-round interview with me. "
        f"Do not lecture. Ask one question at a time. After I answer (via voice or text), "
        f"give me a score from 1-10, tell me what was good, what red flags to avoid, and show a top-tier answer."
    )

    one_click_bundle = f"""==================================================
HUMANIZED APPLICATION PACK: {title} at {company}
(Written in natural first-person voice — Bypasses AI Detectors)
==================================================
Apply URL: {job.get('url', '#')}

--- 1. COVER LETTER / INTRODUCTION ---
Hi {company} team,

{why_interested}

{relevant_experience}

{quality_assurance}

Best,
{name}

--- 2. QUICK FORM ANSWERS ---
[Why are you a fit for this role?]
{why_interested}

[Summarize your relevant background]
{relevant_experience}

[How do you maintain data accuracy under deadlines?]
{quality_assurance}

--- 3. MASTER INTERVIEW PROMPT ---
{master_prompt}
==================================================
"""

    return {
        "why_interested": clean_ai_cliches(why_interested),
        "relevant_experience": clean_ai_cliches(relevant_experience),
        "quality_assurance_strategy": clean_ai_cliches(quality_assurance),
        "master_prompt": master_prompt,
        "one_click_bundle": clean_ai_cliches(one_click_bundle)
    }

def humanize_resume_text(resume_text: str) -> str:
    """Transforms robotic resume text into authentic, high-impact human engineer language."""
    cleaned = clean_ai_cliches(resume_text)
    # Add natural variation
    cleaned = re.sub(r'• Spearheaded', '• Built and led', cleaned)
    cleaned = re.sub(r'• Utilized', '• Used', cleaned)
    cleaned = re.sub(r'• Responsible for', '• Managed', cleaned)
    return cleaned
