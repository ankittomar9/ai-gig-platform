import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import DB_PATH
from app.services.pay_parser import extract_experience_years, check_location_and_language

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
        application_status TEXT DEFAULT 'new',
        min_exp_years INTEGER DEFAULT 0,
        exp_label TEXT DEFAULT '0-2 yrs'
    )
    """)

    # Migration: ensure min_exp_years, exp_label, is_india_eligible, location_status, language_status columns exist
    cursor.execute("PRAGMA table_info(jobs)")
    cols = [r[1] for r in cursor.fetchall()]
    if "min_exp_years" not in cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN min_exp_years INTEGER DEFAULT 0")
    if "exp_label" not in cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN exp_label TEXT DEFAULT '0-2 yrs'")
    if "is_india_eligible" not in cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN is_india_eligible INTEGER DEFAULT 0")
    if "location_status" not in cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN location_status TEXT DEFAULT 'Open Remote'")
    if "language_status" not in cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN language_status TEXT DEFAULT 'English / Hindi'")

    # User profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT DEFAULT 'candidate@example.com',
        phone TEXT DEFAULT '+91 XXXXX XXXXX',
        linkedin TEXT DEFAULT 'linkedin.com/in/candidate',
        skills TEXT,
        resume_text TEXT,
        target_rate REAL,
        experience_years INTEGER,
        preferred_categories TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(user_profile)")
    u_cols = [c[1] for c in cursor.fetchall()]
    if "email" not in u_cols:
        cursor.execute("ALTER TABLE user_profile ADD COLUMN email TEXT DEFAULT 'candidate@example.com'")
    if "phone" not in u_cols:
        cursor.execute("ALTER TABLE user_profile ADD COLUMN phone TEXT DEFAULT '+91 XXXXX XXXXX'")
    if "linkedin" not in u_cols:
        cursor.execute("ALTER TABLE user_profile ADD COLUMN linkedin TEXT DEFAULT 'linkedin.com/in/candidate'")

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Resume personas table (Multi-Resume Support)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_personas (
        id TEXT PRIMARY KEY,
        title TEXT,
        category TEXT,
        skills TEXT,
        summary TEXT,
        full_text TEXT,
        is_active INTEGER DEFAULT 0
    )
    """)

    # Seed default personas if empty
    cursor.execute("SELECT COUNT(*) FROM resume_personas")
    if cursor.fetchone()[0] == 0:
        personas = [
            (
                "production_systems",
                "Application Production Systems Specialist",
                "Production & Support",
                json.dumps(["Java", "Spring Boot", "SQL", "Docker", "GCP", "Linux", "API", "Incident Management"]),
                "Specialist in production environments, incident triage, system uptime, and enterprise cloud operations.",
                "Application Production Systems Specialist with experience in high-availability backend environments, incident response, Linux, and GCP operations.",
                1
            ),
            (
                "software_engineer",
                "Software Engineer & Backend Developer",
                "Coding",
                json.dumps(["Python", "Java", "Spring Boot", "SQL", "Data Structures", "Algorithms", "Git", "API"]),
                "Software engineer experienced in backend architectures, clean code implementation, debugging, and API design.",
                "Software Engineer with hands-on experience in backend services, algorithmic problem-solving, and automated test design.",
                0
            ),
            (
                "ai_rlhf_trainer",
                "AI Trainer & RLHF Specialist",
                "Writing & RLHF",
                json.dumps(["RLHF", "Prompt Engineering", "Model Evaluation", "Pairwise Ranking", "Hallucination Detection", "Quality Assurance"]),
                "AI Trainer skilled in prompt evaluation, rubric scoring, pairwise model comparisons, and adversarial testing.",
                "AI Trainer and Domain Evaluator focusing on alignment, ground-truth annotations, and LLM reasoning verification.",
                0
            ),
            (
                "microtask_evaluator",
                "Data & Quality Evaluation Specialist",
                "Generalist",
                json.dumps(["Data Annotation", "Quality Assurance", "Guideline Compliance", "Attention to Detail", "Search Relevance"]),
                "Detail-oriented evaluator with high accuracy on data annotation, search relevance, and digital workflow benchmarks.",
                "Quality Evaluator specialized in strict guideline compliance, rapid verification, and multi-modal task evaluation.",
                0
            )
        ]
        cursor.executemany("""
        INSERT INTO resume_personas (id, title, category, skills, summary, full_text, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, personas)

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

        min_exp = j.get("min_exp_years")
        exp_label = j.get("exp_label")
        if min_exp is None or exp_label is None:
            exp_info = extract_experience_years(j.get("title", ""), j.get("description", ""), j.get("company", ""))
            min_exp = exp_info["min_exp"]
            exp_label = exp_info["label"]

        is_in = j.get("is_india_eligible")
        loc_stat = j.get("location_status")
        lang_stat = j.get("language_status")
        if is_in is None or loc_stat is None or lang_stat is None:
            loc_info = check_location_and_language(j.get("title", ""), j.get("location", ""), j.get("description", ""))
            is_in = 1 if loc_info["is_india_eligible"] else 0
            loc_stat = loc_info["location_status"]
            lang_stat = loc_info["language_status"]

        cursor.execute("""
        INSERT OR REPLACE INTO jobs (
            id, platform, title, company, url, compensation, comp_min, comp_max,
            comp_unit, tier, category, location, requires_interview, description,
            match_score, matching_skills, scraped_at, is_saved, application_status,
            min_exp_years, exp_label, is_india_eligible, location_status, language_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            j["id"], j["platform"], j["title"], j["company"], j["url"],
            j.get("compensation", "Not listed"), j.get("comp_min", 0.0), j.get("comp_max", 0.0),
            j.get("comp_unit", "hr"), j.get("tier", "Pay Not Listed"), j.get("category", "Generalist"),
            j.get("location", "Remote"), j.get("requires_interview", "AI Interview"),
            j.get("description", ""), j.get("match_score", 0), skills_json,
            now, is_saved, app_status, int(min_exp), str(exp_label),
            int(is_in), str(loc_stat), str(lang_stat)
        ))

    conn.commit()
    conn.close()

