import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from app.config import STATIC_DIR, DATA_DIR
from app.database import (
    init_db, get_all_jobs, get_job_by_id, update_job_status,
    toggle_save_job, get_user_profile, update_user_profile,
    get_settings, set_setting, get_interview_session,
    get_all_personas, activate_persona, get_all_companies
)
from app.models import (
    JobStatusUpdate, SettingsUpdate, UserProfile,
    InterviewChatRequest
)
from app.scrapers.runner import run_full_scan
from app.services.matcher import extract_text_from_file, extract_skills_from_text, calculate_match_score
from app.services.application_pack import generate_application_pack
from app.services.interview_agent import start_new_interview, process_interview_reply
from app.services.resume_generator import generate_tailored_resume
from app.services.speech import check_whisper_status, transcribe_audio_bytes
from app.services.humanizer import humanize_resume_text
from app.services.interview_packet import generate_interview_packet

# Initialize database on startup
init_db()

app = FastAPI(
    title="AI Gig Hunter & Interview Simulator",
    description="Unified platform for AI training jobs, 1-click application packs, and interactive AI interview prep.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "ai-gig-platform"}

@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "AI Gig Hunter API is running. Visit /docs for API documentation."}

@app.post("/api/scan")
async def trigger_scan():
    """Trigger parallel scan across all ATS feeds & platforms"""
    try:
        summary = await run_full_scan()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def list_jobs(
    tier: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    interview_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    max_exp: Optional[int] = Query(None),
    india_only: Optional[bool] = Query(None)
):
    """Retrieve jobs with optional filtering by tier, category, interview, company, search, max experience, and India eligibility"""
    jobs = get_all_jobs(
        tier=tier,
        category=category,
        interview_type=interview_type,
        search=search,
        company=company,
        max_exp=max_exp,
        india_only=india_only
    )
    return {"count": len(jobs), "jobs": jobs}

@app.get("/api/companies")
async def list_companies(india_only: bool = Query(False)):
    """Retrieve list of companies with live job counts and eligible (<3 yrs) breakdown"""
    return {"companies": get_all_companies(india_only=india_only)}

@app.get("/api/metrics")
async def get_dashboard_metrics():
    """Retrieve comprehensive platform metrics for Candidate Dashboard"""
    all_j = get_all_jobs()
    total = len(all_j)
    india_eligible = sum(1 for j in all_j if j.get("is_india_eligible"))
    fits_resume = sum(1 for j in all_j if j.get("min_exp_years", 0) <= 3)
    perfect_match = sum(1 for j in all_j if j.get("is_india_eligible") and j.get("min_exp_years", 0) <= 3)
    high_score = sum(1 for j in all_j if j.get("match_score", 0) >= 70)

    return {
        "total_jobs": total,
        "india_eligible": india_eligible,
        "fits_resume": fits_resume,
        "perfect_match": perfect_match,
        "high_score": high_score
    }

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/jobs/{job_id}/status")
async def update_status(job_id: str, payload: JobStatusUpdate):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    update_job_status(job_id, payload.status)
    return {"status": "success", "job_id": job_id, "new_status": payload.status}

@app.post("/api/jobs/{job_id}/toggle-save")
async def toggle_save(job_id: str):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    new_state = toggle_save_job(job_id)
    return {"status": "success", "job_id": job_id, "is_saved": new_state}

@app.get("/api/jobs/{job_id}/application-pack")
async def get_application_pack(job_id: str, humanize: bool = True):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    profile = get_user_profile()
    pack = generate_application_pack(job, profile, humanize=humanize)
    return pack

@app.get("/api/jobs/{job_id}/tailored-resume")
async def get_job_tailored_resume(job_id: str, humanize: bool = True):
    """Dynamically generate a tailored ATS resume customized for this specific job, with Anti-AI detector humanization"""
    profile = get_user_profile()
    try:
        resume_data = generate_tailored_resume(job_id, profile)
        if humanize:
            resume_data["formatted_resume"] = humanize_resume_text(resume_data["formatted_resume"])
        return resume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}/interview-packet")
