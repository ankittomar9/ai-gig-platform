# SPEC01 Work Order 11 Verification Report: Security Polish (CORS & Key Header)

**Date:** 2026-11-20
**Work Order:** WO-11 (`security/cors-and-key-header-fix`)
**Reported Findings:** F13 (CORS `allow_origins=["*"]` + `allow_credentials=True`), F15 (API key leaked in query param `?key=`)
**Operator / Author:** Gemini Antigravity Executor

---

## 1. Summary of Changes

1. **`app/main.py`**:
   - Replaced wildcard CORS `allow_origins=["*"]` with explicit local origins `allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"]`.
2. **`app/services/interview_agent.py`**:
   - Removed `?key={api_key}` query parameter from the Gemini API request URL.
   - Passed API key securely via the `x-goog-api-key: {api_key}` HTTP header.

---

## 2. Evidence Receipts

### Command: Codebase Grep for `key=` in Request URLs
```powershell
git grep -n "key=" -- ':!review'
```
Output:
*(Command exited with return code 1 — 0 matches)*

### Command: CORS Preflight & Header Construction Test
```powershell
.\venv\Scripts\python.exe -c "
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test 1: OPTIONS preflight from foreign origin
resp_foreign = client.options('/api/jobs', headers={
    'Origin': 'https://evil.example.com',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'content-type'
})
print('Foreign Origin Preflight:')
print('Status:', resp_foreign.status_code)
print('Access-Control-Allow-Origin header:', resp_foreign.headers.get('access-control-allow-origin'))

# Test 2: OPTIONS preflight from allowed origin
resp_allowed = client.options('/api/jobs', headers={
    'Origin': 'http://localhost:8000',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'content-type'
})
print('\nAllowed Origin Preflight:')
print('Status:', resp_allowed.status_code)
print('Access-Control-Allow-Origin header:', resp_allowed.headers.get('access-control-allow-origin'))

# Test 3: Verify Gemini call header construction
import inspect
from app.services.interview_agent import _call_gemini_interview
src = inspect.getsource(_call_gemini_interview)
print('\nKey Header in Gemini call:')
print('x-goog-api-key present:', 'x-goog-api-key' in src)
print('key= in URL present:', 'key=' in src)
"
```

Raw Command Output:
```text
Foreign Origin Preflight:
Status: 400
Access-Control-Allow-Origin header: None

Allowed Origin Preflight:
Status: 200
Access-Control-Allow-Origin header: http://localhost:8000

Key Header in Gemini call:
x-goog-api-key present: True
key= in URL present: False
```

---

## 3. Honest-Judge Verification Pair
- **Known-Bad Assertion (Foreign origin preflight `https://evil.example.com`):**
  - Result: HTTP 400 / Origin rejected (No `Access-Control-Allow-Origin` header). ✅ PASS
- **Known-Good Assertion (Local origin preflight `http://localhost:8000`):**
  - Result: HTTP 200 / `Access-Control-Allow-Origin: http://localhost:8000`. ✅ PASS
- **Key Transmission Assertion:**
  - `x-goog-api-key` header used; zero `key=` query string occurrences. ✅ PASS

---

## 4. Verdict
- Status: **PASS**.
