# Changelog — Iterative Development History

All notable updates, fixes, and feature additions to the **AI Gig Hunter & Interview Simulator** are documented below.

---

## [1.3.0] — 2026-11-20

### Added
- **Candidate Location & Language Shield (India Gate):**
  - Added `check_location_and_language()` in `app/services/pay_parser.py`.
  - Filters out on-site postings in San Francisco, Toronto, New York, London, Berlin, Paris, Tokyo, etc.
  - Excludes jobs requiring foreign languages (German, Spanish, French, Japanese, Arabic, Russian, Portuguese, etc.).
  - Default view on dashboard is now strictly `🇮🇳 India Eligible Only` (curating the 35 verified applicable gigs).
- **Dockerization Suite:**
  - Added `Dockerfile` based on `python:3.12-slim`.
  - Added `docker-compose.yml` with port `8000:8000` mapping, host `./data` volume mount, and healthcheck.
  - Added `.dockerignore` to prevent staging virtual environments and local secrets.
- **Collab Multi-Agent Review Suite:**
  - Added `collab/` directory containing `README.md`, `ARCHITECTURE.md`, `FEATURE_DOSSIER.md`, `REVIEW_CHECKLIST.md`, and `CHANGELOG.md` for external AI agent auditing.
- **System Agent Blueprint (`AGENTS.md`):**
  - Documented the multi-agent architecture and heuristic rubrics.

### Changed
- Refactored `GET /api/jobs` to support `india_only: Optional[bool]`.
- Added `GET /api/metrics` endpoint providing live counters across all candidate dimensions.
- Updated dashboard UI with a top-priority Location & Language Verification Banner with 1-click switcher.

---

## [1.2.0] — 2026-11-19

### Added
- **Experience Level Filter ($\le 3$ Years Match):**
  - Added `extract_experience_years()` in `app/services/pay_parser.py`.
  - Added `min_exp_years` and `exp_label` columns to `jobs` table in SQLite.
  - Implemented `🎯 Fits My Resume (≤ 3 Years)` filter pill enabled by default.
  - Tagged all job cards with visual experience badges (`🎯 0-3 yrs (Fits Resume)` vs `⚠️ 5+ yrs (Senior)`).
- **Company Filter:**
  - Added dynamic company dropdown with live job counts.
  - Added 1-click pills for Scale AI, Outlier, Alignerr, Mercor, Cohere, Surge AI, DataAnnotation, Turing, and Invisible Technologies.
  - Added `GET /api/companies` endpoint.

---

## [1.1.0] — 2026-11-19

### Added
- **Interactive 5-Round AI Interview Simulator:**
  - Added `app/services/interview_agent.py` supporting 5 rounds (Screening, Technical Logic, RLHF, Red-Teaming, Report Card).
  - Integrated Whisper speech-to-text with microphone recording button in modal.
  - Added honest frontier model rubric scoring using `gemini-3.8-flash`.
- **Anti-AI Detector Shield:**
  - Added `clean_ai_cliches()` and sentence burstiness formatter in `app/services/humanizer.py`.
- **Role-Specific Interview Packet:**
  - Added `app/services/interview_packet.py` generating role dossiers with predicted questions, winning formulations, and rubric red flags.
- **Multi-Persona Resume Vault:**
  - Added `resume_personas` table with 4 specialized roles (Production Systems, Software Engineer, AI RLHF Trainer, Quality Evaluator).

---

## [1.0.0] — 2026-11-19

### Initial Release
- Multi-ATS parallel scraper (Ashby, Greenhouse, Lever, Direct Platforms).
- FastAPI backend with SQLite storage (`data/gighunter.db`).
- Interactive Tailwind CSS single-page dashboard.