async def get_job_interview_packet(job_id: str):
    """Generate a comprehensive role-specific interview preparation packet (Questions, A+ Answers, and Rubric)"""
    profile = get_user_profile()
    try:
        packet = generate_interview_packet(job_id, profile)
        return packet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whisper-status")
async def get_whisper_status():
    """Returns availability of local Whisper sidecar (port 8178), Groq Whisper, and Web Speech"""
    return await check_whisper_status()

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribes spoken audio recorded from candidate microphone via Whisper sidecar"""
    try:
        contents = await file.read()
        text = await transcribe_audio_bytes(contents, filename=file.filename or "recording.wav")
        return {"status": "success", "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/personas")
async def list_personas():
    """Retrieve all available resume personas"""
    return {"personas": get_all_personas()}

@app.post("/api/personas/{persona_id}/activate")
async def switch_persona(persona_id: str):
    """Switch active resume persona and re-score all jobs against the new persona's skills"""
    activate_persona(persona_id)
    # Re-score all jobs with newly activated persona skills
    await run_full_scan()
    return {"status": "success", "active_persona": persona_id}

@app.post("/api/interview/start")
async def start_interview(payload: Dict[str, str]):
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")
    try:
        session = await start_new_interview(job_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/chat")
async def interview_chat(payload: InterviewChatRequest):
    try:
        session = await process_interview_reply(payload.session_id, payload.user_message)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/{session_id}")
async def get_interview(session_id: str):
    session = get_interview_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.get("/api/profile")
async def get_profile():
    return get_user_profile()

@app.post("/api/profile")
async def save_profile(profile: UserProfile):
    update_user_profile(profile.model_dump())
    return {"status": "success", "profile": get_user_profile()}

@app.post("/api/profile/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume document (.docx, .txt, .md), auto-extract skills & update profile"""
    raw_name = file.filename or ""
    if not raw_name or ".." in raw_name or "/" in raw_name or "\\" in raw_name:
        raise HTTPException(status_code=400, detail="Invalid filename or path traversal detected.")

    safe_filename = Path(raw_name).name
    ext = Path(safe_filename).suffix.lower()
    if ext not in [".docx", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Only .docx, .txt, and .md files are allowed.")

    temp_path = DATA_DIR / f"temp_{safe_filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = extract_text_from_file(temp_path)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not read text from uploaded file.")

        skills = extract_skills_from_text(extracted_text)
        current = get_user_profile()
        merged_skills = sorted(list(set(current.get("skills", []) + skills)))

        current["resume_text"] = extracted_text
        current["skills"] = merged_skills
        update_user_profile(current)

        return {
            "status": "success",
            "message": f"Successfully parsed {len(skills)} skills from {safe_filename}!",
            "extracted_skills": skills,
            "profile": current
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")
    finally:
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.get("/api/settings")
async def get_app_settings():
    settings = get_settings()
    # Mask API key for security
    raw_key = settings.get("gemini_api_key", "")
    masked_key = f"{raw_key[:4]}...{raw_key[-4:]}" if len(raw_key) > 8 else ("Set" if raw_key else "Not set")
    return {
        "gemini_api_key_set": bool(raw_key),
        "gemini_api_key_masked": masked_key,
        "gemini_model": settings.get("gemini_model", "gemini-3.8-flash"),
        "offline_mode": settings.get("offline_mode", "false").lower() == "true",
        "minimum_rate": float(settings.get("minimum_rate", 0))
    }

@app.put("/api/settings")
@app.post("/api/settings")
async def update_app_settings(payload: SettingsUpdate):
    if payload.gemini_api_key is not None:
        set_setting("gemini_api_key", payload.gemini_api_key.strip())
    if payload.gemini_model is not None:
        set_setting("gemini_model", payload.gemini_model)
    if payload.offline_mode is not None:
        set_setting("offline_mode", str(payload.offline_mode).lower())
    if payload.minimum_rate is not None:
        set_setting("minimum_rate", str(payload.minimum_rate))
    return {"status": "success", "message": "Settings saved successfully"}
