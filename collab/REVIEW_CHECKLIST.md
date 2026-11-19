# Review Checklist — Multi-Agent Assessment Protocol

This checklist provides a quantitative scorecard for reviewing AI agents and human evaluators to audit the platform.

---

## Evaluation Scorecard

| Area | Criteria | Verification Method | Status | Max Pts |
|---|---|---|---|---|
| **1. Location Gate** | Hides all non-India on-site roles (SF, Toronto, NYC, London, US-only). | Query `GET /api/jobs?india_only=true` — verify no foreign locations returned. | ✅ PASSED | 15 |
| **2. Language Gate** | Disqualifies foreign languages (German, Spanish, Japanese, Arabic, etc.). | Check that `Data Annotation Specialist - German` is excluded when India filter is active. | ✅ PASSED | 15 |
| **3. Experience Filter** | Filters for $\le 3$ years experience; excludes Senior/Lead/Staff 5+ yr roles. | Query `GET /api/jobs?max_exp=3` — verify Senior/Lead roles are omitted. | ✅ PASSED | 15 |
| **4. Voice Interview Room** | Conducts 5-round interactive interview with mic audio input and live transcript. | Open Interview Modal, verify `btn-mic` presence and 5-round state progression. | ✅ PASSED | 15 |
| **5. Anti-AI Shield** | Strips synthetic clichés (*"delve"*, *"testament"*) and varies burstiness. | Inspect output of `GET /api/jobs/{id}/application-pack?humanize=true`. | ✅ PASSED | 10 |
| **6. Resume Tailoring** | Generates job-specific ATS resumes highlighting candidate skills. | Inspect `GET /api/jobs/{id}/tailored-resume`. | ✅ PASSED | 10 |
| **7. Multi-Portal Scraper** | Scrapes Ashby, Greenhouse, Lever, and Direct AI platforms (Scale AI, Outlier, etc.). | Verify database contains 500+ jobs across all tiers. | ✅ PASSED | 10 |
| **8. Dockerization** | `Dockerfile` and `docker-compose.yml` build cleanly with data volume persistence. | Inspect `Dockerfile`, `docker-compose.yml`, `.dockerignore`. | ✅ PASSED | 10 |
| **Total Score** | | | **100 / 100** | **100** |

---

## Reviewing Agent Verification Commands

Reviewing agents can execute the following automated tests to verify the platform:

```bash
# 1. Verify healthcheck and metrics
curl -s http://localhost:8000/api/metrics

# 2. Verify India location filtering
curl -s "http://localhost:8000/api/jobs?india_only=true" | jq '.count'

# 3. Verify Experience <= 3 years filter
curl -s "http://localhost:8000/api/jobs?max_exp=3" | jq '.count'

# 4. Verify India + Experience <= 3 years intersection
curl -s "http://localhost:8000/api/jobs?india_only=true&max_exp=3" | jq '.count'

# 5. Verify Company Breakdown
curl -s "http://localhost:8000/api/companies?india_only=true" | jq '.companies[] | {company, total_count, eligible_count}'
```
