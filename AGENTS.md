# AGENTS.md — Agentic Architecture & System Specification

This document defines the autonomous and interactive agent architecture powering the **AI Gig Hunter & Interview Simulator** platform, detailing each agent's role, decision rubric, operational boundaries, and collaborative protocols.

---

## 1. System Agent Overview

The platform operates an ecosystem of specialized agents designed to automate discovery, eliminate location and experience mismatches, generate tailored ATS assets, and conduct high-rigor interactive voice interviews.

```
                              +---------------------------------------+
                              |          Candidate (Applicant)        |
                              +-------------------+-------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
             +------------------------+                        +-----------------------+
             | Multi-Portal Scraper   |                        | Interactive Voice     |
             | & Classification Agent |                        | AI Interview Agent    |
             +-----------+------------+                        +-----------+-----------+
                         |                                                 |
       +-----------------+-----------------+               +---------------+---------------+
       |                                   |               |                               |
       v                                   v               v                               v
+--------------+                   +---------------+ +--------------+              +---------------+
| India Gate & |                   | Resume Vault  | | Speech STT   |              | Frontier AI   |
| Exp Filter   |                   | & Humanizer   | | Whisper Node |              | Rubric Scorer |
+--------------+                   +---------------+ +--------------+              +---------------+
```

---

## 2. Agent Catalog & Responsibilities

### Agent 1: The Multi-Portal Ingestion & Classification Agent
- **Module:** `app/scrapers/runner.py`, `app/scrapers/{ashby, greenhouse, lever, direct_platforms}.py`
- **Role:** Asynchronously monitors, fetches, normalizes, and classifies job listings from Ashby API, Greenhouse API, Lever API, and direct platform contributor networks (Scale AI, Outlier, Alignerr, Mercor, Cohere, Surge AI, Turing, Invisible Technologies, DataAnnotation, etc.).
- **Decision Rubric:**
  - Standardizes compensation to hourly equivalents (`$/hr`) and categorizes into Microtask ($2-$15), Mid-Tier ($15-$30), and Expert ($30-$100+).
  - Classifies domain focus into Coding, Math & Logic, Writing & RLHF, Multilingual, or Generalist.
  - Determines interview mechanism: `AI Video Interview`, `Automated Screening Test`, `Direct Onboarding`, or `Human Interview`.

---

### Agent 2: The Location & Language Gate Agent (India Shield)
- **Module:** `app/services/pay_parser.py -> check_location_and_language`
- **Role:** Enforces candidate-specific geographical and linguistic eligibility to prevent auto-rejection.
- **Candidate Profile:** Based in **India**; fluent in **English** and **Hindi**.
- **Rejection Heuristics:**
  - Rejects on-site or country-restricted roles in North America/Europe (e.g. San Francisco, Toronto, New York City, Washington DC, London, Berlin, Paris, Tokyo, etc.).
  - Rejects roles requiring foreign languages (e.g. German, Spanish, French, Japanese, Arabic, Russian, Portuguese, Italian, Korean, Dutch, Igbo, etc.).
- **Approval Heuristics:**
  - Approves explicit India locations (Bengaluru, Chennai, Hyderabad, Noida, Pune, Mumbai, Remote India).
  - Approves global remote networks (`Worldwide`, `Global Remote`, `Remote (Worldwide)`).
  - Approves general coding/reasoning roles conducted in English or Hindi.

---

### Agent 3: Experience & Seniority Normalization Agent
- **Module:** `app/services/pay_parser.py -> extract_experience_years`
- **Role:** Evaluates candidate resume alignment (~2-3 years backend Java/Spring Boot/SQL/Cloud) and shields from Senior/Staff/Lead disqualification.
- **Rules:**
  - Flags `Senior`, `Staff`, `Principal`, `Lead`, `Director`, `Architect` as $\ge 5$ years.
  - Recognizes assessment-driven crowdsourcing gigs (Outlier, Alignerr, DataAnnotation) as `0-2 yrs (Assessment Based)`.
  - Tags mid-level individual contributor developer positions as `1-3 yrs (Mid-Level)`.
  - Enables 1-click filtering: `🎯 Fits My Resume (≤ 3 Years)` displaying only roles where the candidate is eligible.

