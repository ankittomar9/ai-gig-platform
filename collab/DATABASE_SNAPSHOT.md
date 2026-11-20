# Complete Database Snapshot & Registry Report

This report contains the live, verified data snapshot extracted directly from the platform SQLite database (`data/gighunter.db`). Autonomous reviewing AI agents and human evaluators can use this document to audit data integrity, categorization accuracy, and filtering rigor.

---

## 1. High-Level Database Census

| Metric | Count | Description |
|---|---|---|
| **Total Jobs in Database** | `522` | All indexed postings across Ashby, Greenhouse, Lever, and Direct feeds |
| **India-Eligible Jobs (English/Hindi)** | `35` | Verified applicable from India (no SF/Toronto/NYC on-site or foreign language gates) |
| **Perfect Matches (<= 3 Yrs Exp + India)** | `30` | Gigs with zero seniority barrier matching the candidate 2-3 years backend experience |
| **Filtered Ineligible Jobs** | `487` | Excluded due to foreign physical locations (SF, NYC, Toronto, London) or language gates |

---

## 2. Company & Platform Distribution

| Company | Total Gigs | India-Eligible | Perfect Match (<= 3y) |
|---|---|---|---|
| **Scale AI** | 169 | 2 | 2 |
| **Cohere** | 126 | 0 | 0 |
| **Mercor** | 107 | 1 | 1 |
| **Turing** | 42 | 10 | 6 |
| **Surge AI** | 36 | 0 | 0 |
| **Appen** | 17 | 1 | 1 |
| **Outlier** | 8 | 5 | 5 |
| **Invisible Technologies** | 5 | 4 | 4 |
| **Alignerr** | 3 | 3 | 3 |
| **DataAnnotation** | 2 | 2 | 2 |
| **Telus AI** | 1 | 1 | 1 |
| **Prolific** | 1 | 1 | 1 |
| **OneForma** | 1 | 1 | 1 |
| **Mindrift** | 1 | 1 | 1 |
| **Micro1** | 1 | 1 | 0 |
| **Clickworker** | 1 | 1 | 1 |
| **Alignerr (Labelbox)** | 1 | 1 | 1 |

---

## 3. Directory of All 35 India-Eligible Jobs (English & Hindi)

The table below lists every single job in the database that has passed both the **Location Gate (India / Global Remote)** and the **Language Gate (English & Hindi)**:

