# System Architecture & Technical Specifications

This document outlines the software design, data models, API contracts, and integration layers of the **AI Gig Hunter & Interview Simulator**.

---

## 1. High-Level System Architecture

The application is structured as a unified Python FastAPI backend powering an interactive single-page web dashboard (HTML5 + Tailwind CSS + Lucide Icons) with SQLite storage:

```
+---------------------------------------------------------------------------------+
|                                Frontend Dashboard                               |
|   - Real-time Job Grid with Dynamic Badges (India, Exp, Compensation, Match)    |
|   - 5-Round Voice Interview Room with Whisper Speech-to-Text Input              |
|   - Resume Persona Vault & 1-Click Tailored ATS Generator                       |
|   - Filter Controls: Location Gate (India), Exp (<=3y), Company, Tier, Domain   |
+---------------------------------------------------------------------------------+
                                       | REST API
                                       v
+---------------------------------------------------------------------------------+
|                               FastAPI Application                               |
|   - Routing & Controllers: app/main.py                                          |
|   - Data Access Layer: app/database.py (SQLite)                                 |
|   - Configuration & Constants: app/config.py                                    |
+---------------------------------------------------------------------------------+
          |                               |                                |
          v                               v                                v
+-------------------+           +-------------------+            +-------------------+
| Scraper Engine    |           | Services Layer    |            | Database Layer    |
| - Ashby ATS       |           | - Matcher         |            | - SQLite          |
| - Greenhouse ATS  |           | - Humanizer       |            |   (gighunter.db)  |
| - Lever ATS       |           | - Speech / STT    |            | - Jobs Table      |
| - Direct AI Feeds |           | - Interview Agent |            | - Personas Table  |
|   (Outlier,       |           | - Resume Gen      |            | - Sessions Table  |
|    Alignerr, etc) |           | - Pay & Exp Parser|            | - Profile Table   |
+-------------------+           +-------------------+            +-------------------+
```

---

## 2. Database Schema (SQLite: `data/gighunter.db`)

### Table: `jobs`
| Column | Type | Description |
|---|---|---|
| `id` | `TEXT PRIMARY KEY` | Unique job identifier (e.g. `gh_scaleai_12345`) |
| `platform` | `TEXT` | Source board name (Ashby, Greenhouse, Direct) |
| `title` | `TEXT` | Job title |
| `company` | `TEXT` | Company name (Scale AI, Outlier, Alignerr, Mercor, etc.) |
| `url` | `TEXT` | Direct application URL |
| `compensation` | `TEXT` | Normalized compensation string (e.g. `$35 - $60/hr`) |
| `comp_min` | `REAL` | Minimum hourly rate equivalent |
| `comp_max` | `REAL` | Maximum hourly rate equivalent |
| `comp_unit` | `TEXT` | Unit (`hr` or `task`) |
| `tier` | `TEXT` | `Microtask ($2-$15)`, `Mid-Tier ($15-$30)`, `Expert ($30-$100+)` |
| `category` | `TEXT` | `Coding`, `Writing & RLHF`, `Math & Reasoning`, `Generalist` |
| `location` | `TEXT` | Raw location string from source ATS |
| `requires_interview` | `TEXT` | `AI Interview`, `Automated Test`, `Direct Onboarding` |
| `description` | `TEXT` | Job description text (trimmed for storage) |
| `match_score` | `INTEGER` | ATS match score (0-100) based on candidate skills |
| `matching_skills` | `TEXT` | JSON list of overlapping skills |
| `min_exp_years` | `INTEGER` | Minimum experience required (0, 1, 2, 3, 5, 7+) |
| `exp_label` | `TEXT` | Clean badge label (`0-2 yrs`, `1-3 yrs`, `5+ yrs`) |
| `is_india_eligible` | `INTEGER` | Boolean (1 = applicable from India in EN/HI, 0 = Ineligible) |
| `location_status` | `TEXT` | Status message (`India (Local/Remote)`, `Global Remote`, `Ineligible Location`) |
| `language_status` | `TEXT` | Status message (`English / Hindi Eligible`, `Foreign Language Required`) |
| `is_saved` | `INTEGER` | Bookmark toggle |
| `application_status` | `TEXT` | Tracking status (`new`, `saved`, `applied`, `interviewing`) |
| `scraped_at` | `TEXT` | Timestamp of last sync |

### Table: `interview_sessions`
Tracks active and historical simulated interviews across the 5 rounds:
`session_id`, `job_id`, `company`, `role_title`, `current_round`, `total_rounds`, `round_name`, `is_completed`, `overall_score`, `feedback_summary`, `history` (JSON messages), `updated_at`.

### Table: `resume_personas`
Stores multiple specialized candidate profiles:
- `production_systems`: Application Production Systems Specialist (Java, Spring Boot, SQL, Docker, Linux, GCP).
- `software_engineer`: Software Engineer & Backend Developer.
- `ai_rlhf_trainer`: AI Trainer & RLHF Specialist.
- `microtask_evaluator`: Data & Quality Evaluation Specialist.

---

## 3. Speech & Voice Architecture

```
[Candidate Mic]
       |
       v (Web Speech API / Audio Recording)
+--------------------------------------------------------------+
| In-Browser Speech Recognition (webkitSpeechRecognition)      |
|  - Real-time zero-latency streaming text input               |
+--------------------------------------------------------------+
       | (Fallback if browser STT unavailable)
       v (MediaRecorder audio/webm blob)
+--------------------------------------------------------------+
| POST /api/transcribe                                         |
|  1. Local Whisper Sidecar (http://localhost:8178/inference)  |
|  2. Groq Cloud Whisper API (whisper-large-v3-turbo)          |
+--------------------------------------------------------------+
```

---

## 4. API Endpoints Reference

- `GET /api/jobs`: Query parameters: `tier`, `category`, `company`, `max_exp`, `india_only`, `search`.
- `GET /api/companies`: Returns all companies with total gigs, eligible experience counts, and India counts.
- `GET /api/metrics`: Live counters for total jobs, India-eligible jobs, resume matches ($\le 3$ yrs), and perfect matches.
- `POST /api/scan`: Triggers asynchronous scan across all scrapers.
- `GET /api/jobs/{id}/tailored-resume`: Produces ATS resume tailored for the selected job with Anti-AI detector burstiness.
- `GET /api/jobs/{id}/interview-packet`: Generates role-specific dossier with predicted questions, winning answers, and rubric criteria.
- `POST /api/interview/start`: Initializes a new 5-round interactive interview session.
- `POST /api/interview/chat`: Processes candidate spoken/written response and advances the interview state machine.
- `GET /api/whisper-status`: Reports health status of local Whisper and Groq STT engines.
- `POST /api/transcribe`: Accepts audio recording upload and returns transcribed text.
