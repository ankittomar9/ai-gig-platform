# [SPEC01-AUDIT] Independent Re-Audit of the Remediation Pass

- **Task ID:** SPEC01-AUDIT
- **Author:** Z.ai (Independent Reviewer / Architect)
- **Date:** 2026-11-20
- **Base Commit:** `1695824` (`main`, executor merge head)
- **Audited execution:** `collab/gemini/SPEC01-PROGRESS.md` (WO-1…WO-14, WO-15 gated)
- **Verdict:** **CONDITIONAL PASS — 11 gates PASS / 3 CONDITIONAL / 0 FAIL. DoD not yet met: conditions C-1, C-2 open; G-4 receipt deferred to a Docker-enabled run.**

---

## 1. Method

Every gate was re-verified independently of the executor's reports: full static diff review of all 14 branches (`1734010f` → `1695824`, 49 files, +1911/−1193), plus a fresh-clone dynamic run (clean venv, pinned requirements, `uvicorn` boot, live network scan of 8 boards, full 4-round interview session, mocked-transport prompt capture, unit-level gate tests, pytest on fresh and warm DBs). Receipts below are verbatim from the audit run, not copied from executor reports.

## 2. Governance compliance (branch protocol)

| Rule | Result |
|---|---|
| Pre-assigned branch names (14/14) | ✅ all match `review/FIX_WORK_ORDERS.md` |
| `--no-ff` merges | ✅ `merge(wo-N)` commits present on `main` |
| Branches pushed & retained | ✅ all 14 on remote |
| No force-push / history rewrite | ✅ reviewer's 6 governance commits (`fa1f34bf`…`1734010f`) all still ancestors of `main` |
| `review/` untouched by executor | ✅ only reviewer commits touch `review/` |
| Reports in `collab/gemini/` with headers + pasted receipts | ✅ 14 reports + ledger, zero DEVIATION/BLOCKED |
| WO-15 (history purge) correctly gated | ✅ not executed |

Ledger sha note: WO-4 ledger cites fix commit `fcb11d8`; branch tip `5a3ecaf` is the report-doc commit on the same branch. Accurate, no discrepancy.

## 3. Gate verdicts

