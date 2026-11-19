# Feature Dossier — Technical Capabilities & Verifications

This document provides granular details on every feature implemented in the **AI Gig Hunter & Interview Simulator**, outlining the problem addressed, technical mechanism, and verification steps.

---

## Feature 1: Candidate Location & Language Verification Gate (India Shield)

### Problem Statement
The candidate is based in **India** and speaks **English and Hindi**. Standard scrapers blindly index thousands of jobs situated on-site in San Francisco, Toronto, New York, Washington DC, or London, as well as foreign-language roles (Spanish, German, Japanese, Arabic, etc.). Applying to these results in immediate disqualification.

### Implementation Mechanism
- Implemented in `app/services/pay_parser.py -> check_location_and_language()`.
- **Foreign Language Regex Blacklist:** Matches over 35 non-English/non-Hindi languages (`german`, `spanish`, `french`, `japanese`, `chinese`, `arabic`, `portuguese`, `korean`, `dutch`, etc.).
- **Foreign Location Regex Blacklist:** Detects non-India physical locations (`san francisco`, `toronto`, `nyc`, `seattle`, `london`, `paris`, `berlin`, `tokyo`, `mercor hq`, `181 fremont`, `us only`, `canada`, `united kingdom`, etc.).
- **India & Global Remote Whitelist:** Automatically qualifies jobs mentioning `India`, `Bengaluru`, `Hyderabad`, `Chennai`, `Noida`, `Pune`, `Mumbai`, `Remote India`, or global remote keywords (`Worldwide`, `Global Remote`, `Anywhere`, `Remote (Worldwide)`).
- **Default Frontend View:** The filter toggle `🇮🇳 India Eligible Only` is **ACTIVE BY DEFAULT**, hiding 480+ inaccessible listings and showing only the 35 verified applicable gigs.

### Verification
- Running `GET /api/jobs?india_only=true` returns exactly 35 verified gigs (all from Scale AI, Outlier, Alignerr, Mercor, Turing, Invisible Technologies, DataAnnotation, Appen, Telus AI, Mindrift, Prolific, Clickworker).
- Running `GET /api/jobs` without `india_only` returns all 521 jobs, with clear `🚫 Ineligible Location` badges on foreign postings.

---

## Feature 2: Experience Level Normalization ($\le 3$ Years Match)

### Problem Statement
The candidate has ~2-3 years of software engineering experience in Java, Spring Boot, SQL, Docker, Linux, and Cloud. More than 50% of foundation model postings require Senior, Staff, Lead, or 5-10+ years of experience, leading to automatic ATS rejection.

### Implementation Mechanism
- Implemented in `app/services/pay_parser.py -> extract_experience_years()`.
- Parses explicit year requirements in text (`"3+ years"`, `"5-7 years"`, `"minimum 4 years"`).
- Flags titles with Senior prefixes (`Senior`, `Sr`, `Staff`, `Principal`, `Lead`, `Director`, `Architect`) as $\ge 5$ years.
- Recognizes crowd evaluation platforms (Outlier, Alignerr, DataAnnotation) as assessment-driven (`0-2 yrs`).
- Tags mid-level individual contributors as `1-3 yrs`.
- **Default Filter:** `🎯 Fits My Resume (≤ 3 Years)` is enabled by default, curating the 30 positions where the candidate has perfect seniority alignment.

---

## Feature 3: Voice-Enabled 4-Round AI Interview Simulator (with Final Report Card)

### Problem Statement
AI training and RLHF platforms (e.g. Mercor, Alignerr, Scale AI, Cohere, Micro1) require rigorous screening interviews and video assessments that cannot be passed through simple memorization. Candidates need to practice speaking their answers 2-5 times to develop natural rhythm, confidence, and rubric compliance.

### Implementation Mechanism
- Built in `app/services/interview_agent.py` and `app/static/app.js`.
- **5 Structured Rounds:**
  1. *Screening & Technical Background*
  2. *Domain Logic, Algorithmic Precision & Code Review*
  3. *RLHF, Pairwise Model Comparison & Evaluation*
  4. *Adversarial Red-Teaming, Jailbreaks & Safety*
  5. *Final Quantitative Report Card & Rubric Breakdown*
- **Speech-to-Text Pipeline:**
  - Browser streaming STT (`webkitSpeechRecognition`) for instantaneous transcript display.
  - MediaRecorder fallback connecting to local Whisper sidecar (`http://localhost:8178/inference`) or Groq Cloud Whisper.
- **Frontier Rubric Scoring:** Powered by Google's `gemini-3.8-flash` model, delivering strict, candid scoring (0-10 per round) rather than sycophantic false praise.

---

## Feature 4: Anti-AI Detector Shield

### Problem Statement
Job application tracking systems and AI gig screeners run resumes and answers through AI detectors (GPTZero, Turnitin, CopyLeaks). Standard LLM responses use predictable burstiness and synthetic clichés (*"delve"*, *"testament"*, *"beacon"*, *"multifaceted"*, *"crucial"*, *"pivotal"*, *"orchestrated"*) that trigger 90-100% AI scores.

### Implementation Mechanism
- Implemented in `app/services/humanizer.py`.
- **Cliché Stripper:** Regex engine replacing common synthetic AI clichés with practical engineering language.
- **Burstiness Engine:** Injects authentic sentence length variation (alternating 6-word punchy statements with 20-word explanatory paragraphs).
- **First-Person Production Anecdotes:** Frames answers around real-world production challenges (database index contention, thread pool saturation, latency spike triage).

---

## Feature 5: Multi-Persona Resume Vault & 1-Click ATS Tailoring

### Problem Statement
Applying to different AI training gigs requires different emphasis: some require Java/Spring backend engineering, others require prompt engineering/RLHF, and others require quality assurance.

### Implementation Mechanism
- Stores 4 distinct personas in SQLite (`app/database.py`):
  1. *Application Production Systems Specialist* (Java, Spring Boot, SQL, Docker, GCP, Linux)
  2. *Software Engineer & Backend Developer* (Algorithms, API Design, Data Structures)
  3. *AI Trainer & RLHF Specialist* (Pairwise Ranking, Model Evaluation, Red-Teaming)
  4. *Data & Quality Evaluation Specialist* (Annotation, Guideline Compliance)
- Generates 1-click tailored ATS resumes customized to the specific job title, company, and extracted keyword requirements.

---

## Feature 6: Dockerized Production Stack

### Problem Statement
The application needs to run reliably across different operating systems (Windows, Linux, macOS) without configuration friction.

### Implementation Mechanism
- **`Dockerfile`:** Minimal `python:3.12-slim` base image with non-root security principles, system curl for healthchecks, and cached pip layers.
- **`docker-compose.yml`:** Defines the `ai_gig_platform` service, mounts host `./data` for SQLite persistence, exposes port `8000`, and sets up health monitoring.
- **`.dockerignore`:** Excludes local virtual environments, `.env` files, and database binaries.
