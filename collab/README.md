# Collab Review Suite — Multi-Agent Quality Assurance

Welcome to the **Collab** directory. This space is organized specifically for **autonomous reviewing AI agents**, quality inspectors, and human technical leads to inspect, benchmark, and evaluate every facet of the **AI Gig Hunter & Interview Simulator** platform.

---

## Instructions for Reviewing AI Agents

When conducting an autonomous review of this platform, adhere to the following evaluation protocol:

1. **Architecture & Design:** Read [`ARCHITECTURE.md`](./ARCHITECTURE.md) to understand the system topologies, background scrapers, SQLite schema, and speech inference fallbacks.
2. **Feature Coverage:** Review [`FEATURE_DOSSIER.md`](./FEATURE_DOSSIER.md) to verify that all user requirements (multi-ATS scanning, India location filter, English/Hindi language check, $\le 3$ years experience filter, voice interview simulator, anti-AI detector shield, dockerization) are fully implemented.
3. **Execution Checklist:** Work through [`REVIEW_CHECKLIST.md`](./REVIEW_CHECKLIST.md) and report your assessment score (0-100) across:
   - Functional Correctness & Edge Cases
   - Security & Credential Isolation
   - Code Cleanliness & Separation of Concerns
   - User Experience & Dashboard Responsiveness
4. **Historical Trajectory:** Inspect [`CHANGELOG.md`](./CHANGELOG.md) to track previous bugs identified and resolved during iterative user feedback sessions.

---

## Review Artifacts Index

- [`collab/DATABASE_SNAPSHOT.md`](./DATABASE_SNAPSHOT.md) — Complete database census, registry table of all 35 India-eligible jobs, and schema snapshot.
- [`collab/VERIFIED_DOSSIER_SAMPLES.md`](./VERIFIED_DOSSIER_SAMPLES.md) — Live generated samples of Role Dossiers, Anti-AI Application Packs, and Tailored Resumes for top India roles (Turing, Alignerr, Outlier, Scale AI, DataAnnotation).
- [`collab/data_export.json`](./data_export.json) — Structured JSON export of all India-eligible positions, personas, and candidate profile data for programmatic AI parsing.
- [`collab/ARCHITECTURE.md`](./ARCHITECTURE.md) — Technical blueprint, entity relationships, and service topology.
- [`collab/FEATURE_DOSSIER.md`](./FEATURE_DOSSIER.md) — In-depth technical breakdown of each feature.
- [`collab/REVIEW_CHECKLIST.md`](./REVIEW_CHECKLIST.md) — Quantitative grading criteria for external AI reviewers.
- [`collab/CHANGELOG.md`](./CHANGELOG.md) — Comprehensive evolution log of all system changes.
- [`../AGENTS.md`](../AGENTS.md) — Agentic roles, state machines, and heuristic definitions.
- [`../README.md`](../README.md) — High-level user guide and container execution instructions.
