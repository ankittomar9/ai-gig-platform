# AI Gig Hunter & Interview Simulator OS ⚡

A unified, full-stack platform built with **Python FastAPI** that aggregates and filters AI data annotation, RLHF, prompt engineering, and domain evaluation contracts across **8 live ATS boards** (including Ashby, Greenhouse, Lever) plus **19 curated direct platform listings** (~12–19 distinct AI evaluation brands, with on-demand and initial-scan fetching).

Equipped with a **Location & Language Eligibility Gate (India Shield)**, **Experience Normalizer ($\le 3$ Years)**, **1-Click Application Pack Generator**, **Anti-AI Detector Shield**, **Docker Containerization**, and an **Interactive 4-Round Voice AI Interview Simulator (with Final Quantitative Report Card)**.

---

## 🌟 Key Capabilities

### 1. 🇮🇳 Candidate Location & Language Verification Gate (India Shield)
- Specifically calibrated for candidates based in **India** fluent in **English and Hindi**.
- **Location Disqualification:** Automatically filters out all on-site or country-restricted roles in North America and Europe (San Francisco, Toronto, New York City, Washington DC, London, Berlin, Paris, Tokyo, etc.).
- **Language Disqualification:** Rejects roles requiring foreign non-English/non-Hindi languages (German, Spanish, French, Japanese, Arabic, Russian, Portuguese, Italian, Korean, Dutch, Igbo, etc.).
- **1-Click Toggle:** Active by default, presenting a curated feed of verified positions you can apply for from India without visa or location barriers.

### 2. 🎯 Experience Level Matcher ($\le 3$ Years Fit)
- Aligned to the candidate's ~2-3 years backend software engineering background (Java, Spring Boot, SQL, Docker, GCP, Linux).
- Automatically filters out Senior, Staff, Principal, Lead, and 5-10+ year positions that lead to automatic rejection.
- Prioritizes assessment-based platforms (Outlier, Alignerr, DataAnnotation) and mid-level software engineering roles.

### 3. 🏢 Platform & Company Breakdown (520+ Gigs Indexed)
- **Greenhouse ATS:** Scale AI, Outlier (Remotasks), Turing, Invisible Technologies.
- **Ashby ATS:** Mercor, Cohere, Surge AI.
- **Lever ATS:** Appen.
- **Direct Contributor Platforms:** Alignerr (Labelbox), DataAnnotation.tech, Micro1, Mindrift (Toloka), Clickworker/UHRS, Prolific, Telus International AI, OneForma.

### 4. 🎙️ Interactive 4-Round Voice AI Interview Simulator (with Final Report Card)
- **Voice STT Input:** In-browser streaming Speech-to-Text (`webkitSpeechRecognition`) with MediaRecorder fallbacks to local Whisper sidecars (`http://localhost:8178`) and Groq Cloud Whisper.
- **4 Structured Rounds + Final Evaluation:**
  1. *Background & Technical Screening*
  2. *Domain Logic & Algorithmic Code Review*
  3. *RLHF & Pairwise Model Output Ranking*
  4. *Adversarial Red-Teaming, Jailbreaks & Safety*
  - *Final Quantitative Report Card & Rubric Evaluation*
- **Frontier AI Scoring:** Evaluated by Google's `gemini-3.8-flash` for honest, non-sycophantic scoring.

### 5. 🛡️ Anti-AI Detector Shield
- Humanizes application answers and generated resumes to bypass AI detectors (GPTZero, Turnitin, CopyLeaks).
- Replaces common synthetic AI clichés (*"delve"*, *"testament"*, *"beacon"*, *"multifaceted"*, *"pivotal"*) with authentic developer language.
- Enforces natural burstiness (varying sentence lengths) and anchors claims in real-world production engineering anecdotes.

### 6. 📁 Multi-Persona Resume Vault & 1-Click Tailored ATS Resumes
- Pre-loaded with 4 specialized candidate personas:
  - Application Production Systems Specialist (Java, Spring Boot, SQL, Docker, Linux, GCP)
  - Software Engineer & Backend Developer
  - AI Trainer & RLHF Specialist
  - Data & Quality Evaluation Specialist
- Generates dynamic tailored ATS resumes tailored to the specific target gig in one click.

---

## 🐳 Docker Deployment

The application is fully containerized and can be started with a single command:

```bash
# Build and run with Docker Compose
docker compose up -d --build
```

The service will be live at `http://localhost:8000` with automated healthchecks and persistent SQLite storage mounted to `./data`.

To stop the container:
```bash
docker compose down
```

---

## 🚀 Local Quick Start (Without Docker)

### Option 1: One-Click Windows Runner
Double-click `run.bat` in the repository root:
```cmd
run.bat
```

### Option 2: Manual PowerShell Launch
```powershell
# 1. Activate Virtual Environment
cd ai-gig-platform
.\venv\Scripts\activate

# 2. Start FastAPI Server
$env:PYTHONPATH="."
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 👥 Collab Review Suite for AI Agents

For autonomous reviewing AI agents and human evaluators auditing this repository:
- Review the agentic system specification in [`AGENTS.md`](./AGENTS.md).
- Inspect the architectural blueprint in [`collab/ARCHITECTURE.md`](./collab/ARCHITECTURE.md).
- Verify feature coverage against [`collab/FEATURE_DOSSIER.md`](./collab/FEATURE_DOSSIER.md).
- Execute the verification scorecard in [`collab/REVIEW_CHECKLIST.md`](./collab/REVIEW_CHECKLIST.md).
- Track the iterative development history in [`collab/CHANGELOG.md`](./collab/CHANGELOG.md).

---

## 🔒 Security & Privacy

- Strict `.gitignore` and `.dockerignore` prevent leaking `.env`, private keys, or SQLite databases.
- Masked API key display on the web dashboard.
- Zero local network exposure; binds locally by default.