| Gate | WO / Finding | Verdict | Evidence (independently reproduced unless noted) |
|---|---|---|---|
| G-1 | WO-1 / F1 scoring honesty | ✅ **PASS** | Invalid key + `offline_mode=false`: Google HTTP 400 surfaced verbatim in `fallback_reason`; every round `evaluation_source: "heuristic"`; `is_offline_fallback: true`; report card `[OFFLINE HEURISTIC EVALUATION]`; message text `(Offline Heuristic)`; `response_mime_type: application/json` in payload; no silent `except: pass` remains |
| G-2 | WO-2 / F2 job-aware prompts | ✅ **PASS** | Mocked-transport capture: JD excerpt + skills + category + last-4-pairs history in prompt; prompts differ by job (Java/Spring vs Python/RLHF); zero `If curr_round` source-code literals |
| G-3 | WO-3 / F5 model reset | ✅ **PASS** | 3-step reproduced: set `gemini-2.5-pro` → save only key → GET returns `gemini-2.5-pro`; `offline_mode`/`minimum_rate` same-class defaults also fixed (beyond spec, correct) |
| G-4 | WO-4 / F4 Docker | ⚠️ **CONDITIONAL PASS** (receipt-verified, not independently reproduced — no Docker in audit sandbox) | Static: `COPY data/` removed, `env_file: required: false`, `/health` added (live-verified locally: `{"status":"ok","app":"ai-gig-platform"}`), healthchecks aligned. Executor receipt: fresh-clone `docker build` DONE + container health 200. **Deferred to first Docker-enabled independent run** (same pattern as GateLMS ForceAuthzIT deferral) |
| G-5 | WO-5 / F3 PII purge | ⚠️ **CONDITIONAL PASS** | Enumerated acceptance greps pass: phone/email/LinkedIn/employers zero hits; `resume_generator` now profile-driven; `collab/data_export.json` deleted + gitignored. **Condition C-1:** full real name "Ankit Singh Tomar" remains in 4 places (§5) — same defect class as the fixed `resume_generator.py:16`. Note: the name pattern was not in the WO-5 acceptance grep; the executor did not fail their stated test — this is a net-new catch by this audit |
| G-6 | WO-6 / F6 model story | ✅ **PASS** | One story everywhere: `config.py`, `main.py`, `interview_agent.py`, dropdown, README, AGENTS, CHANGELOG, FEATURE_DOSSIER all `gemini-3.8-flash`; GET /api/settings default matches. Corroborating runtime evidence: executor WO-1 receipt shows Google 404 "models/gemini-2.5-flash is no longer available to new users" — the retirement of 2.5-flash is what the 3.8 default responds to. Advisory A-1: dropdown still offers `gemini-1.5-flash`/`gemini-1.5-pro` — almost certainly retired; prune or verify with a live key |
| G-7 | WO-7 / F7 India gate | ✅ **PASS** | `Ahmedabad, Gujarat` / `Kolkata, WB, India` / `Jaipur, Rajasthan` / `Kochi, Kerala` / `Remote — India (West)` → all eligible; `New York, NY` → ineligible; unknown (`Zug, Switzerland`) → eligible + `Flagged for Review` (no silent drop) |
| G-8 | WO-8 / F8+F14 upload | ✅ **PASS** | Corrupted `.docx` → 400; `../../etc/passwd` → 400 (not 500); valid `.txt` → 200 with real resume text, no error-string-as-data |
| G-9 | WO-9 / F10 compensation | ✅ **PASS** | Live scan: Greenhouse 211/211 rows `Not listed` (0 invented ranges, `comp_min/max = 0`); direct posts labeled `(estimate)` (12/12 matched; 19 curated posts exist in code) |
| G-10 | WO-10 / F9+F11+F22 docs | ✅ **PASS** | No `40+`, no `5-Round`, no broken `ttp://` link (precise grep); header badge and spinner corrected; `run.bat` no `--reload`; `run_dev.bat` split out; PowerShell path relativized |
| G-11 | WO-11 / F13+F15 CORS+key | ✅ **PASS** | Preflight: foreign origin rejected (400, no ACAO header), `http://localhost:8000` allowed; API key in `x-goog-api-key` header, `key=` absent from URL (transport capture) |
| G-12 | WO-12 / F12+F16 scores | ✅ **PASS** | Default-88 removed (`overall_score: None`); `score \|\| 8` replaced with null-check (`—`); `renderSafeMarkdown` escapes HTML **first**, then formats a minimal subset — XSS discipline preserved |
| G-13 | WO-13 / F18+F20+F21 | ✅ **PASS** | `extract_skills_from_text("...sql and rest api... aws gcp spring boot python")` → `['API','AWS','GCP','Python','SQL','Spring Boot']`; `cover_letter` duplication, `web_speech_supported: True` lie removed; `groq_api_key` now settable (bonus); requirements pinned `==`; pytest added |
| G-14 | WO-14 / tests | ⚠️ **CONDITIONAL PASS** | **Condition C-2:** on a fresh clone (the acceptance scenario), 3/17 tests fail — `test_interview_state_machine.py` requires job `direct_turing_java_engineer` which only exists after a live scan. 14/17 green and meaningful. Additionally the tests **pollute the real user DB**: they leave `gemini_api_key='test-key-999'` and `offline_mode='true'` in `data/gighunter.db` (`tests/test_interview_state_machine.py:18,35`) — running pytest on a dev machine silently switches the owner's next practice session into offline mode (loudly banner-flagged thanks to WO-1, but still wrong) |
| G-15 | WO-15 / history purge | ✅ correctly GATED | Not executed; awaits Operator decision |

## 4. Key receipts (verbatim, audit run 2026-11-20)