def get_all_jobs(
    tier: Optional[str] = None,
    category: Optional[str] = None,
    interview_type: Optional[str] = None,
    search: Optional[str] = None,
    company: Optional[str] = None,
    max_exp: Optional[int] = None,
    india_only: Optional[bool] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if india_only:
        query += " AND is_india_eligible = 1"

    if tier and tier != "all":
        query += " AND tier = ?"
        params.append(tier)
    
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if interview_type and interview_type != "all":
        query += " AND requires_interview = ?"
        params.append(interview_type)

    if company and company != "all":
        query += " AND (company = ? OR company LIKE ? OR platform LIKE ?)"
        s_comp = f"%{company}%"
        params.extend([company, s_comp, s_comp])

    if max_exp is not None:
        query += " AND min_exp_years <= ?"
        params.append(int(max_exp))

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
        d["is_fits_resume"] = bool(d.get("min_exp_years", 0) <= 3)
        d["is_india_eligible"] = bool(d.get("is_india_eligible", 0))
        result.append(d)

    conn.close()
    return result

def get_all_companies(india_only: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    where_clause = " WHERE is_india_eligible = 1" if india_only else ""
    cursor.execute(f"""
    SELECT 
        company, 
        COUNT(*) as total_count,
        SUM(CASE WHEN min_exp_years <= 3 THEN 1 ELSE 0 END) as eligible_count,
        SUM(CASE WHEN is_india_eligible = 1 THEN 1 ELSE 0 END) as india_count
    FROM jobs 
    {where_clause}
    GROUP BY company 
    ORDER BY total_count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "company": r["company"],
            "total_count": r["total_count"],
            "eligible_count": r["eligible_count"] if r["eligible_count"] is not None else 0,
            "india_count": r["india_count"] if r["india_count"] is not None else 0
        }
        for r in rows
    ]

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
        d.setdefault("email", "candidate@example.com")
        d.setdefault("phone", "+91 XXXXX XXXXX")
        d.setdefault("linkedin", "linkedin.com/in/candidate")
        return d
    return {
        "name": "Candidate",
        "email": "candidate@example.com",
        "phone": "+91 XXXXX XXXXX",
        "linkedin": "linkedin.com/in/candidate",
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
        email = ?,
        phone = ?,
        linkedin = ?,
        skills = ?,
        resume_text = ?,
        target_rate = ?,
        experience_years = ?,
        preferred_categories = ?
    WHERE id = 1
    """, (
        data.get("name", "Candidate"),
        data.get("email", "candidate@example.com"),
        data.get("phone", "+91 XXXXX XXXXX"),
        data.get("linkedin", "linkedin.com/in/candidate"),
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
        session.get("overall_score"), session.get("feedback_summary", ""),
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
    d["is_offline_fallback"] = any(m.get("evaluation_source") == "heuristic" for m in d["messages"])
    return d

def get_all_personas() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_personas ORDER BY is_active DESC, title ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d["skills"]) if d["skills"] else []
        d["is_active"] = bool(d["is_active"])
        result.append(d)
    return result

def get_active_persona() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_personas WHERE is_active = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["skills"] = json.loads(d["skills"]) if d["skills"] else []
    d["is_active"] = True
    return d

def activate_persona(persona_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE resume_personas SET is_active = 0")
    cursor.execute("UPDATE resume_personas SET is_active = 1 WHERE id = ?", (persona_id,))
    
    # Also sync to user_profile for scoring
    cursor.execute("SELECT * FROM resume_personas WHERE id = ?", (persona_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
        UPDATE user_profile SET
            skills = ?,
            resume_text = ?
        WHERE id = 1
        """, (row["skills"], row["full_text"]))

    conn.commit()
    conn.close()
    return True