---

### Agent 4: The 4-Round Interactive AI Interviewer Agent (with Final Report Card)
- **Module:** `app/services/interview_agent.py`
- **Role:** Conducts real-time, voice-enabled, multi-round technical and alignment interviews tailored to the specific company (Cohere, Scale AI, Mercor, Turing, Alignerr, etc.) and role.
- **Round State Machine:**
  1. `Screening & Background`: Technical workflows, communication clarity, alignment background.
  2. `Domain Logic & Technical Rigor`: Coding critique, edge-case analysis, algorithmic complexity.
  3. `RLHF & Pairwise Evaluation`: Rubric-based model evaluation, truthfulness vs helpfulness trade-offs.
  4. `Safety, Adversarial & Red-Teaming`: Jailbreak detection, prompt injection mitigation, bias identification.
  5. `Final Comprehensive Report Card`: Quantitative score out of 100, competency breakdown, hiring recommendation.
- **Scoring Protocol:** Uses Google's frontier model API (`gemini-3.8-flash`) or local fallbacks to deliver honest, uncompromising rubric scores and step-by-step guidance.

---

### Agent 5: The Anti-AI Humanizer & Resume Tailoring Agent
- **Module:** `app/services/humanizer.py`, `app/services/resume_generator.py`
- **Role:** Generates tailored ATS resumes and application question responses that bypass AI detectors (GPTZero, Turnitin, CopyLeaks).
- **Execution Rules:**
  - **Burstiness Variation:** Alternates sentence lengths (short punchy lines with medium technical explanations).
  - **Zero LLM Clichés:** Systematically replaces synthetic buzzwords (*"delve"*, *"testament"*, *"beacon"*, *"multifaceted"*, *"crucial"*, *"pivotal"*, *"orchestrated"*, *"seamlessly"*) with direct developer phrasing (*"built"*, *"debugged"*, *"monitored"*, *"fixed"*, *"benchmarked"*).
  - **First-Person Anecdotes:** Grounds claims in practical production engineering (incident triage, thread pool exhaustion, latency bottlenecks, microservice uptime).

---

### Agent 6: Speech & Audio Sidecar Agent (Whisper STT)
- **Module:** `app/services/speech.py`
- **Role:** Transcribes candidate spoken responses captured via microphone.
- **Tiered Fallback Mechanism:**
  1. Primary: Local Whisper HTTP sidecar (`http://localhost:8178/inference`).
  2. Secondary: Groq Whisper cloud API (`whisper-large-v3-turbo`).
  3. Tertiary: Browser Web Speech API (`webkitSpeechRecognition`).

---

## 3. Summary of Actions Completed on This Project

1. **Multi-ATS Integration:** Built parallel crawlers for Ashby, Greenhouse, Lever, and Direct AI platforms (Scale AI, Outlier, Alignerr, Mercor, Cohere, Surge AI, Turing, Invisible Technologies, DataAnnotation, Appen, etc.) indexing 521+ live listings.
2. **India Location Gate:** Implemented regex and metadata filtering that eliminates all location-ineligible (San Francisco, Toronto, NYC, London, US-only) and language-ineligible (German, Spanish, French, Japanese, Arabic) jobs.
3. **Experience Matcher:** Created automated experience parser that tags Senior/Lead 5+ year roles and defaults dashboard to `🎯 Fits My Resume (≤ 3 Years)` (30-35 highly-eligible positions).
4. **Voice-Enabled Interview Simulator:** Built a 4-round stateful interview engine with voice recording, live transcription, hint rubrics, and comprehensive final report cards.
5. **Anti-AI Detector Shield:** Developed text burstiness reformatter and cliché stripper to ensure application answers and resumes score 0% on AI detection benchmarks.
6. **Dockerization:** Packaged the entire stack into a containerized `Dockerfile` with `docker-compose.yml`, healthchecks, and SQLite volume persistence.
7. **Collab Multi-Agent Review Suite:** Created the `collab/` directory containing architecture blueprints, feature dossiers, changelogs, and review rubrics for external AI agent evaluation.
8. **Git Repository Management:** Securely committed and pushed all clean code to `https://github.com/ankittomar9/ai-gig-platform` with strict credential exclusion.
