# SPEC01 — Production-Grade Remediation of ai-gig-platform

- **Task ID:** SPEC01
- **Author:** Z.ai (Independent Reviewer / Architect)
- **Date:** 2026-11-20
- **Base Commit:** `afa012a8` (branch `main`)
- **Status / Verdict:** BINDING — DISPATCHED FOR EXECUTION
- **Executor:** Gemini / Antigravity (per `GEMINI.md` operating guidelines)
- **Amendments:** none (§7)

---

## 1. Goal & Scope

Bring `ai-gig-platform` from its audited state (**6 PASS / 6 PARTIAL / 8 FAIL**, see [REVIEWER_REPORT.md](REVIEWER_REPORT.md)) to production-grade for the Operator's stated goal: *discover India-eligible AI-training gigs fast, practice company-tailored interviews with genuine AI scoring, and generate application packs — with a deployment path that actually builds and documentation that tells the truth.*

Scope = the 15 work orders in [FIX_WORK_ORDERS.md](FIX_WORK_ORDERS.md), derived from audit findings F1–F22. Nothing else. No new features, no refactors beyond the named findings, no dependency upgrades beyond WO-13's pinning.

**Out of scope:** the Git history purge (WO-15) is spec'd but gated on an explicit Operator decision; the reviewer's `review/` folder; the original `collab/` artifacts except where a work order names them.

## 2. Binding Requirements

Each requirement is satisfied only when its work order's acceptance test passes with pasted evidence (§3). Line references are to the audited tree, byte-identical to `main` at dispatch.

| Req | Requirement (verifiable) | Source | Work Order | Gate |
|---|---|---|---|---|
| R-1 | Every interview evaluation carries a persisted `evaluation_source: "gemini"\|"heuristic"`; offline fallback is user-visible (banner + report-card label); Gemini calls use JSON response mode; no silent `except: pass` on the scoring path | F1 | WO-1 | G-1 |
| R-2 | The interview prompt contains the job description (≤2000 chars), category, tier, and the last 4 message pairs; no source-code literals leak into the prompt | F2 | WO-2 | G-2 |
| R-3 | Saving any subset of settings never changes fields the request omitted (`gemini_model: Optional[str] = None`) | F5 | WO-3 | G-3 |
| R-4 | `docker build` + `docker compose up` succeed from a fresh clone with no `data/` and no pre-existing `.env`; health check returns 200 | F4 | WO-4 | G-4 |
| R-5 | Zero personal-data hits in the working tree (grep acceptance in WO-5); contact info is profile-driven, not hardcoded | F3 | WO-5 | G-5 |
| R-6 | Docs, dropdown, and code agree on exactly one model story; no unverifiable model claims | F6 | WO-6 | G-6 |
| R-7 | India gate recognizes the listed major cities/states; unknown locations are flagged for review, not silently dropped | F7 | WO-7 | G-7 |
| R-8 | Resume-upload failures return 4xx and never persist error strings as resume text; filenames sanitized | F8, F14 | WO-8 | G-8 |
| R-9 | No invented compensation: unparsed pay renders "Not listed"; curated ranges labeled "estimate" | F10 | WO-9 | G-9 |
| R-10 | README/AGENTS/CHANGELOG claims match reality (platform counts, round count, links, launch paths) | F9, F11, F22 | WO-10 | G-10 |
| R-11 | CORS restricted to localhost origins; Gemini key sent via header, never URL query | F13, F15 | WO-11 | G-11 |
| R-12 | No fabricated scores: default-88 removed, missing rounds render "—", Markdown rendered safely in interview chat | F12, F16 | WO-12 | G-12 |
| R-13 | Dead code removed, acronym casing fixed, title bonus capped as documented, dependencies pinned | F18, F20, F21 | WO-13 | G-13 |
| R-14 | Test suite exists covering pay_parser, matcher, and the interview state machine; `pytest` green with 4-number receipt | report §6.14 | WO-14 | G-14 |
| R-15 | *(Operator-gated)* History purge of F3 PII via `git filter-repo`, coordinated, single execution | F3 | WO-15 | G-15 |

## 3. Verification & Evidence Protocol

1. **Acceptance receipts.** Each gate G-n passes only on raw, pasted command output (or screenshot where the acceptance test says so) recorded in `collab/gemini/SPEC01-WO-<N>-REPORT.md`. Summaries without receipts are void.
2. **Honest-judge pairs.** Any scoring/parsing logic touched must show one known-good (PASS) and one deliberately-wrong (FAIL) assertion.
3. **4-number test metric.** `files / test-cases / assertions / failures` for every test run reported (`n/r` where the runner does not report).
4. **Fresh-environment rule.** G-4 (Docker) must be executed from a fresh clone, not a warm working tree.
5. **No self-grading.** The executor does not close gates; the executor submits evidence. Z.ai re-runs the acceptance tests independently and records the verdict ledger in `review/SPEC01-AUDIT-LEDGER.md` (created at first audit).

## 4. Branch & Integration Protocol

Per `.agents/rules/branch-hygiene.md` (always-on) and `GEMINI.md` §1: zero code changes on `main`; one work order per branch (`<domain>/<slug>` names pre-assigned in FIX_WORK_ORDERS.md); atomic commits with conventional messages; `--no-ff` merges; branches retained permanently; force-push of `main` prohibited. Reports and ledger are doc-only and may land with the merge or directly on `main`.

## 5. Reporting & Audit Cycle

```
Operator dispatch (this SPEC) → Gemini executes WO-n on branch
  → report: collab/gemini/SPEC01-WO-<n>-REPORT.md (evidence pasted)
  → ledger:  collab/gemini/SPEC01-PROGRESS.md (WO | status | branch | sha | evidence)
  → Z.ai independent re-audit → verdict in review/SPEC01-AUDIT-LEDGER.md
  → Operator acceptance on the ledger
```

Execution order is fixed: **P0 batch (WO-1…5) → P1 batch (WO-6…10) → P2 batch (WO-11…14)**. WO-15 waits for the Operator.

## 6. Definition of Done

- All gates G-1…G-10 (P0+P1) verified PASS by Z.ai re-audit with reproduced receipts.
- G-11…G-14 verified PASS or explicitly waived by the Operator with reason.
- Updated verdict delta appended to `review/REVIEWER_REPORT.md` (reviewer-authored).
- A fresh clone passes: install → boot → scan → interview session with visible evaluation source → Docker build.

## 7. Change Control

This spec is binding. Amendments require a dated entry in the Amendments table above and co-sign-off (Z.ai + Operator). Executor deviations discovered mid-flight go into the WO report as a `DEVIATION` section and freeze that branch until adjudicated.

## 8. Reference Index

- Audit evidence: [REVIEWER_REPORT.md](REVIEWER_REPORT.md) (findings F1–F22, 20-check verdict table, file-by-file appendix)
- Execution tasks: [FIX_WORK_ORDERS.md](FIX_WORK_ORDERS.md) (15 WOs with acceptance tests, pre-assigned branch names)
- Governance: [`GEMINI.md`](../GEMINI.md) (executor guidelines) · [`.agents/rules/branch-hygiene.md`](../.agents/rules/branch-hygiene.md) (branch protocol)
