# [SPEC01-WO-3] Stop Settings Save from Resetting Model (F5 Remediation)
- **Author:** Gemini / Antigravity
- **Date:** 2026-11-20
- **Base Commit:** `9793e1b`
- **Branch:** `settings/model-reset-fix`
- **Verdict:** EXECUTED

---

## 1. Summary of Changes
- **Pydantic Model Default Remediation:** In `app/models.py`, changed `SettingsUpdate.gemini_model` from default `"gemini-2.5-flash"` to `Optional[str] = None`. Also changed `offline_mode` and `minimum_rate` defaults to `None`.
- **Partial Update Isolation:** With defaults set to `None`, omitted fields in update payloads are never overwritten or reset.
- **Added HTTP PUT Route:** Added `@app.put("/api/settings")` alongside `@app.post("/api/settings")` in `app/main.py`.

---

## 2. Acceptance Test Evidence (Verbatim Receipts)

Commands executed:
```bash
# 1. Update model to gemini-2.5-pro
curl -s -X PUT "http://127.0.0.1:8000/api/settings" -H "Content-Type: application/json" -d '{"gemini_model": "gemini-2.5-pro"}'

# 2. Update ONLY gemini_api_key (omitting gemini_model)
curl -s -X PUT "http://127.0.0.1:8000/api/settings" -H "Content-Type: application/json" -d '{"gemini_api_key": "sec-key-12345678"}'

# 3. GET current settings
curl -s "http://127.0.0.1:8000/api/settings"
```

Raw Command Output:
```text
{"status":"success","message":"Settings saved successfully"}
{"status":"success","message":"Settings saved successfully"}
{"gemini_api_key_set":true,"gemini_api_key_masked":"sec-...5678","gemini_model":"gemini-2.5-pro","offline_mode":false,"minimum_rate":0.0}
```

---

## 3. Honest-Judge Verification Pair
- **Known-Good Assertion:**
  - `GET /api/settings` returned `"gemini_model": "gemini-2.5-pro"` after setting key only.
  - Verified: Model persisted without reverting to flash. ✅ PASS
- **Deliberate Failure Test:**
  - Tested: `assert get_settings()["gemini_model"] == "gemini-2.5-flash"` -> Fails as expected (model remained pro).
