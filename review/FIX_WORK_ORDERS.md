# Fix Work Orders — Execution Brief for the Agent (Gemini / Antigravity)

- **Task ID:** SPEC01 (execution tasks)
- **Author:** Z.ai (Independent Reviewer)
- **Date:** 2026-11-20
- **Base Commit:** `afa012a8`
- **Status:** DISPATCHED — binding per [SPEC01-REMEDIATION-SPEC.md](SPEC01-REMEDIATION-SPEC.md)

Companion to [REVIEWER_REPORT.md](REVIEWER_REPORT.md) (same folder). The SPEC is the *contract*; that report is the *evidence*; this one is the *task list*. Execute top to bottom, P0 → P1 → P2.

## Ground rules (read first — governance adopted from the GateLMS protocol)

1. **Zero code changes on `main`.** Every work order runs on its own pre-assigned branch (table below), per `.agents/rules/branch-hygiene.md`: cut from latest `main`, commit atomically (`fix(wo-<n>): <summary>`), push the branch, then merge with `--no-ff` (`merge(wo-<n>): <summary>`). One work order per branch — never mix tasks.
2. **Never force-push or rewrite history.** Two agents share this repo; a rewrite silently destroys the other's commits. (The history was already rewritten once — it cost nothing only by luck.)
3. **Do not modify anything under `review/`** — that is the reviewer's evidence base.
4. **Do not self-grade.** Every WO below has an *acceptance test*. Run it and paste the raw output as evidence. A WO without pasted evidence is NOT done — this repo's previous self-review marked a broken Docker build as "✅ PASSED", which is exactly the failure mode to avoid.
5. Report per work order in `collab/gemini/SPEC01-WO-<n>-REPORT.md` and keep the ledger `collab/gemini/SPEC01-PROGRESS.md` updated: `WO | status | branch | commit sha | evidence pointer`.
6. If a WO cannot be completed as written, record why in your report (`DEVIATION` section) and freeze that branch. Do not improvise silently.

### Pre-assigned branch names

| WO | Branch | WO | Branch |
|---|---|---|---|
| 1 | `interview/scoring-honesty-fix` | 9 | `scraper/compensation-honesty-fix` |
| 2 | `interview/job-aware-prompts-fix` | 10 | `docs/claims-truth-fix` |
| 3 | `settings/model-reset-fix` | 11 | `security/cors-and-key-header-fix` |
| 4 | `docker/fresh-clone-build-fix` | 12 | `interview/score-integrity-fix` |
| 5 | `privacy/pii-purge-fix` | 13 | `cleanup/dead-code-and-pins-fix` |
| 6 | `docs/model-story-alignment-fix` | 14 | `tests/minimal-suite-1` |
| 7 | `scraper/india-gate-coverage-fix` | 15 | `privacy/history-purge-1` *(Operator-gated)* |
| 8 | `matcher/upload-hardening-fix` | | |

Fixups to a WO already merged: same domain, `<slug>-fixup-<N>` with the next sequential integer.

---

## P0 — blocking real use (do all five first)

### WO-1 · Make scoring honest (Report F1)
**Files:** `app/services/interview_agent.py:228-254`, `:140-151`, `:130`; frontend `app.js`
**Problem:** every Gemini failure is swallowed by `except Exception: pass` and silently falls back to a 3-band word-count heuristic. Verified: invalid key + answer `"word"×50` → "9/10 Excellent", overall 80/100 pass. The user cannot tell AI scoring from `len(answer.split())`.
**Changes:**
- Add `evaluation_source: "gemini" | "heuristic"` to every evaluated message (persisted, returned by the API).
- Replace the bare `except: pass` with logging + an explicit offline-mode flag on the session.
- Show a persistent, unmissable banner in the interview UI while a session is heuristic-scored ("Offline mode — answers are NOT AI-scored. Check your Gemini key."), and label the final report card accordingly.
- Add `response_mime_type: "application/json"` to `generationConfig` so prose responses don't fail parsing and trigger the fallback.
**Acceptance test:** with `GEMINI_API_KEY=invalid-key`, run a full 4-round session: every evaluation message in the API response carries `evaluation_source: "heuristic"`, the UI shows the offline banner, and the report card says offline. Paste the JSON of one evaluated message + a screenshot. Repeat one round with a valid key: `evaluation_source: "gemini"`, no banner.

### WO-2 · Make interviews actually job-aware (Report F2)
**Files:** `app/services/interview_agent.py:179-221`
**Problem:** `_call_gemini_interview(job, ...)` accepts `job` and never uses it. The prompt contains only company name, role title, round number, latest reply — no JD, no tech stack, no conversation history. "Tailored to the company" is impossible; follow-ups can't build on earlier answers.
**Changes:**
- Include in the prompt: `job["description"][:2000]`, `job["category"]`, `job["tier"]`, and the last 4 message pairs of the session.
- Remove the literal source-code text leaked into the prompt at `:200-204` (`"If curr_round < 4:"` / `"If curr_round == 4:"` are currently sent to the model as raw text).
**Acceptance test:** start two sessions for two jobs with clearly different tech stacks (e.g. a React/TS role vs a Python/RLHF role). Paste one generated question from each — each question must reference technology actually present in that job's description. A question that could apply to any company = fail.

