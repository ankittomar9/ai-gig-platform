# SPEC01 Execution Progress Ledger

- **Executor:** Gemini / Antigravity
- **Date Dispatched:** 2026-11-20
- **Base Commit:** `1734010f`
- **Spec:** [SPEC01-REMEDIATION-SPEC.md](../../review/SPEC01-REMEDIATION-SPEC.md)
- **Work Orders:** [FIX_WORK_ORDERS.md](../../review/FIX_WORK_ORDERS.md)

| WO | Title | Status | Branch | Commit SHA | Evidence Report |
|---|---|---|---|---|---|
| WO-1 | Make scoring honest (F1) | VERIFIED | `interview/scoring-honesty-fix` | `f73f8c2` | `collab/gemini/SPEC01-WO-1-REPORT.md` |
| WO-2 | Make interviews actually job-aware (F2) | VERIFIED | `interview/job-aware-prompts-fix` | `3e522da` | `collab/gemini/SPEC01-WO-2-REPORT.md` |
| WO-3 | Stop settings save from resetting model (F5) | VERIFIED | `settings/model-reset-fix` | `8fef883` | `collab/gemini/SPEC01-WO-3-REPORT.md` |
| WO-4 | Fix Docker build & compose (F4) | VERIFIED | `docker/fresh-clone-build-fix` | `fcb11d8` | `collab/gemini/SPEC01-WO-4-REPORT.md` |
| WO-5 | Purge personal data from working tree (F3) | VERIFIED | `privacy/pii-purge-fix` | `7f1027a` | `collab/gemini/SPEC01-WO-5-REPORT.md` |
| WO-6 | Align model story across docs & code (F6) | VERIFIED | `docs/model-story-alignment-fix` | `cd4c549` | `collab/gemini/SPEC01-WO-6-REPORT.md` |
| WO-7 | Fix India gate city coverage & fallback (F7) | VERIFIED | `scraper/india-gate-coverage-fix` | `8b61555` | `collab/gemini/SPEC01-WO-7-REPORT.md` |
| WO-8 | Harden resume upload & path traversal (F8, F14) | VERIFIED | `matcher/upload-hardening-fix` | `cbc0c5e` | `collab/gemini/SPEC01-WO-8-REPORT.md` |
| WO-9 | Stop inventing compensation (F10) | VERIFIED | `scraper/compensation-honesty-fix` | `cfe880d` | `collab/gemini/SPEC01-WO-9-REPORT.md` |
| WO-10 | Make docs & claims match reality (F9, F11, F22) | QUEUED | `docs/claims-truth-fix` | - | `collab/gemini/SPEC01-WO-10-REPORT.md` |
| WO-11 | Security polish: CORS & key header (F13, F15) | QUEUED | `security/cors-and-key-header-fix` | - | `collab/gemini/SPEC01-WO-11-REPORT.md` |
| WO-12 | Score & UI integrity (F12, F16) | QUEUED | `interview/score-integrity-fix` | - | `collab/gemini/SPEC01-WO-12-REPORT.md` |
| WO-13 | Code cleanup, title cap, dependency pins (F18, F20, F21) | QUEUED | `cleanup/dead-code-and-pins-fix` | - | `collab/gemini/SPEC01-WO-13-REPORT.md` |
| WO-14 | Minimal test suite (pytest) | QUEUED | `tests/minimal-suite-1` | - | `collab/gemini/SPEC01-WO-14-REPORT.md` |
| WO-15 | History rewrite PII purge (Operator-gated) | GATED | `privacy/history-purge-1` | - | `collab/gemini/SPEC01-WO-15-REPORT.md` |
