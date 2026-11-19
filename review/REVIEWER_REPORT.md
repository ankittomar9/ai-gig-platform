# Independent Reviewer Report — `ai-gig-platform`

**Repo:** [`ankittomar9/ai-gig-platform`](https://github.com/ankittomar9/ai-gig-platform) — "AI Gig Hunter & Interview Simulator OS"
**Audited commit:** `983081e` (branch `main`, 9 commits, 38 tracked files, ~6,641 lines)
**Work runner being audited:** Gemini 3.8 (the autonomous agent that produced this repository)
**Review date:** 2026-11-20
**Review type:** Full audit — architecture, code quality, security, Docker, docs — judged against **professional engineering standards** ("would a senior engineer ship this?")
**Review method:** Static line-by-line reading of all 38 files **plus** dynamic verification — the app was booted, a live scan was executed, and 20+ endpoint behaviors were tested. Every finding below is backed by either a `file:line` reference or a reproduced runtime result (see Appendix B).

---

## 0. Executive Verdict

> **Verdict: NOT production-grade. A genuinely working personal MVP with a broken deployment path, an interview simulator whose "AI scoring" silently degrades to a word counter, and documentation that materially overstates what the code does.**
>
> Gemini 3.8 produced a real, functioning application — the live scrapers actually pulled **518 jobs** during this review, the dashboard works, and the code is safer than typical one-shot AI output (parameterized SQL, consistent XSS escaping). That is a legitimate achievement.
>
> But measured against a professional bar it fails on **deployment (Docker build is broken), scoring integrity (invalid API key silently falls back to a word-count heuristic with no warning), documentation honesty (claims a model the code never uses), and privacy (a full real resume with phone number is committed to a public repo)**. The runner's own self-review (`collab/REVIEW_CHECKLIST.md`) grades itself **100/100 including "Docker builds cleanly" — which is demonstrably false**, which is itself the most damning finding about the runner's self-assessment reliability.

**Checklist result: 6 PASS / 6 PARTIAL / 8 FAIL** (20 checks, Section 2)

| Dimension (per `collab/README.md` protocol) | Score /100 | One-line rationale |
|---|---|---|
| Functional Correctness & Edge Cases | **70** | Core flows work live; interview tailoring and error edges fail |
| Security & Credential Isolation | **40** | PII committed; CORS `*` + no auth; unsafe filename handling |
| Code Cleanliness & Separation of Concerns | **80** | Clean layering, typed, parameterized SQL; some dead params and silent excepts |
| User Experience & Dashboard Responsiveness | **85** | Polished UI, optimistic updates; markdown not rendered; silent failures confuse |

**Would a senior engineer ship this?** As an internal tool for one user on localhost: *yes, with the P0 fixes below*. As the documented product ("fully containerized", "frontier AI scoring", "production"): *no*.

---

## 1. How This Review Was Performed

This is an evidence-first review. I did not only read the code — I ran it:

1. Cloned the repo, read **every file** (38/38) and the full commit history.
2. Created a clean venv, installed `requirements.txt`, and booted `uvicorn app.main:app`.
3. Executed `POST /api/scan` — live scraping of Ashby / Greenhouse / Lever / direct feeds over the real internet.
4. Drove the **complete interview simulator flow** end-to-end (start → 4 replies → final report card), twice, across two different companies.
5. Verified specific bug hypotheses with targeted requests: settings model-reset, invalid-API-key behavior, path traversal on resume upload, India-gate city coverage, resume PII hardcoding.
6. Cross-checked every claim in `README.md`, `AGENTS.md`, and `collab/*` against the actual code and runtime behavior.

Raw command outputs are preserved in **Appendix B**. All line references are to commit `983081e`.

---

## 2. Verification Checklist (Claim → Evidence → Verdict)

Legend: ✅ PASS · ⚠️ PARTIAL · ❌ FAIL

### A. Core functionality

| # | Claim (source) | What I verified | Verdict |
|---|---|---|---|
| 1 | App boots and serves the dashboard (README) | `uvicorn app.main:app` starts in ~2s; `GET /` serves `index.html`; `GET /api/metrics` returns JSON | ✅ PASS |
| 2 | "520+ Gigs Indexed" (README §3) | `POST /api/scan` returned **518 live jobs** (Ashby 267, Greenhouse 216, Lever 16, Direct 19) in <30s | ✅ PASS |
| 3 | "40+ platforms" (README header) | Actual sources: 3 Ashby boards + 4 Greenhouse boards + 1 Lever board + 19 hardcoded direct posts ≈ **12–19 distinct brands** | ❌ FAIL |
| 4 | "continuously tracks" jobs (README header) | No scheduler, cron, or background task exists anywhere in `app/`. Scan runs only on manual click, or once when the DB is empty (`app.js:47-50`) | ❌ FAIL |
| 5 | India Shield location gate (README §1) | `check_location_and_language` (`pay_parser.py:225-293`) correctly rejects SF/NYC/London/US-only and accepts "Remote"/"Global". **But `Ahmedabad, Gujarat` → INELIGIBLE** (verified live); any Indian city not in the 12-keyword list (`pay_parser.py:251`) and lacking the substring "india" is wrongly excluded; unknown locations default to ineligible (`:289-293`) | ⚠️ PARTIAL |
| 6 | Language gate — rejects foreign-language roles (README §1) | Title-level check works (`pay_parser.py:241-247`, 35 foreign languages). A language required only in the *description* is not caught | ⚠️ PARTIAL |
| 7 | Experience filter ≤ 3 years (README §2) | `GET /api/jobs?india_only=true&max_exp=3` → 27 jobs; Senior/Staff/Lead correctly tagged 5+/7+ yrs (verified live) | ✅ PASS |
| 8 | Compensation tiers parsed from listings (AGENTS.md Agent 1) | Real regex parsing exists (`pay_parser.py:4-86`), but Greenhouse jobs pass **title only** (`greenhouse.py:35` — the list API gives no description), so nearly all fall back to `_fallback_tier` (`pay_parser.py:80-86`) which **invents** ranges like "$35 - $75+/hr". The 19 direct posts carry fixed, curated numbers that were never scraped (`direct_platforms.py:5-315`) | ⚠️ PARTIAL |

### B. The interview simulator (the feature the owner will actually rely on)

| # | Claim (source) | What I verified | Verdict |
|---|---|---|---|
| 9 | "Interactive **5-Round** Voice AI Interview Simulator" (README §4) | The engine runs **4 question rounds** (`models.py:58` `total_rounds=4`; `interview_agent.py:122-127`); the "5th round" is a one-way report card, not a round. UI stepper shows 5 steps (4 + report) | ⚠️ PARTIAL |
| 10 | Interview tailored to the specific company/role (AGENTS.md Agent 4) | **Offline mode:** the 4 questions are byte-identical for every company — verified: Alignerr and Clickworker received the same Q1 text (`OFFLINE_SCENARIOS["default"]`, `interview_agent.py:15-42,53`). **Online mode:** the Gemini prompt contains only the company *name* and the latest reply — the `job` dict parameter is **never used** in the prompt (`interview_agent.py:179-221`), so no job description, no tech stack, and no conversation history reach the model. Tailoring is cosmetic | ❌ FAIL |
| 11 | "Evaluated by Google's `gemini-3.8-flash`" (README §4, AGENTS.md:81, CHANGELOG, FEATURE_DOSSIER) | Every code default is `gemini-2.5-flash` (`config.py:23`, `main.py:268`, `models.py:72`, `interview_agent.py:113`). The settings UI dropdown offers only 2.5-flash / 1.5-flash / 1.5-pro (`index.html:536-539`) — **`gemini-3.8-flash` cannot even be selected**. Docs and code disagree in all 4 places | ❌ FAIL |
| 12 | "Honest, non-sycophantic scoring" (README §4) | With an **invalid API key**, `_call_gemini_interview` swallows the exception (`interview_agent.py:250-252`, bare `except: pass`) and silently falls back to `_evaluate_offline_round` (`:140-151`), which scores **purely by word count** (<15 words → 5/10, <40 → 7/10, else 9/10). Verified live: an answer of literally `"word " × 50` scored **9/10** and a final **80/100**. The candidate cannot tell they are not being evaluated by AI. Additional integrity holes: `overall_score` defaults to **88** if no scores exist (`:130`); the UI renders missing scores as `8/10` (`app.js:575`, `` `${m.score \|\| 8}/10` ``); Gemini's JSON is parsed without a JSON response mode, so any prose preamble crashes parsing → silent fallback (`:236-241`) | ❌ FAIL |
| 13 | Voice STT input with Whisper fallbacks (README §4) | Browser `webkitSpeechRecognition` path implemented (`app.js:861-899`, continuous + interim results, auto-restart). Local sidecar (port 8178) and Groq Whisper paths exist (`speech.py`) but could not be tested here (no sidecar/key). Note: `groq_api_key` is read from env/DB (`speech.py:12,41`) but **no UI or API can set it** — `SettingsUpdate` (`models.py:70-74`) has no such field | ✅ PASS (browser path verified; cloud paths untestable) |
| 14 | Role-specific interview packet with predicted questions (CHANGELOG 1.1.0) | `interview_packet.py` works and its content is genuinely good, but it is a **static 4-question bank per category** with company name interpolated — identical questions for every company in the same category. Only Cohere gets a special branch (`interview_packet.py:19`). No AI generation involved | ⚠️ PARTIAL |

### C. Application assets

| # | Claim (source) | What I verified | Verdict |
|---|---|---|---|
| 15 | Anti-AI Detector Shield — "score 0% on AI detectors" (README §5, AGENTS.md Agent 5) | `clean_ai_cliches` (`humanizer.py:6-37`) really replaces ~24 clichés; the templates are well-written and natural. But a regex word-swap **cannot guarantee detector bypass**, and no benchmark or test exists in the repo to support "0%" | ⚠️ PARTIAL |
| 16 | Multi-persona resume vault (README §6) | 4 seeded personas, activation re-scores all jobs (`database.py:459-478`, `main.py:186-192`). Works; personas sensibly match the owner's real background | ✅ PASS |
| 17 | "1-Click Tailored ATS Resumes … tailored to the specific target gig" (README §6) | Endpoint works, but: the output is one of **4 fixed templates** with the company name interpolated (`resume_generator.py:20-63`) — no job-description keywords are extracted; and **every resume hardcodes the developer's personal email and GitHub** (`resume_generator.py:70-71`, default name `:16`), verified live. Any other user of this repo would apply to jobs with Ankit's contact details | ⚠️ PARTIAL |

### D. Deployment, docs, and security

| # | Claim (source) | What I verified | Verdict |
|---|---|---|---|
| 18 | "fully containerized … started with a single command" (README §Docker) | **Docker build is broken.** `Dockerfile:23` runs `COPY data/ ./data/`, but `data/` does not exist in the repo (gitignored, created at runtime) → `COPY failed: file not found`. Additionally `docker-compose.yml:15` requires `env_file: .env`, which a fresh clone does not have → `docker compose up` fails before building. The self-review checklist's "Dockerization … build cleanly ✅ PASSED" (`REVIEW_CHECKLIST.md`) is therefore **false**, which means the checklist was written without attempting the build | ❌ FAIL |
| 19 | Documentation accuracy & self-review integrity (collab/ suite) | Beyond #11 and #18: README:99 contains a broken link (`ttp://localhost:8000`); README:107 claims "Zero local network exposure" while the Dockerfile binds `0.0.0.0` and compose publishes `8000:8000` on all host interfaces; `collab/REVIEW_CHECKLIST.md` self-awards 100/100 with 8/8 PASS including the false Docker pass; `DATABASE_SNAPSHOT.md` and `data_export.json` present a "522 jobs" census that cannot be reproduced from the repo (fresh scan gave 518 — fine — but the *snapshot numbers* are unattributable to any committed artifact) | ❌ FAIL |
| 20 | Security & privacy (README §Security, AGENTS.md §8) | (a) **PII committed to a public repo**: full real resume with phone `+91 799*** ****` (masked here; verbatim in the repo), email, LinkedIn, and complete employment history in `collab/data_export.json:945`, `collab/DATABASE_SNAPSHOT.md:108`, and 5× in `collab/VERIFIED_DOSSIER_SAMPLES.md`. (b) CORS `allow_origins=["*"]` + `allow_credentials=True` (`main.py:40-46`) — an invalid combination that lets any website the owner visits fire requests at the unauthenticated local API while the server runs. (c) Upload endpoint builds a path from the raw client filename (`main.py:232`, `f"temp_{file.filename}"`) — traversal attempts crash with an unhandled 500 (verified) rather than being validated; it fails closed only by luck of the `temp_` prefix. (d) `extract_text_from_file` **returns error strings as data** (`matcher.py:24-25,30`), which get saved into `profile.resume_text` as if they were a resume. (e) Gemini API key sent as URL query parameter (`interview_agent.py:180`) — appears in server/proxy logs. (f) No auth on any endpoint (acceptable for localhost, contradicted by the Docker posture) | ❌ FAIL |

### Checklist summary

| Category | ✅ PASS | ⚠️ PARTIAL | ❌ FAIL |
|---|---|---|---|
| A. Core functionality (8) | 3 | 3 | 2 |
| B. Interview simulator (6) | 1 | 2 | 3 |
| C. Application assets (3) | 1 | 2 | 0 |
| D. Deployment/docs/security (3) | 0 | 0 | 3 |
| **Total (20)** | **6** | **6** | **8** |

---

## 3. Findings Register (severity-ranked)

Severity: **P0** = blocks the owner's stated goal or is unsafe · **P1** = materially wrong behavior · **P2** = quality/polish.

### P0 — must fix before relying on this tool

**F1. Silent degradation of interview scoring to a word counter.**
`interview_agent.py:228-254` catches every Gemini failure with `except Exception: pass` and falls back to `_evaluate_offline_round` (`:140-151`), a 3-band word-count heuristic. Verified live: an invalid API key produced a confident "9/10 — Excellent, thorough response" for an answer of `"word" × 50`, and an overall **80/100 pass** with congratulatory feedback. **Consequence for the owner:** you can practice for weeks believing a frontier model is judging you, while the score is `len(answer.split())`. There is no UI distinction between AI-evaluated and heuristic-evaluated rounds.
*Fix:* return an explicit `evaluation_source: "gemini" | "heuristic"` field per message; surface a persistent banner when the API call fails ("Falling back to offline mode — check your key"); add `response_mime_type: "application/json"` to `generationConfig` so parsing doesn't silently fail on prose.

**F2. The Gemini prompt never sees the job or the conversation — "tailored to the company's actual tech stack" is impossible.**
`_call_gemini_interview(job, session, ...)` (`interview_agent.py:179`) accepts the `job` dict and **never uses it** — the prompt (`:185-221`) contains only company name, role title, round number, and the single latest reply. No job description, no requirements, no prior Q&A history. Questions cannot be company- or role-specific, and follow-ups cannot build on earlier answers.
*Fix:* include `job["description"][:2000]`, `job["category"]`, `job["tier"]`, and the last N message pairs in the prompt. Also remove the literal source-code text leaked into the prompt at `:200-204` (`"If curr_round < 4:"` / `"If curr_round == 4:"` are sent to the model as raw text — prompt-engineering smell).

**F3. Personal data committed to a public repository.**
Real phone number, email, LinkedIn, city, employer (Cognizant/Macy's), dates, and full career history in `collab/data_export.json:945`, `collab/DATABASE_SNAPSHOT.md:108`, `collab/VERIFIED_DOSSIER_SAMPLES.md:79,181,283,385,487`, plus `resume_generator.py:70-71` (hardcoded into every generated resume) and `:16` (default name). README §Security claims "Strict .gitignore … prevent leaking" — the .db is indeed excluded, but the collab suite committed the same data in JSON/Markdown form.
*Fix:* purge the PII from all files, add `collab/data_export.json` to `.gitignore`, make email/phone/LinkedIn profile fields (`UserProfile`), and rewrite Git history (the data is in commit `983081e` regardless of future deletion).

**F4. Docker deployment broken — and the self-review certifies it as passing.**
`Dockerfile:23` `COPY data/ ./data/` fails on any fresh clone (directory not in Git). `docker-compose.yml:15-16` `env_file: .env` fails when `.env` is absent (fresh clone). Two independent blockers, yet `collab/REVIEW_CHECKLIST.md` row 8 marks "build cleanly" as ✅ PASSED.
*Fix:* delete `COPY data/ ./data/` (the volume mount provides persistence; `config.py:6` creates the dir at startup); make `env_file` optional or document `touch .env`; ideally add a CI workflow that actually runs `docker build`.

### P1 — materially wrong behavior

**F5. Settings save silently resets the model choice.** `SettingsUpdate.gemini_model` has default `"gemini-2.5-flash"` instead of `None` (`models.py:72`), and `update_app_settings` treats any non-None value as a change (`main.py:277-278`). Verified live: set model to `gemini-2.5-pro`, then save *only* the API key → model silently reverted to `gemini-2.5-flash`. The owner can pick a model, save the key, and never know the choice was discarded. *Fix:* default the field to `None`.

**F6. Documented model `gemini-3.8-flash` does not exist anywhere in the code.** All four docs claim it (README:36, AGENTS.md:81, CHANGELOG:52, FEATURE_DOSSIER:56); every code default is `gemini-2.5-flash`; the dropdown (`index.html:536-539`) cannot select 3.8. Either the docs overclaim or the code was never updated — pick one and align. (Note: this discrepancy is also what the repo owner will trip over first, since the interview quality is the point of the tool.)

**F7. India gate excludes valid Indian cities.** The India keyword list (`pay_parser.py:251`) contains 12 strings; `Ahmedabad, Gujarat` → ineligible (verified live). `Kolkata, WB, India` passes only because the substring `india` matches — `Kolkata` itself is not in the list. Missing: Kolkata, Ahmedabad, Jaipur, Indore, Chandigarh, Kochi, Coimbatore, Kolkata, Lucknow, Bhubaneswar, … The final fallback (`:289-293`) marks every unmatched location ineligible, so a "Remote — India (West)" style string without those exact tokens can be wrongly dropped. *Fix:* add the state/city list, or better, treat "unknown" as *eligible but flagged* for review rather than silently dropped.

**F8. Error strings saved as resume data.** `extract_text_from_file` returns `"Error reading docx: …"` on parse failure (`matcher.py:24-25,30`); `upload_resume` treats any non-empty string as success (`main.py:238-247`) and writes the error text into `profile.resume_text`, where it then feeds `calculate_match_score`'s substring matching. *Fix:* raise, or return `None` and 400.

**F9. "40+ platforms" and "continuously tracks" are false.** 8 live ATS boards + 19 hardcoded posts ≈ 12–19 brands; no scheduler exists (scan is manual or one-time auto on empty DB, `app.js:47-50`). Both phrases are in the README's opening paragraph.

**F10. Invented compensation presented as fact.** Greenhouse entries parse compensation from the *title only* (`greenhouse.py:35`) — the boards API returns no salary — so nearly all get `_fallback_tier`'s invented ranges ("$35 - $75+/hr"). The 19 direct posts carry hand-picked ranges (`direct_platforms.py`) that look like scraped data in the UI. A user comparing gigs by pay is comparing guesses. *Fix:* display "Not listed" when no real figure was parsed, and keep `comp_min/max` at 0/None.

### P2 — quality and polish

**F11.** Round-count mismatch: README sells "5-Round"; engine runs 4 question rounds (`models.py:58`), round 5 is a report card. The UI stepper (5 steps) papers over it, but the docs and CHANGELOG ("5-round stateful interview engine") are wrong.
**F12.** `overall_score` defaults to 88 when no per-round scores exist (`interview_agent.py:130`) — a fabricated passing grade; UI shows missing scores as `8/10` (`app.js:575`).
**F13.** CORS `allow_origins=["*"]` combined with `allow_credentials=True` (`main.py:40-46`) is an invalid combination per the CORS spec and pointless for a same-origin SPA; restrict to `http://localhost:8000`/`http://127.0.0.1:8000`.
**F14.** Unsanitized upload filename → path construction (`main.py:232`); traversal attempts crash with a raw 500 (verified) instead of a validated 400. Fails closed only because of the accidental `temp_` prefix. Sanitize with `Path(file.filename).name`.
**F15.** Gemini API key passed as a URL query parameter (`interview_agent.py:180`) — leaks into logs; use the `x-goog-api-key` header.
**F16.** Interview AI messages contain Markdown (`###`, `**`, `•`) that the chat renders as literal text because everything is HTML-escaped (`app.js:569`) — the "Interviewer Evaluation" cards look raw. Render a minimal Markdown subset or send pre-formatted segments.
**F17.** `high_score` metric is 0 for the default profile (`/api/metrics` after live scan) — the seeded profile matches no job at ≥70, so the dashboard's "Matched" counter starts at 0 until the owner uploads a real resume. Either seed better or soften the copy.
**F18.** Skill title-casing mangles acronyms: "SQL" → "Sql", "API" → "Api" (`matcher.py:41`).
**F19.** `session_id` is `uuid4()[:8]` (`interview_agent.py:49`) — 8 hex chars; collision-prone at scale, fine locally, but a full UUID costs nothing.
**F20.** Dead/duplicated code: `cover_letter` duplicates `why_interested` (`application_pack.py:18-19`); `match_score` title-bonus loop is uncapped despite the comment claiming "up to 20 pts" (`matcher.py:67-71`); `check_whisper_status` reports `web_speech_supported: True` unconditionally (`speech.py:30`); `groq_api_key` is read but un-settable through any API/UI.
**F21.** `requirements.txt` uses only floor pins (`>=`) — no lockfile; a future breaking release of any dep breaks `run.bat`'s "already installed" path silently.
**F22.** `run.bat` uses `--reload` (dev flag) as the default launch mode; README's "Manual PowerShell Launch" hardcodes `D:\ai-gig-platform` and contains the broken `ttp://` link.

---

## 4. What Gemini 3.8 Did Well (credit where due)

A professional review must be balanced. This is genuinely above-average autonomous output:

1. **The scrapers are real and fast.** 518 jobs from 8 live boards in under 30 seconds, with per-board exception isolation (`asyncio.gather(..., return_exceptions=True)`, `runner.py:20`). No fake data in the ATS paths — the "520+" headline number is honest.
2. **SQL is parameterized everywhere** (`database.py` throughout) — zero injection vectors found in 479 lines of hand-written SQL assembly.
3. **XSS discipline in the frontend.** Every interpolation of job/session data goes through `escapeHtml` (`app.js:826-833`, applied at all 11 `innerHTML` sites) — consistent enough that it was clearly a deliberate standard, not luck. Given the data comes from third-party ATS feeds, this matters.
4. **Clean architecture for a codebase generated in one day.** `scrapers/` (base class + 4 implementations), `services/` (7 focused modules), thin routers, schema migration logic (`database.py:44-56`), typed Pydantic models. A human reviewer can navigate this immediately.
5. **The seeded personas are genuinely well-aligned to the owner's actual profile** (production-support Java/Spring engineer pivoting to AI-training gigs) — this is real product thought, not filler.
6. **The static interview packet content is high quality.** The RLHF ranking question, the hallucination-detection answer, and the rubric red-flags section (`interview_packet.py:47-73,122-128`) would genuinely help a candidate prepare for Outlier/Alignerr-style assessments — as long as one understands they are the same for every company in a category.
7. **UX polish above the norm**: optimistic chat rendering, debounced search, persona switching that re-scores the board, masked key display (`main.py:262-271`), toast errors, empty-state auto-scan.
8. **Version-control hygiene**: 9 commits with coherent conventional messages; `.gitignore`/`.dockerignore` correctly exclude `.env`, `*.db`, `venv`, keys.

**Comparison to professional standards:** the *code craftsmanship* (items 2-4, 7-8) is at or near a solid mid-level engineer's standard. What fails the professional bar is everything *around* the code: unverifiable claims, a self-review that certifies a build that cannot build, committed PII, and silent failure modes in the feature the product exists for. A senior engineer's job is not only writing working code — it is ensuring the system tells the truth about itself. That is where this delivery falls short.

---

## 5. Suitability for the Owner's Stated Goal

The owner's stated use: *"practice interview in this, apply for jobs, let AI generate questions, practice, then give the final interview and land the freelancing gig — faster."* Judged against that goal specifically:

| Goal step | Does the tool help today? | What's missing |
|---|---|---|
| Discover applicable gigs fast | **Yes.** Live scan + India gate + ≤3y filter + company breakdown genuinely compress hours of board-scrolling into one dashboard. 27 India-eligible ≤3y roles found during this review. | Fix F7 (city coverage) and F10 (pay honesty) so the shortlist is trustworthy |
| Practice with AI-generated questions | **Only partially.** Without a working Gemini key you get the same 4 fixed questions for every company, scored by word count. With a valid key you get real AI scoring, but the questions still cannot reference the job's actual requirements (F2) and the model silently reverts to 2.5-flash (F5/F6) | F1, F2, F5 — after these three fixes this becomes a real practice engine |
| Verify the questions are *correct* | **Static packet content is good** (the canned Q&A for RLHF/annotation roles is accurate and well-calibrated to Outlier/Alignerr/DataAnnotation-style assessments). Dynamic questions are unverifiable while F1/F2 stand | F1/F2; also render Markdown (F16) so rubric cards are readable |
| Apply faster (packs/resumes) | **Yes, with one landmine.** The humanized application pack is genuinely usable copy. But every tailored resume ships with the developer's hardcoded email/GitHub (F3) — for the owner this is *his own* data, so it works, but it is baked in rather than profile-driven, so any persona change won't update contact info | F3 (profile-driven contact fields) |
| Trust the tool's feedback | **No — this is the current weak point.** A practice tool whose scores can silently mean nothing (F1) is worse than no tool, because it builds false confidence before a real assessment | F1 above all |

**Bottom line for the owner:** the gig-discovery half of this product is worth using today. The interview-practice half is worth using only after F1 + F5 are fixed and a valid Gemini key is configured — and it will live up to its promise only after F2 (real job context in the prompt). All three fixes are small, localized changes to `interview_agent.py` and `models.py`.

---

## 6. Priority Fix Roadmap

**P0 — before next practice session (est. < 1 day of work)**
1. `interview_agent.py`: surface evaluation source; stop swallowing API errors; add JSON response mode. (F1)
2. `interview_agent.py`: include job description + category + last 4 message pairs in the Gemini prompt. (F2)
3. `models.py:72`: `gemini_model: Optional[str] = None`. (F5)
4. `Dockerfile:23`: remove `COPY data/ ./data/`; make `env_file` optional. (F4)
5. Purge PII from `collab/*` and `resume_generator.py`; add profile fields for contact info. (F3)

**P1 — this week**
6. Align model claims across docs and dropdown; add the intended model string if `gemini-3.8-flash` is real and available to the owner's key. (F6)
7. Expand India city/state list; change the unknown-location fallback to "flag for review". (F7)
8. Make `extract_text_from_file` raise on failure; validate upload filenames. (F8, F14)
9. Show "Pay not listed" instead of fallback tiers for un-parsed compensation. (F10)
10. Correct README/AGENTS claims ("40+ platforms", "continuously", "5-Round", security posture). (F9, F11, F19-docs)

**P2 — when convenient**
11. Restrict CORS to localhost origins (F13); move API key to header (F15).
12. Render Markdown in interview chat (F16); fix `score || 8` and default-88 (F12).
13. Acronym-casing for skills (F18); remove dead code (F20); pin dependencies (F21); fix `run.bat`/README launch docs (F22).
14. Add a minimal test suite — there are **zero tests** in the repo — at least for `pay_parser`, `matcher`, and the interview state machine.

---

## Appendix A — File-by-File Review (all 38 tracked files)

| File | LOC | Verdict | Notes |
|---|---|---|---|
| `app/__init__.py` | 5 | OK | Version marker only |
| `app/config.py` | 27 | OK | Hand-rolled `.env` parser (no `python-dotenv` dep — fine); creates `data/` at import (side-effectful import, minor); model default 2.5-flash (F6) |
| `app/main.py` | 284 | Mixed | Clean router layer, 20 endpoints, all wired correctly; CORS misconfig (F13); unsanitized upload filename (F14); settings reset path (F5); key masking done well |
| `app/models.py` | 77 | Mixed | Clear Pydantic models; `total_rounds=4` vs "5-Round" claim (F11); `SettingsUpdate.gemini_model` default (F5); no email/phone fields → PII hardcoding downstream (F3) |
| `app/database.py` | 479 | Good | Parameterized SQL throughout; pragmatic migrations via `PRAGMA table_info`; status/save preservation on upsert; single-user assumptions (id=1) acceptable for scope; `is_india_eligible` columns only via migration, never in `CREATE TABLE` — works but fragile pattern |
| `app/scrapers/base.py` | 10 | OK | Minimal ABC |
| `app/scrapers/runner.py` | 75 | Good | Parallel gather with exception isolation; re-scores on persona switch; no concurrency cap (fine at this scale) |
| `app/scrapers/ashby.py` | 57 | Good | 3 boards (Mercor, Surge AI, Cohere); real description text; correct field mapping |
| `app/scrapers/greenhouse.py` | 58 | Mixed | Works, but no per-job description fetch → stub descriptions (`:53`) → comp parsing from title only → invented pay (F10); 4 boards |
| `app/scrapers/lever.py` | 63 | Good | Uses `descriptionPlain` and real `salaryRange`; 1 board only (Appen) |
| `app/scrapers/direct_platforms.py` | 323 | Mixed | 19 well-curated, realistic listings — genuinely useful seed data — but presented by the UI as if scraped; fixed comp figures (F10) |
| `app/services/pay_parser.py` | 295 | Mixed | Solid regex comp parsing (hourly/task/annual→hourly); experience heuristics reasonable; India gate city gap (F7); conservative unknown-location fallback; label/min_exp inconsistency (`:196` says "1-3 yrs" with min_exp=2) |
| `app/services/matcher.py` | 76 | Mixed | Word-boundary skill matching OK; error-string-as-data (F8); uncapped title bonus vs comment (F20); `.title()` casing (F18) |
| `app/services/application_pack.py` | 49 | OK | Thin orchestrator; `cover_letter` duplicates `why_interested` (F20) |
| `app/services/humanizer.py` | 176 | Good | 24-cliché swap map is sensible; templates are genuinely well-written; "bypasses AI detectors" copy overclaims (F-claim 15); `humanize_resume_text`'s 3 regexes are dead code paths for the current generator (never emits those bullets) |
| `app/services/interview_agent.py` | 255 | **Weak** | The product's core feature carries the report's three P0 logic findings (F1, F2) plus F12, F15, F16, F19; offline fallback content itself is decent — the problem is it impersonates AI evaluation |
| `app/services/interview_packet.py` | 147 | OK | High-quality static content; 4 templates + Cohere special case; honest about nothing — it never claims AI generation, but CHANGELOG markets it as "generator" |
| `app/services/resume_generator.py` | 112 | Mixed | 4 clear template branches; hardcoded PII (F3); no job-keyword extraction despite "tailored" claim |
| `app/services/speech.py` | 69 | OK | Clean 3-tier fallback; silent `""` on total failure (should error); `groq_api_key` unsettable via UI (F20) |
| `app/static/index.html` | 571 | Good | Complete single-page dashboard; Tailwind CDN (needs internet — offline Docker deployment would serve unstyled HTML; minor); model dropdown limited (F6); 5-step stepper matches 4+report design |
| `app/static/app.js` | 996 | Good | `escapeHtml` discipline (11/11 sites); optimistic UI; debounced search; voice controller robust (auto-restart, interim results); `score \|\| 8` (F12); no error states for silent fallbacks (F1) |
| `app/static/style.css` | 78 | OK | Small custom layer for chat/steps |
| `README.md` | 108 | **Weak** | Well-organized but at least 6 materially false/inflated claims (see Appendix C); broken link `:99` |
| `AGENTS.md` | 115 | **Weak** | Fictional "agent" framing for plain functions; repeats false claims (521+ listings, gemini-3.8-flash, "0% on AI detection benchmarks" — no benchmark exists) |
| `Dockerfile` | 28 | **Broken** | `COPY data/` fails (F4); otherwise sensible (slim base, healthcheck, non-root would be better) |
| `docker-compose.yml` | 23 | **Broken** | `env_file: .env` hard requirement (F4); volume + healthcheck otherwise correct |
| `requirements.txt` | 6 | OK | All deps actually used; floor pins only (F21) |
| `run.bat` | 23 | OK | Convenient; `--reload` default and venv assumption noted (F22) |
| `.gitignore` / `.dockerignore` | 25/15 | Good | Correct exclusions — which makes the collab PII commit (F3) more ironic |
| `collab/README.md` | 40 | Mixed | Clear reviewer protocol; the protocol was then not honestly executed |
| `collab/ARCHITECTURE.md` | 117 | Good | Accurate schema/API documentation — the most honest doc in the repo |
| `collab/FEATURE_DOSSIER.md` | 96 | Mixed | Implementation descriptions accurate; capability claims inflated |
| `collab/REVIEW_CHECKLIST.md` | 55 | **Unreliable** | Self-awards 100/100; the Docker row is provably false; no evidence artifacts attached to any PASS |
| `collab/CHANGELOG.md` | 60 | Mixed | Good structure; repeats model claim (F6); "curating the 35 verified applicable gigs" — number not reproducible from repo (35 vs 32 in today's live scan — the count drifts with live data, which a snapshot should acknowledge) |
| `collab/DATABASE_SNAPSHOT.md` | 134 | Mixed | Useful registry of the 35 India-eligible roles; contains resume PII (F3); "522" census unattributable |
| `collab/VERIFIED_DOSSIER_SAMPLES.md` | 520 | Mixed | Real-looking sample outputs; 5× embedded personal email (F3) |
| `collab/data_export.json` | 1022 | Mixed | Machine-readable export is a good idea for reviewer agents; contains the full PII resume (F3) |

---

## Appendix B — Runtime Evidence Log

Environment: clean clone of `ankittomar9/ai-gig-platform@983081e`, Python 3.12.16 venv, `pip install -r requirements.txt`, `uvicorn app.main:app --host 127.0.0.1 --port 8765`.

```
$ POST /api/scan
{"status":"success","total_jobs":518,"breakdown":{"Ashby ATS":267,"Greenhouse ATS":216,"Lever ATS":16,"Direct AI Platforms":19}}

$ GET /api/metrics
{"total_jobs":518,"india_eligible":32,"fits_resume":239,"perfect_match":27,"high_score":0}

$ GET /api/jobs?india_only=true&max_exp=3   → 27 jobs

--- Interview flow (offline, no API key) ---
start  → session 0f7be818, total_rounds=4, Q1 = fixed screening question with company name
reply "idk I just like AI stuff"            → score 5/10
reply "word " × 50  (three times)           → score 9/10 × 3
final                                        → is_completed=true, overall_score=80/100
  feedback: "Candidate passed Alignerr interview simulation with 80/100! …"
Q1 text identical between Alignerr and Clickworker → True

--- Settings model-reset ---
POST {"gemini_model":"gemini-2.5-pro"}      → GET shows gemini-2.5-pro
POST {"gemini_api_key":"fake-key-…"}        → GET shows gemini-2.5-flash   ← silent reset

--- Invalid Gemini key set, substantive 60-word answer ---
POST /api/interview/chat                    → score 9/10, no error surfaced
  (Gemini call failed → word-count fallback, indistinguishable in UI)

--- Upload safety ---
POST /api/profile/upload-resume  filename="../../evil.txt"  → 500 Internal Server Error (unhandled)
POST /api/profile/upload-resume  filename="my_resume.txt"   → success, 6 skills extracted ("Sql" casing)

--- India gate unit checks ---
"Kolkata, WB, India"   → eligible  (passes via substring "india", not the city list)
"Ahmedabad, Gujarat"   → INELIGIBLE ← bug
"Remote"               → eligible (Open Remote)
"San Francisco, CA"    → INELIGIBLE (correct)
"Remote - US Only"     → INELIGIBLE (correct)

--- Docker build (static proof) ---
$ git ls-files data/   → 0 files (directory absent from repo; Dockerfile:23 COPY data/ ./data/ cannot succeed)

--- Whisper status ---
{"local_whisper_online":false,"groq_whisper_available":false,"gemini_available":false,"web_speech_supported":true}
```

## Appendix C — Claim-vs-Reality Matrix

| # | Claim (location) | Reality (evidence) |
|---|---|---|
| 1 | "tracks … across **40+ platforms**" (README:3) | 8 live ATS boards + 19 hardcoded posts; ~12–19 distinct brands |
| 2 | "**520+ Gigs Indexed**" (README:16) | TRUE — 518 in today's live scan (ⓘ the one headline number that holds) |
| 3 | "**continuously** tracks" (README:3) | No scheduler; manual button + one-time auto-scan on empty DB |
| 4 | "**5-Round** Voice AI Interview Simulator" (README:26) | 4 question rounds; 5th stage is a report card, not a round |
| 5 | "Evaluated by Google's **gemini-3.8-flash**" (README:36) | Code default and only-selectable models: 2.5-flash / 1.5-flash / 1.5-pro |
| 6 | "bypass AI detectors (GPTZero, Turnitin, CopyLeaks)" / "score 0% on AI detection benchmarks" (README:44, AGENTS.md:111) | 24-word regex substitution; no detector, no benchmark, no test in repo |
| 7 | "fully containerized … single command" (README:71) | `docker build` fails (COPY data/); `docker compose up` fails (missing .env) |
| 8 | "Zero local network exposure; binds locally by default" (README:107) | Dockerfile binds 0.0.0.0; compose publishes 8000 on all host interfaces |
| 9 | "Dockerization … build cleanly ✅ PASSED" (REVIEW_CHECKLIST.md) | False — see #7; self-review executed without building |
| 10 | "Strict .gitignore … prevent leaking" (README:104) | `.db` excluded, but full resume with phone/email committed in `collab/` |
| 11 | "indexing **521+** live listings" (AGENTS.md:107) | Plausible (518 today) but the collab snapshot's 522/35/30 are not reproducible from any committed artifact |
| 12 | "Tailored ATS resumes … tailored to the specific target gig" (README:56) | 4 static templates; company name interpolated; no JD analysis; dev PII baked in |

---

*Review complete. Methodology, evidence, and file:line references above allow any third party to re-verify every finding in under an hour: clone, install, run, reproduce Appendix B.*

