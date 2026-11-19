import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        platform TEXT,
        title TEXT,
        company TEXT,
        url TEXT,
        compensation TEXT,
        comp_min REAL,
        comp_max REAL,
        comp_unit TEXT,
        tier TEXT,
        category TEXT,
        location TEXT,
        requires_interview TEXT,
        description TEXT,
        match_score INTEGER DEFAULT 0,
        matching_skills TEXT,
        scraped_at TEXT,
        is_saved INTEGER DEFAULT 0,
        application_status TEXT DEFAULT 'new'
    )
    """)

    # User profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        skills TEXT,
        resume_text TEXT,
        target_rate REAL,
        experience_years INTEGER,
        preferred_categories TEXT
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Interview sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        session_id TEXT PRIMARY KEY,
        job_id TEXT,
        company TEXT,
        role_title TEXT,
        current_round INTEGER,
        total_rounds INTEGER,
        round_name TEXT,
        is_completed INTEGER,
        overall_score INTEGER,
        feedback_summary TEXT,
        history TEXT,
        updated_at TEXT
    )
    """)

    # Default profile if not exists
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO user_profile (id, name, skills, resume_text, target_rate, experience_years, preferred_categories)
        VALUES (1, 'Candidate', ?, ?, 25.0, 2, ?)
        """, (
            json.dumps(["Python", "Machine Learning", "Prompt Engineering", "Data Analysis", "Writing", "Problem Solving", "RLHF", "Code Review"]),
            "Software engineer with experience in Python, AI evaluation, LLM prompt engineering, and data quality assurance.",
            json.dumps(["Coding", "Writing & RLHF", "Generalist"])
        ))

    conn.commit()
    conn.close()

def save_or_update_jobs(jobs: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    for j in jobs:
        skills_json = json.dumps(j.get("matching_skills", []))
        # Keep existing application_status and is_saved if job already exists
        cursor.execute("SELECT is_saved, application_status FROM jobs WHERE id = ?", (j["id"],))
        existing = cursor.fetchone()
        is_saved = existing["is_saved"] if existing else 0
        app_status = existing["application_status"] if existing else "new"

        cursor.execute("""
        INSERT OR REPLACE INTO jobs (
            id, platform, title, company, url, compensation, comp_min, comp_max,
            comp_unit, tier, category, location, requires_interview, description,
            match_score, matching_skills, scraped_at, is_saved, application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            j["id"], j["platform"], j["title"], j["company"], j["url"],
            j.get("compensation", "Unspecified"), j.get("comp_min", 0.0), j.get("comp_max", 0.0),
            j.get("comp_unit", "hr"), j.get("tier", "Mid-Tier ($15-$30)"), j.get("category", "Generalist"),
            j.get("location", "Remote"), j.get("requires_interview", "AI Interview"),
            j.get("description", ""), j.get("match_score", 0), skills_json,
            now, is_saved, app_status
        ))

    conn.commit()
    conn.close()

def get_all_jobs(tier: Optional[str] = None, category: Optional[str] = None, interview_type: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if tier and tier != "all":
        query += " AND tier = ?"
        params.append(tier)
    
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if interview_type and interview_type != "all":
        query += " AND requires_interview = ?"
        params.append(interview_type)

    if search:
        query += " AND (title LIKE ? OR company LIKE ? OR platform LIKE ? OR description LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    query += " ORDER BY match_score DESC, comp_max DESC, scraped_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d["matching_skills"] = json.loads(d["matching_skills"]) if d["matching_skills"] else []
        d["is_saved"] = bool(d["is_saved"])
        result.append(d)

    conn.close()
    return result

def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["matching_skills"] = json.loads(d["matching_skills"]) if d["matching_skills"] else []
    d["is_saved"] = bool(d["is_saved"])
    return d

def update_job_status(job_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET application_status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()

def toggle_save_job(job_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_saved FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    new_val = 0
    if row:
        new_val = 0 if row["is_saved"] else 1
        cursor.execute("UPDATE jobs SET is_saved = ? WHERE id = ?", (new_val, job_id))
        conn.commit()
    conn.close()
    return bool(new_val)

def get_user_profile() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["skills"] = json.loads(d["skills"]) if d["skills"] else []
        d["preferred_categories"] = json.loads(d["preferred_categories"]) if d["preferred_categories"] else []
        return d
    return {
        "name": "Candidate",
        "skills": ["Python", "Machine Learning", "Prompt Engineering", "Data Analysis", "Writing"],
        "resume_text": "",
        "target_rate": 25.0,
        "experience_years": 2,
        "preferred_categories": ["Coding", "Writing & RLHF", "Generalist"]
    }

def update_user_profile(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE user_profile SET
        name = ?,
        skills = ?,
        resume_text = ?,
        target_rate = ?,
        experience_years = ?,
        preferred_categories = ?
    WHERE id = 1
    """, (
        data.get("name", "Candidate"),
        json.dumps(data.get("skills", [])),
        data.get("resume_text", ""),
        float(data.get("target_rate", 20.0)),
        int(data.get("experience_years", 2)),
        json.dumps(data.get("preferred_categories", ["Generalist"]))
    ))
    conn.commit()
    conn.close()

def get_settings() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    settings = {}
    for r in rows:
        settings[r["key"]] = r["value"]
    return settings

def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def save_interview_session(session: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO interview_sessions (
        session_id, job_id, company, role_title, current_round, total_rounds,
        round_name, is_completed, overall_score, feedback_summary, history, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["session_id"], session["job_id"], session["company"], session["role_title"],
        session.get("current_round", 1), session.get("total_rounds", 4),
        session.get("round_name", "Screening"), int(session.get("is_completed", False)),
        session.get("overall_score", 0), session.get("feedback_summary", ""),
        json.dumps(session.get("messages", [])), datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_interview_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interview_sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["messages"] = json.loads(d["history"]) if d["history"] else []
    d["is_completed"] = bool(d["is_completed"])
    return d