```
WO-1 (invalid key, offline_mode=false):
  evaluation_source: heuristic
  is_offline_fallback: True
  fallback_reason: Gemini API HTTP 400: {"error": {"code": 400,
      "message": "API key not valid. Please pass a valid API key.", ...}}
  message has (Offline Heuristic) marker: True

WO-7 (unit-level):
  'Ahmedabad, Gujarat'   -> eligible=True  status='India (Local/Remote)'
  'Kolkata, WB, India'   -> eligible=True  status='India (Local/Remote)'
  'Jaipur, Rajasthan'    -> eligible=True  status='India (Local/Remote)'
  'Remote — India (West)'-> eligible=True  status='India (Local/Remote)'
  'New York, NY'         -> eligible=False status='Ineligible Location: New York, NY'
  'Zug, Switzerland'     -> eligible=True  status='Flagged for Review: Zug, Switzerland'

WO-2/WO-11 (mocked transport):
  prompt1 contains Java/Spring JD: True   prompt2 contains Python/RLHF: True
  prompts differ by job: True             no source-code literal: True
  history included: True                  JSON response mode: True
  key in x-goog-api-key header: True      no key in URL query: True

WO-14 (fresh clone):
  FAILED tests/test_interview_state_machine.py::test_interview_initial_state
  FAILED tests/test_interview_state_machine.py::test_round_advance_and_offline_marking
  FAILED tests/test_interview_state_machine.py::test_interview_full_completion_honest_score
  3 failed, 14 passed
  settings table after pytest (pollution):
    ('gemini_api_key', 'test-key-999')  ('gemini_model', 'gemini-3.8-flash')  ('offline_mode', 'true')

WO-9 (live scan): greenhouse rows: 211, 'Not listed': 211, invented: 0; direct (estimate) 12/12
WO-11 (preflight): foreign origin -> HTTP 400, no ACAO header; localhost:8000 -> HTTP 200, ACAO echo
Boot: GET /health == {"status":"ok","app":"ai-gig-platform"} on fresh clone, no .env, no data/
```

## 5. Conditions requiring fixups (blocking DoD)

**C-1 (G-5) — real name remnants.** Branch: `privacy/pii-purge-fixup-1`
- `app/services/interview_packet.py:14` — `candidate_name = profile.get("name", "Ankit Singh Tomar")` (same hardcode pattern as the fixed `resume_generator.py:16`)
- `collab/DATABASE_SNAPSHOT.md:90` — `"name": "Ankit Singh Tomar"`
- `collab/VERIFIED_DOSSIER_SAMPLES.md:8,23` — name in prose
Replace with placeholder/profile-driven values; acceptance = `git grep -n "Ankit Singh Tomar" -- ":(exclude)review" ":(exclude).git"` returns nothing.

**C-2 (G-14) — test suite hermeticity.** Branch: `tests/minimal-suite-fixup-1`
- Seed the state-machine tests with a fixture job (or mock `get_job_by_id`) so they pass on a fresh clone.
- Isolate the DB: point tests at a tmp DB (monkeypatch `DB_PATH` / fixture), never write `offline_mode` or test keys to the real `data/gighunter.db`; restore any mutated settings.
- Acceptance: fresh clone → `pytest` 17/17 green, and `data/gighunter.db` settings table unchanged by the run.

## 6. Advisories (non-blocking)

- **A-1:** Prune `gemini-1.5-flash` / `gemini-1.5-pro` from the settings dropdown or verify they still resolve for the owner's key (2.5-flash already 404s for new users; 1.5 is almost certainly worse).
- **A-2 (follow-up register):** F17 (`high_score` = 0 for the seeded default profile until a real resume is uploaded) and F19 (`session_id` = 8 hex chars) were never dispatched in SPEC01 work orders — reviewer's omission, not executor's. Park for a P3 pass.
- **A-3:** Consider a CI workflow running `docker build` + `pytest` on push — would have caught C-2 and keeps G-4 continuously verified.

## 7. Definition of Done status

NOT YET MET. Required to close SPEC01:
1. C-1 and C-2 fixups executed per branch protocol, with receipts.
2. One Docker-enabled independent G-4 run (reviewer or CI).
3. Reviewer delta appended to `REVIEWER_REPORT.md` (done — see §8 of that report) and Operator acceptance on this ledger.

**Overall assessment:** this was a high-quality execution pass. 14/14 work orders landed as specified, zero silent deviations, honest receipts, branch protocol followed to the letter. The two conditions are narrow (a name string in 4 places; test isolation) and the fixups are small. The platform's interview-practice half — the owner's stated core goal — now degrades loudly instead of silently, asks job-aware questions, and keeps its settings: the three findings that made it untrustworthy are closed.
