# collab/gemini/ — Executor Workspace (Gemini / Antigravity)

**Owner:** Gemini / Antigravity (executor agent). Only the executor writes here.

## Purpose
- `SPEC01-WO-<N>-REPORT.md` — one report per work order, acceptance evidence pasted verbatim.
- `SPEC01-PROGRESS.md` — running ledger: `WO | status | branch | commit sha | evidence pointer`.
- Fixup reports: `SPEC01-WO-<N>-FIXUP-<M>-REPORT.md`.

## Standard artifact header (mandatory)
```markdown
# [TASK-ID] [Title]
- **Author:** Gemini / Antigravity
- **Date:** [YYYY-MM-DD]
- **Base Commit:** [short sha]
- **Verdict:** [EXECUTED | DEVIATION | BLOCKED]
```

## Rules
1. Evidence is pasted raw output — summaries are void (see `GEMINI.md` §2).
2. Never place secrets or personal data in reports (scan before commit).
3. Never modify `review/` or other agents' folders.
