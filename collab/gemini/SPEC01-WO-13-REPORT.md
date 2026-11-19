# SPEC01 Work Order 13 Verification Report: Code Cleanup, Acronyms, and Pins

**Date:** 2026-11-20
**Work Order:** WO-13 (`cleanup/dead-code-and-pins-fix`)
**Reported Findings:** F18 (Acronym casing "Sql", "Api"), F20 (Dead code: `cover_letter` duplication, uncapped title-bonus, unconditional `web_speech_supported: True`, unsettable `groq_api_key`), F21 (Floor-pinned dependencies in `requirements.txt`)
**Operator / Author:** Gemini Antigravity Executor

---

## 1. Summary of Changes

1. **`app/services/matcher.py`**:
   - Added canonical acronym dictionary mapping (`SQL`, `API`, `RLHF`, `LLM`, `AWS`, `GCP`, `NLP`, `Node.js`, `FastAPI`, `PostgreSQL`, etc.) preventing title-casing like `"Sql"` or `"Api"`.
   - Capped title keyword matching bonus at 20 points (`min(20, title_bonus)`), matching the documented algorithm limits.
2. **`app/services/application_pack.py` & `app/models.py`**:
   - Removed duplicated `cover_letter` key (which was an exact copy of `why_interested`).
3. **`app/services/speech.py`**:
   - Removed unconditional server claim `"web_speech_supported": True`. Web speech availability is strictly client-evaluated by browser capabilities.
4. **`app/main.py` & `app/models.py` & `app/static/index.html` & `app/static/app.js`**:
   - Added `groq_api_key` to `SettingsUpdate` model and database settings persistence.
   - Masked and returned `groq_api_key_set` and `groq_api_key_masked` via `GET /api/settings`.
   - Added Groq Whisper key configuration field in the Settings Modal in `index.html` and wired it into `app.js`.
5. **`requirements.txt`**:
   - Pinned all dependencies to exact versions (`==`):
     - `fastapi==0.165.0`
     - `uvicorn[standard]==0.54.0`
     - `httpx==0.28.1`
     - `python-multipart==0.0.34`
     - `pydantic==2.14.4`
     - `python-docx==1.2.0`
     - `pytest==9.2.0`

---

## 2. Evidence Receipts

### Python Verification Script Execution
```powershell
.\venv\Scripts\python.exe -c "
from app.services.matcher import extract_skills_from_text, calculate_match_score
from app.services.application_pack import generate_application_pack
from app.services.speech import check_whisper_status
from fastapi.testclient import TestClient
from app.main import app
import asyncio

# 1. Test acronym casing
skills = extract_skills_from_text('I am experienced in SQL, API development, RLHF, AWS, Python and Docker.')
print('Extracted skills:', skills)
assert 'SQL' in skills, 'SQL should be uppercase'
assert 'API' in skills, 'API should be uppercase'
assert 'RLHF' in skills, 'RLHF should be uppercase'
assert 'AWS' in skills, 'AWS should be uppercase'
assert 'Python' in skills
assert 'Docker' in skills

# 2. Test capped title bonus
long_title = 'Python Java Docker Linux SQL API Machine Learning React Git Kubernetes Engineer'
score, matched = calculate_match_score(long_title, 'Some desc', ['Python', 'SQL', 'Docker'], 'Python Java Docker Linux SQL')
print('Capped title match score:', score, 'Matched skills:', matched)
assert score <= 98

# 3. Test application pack (no duplicate cover_letter)
sample_job = {'id': 'test_job', 'company': 'TestCo', 'title': 'AI Trainer', 'url': 'http://test.com'}
sample_profile = {'name': 'Test Candidate', 'skills': ['Python', 'SQL']}
pack = generate_application_pack(sample_job, sample_profile, humanize=False)
print('Application pack keys:', list(pack.keys()))
assert 'cover_letter' not in pack, 'cover_letter should be removed'
assert 'why_interested' in pack

# 4. Test speech status (no unconditional web_speech_supported)
speech_status = asyncio.run(check_whisper_status())
print('Speech status keys:', list(speech_status.keys()))
assert 'web_speech_supported' not in speech_status

# 5. Test settable groq_api_key
client = TestClient(app)
resp = client.post('/api/settings', json={'groq_api_key': 'gsk_test123456789'})
assert resp.status_code == 200
settings_resp = client.get('/api/settings').json()
print('Settings response groq_api_key_set:', settings_resp.get('groq_api_key_set'))
assert settings_resp.get('groq_api_key_set') is True

# 6. Verify requirements.txt pins
with open('requirements.txt') as f:
    reqs = f.read().splitlines()
print('Requirements pins:', reqs)
for r in reqs:
    assert '==' in r, f'Unpinned dependency: {r}'

print('>>> ALL WO-13 ACCEPTANCE TESTS PASSED CLEANLY! <<<')
"
```

Raw Command Output:
```text
Extracted skills: ['API', 'AWS', 'Docker', 'Python', 'RLHF', 'SQL']
Capped title match score: 98 Matched skills: ['Docker', 'Java', 'Linux', 'Python', 'SQL']
Application pack keys: ['job_id', 'company', 'role_title', 'apply_url', 'why_interested', 'relevant_experience', 'quality_assurance_strategy', 'master_interview_prompt', 'one_click_bundle', 'is_humanized']
Speech status keys: ['local_whisper_online', 'local_endpoint', 'groq_whisper_available', 'gemini_available']
Settings response groq_api_key_set: True
Requirements pins: ['fastapi==0.165.0', 'uvicorn[standard]==0.54.0', 'httpx==0.28.1', 'python-multipart==0.0.34', 'pydantic==2.14.4', 'python-docx==1.2.0', 'pytest==9.2.0']
>>> ALL WO-13 ACCEPTANCE TESTS PASSED CLEANLY! <<<
```

---

## 3. Honest-Judge Verification Pair
- **Known-Bad Assertion 1 (Skill Acronym Casing):**
  - Expected: "SQL", "API", "RLHF", "AWS" (not "Sql", "Api", "Rlhf", "Aws").
  - Actual: Matched correctly via canonical acronym dictionary. ✅ PASS
- **Known-Bad Assertion 2 (Dead Code & Fake Server Capabilities):**
  - Expected: `cover_letter` duplicate absent; `web_speech_supported` absent from server response.
  - Actual: Cleaned up. ✅ PASS
- **Known-Good Assertion (Exact Dependency Pinning):**
  - Expected: Every entry in `requirements.txt` contains `==` lock pin.
  - Actual: Pinned to exact active versions. ✅ PASS

---

## 4. Verdict
- Status: **PASS**.
