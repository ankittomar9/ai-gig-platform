# [SPEC01-WO-2] Make Interviews Actually Job-Aware (F2 Remediation)
- **Author:** Gemini / Antigravity
- **Date:** 2026-11-20
- **Base Commit:** `eb75a0c`
- **Branch:** `interview/job-aware-prompts-fix`
- **Verdict:** EXECUTED

---

## 1. Summary of Changes
- **Target Role & Job Description Injection:** Injected `job["description"][:2000]`, `job["category"]`, `job["tier"]`, and `job["skills"]` into the Gemini evaluation and question generation prompt.
- **Conversation History Context:** Extracted prior conversation turns (up to the last 4 message pairs / 8 messages) and injected them into the prompt so follow-up questions build dynamically on candidate answers.
- **Removed Leaked Code Literals:** Eliminated literal Python code snippets (`"If curr_round < 4:"` / `"If curr_round == 4:"`) from the prompt text, replacing them with dynamic, context-aware `round_objective` instructions.

---

## 2. Acceptance Test Evidence (Verbatim Receipts)

Command executed:
```python
import asyncio
from unittest.mock import patch, MagicMock
from app.services.interview_agent import _call_gemini_interview
from app.database import get_job_by_id

async def test():
    job1 = get_job_by_id('direct_turing_java_engineer')
    session1 = {
        'session_id': 'sess-java',
        'company': job1['company'],
        'role_title': job1['title'],
        'current_round': 1,
        'messages': [
            {'sender': 'ai', 'message': 'Welcome to Turing screening!', 'round_number': 1},
            {'sender': 'user', 'message': 'I have 3 years of Java Spring Boot experience designing microservices.', 'round_number': 1}
        ]
    }

    job2 = get_job_by_id('direct_outlier_coding')
    session2 = {
        'session_id': 'sess-python',
        'company': job2['company'],
        'role_title': job2['title'],
        'current_round': 1,
        'messages': [
            {'sender': 'ai', 'message': 'Welcome to Outlier screening!', 'round_number': 1},
            {'sender': 'user', 'message': 'I have experience evaluating Python code outputs and RLHF rankings.', 'round_number': 1}
        ]
    }

    intercepted_prompts = []

    async def mock_post(self, url, *args, **kwargs):
        payload = kwargs.get('json', {})
        intercepted_prompts.append(payload['contents'][0]['parts'][0]['text'])
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '{\n  "score": 9,\n  "feedback": "Solid depth.",\n  "message": "### Interviewer Evaluation\\n\\n### Next Question (Round 2):\\nHow would you debug a Spring Boot / JVM memory leak?",\n  "suggested_answer": "Optimal answer."\n}'
                    }]
                }
            }]
        }
        return mock_resp

    with patch('httpx.AsyncClient.post', new=mock_post):
        await _call_gemini_interview(job1, session1, session1['messages'][1]['message'], 'fake-key', 'gemini-2.5-flash')
        await _call_gemini_interview(job2, session2, session2['messages'][1]['message'], 'fake-key', 'gemini-2.5-flash')

    prompt1 = intercepted_prompts[0]
    prompt2 = intercepted_prompts[1]

    print('=== PROMPT 1 (TURING JAVA / SPRING BOOT) ===')
    print('Contains Java & Spring:', ('Java' in prompt1 and 'Spring' in prompt1))
    print('Contains JD Excerpt:', job1['description'][:80] in prompt1)
    print('Contains source-code leak ("If curr_round < 4:"):', 'If curr_round < 4:' in prompt1)
    print('Contains candidate history turn:', 'Java Spring Boot' in prompt1)

    print('\n=== PROMPT 2 (OUTLIER PYTHON / RLHF) ===')
    print('Contains Python / RLHF:', ('Python' in prompt2 or 'RLHF' in prompt2))
    print('Contains JD Excerpt:', job2['description'][:80] in prompt2)
    print('Contains source-code leak ("If curr_round < 4:"):', 'If curr_round < 4:' in prompt2)
    print('Contains candidate history turn:', 'evaluating Python code outputs' in prompt2)

    assert ('Java' in prompt1) and ('Spring' in prompt1)
    assert ('Python' in prompt2) or ('RLHF' in prompt2)
    assert 'If curr_round < 4:' not in prompt1
    assert 'If curr_round < 4:' not in prompt2
    print('\nAll job-awareness and prompt-hygiene assertions passed!')

asyncio.run(test())
```

Raw Command Output:
```text
=== PROMPT 1 (TURING JAVA / SPRING BOOT) ===
Contains Java & Spring: True
Contains JD Excerpt: True
Contains source-code leak ("If curr_round < 4:"): False
Contains candidate history turn: True

=== PROMPT 2 (OUTLIER PYTHON / RLHF) ===
Contains Python / RLHF: True
Contains JD Excerpt: True
Contains source-code leak ("If curr_round < 4:"): False
Contains candidate history turn: True

All job-awareness and prompt-hygiene assertions passed!
```

### Honest-Judge Pair
- **Known-Good Assertion (Prompt 1 matches Job 1 tech stack):**
  - Expected: Contains `"Java"` and `"Spring"` and Job Description excerpt.
  - Actual: `True` ✅ PASS
- **Deliberate Failure Assertion (Asserting Prompt 1 contains source code leak):**
  - Checked: `assert 'If curr_round < 4:' in prompt1` -> Fails as expected (code leak completely removed).
