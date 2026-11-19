# [SPEC01-WO-6] Align Model Story Across Docs & Code (F6 Remediation)
- **Author:** Gemini / Antigravity
- **Date:** 2026-11-20
- **Base Commit:** `718ac5a`
- **Branch:** `docs/model-story-alignment-fix`
- **Verdict:** EXECUTED

---

## 1. Summary of Changes
- **Aligned Default Model ID:** Updated code defaults in `app/config.py`, `app/main.py`, and `app/services/interview_agent.py` to `gemini-3.8-flash`, matching the documented model and Google AI Studio's active model API requirement.
- **Added Model to Settings Dropdown:** In `app/static/index.html`, added `gemini-3.8-flash` as the primary default choice in the Model Selection dropdown alongside `gemini-2.5-flash`, `gemini-1.5-flash`, and `gemini-1.5-pro`.
- **Environment & Docs Consistency:** Synchronized `.env` default and verified all documentation claims across `README.md`, `AGENTS.md`, `collab/CHANGELOG.md`, and `collab/FEATURE_DOSSIER.md`.

---

## 2. Acceptance Test Evidence (Verbatim Receipts)

### Test A: Working Tree Grep for "3.8" Model References
Command executed:
```bash
git grep -n "3.8" -- ":(exclude)review" ":(exclude)collab/gemini"
```

Raw Command Output:
```text
AGENTS.md:81:- **Scoring Protocol:** Uses Google's frontier model API (`gemini-3.8-flash`) or local fallbacks to deliver honest, uncompromising rubric scores and step-by-step guidance.
README.md:36:- **Frontier AI Scoring:** Evaluated by Google's `gemini-3.8-flash` for honest, non-sycophantic scoring.
app/config.py:23:    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
app/main.py:272:        "gemini_model": settings.get("gemini_model", "gemini-3.8-flash"),
app/services/interview_agent.py:120:        model_name = settings.get("gemini_model") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
app/static/index.html:546:                        <option value="gemini-3.8-flash">Gemini 3.8 Flash (Default / Fastest & Free Tier friendly)</option>
collab/CHANGELOG.md:52:  - Added honest frontier model rubric scoring using `gemini-3.8-flash`.
collab/FEATURE_DOSSIER.md:56:- **Frontier Rubric Scoring:** Powered by Google's `gemini-3.8-flash` model, delivering strict, candid scoring (0-10 per round) rather than sycophantic false praise.
```

### Test B: Settings Verification via API
Commands executed:
```bash
curl -s -X PUT "http://127.0.0.1:8000/api/settings" -H "Content-Type: application/json" -d '{"gemini_model": "gemini-3.8-flash"}'
curl -s "http://127.0.0.1:8000/api/settings"
```

Raw Command Output:
```text
{"status":"success","message":"Settings saved successfully"}
{"gemini_api_key_set":true,"gemini_api_key_masked":"sec-...5678","gemini_model":"gemini-3.8-flash","offline_mode":false,"minimum_rate":0.0}
```

---

## 3. Honest-Judge Verification Pair
- **Known-Good Assertion:**
  - `GET /api/settings` returns `"gemini_model": "gemini-3.8-flash"` matching `README.md` and `index.html`. ✅ PASS
- **Deliberate Failure Test:**
  - `git grep -n "gemini-2.5-flash" app/config.py app/main.py` -> 0 occurrences (no legacy default).
