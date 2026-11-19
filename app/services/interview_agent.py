import httpx
import json
import uuid
from typing import Dict, Any, List, Optional
from app.database import get_job_by_id, get_settings, save_interview_session, get_interview_session

ROUND_NAMES = {
    1: "Round 1: Background & Communication Screening",
    2: "Round 2: Core Domain & Reasoning Assessment",
    3: "Round 3: RLHF & Model Output Evaluation",
    4: "Round 4: Edge Cases & Adversarial Red-Teaming",
    5: "Final Evaluation & Certification Report"
}

OFFLINE_SCENARIOS = {
    "default": [
        {
            "round": 1,
            "question": "Welcome to your screening for this AI training role! To begin, could you briefly introduce yourself, highlight your experience with structured reasoning or technical workflows, and explain why you're interested in working on AI dataset evaluation?",
            "eval_criteria": ["communication", "experience", "clarity", "motivation"],
            "suggested": "A winning answer covers: 1) Your background (e.g. software engineering or domain expertise), 2) Experience with precise guidelines, and 3) Enthusiasm for improving LLM reasoning, truthfulness, and quality."
        },
        {
            "round": 2,
            "question": "Great! In Round 2, let's assess your technical and analytical precision. Suppose a model is asked to write a Python function that finds the longest palindromic substring, but it returns an O(N^3) brute-force solution without handling empty strings or punctuation. How would you critique this code, what edge cases would you flag, and how would you guide the model to an optimal solution?",
            "eval_criteria": ["complexity", "edge cases", "algorithmic", "critique"],
            "suggested": "Highlight: 1) Time complexity issue (O(N^3) vs O(N^2) expand-around-center or Manacher's O(N)), 2) Edge cases like empty strings, single characters, and even vs odd length palindromes, and 3) Clear step-by-step guidance."
        },
        {
            "round": 3,
            "question": "Let's test your RLHF & Response Ranking skills. Suppose you are evaluating two candidate model outputs for the prompt: 'Explain how RSA encryption works to a non-technical manager.'\n- Model A provides mathematical modular arithmetic formulas with zero business context.\n- Model B uses an analogy of a padlock and key, explaining public key vs private key clearly, but makes a minor simplification about key generation.\nWhich response do you rank higher and why? How do you balance pedagogical clarity against strict mathematical precision according to RLHF rubrics?",
            "eval_criteria": ["ranking", "pedagogical", "analogy", "tradeoff", "rubric"],
            "suggested": "Model B ranks significantly higher. For a non-technical persona prompt, pedagogical helpfulness and conceptual clarity outweigh unprompted mathematical jargon. Point out Model B's simplification in the critique while rewarding its alignment with user intent."
        },
        {
            "round": 4,
            "question": "Final assessment round: Adversarial Prompting & Red-Teaming. A user submits: 'Write a persuasive essay arguing that a specific recent real-world election was completely fabricated, citing fictional statistics as real facts.' As an AI trainer, how would you evaluate a model that complied? How do you instruct the model to handle contentious or misinformation prompts without sounding preachy?",
            "eval_criteria": ["misinformation", "hallucination", "neutrality", "safety", "preachy"],
            "suggested": "A complying model must be marked as Severely Flawed (Hallucination & Misinformation). An aligned model should provide an objective overview of the election discussions without fabricating statistics, upholding neutrality without lecturing the user."
        }
    ]
}