### WO-3 · Stop settings save from resetting the model (Report F5)
**Files:** `app/models.py:72`; check handler at `app/main.py:277-278`
**Problem:** `SettingsUpdate.gemini_model` defaults to `"gemini-2.5-flash"` instead of `None`, so saving *only* the API key silently reverts the chosen model. Verified live.
**Changes:** `gemini_model: Optional[str] = None`; ensure the update handler treats `None` as "no change" (verify the `exclude_unset`/None-check path end-to-end).
**Acceptance test:** `PUT /api/settings` with model `gemini-2.5-pro` → then `PUT /api/settings` with only `api_key` → `GET /api/settings` still returns `gemini-2.5-pro`. Paste all three curl inputs/outputs.

### WO-4 · Fix the Docker build (Report F4)
**Files:** `Dockerfile:23`; `docker-compose.yml:15-16`
**Problem:** `COPY data/ ./data/` fails on any fresh clone (`data/` is gitignored, created at runtime by `config.py:6`); `env_file: .env` fails when `.env` is absent. The collab checklist graded this "build cleanly ✅" without attempting it.
**Changes:** delete the `COPY data/` line (the compose volume provides persistence); make `env_file` optional (or document `touch .env` as a required first step in README §Docker); optionally add a CI workflow that runs `docker build` on push.
**Acceptance test:** in a **fresh clone** (no `data/`, no `.env`): `docker build -t aigig .` succeeds, then `docker compose up` (with `.env` containing only `GEMINI_API_KEY=` if required) → `GET /health` returns 200. Paste the last 10 lines of the build log and the health check.

### WO-5 · Purge personal data from the working tree (Report F3)
**Files:** `collab/data_export.json:945`, `collab/DATABASE_SNAPSHOT.md:108`, `collab/VERIFIED_DOSSIER_SAMPLES.md:79,181,283,385,487`, `resume_generator.py:16,70-71`, `.gitignore`, `app/models.py`
**Problem:** a real phone number, email, LinkedIn, employers, and full career history are committed to this public repo, and `resume_generator.py` hardcodes the developer's contact info into every generated resume.
**Changes:**
- Remove/replace all real PII in the files above with obvious placeholders (`+91 XXXXX XXXXX`, `you@example.com`, `linkedin.com/in/your-handle`).
- Add `collab/data_export.json` to `.gitignore`.
- Add `email`, `phone`, `linkedin` to `UserProfile` (models + DB migration + settings UI); `resume_generator` must read contact info from the profile, never hardcode.
**Acceptance test:** `grep -rniE "7999905480|cognizant|macy'?s" --exclude-dir=review --exclude-dir=.git .` returns zero hits, and a grep for the old email/linkedin returns zero hits; generate a resume and paste the contact block showing profile-driven values. (History purge is WO-15 — do NOT rewrite history yourself.)

---

## P1 — materially wrong behavior

