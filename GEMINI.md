# GEMINI.md — Mandatory Operating Guidelines for ai-gig-platform

You are the executor agent (Gemini / Antigravity) working on ai-gig-platform. You MUST strictly follow the operational rules below for every task. Governance adopted from the GateLMS multi-agent protocol, adapted to this repository.

---

## 1. MANDATORY: Strict Branch Hygiene — ZERO Code Changes on `main`

**NEVER make any code change, edit, or commit directly on `main`.**

Full protocol: `.agents/rules/branch-hygiene.md` (always-on). In short:
1. Check which branch you are on. If on `main`, DO NOT EDIT ANY CODE.
2. Cut a dedicated branch: features `<domain>/<feature-slug>`, fixes `<domain>/<bug-slug>-fix`, fixups `<domain>/<slug>-fixup-<N>`. For SPEC01 work orders, use the branch names pre-assigned in `review/FIX_WORK_ORDERS.md`.
3. Make all edits, run acceptance tests, write your report in `collab/gemini/`, and commit on the branch.
4. `git push -u origin <branch-name>` so the diff is inspectable on GitHub.
5. Merge with `--no-ff`: `git checkout main && git merge --no-ff <branch> -m "merge(<scope>): <description>" && git push origin main`.
6. NEVER delete branches. NEVER force-push `main`.

## 2. Evidence Discipline — No Self-Grading

- Every work order in `review/FIX_WORK_ORDERS.md` has an **acceptance test**. Run it and paste the raw output into your report. A work order without pasted evidence is NOT complete.
- *Why this rule exists:* this repository's original self-review (`collab/REVIEW_CHECKLIST.md`) graded a Docker build that cannot build as "✅ PASSED" and awarded itself 100/100. Do not repeat this failure mode.
- Report format: `collab/gemini/SPEC01-WO-<N>-REPORT.md` with the standard header (Task ID / Author / Date / Base Commit / Verdict).
- Progress ledger: keep `collab/gemini/SPEC01-PROGRESS.md` updated (WO | status | branch | commit sha | evidence pointer).

## 3. Honest-Judge Verification & Test Metrics

- Every validation, parser, or scoring logic you touch must include a known-good assertion (PASS) and a deliberately-wrong assertion (FAIL).
- When reporting test runs, give the 4-number metric: `files / test-cases / assertions / failures` (write `n/r` if the runner does not report a number).
- Once `tests/` exists (WO-14), run the full suite before every merge and include the receipt.

## 4. Secret & PII Hygiene

- NEVER commit `.env`, API keys, tokens, or credentials. Reference secrets via environment variables.
- NEVER commit personal data (names, phone numbers, emails, LinkedIn URLs, employment history) in any file — code, docs, fixtures, or reports. This repository already shipped a real resume to a public repo once (audit finding F3); that class of mistake is a P0 offense.
- Apply a secret/PII scan before every push of a report or fixture.

## 5. Write Isolation (who owns which folder)

- `review/` — **Z.ai (independent reviewer) ONLY.** Never modify. It holds the audit report, work orders, and specs.
- `collab/gemini/` — **you.** Execution reports, proposals, progress ledger.
- `collab/` (original build artifacts) — read-only for you except where a work order explicitly instructs a change (e.g. WO-5 PII purge, WO-10 doc corrections).
- `app/`, `Dockerfile`, `docker-compose.yml`, docs — via branches only, per the work orders.

## 6. Review Cycle

```
[Operator directive] → [Z.ai spec + work orders (review/)]
        → [You: execute on branch + report (collab/gemini/)]
        → [Z.ai independent re-audit (review/)]
        → [Operator acceptance]
```

If a work order cannot be completed as written, record why in your report and stop that branch — do not improvise silently, do not expand scope.