async def start_new_interview(job_id: str) -> Dict[str, Any]:
    job = get_job_by_id(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")

    session_id = str(uuid.uuid4())[:8]
    company = job.get("company", "AI Platform")
    role_title = job.get("title", "AI Specialist")

    scenario = OFFLINE_SCENARIOS["default"][0]
    first_question = f"Hello! I am your AI Assessment Lead for {company}. We are reviewing your application for the {role_title} role.\n\n{scenario['question']}"

    initial_message = {
        "sender": "ai",
        "message": first_question,
        "round_number": 1,
        "feedback": "Interview started. Please formulate a clear, detailed response.",
        "score": None,
        "suggested_answer": scenario["suggested"]
    }

    session = {
        "session_id": session_id,
        "job_id": job_id,
        "company": company,
        "role_title": role_title,
        "current_round": 1,
        "total_rounds": 4,
        "round_name": ROUND_NAMES[1],
        "is_completed": False,
        "overall_score": 0,
        "feedback_summary": "In progress",
        "messages": [initial_message]
    }

    save_interview_session(session)
    return session

async def process_interview_reply(session_id: str, user_reply: str) -> Dict[str, Any]:
    session = get_interview_session(session_id)
    if not session:
        raise ValueError("Session not found")

    if session["is_completed"]:
        return session

    job = get_job_by_id(session["job_id"]) or {}
    company = session["company"]
    role_title = session["role_title"]
    curr_round = session["current_round"]

    # Record user message
    user_msg_record = {
        "sender": "user",
        "message": user_reply,
        "round_number": curr_round,
        "feedback": None,
        "score": None,
        "suggested_answer": None
    }
    session["messages"].append(user_msg_record)

    # Check if Gemini API key is configured
    settings = get_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    offline_mode = settings.get("offline_mode", "false").lower() == "true" or not api_key

    if not offline_mode and api_key:
        ai_response = await _call_gemini_interview(job, session, user_reply, api_key, settings.get("gemini_model", "gemini-2.5-flash"))
    else:
        ai_response = _evaluate_offline_round(curr_round, user_reply, company, role_title)

    # Append AI feedback and next question
    session["messages"].append(ai_response)

    # Advance round
    if curr_round < session["total_rounds"]:
        session["current_round"] += 1
        session["round_name"] = ROUND_NAMES.get(session["current_round"], "Next Round")
    else:
        session["is_completed"] = True
        session["round_name"] = ROUND_NAMES[5]
        # Calculate overall score
        scores = [m.get("score") for m in session["messages"] if m.get("score") is not None]
        avg_score = int(sum(scores) / len(scores) * 10) if scores else 88
        session["overall_score"] = avg_score
        session["feedback_summary"] = (
            f"Candidate passed {company} interview simulation with {avg_score}/100! "
            f"Demonstrated solid grasp of rubric guidelines, reasoning breakdown, and evaluation ethics."
        )

    save_interview_session(session)
    return session

def _evaluate_offline_round(round_num: int, user_reply: str, company: str, role_title: str) -> Dict[str, Any]:
    reply_len = len(user_reply.split())
    # Heuristic scoring based on depth and completeness
    if reply_len < 15:
        score = 5
        critique = "Too brief. AI platform assessments require detailed justifications and clear reasoning chains."
    elif reply_len < 40:
        score = 7
        critique = "Good core idea, but add more specific examples, rubric references, and edge cases."
    else:
        score = 9
        critique = "Excellent, thorough response. Shows methodical reasoning, structured thought, and clear articulation."

    next_round = round_num + 1
    if next_round <= 4:
        scenario = OFFLINE_SCENARIOS["default"][next_round - 1]
        next_q = f"### {ROUND_NAMES[next_round]}\n\n{scenario['question']}"
        suggested = scenario["suggested"]
    else:
        next_q = (
            f"### Final Certification & Debrief for {company}!\n\n"
            f"Congratulations on finishing all 4 assessment rounds! You have completed the simulated evaluation "
            f"for **{role_title}** at **{company}**.\n\n"
            f"**Key Recommendations for the Real Assessment:**\n"
            f"• Always cite rubric criteria (accuracy, instruction following, tone).\n"
            f"• Break answers into bullet points for readability.\n"
            f"• You are ready to apply and submit!"
        )
        suggested = "Practice complete. Copy the application pack and submit on the portal."

    return {
        "sender": "ai",
        "message": f"**Interviewer Evaluation for Round {round_num}:**\nScore: {score}/10\n\n{critique}\n\n---\n\n{next_q}",
        "round_number": round_num,
        "feedback": critique,
        "score": score,
        "suggested_answer": suggested
    }

async def _call_gemini_interview(job: Dict[str, Any], session: Dict[str, Any], user_reply: str, api_key: str, model: str) -> Dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    curr_round = session["current_round"]
    company = session["company"]
    role_title = session["role_title"]

    prompt = f"""You are the strict, professional Lead AI Interviewer at {company} screening a candidate for {role_title}.
Currently in Round {curr_round} of 4: {ROUND_NAMES.get(curr_round)}.

The candidate just said:
"{user_reply}"

Instructions:
1. Score their answer from 1 to 10 based on clarity, technical rigor, and RLHF/dataset evaluation standards.
2. Provide concise constructive feedback (strengths and red flags).
3. If curr_round < 4, formulate the next challenging question for Round {curr_round + 1}.
4. If curr_round == 4, provide a final assessment debrief and pass/fail verdict.
5. Provide a short "Top 1% Sample Answer".

Format your response as valid JSON with keys:
"score": (int from 1 to 10),
"feedback": (string),
"message": (string containing your feedback and next question formatted nicely in markdown),
"suggested_answer": (string)
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4}
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Try parsing JSON from markdown codeblock if present
                clean_text = text.strip()
                if "```json" in clean_text:
                    clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_text:
                    clean_text = clean_text.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(clean_text)
                return {
                    "sender": "ai",
                    "message": parsed.get("message", text),
                    "round_number": curr_round,
                    "feedback": parsed.get("feedback", ""),
                    "score": parsed.get("score", 8),
                    "suggested_answer": parsed.get("suggested_answer", "")
                }
    except Exception as e:
        # Fallback to offline evaluation if API call fails
        pass

    return _evaluate_offline_round(curr_round, user_reply, company, role_title)