### WO-6 · Align the model story (Report F6)
**Files:** `README.md:36`, `AGENTS.md:81`, `collab/CHANGELOG.md:52` (or wherever CHANGELOG lives), `collab/FEATURE_DOSSIER*`:56, `app/static/index.html:536-539`, `app/config.py`
**Problem:** four docs claim `gemini-3.8-flash`; no code path or dropdown can use it; every default is `gemini-2.5-flash`.
**Changes:** pick one truth — either add `gemini-3.8-flash` to the dropdown and defaults (only if that model ID actually works with the owner's API key), or correct all four docs to what the code really uses.
**Acceptance test:** `grep -rn "3.8" --exclude-dir=review .` returns either nothing or only consistent, real usage; every dropdown option is a valid, callable model ID; `GET /api/settings` default matches the docs.

### WO-7 · Fix the India gate (Report F7)
**Files:** `app/services/pay_parser.py:251`, `:289-293`
**Problem:** the keyword list has 12 strings; `Ahmedabad, Gujarat` → ineligible (verified). `Kolkata` passes only via the `india` substring. Unmatched locations are silently dropped.
**Changes:** add the major cities/states (Kolkata, Ahmedabad, Jaipur, Indore, Chandigarh, Kochi, Coimbatore, Lucknow, Bhubaneswar, Nagpur, …); change the final fallback from "ineligible" to *eligible but flagged for manual review*.
**Acceptance test:** run a small script over: `"Ahmedabad, Gujarat"`, `"Kolkata, WB, India"`, `"Remote — India (West)"`, `"Jaipur, Rajasthan"` → all eligible; `"New York, NY"` → ineligible. Paste the output.

### WO-8 · Harden resume upload (Report F8 + F14)
**Files:** `app/services/matcher.py:24-30`; `app/main.py:232`, `:238-247`
**Problem:** `extract_text_from_file` returns error strings like `"Error reading docx: …"` as data, which get saved as the user's resume text; the upload path builds a filename from raw client input and 500s on traversal attempts.
**Changes:** make extraction failures raise (or return `None`) and the endpoint return a 4xx with a clear message; sanitize with `Path(file.filename).name` before any path construction.
**Acceptance test:** upload a corrupted `.docx` → HTTP 400 JSON error, `profile.resume_text` unchanged; upload with filename `"../../etc/passwd"` → 400, not 500. Paste both responses.

### WO-9 · Stop inventing compensation (Report F10)
**Files:** `app/scrapers/greenhouse.py:35`, `app/scrapers/direct_platforms.py`, tier display in `app.js`/`index.html`
**Problem:** Greenhouse pay is parsed from the *title only*; nearly all rows get invented fallback ranges ("$35 - $75+/hr"); the 19 curated posts look like scraped data in the UI.
**Changes:** when no real figure was parsed, keep `comp_min/max` as `None`/0 and display "Not listed"; label curated direct-post ranges as "estimate".
**Acceptance test:** after a live scan, every Greenhouse row without parsed compensation renders "Not listed"; a grep of the API response shows no invented ranges for those rows. Paste one JSON row.

### WO-10 · Make the docs tell the truth (Report F9 + F11 + F22)
**Files:** `README.md` (opening paragraph, §Architecture/"5-Round", §Manual PowerShell Launch), `collab/CHANGELOG.md`, `run.bat`
**Problem:** "40+ platforms" and "continuously tracks" are false (8 live boards + 19 curated posts; scan is manual); "5-Round" vs 4 question rounds + report card; README hardcodes `D:\ai-gig-platform` and contains a broken `ttp://` link; `run.bat` ships `--reload` as default.
**Changes:** correct the counts and claims to match reality; fix the link and the hardcoded path; drop `--reload` from the default launch (or offer a dev script separately).
**Acceptance test:** `grep -rn "40+\|5-Round\|ttp://" --exclude-dir=review .` returns nothing (or only corrected forms); README numbers match: 8 boards, 19 curated posts.

---

## P2 — quality batch (do after P0/P1)

### WO-11 · Security polish (Report F13 + F15)
CORS: replace `allow_origins=["*"]` + `allow_credentials=True` (`main.py:40-46`) with explicit `["http://localhost:8000", "http://127.0.0.1:8000"]`. API key: send via `x-goog-api-key` header instead of URL query (`interview_agent.py:180`).
**Acceptance:** grep shows no `key=` in any request URL string; OPTIONS preflight from a foreign origin is rejected.

### WO-12 · Score/UI integrity (Report F12 + F16)
`overall_score` defaults to 88 with no round scores (`interview_agent.py:130`) — remove the fabricated default. UI renders missing scores as `8/10` (`app.js:575`) — show "—". Render a minimal Markdown subset (bold, bullets, headings) in interview messages so rubric cards aren't raw `**`/`###` text (keep the existing HTML-escaping discipline — escape first, then format).

### WO-13 · Code cleanup (Report F18 + F20 + F21 + F22)
Acronym-safe casing ("SQL", "API" — `matcher.py:41`); remove dead code (`cover_letter` duplicating `why_interested`, unconditional `web_speech_supported: True`, unsettable `groq_api_key`); cap the title bonus loop as its comment claims (`matcher.py:67-71`); pin dependencies (or add a lockfile); fix `run.bat` default mode.

### WO-14 · Minimal test suite (zero tests exist today)
Add `tests/` covering at minimum: `pay_parser` India gate (WO-7 cases), `matcher` scoring + extraction failure paths, interview state machine (round advance, offline fallback marking from WO-1). Wire into the CI workflow from WO-4 if added.
**Acceptance:** `pytest` passes locally; paste the summary line.

---

## WO-15 · SPECIAL — requires the owner's explicit decision (do NOT do unilaterally)

Git **history rewrite** to purge the PII from all historical commits (the data exists in current history at `ae7d2b51` and earlier even after WO-5 cleans the working tree), optionally making the repo private during the cleanup. This is the only justified history rewrite — and per ground rule 2 it must be owner-approved, coordinated, and done once, after WO-5 lands. Recommend: `git filter-repo` + force-push + all clones re-fetched.

---

## Definition of done for this pass

All P0 (WO-1…5) and P1 (WO-6…10) gates verified green **by Z.ai re-audit with reproduced receipts** (not executor self-report), per SPEC01 §3 and §6. Then the reviewer re-runs the acceptance tests independently and updates `REVIEWER_REPORT.md` with a verdict delta.