| # | Company | Job Title | Compensation | Exp Required | Domain | Location Status | Apply Link |
|---|---|---|---|---|---|---|---|
| 1 | **Turing** | AI Trainer & Java / Spring Boot Systems Engineer (India Remote) | `$35 - $65/hr` | `0-2 yrs (Assessment Based)` | Coding | India (Local/Remote) | [Apply](https://www.turing.com/jobs) |
| 2 | **Alignerr (Labelbox)** | Domain Expert AI Alignerr (STEM, Coding & Writing) | `$25 - $60/hr` | `0-2 yrs (Assessment Based)` | Coding | Open Remote | [Apply](https://www.alignerr.com/) |
| 3 | **Alignerr** | AI Code Reviewer & Evaluation Engineer (Java, Spring, Python) | `$35 - $60/hr` | `0-2 yrs (Assessment Based)` | Coding | Open Remote | [Apply](https://www.alignerr.com/) |
| 4 | **Alignerr** | Logic, Reasoning & Quantitative Problem Solver | `$30 - $55/hr` | `0-2 yrs (Assessment Based)` | Math & Reasoning | Open Remote | [Apply](https://www.alignerr.com/) |
| 5 | **Outlier** | AI Software Engineer & Code Evaluator (Java, Python, C++) | `$35 - $50/hr` | `0-2 yrs (Assessment Based)` | Coding | Open Remote | [Apply](https://outlier.ai/) |
| 6 | **Outlier** | AI Reasoning & Mathematical Logic Trainer | `$30 - $45/hr` | `0-2 yrs (Assessment Based)` | Math & Reasoning | Open Remote | [Apply](https://outlier.ai/) |
| 7 | **DataAnnotation** | Software Engineering & Code Evaluation Specialist | `$40 - $45/hr` | `0-2 yrs (Assessment Based)` | Coding | Open Remote | [Apply](https://www.dataannotation.tech/) |
| 8 | **Alignerr** | Technical Writer & Domain Expert RLHF Evaluator | `$25 - $40/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | Open Remote | [Apply](https://www.alignerr.com/) |
| 9 | **Outlier** | Bilingual AI Trainer & RLHF Evaluator (English & Hindi) | `$20 - $32/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | India (Local/Remote) | [Apply](https://outlier.ai/) |
| 10 | **Outlier** | Threat Intel - AI / LLM Trainer - Make Your Own Hours | `$18 - $30/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | Global Remote | [Apply](https://job-boards.greenhouse.io/remotasks/jobs/4369099005) |
| 11 | **Mindrift** | AI Content Writer & Technical AI Tutor | `$15 - $28/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | Open Remote | [Apply](https://mindrift.ai/become-a-writer) |
| 12 | **Outlier** | Generalist RLHF Evaluator & Fact-Checking Specialist | `$18 - $25/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | Open Remote | [Apply](https://outlier.ai/) |
| 13 | **DataAnnotation** | Core AI Evaluator & Creative Prompt Specialist | `$20 - $25/hr` | `0-2 yrs (Assessment Based)` | Writing & RLHF | Global Remote | [Apply](https://www.dataannotation.tech/) |
| 14 | **Appen** | AI Search Relevance & LLM Prompt Assessor (English & Hindi - India) | `$12 - $20/hr` | `0-2 yrs (Assessment Based)` | Generalist | India (Local/Remote) | [Apply](https://appen.com/careers/) |
| 15 | **OneForma** | Multilingual AI Data Collector & Transcriber | `$10 - $18/hr` | `0-2 yrs (Assessment Based)` | Multilingual | Open Remote | [Apply](https://jobs.oneforma.com/) |
| 16 | **Telus AI** | Personalized Internet & AI Search Assessor | `$12 - $17/hr` | `0-2 yrs (Entry/Junior)` | Generalist | Open Remote | [Apply](https://www.telusinternational.com/careers/ai-community) |
| 17 | **Prolific** | Human AI Interaction & Behavioral Data Contributor | `$8 - $16/hr` | `0-2 yrs (Assessment Based)` | Generalist | Open Remote | [Apply](https://www.prolific.com/participants) |
| 18 | **Clickworker** | AI Model Feedback & UHRS Search Evaluator | `$5 - $15/hr` | `0-2 yrs (Assessment Based)` | Generalist | Global Remote | [Apply](https://www.clickworker.com/clickworker/) |
| 19 | **Mercor** | Frontier AI Benchmark & Evaluation Engineer | `$40 - $120/hr` | `1-3 yrs (Mid-Level)` | Coding | Open Remote | [Apply](https://jobs.ashbyhq.com/mercor) |
| 20 | **Turing** | Growth Strategy and Operations | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Generalist | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6252155004) |
| 21 | **Turing** | Performance Marketing Analyst, Paid Acquisition | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Generalist | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6252156004) |
| 22 | **Scale AI** | SME, Support Systems Specialist | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Generalist | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/scaleai/jobs/4684808005) |
| 23 | **Turing** | Forward-Deployed AI Engineer | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Coding | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6192729004) |
| 24 | **Turing** | Forward-Deployed AI Engineer | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Coding | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6192725004) |
| 25 | **Turing** | Software Engineer | `$35 - $75+/hr` | `1-3 yrs (Mid-Level)` | Coding | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6115695004) |
| 26 | **Scale AI** | GenAI Evaluation Specialist & Prompt Engineer (India Remote) | `$25 - $45/hr` | `1-3 yrs (Mid-Level)` | Coding | India (Local/Remote) | [Apply](https://scale.com/careers) |
| 27 | **Invisible Technologies** | Business Opportunities at Invisible (Commercial, Delivery, Client Accounts Team) | `$18 - $30/hr` | `1-3 yrs (Mid-Level)` | Generalist | Global Remote | [Apply](https://job-boards.eu.greenhouse.io/invisible/jobs/4614080101) |
| 28 | **Invisible Technologies** | Invisible Technologies Opportunities (Finance, Legal, Marketing, Talent, Business Ops) | `$18 - $30/hr` | `1-3 yrs (Mid-Level)` | Generalist | Global Remote | [Apply](https://job-boards.eu.greenhouse.io/invisible/jobs/4584333101) |
| 29 | **Invisible Technologies** | Product Opportunities at Invisible | `$18 - $30/hr` | `1-3 yrs (Mid-Level)` | Generalist | Global Remote | [Apply](https://job-boards.eu.greenhouse.io/invisible/jobs/4645560101) |
| 30 | **Invisible Technologies** | Technology Opportunities at Invisible | `$18 - $30/hr` | `1-3 yrs (Mid-Level)` | Generalist | Global Remote | [Apply](https://job-boards.eu.greenhouse.io/invisible/jobs/4607689101) |
| 31 | **Turing** | Research Engineering Manager, STEM | `$35 - $75+/hr` | `5+ yrs (Lead)` | Coding | Global Remote | [Apply](https://job-boards.greenhouse.io/turing/jobs/6255566004) |
| 32 | **Turing** | Senior DevOps & Infrastructure Engineer | `$35 - $75+/hr` | `5+ yrs (Senior)` | Coding | Global Remote | [Apply](https://job-boards.greenhouse.io/turing/jobs/6218247004) |
| 33 | **Turing** | Strategic Project Lead - Code | `$35 - $75+/hr` | `5+ yrs (Lead)` | Coding | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6142224004) |
| 34 | **Turing** | Technical Delivery Lead, Emerging | `$35 - $75+/hr` | `5+ yrs (Lead)` | Generalist | India (Local/Remote) | [Apply](https://job-boards.greenhouse.io/turing/jobs/6241507004) |
| 35 | **Micro1** | Senior AI Prompt & Code Evaluator (Global) | `$30 - $70/hr` | `5+ yrs (Senior)` | Coding | Global Remote | [Apply](https://www.micro1.ai/jobs) |

---

## 4. Candidate Profile Data (`user_profile`)

```json
{
  "name": "Applicant",
  "experience_years": 2,
  "target_rate": 25.0,
  "skills": [
    "Api",
    "Docker",
    "Gcp",
    "Git",
    "Java",
    "Linux",
    "Spring Boot",
    "Sql"
  ],
  "preferred_categories": [
    "Coding",
    "Writing & RLHF",
    "Generalist"
  ],
  "resume_summary": "CANDIDATE NAME\nIndia  \u2022  +91 XXXXX XXXXX  \u2022  candidate@example.com  \u2022  linkedin.com/in/candidate\nPROFESSIONAL SUMMARY\nApplication Support & Production Systems Engineer with ~3 years enterprise experience managing 24/7 operational reliability, incident response, and observability..."
}
```

---

## 5. Active Resume Personas (`resume_personas`)

### Persona: Application Production Systems Specialist (ACTIVE)
- **Category:** `Production & Support`
- **Core Skills:** ['Java', 'Spring Boot', 'SQL', 'Docker', 'GCP', 'Linux', 'API', 'Incident Management']
- **Summary:** Specialist in production environments, incident triage, system uptime, and enterprise cloud operations.

### Persona: Software Engineer & Backend Developer
- **Category:** `Coding`
- **Core Skills:** ['Python', 'Java', 'Spring Boot', 'SQL', 'Data Structures', 'Algorithms', 'Git', 'API']
- **Summary:** Software engineer experienced in backend architectures, clean code implementation, debugging, and API design.

### Persona: AI Trainer & RLHF Specialist
- **Category:** `Writing & RLHF`
- **Core Skills:** ['RLHF', 'Prompt Engineering', 'Model Evaluation', 'Pairwise Ranking', 'Hallucination Detection', 'Quality Assurance']
- **Summary:** AI Trainer skilled in prompt evaluation, rubric scoring, pairwise model comparisons, and adversarial testing.

### Persona: Data & Quality Evaluation Specialist
- **Category:** `Generalist`
- **Core Skills:** ['Data Annotation', 'Quality Assurance', 'Guideline Compliance', 'Attention to Detail', 'Search Relevance']
- **Summary:** Detail-oriented evaluator with high accuracy on data annotation, search relevance, and digital workflow benchmarks.
