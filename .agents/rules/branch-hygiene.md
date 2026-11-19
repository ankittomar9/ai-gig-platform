---
description: Mandatory strict branch hygiene rules for all code changes in ai-gig-platform
globs: ["**/*"]
always_on: true
---

# ai-gig-platform Branch Hygiene & Development Protocol

> Adopted from the GateLMS protocol (`.agents/rules/branch-hygiene.md`, guardrail G9).
> This repo's trunk is **`main`** (there is no `master`; the stale `master` branch was removed 2026-11-20).

## ZERO CODE CHANGES ON MAIN
Under no circumstances may any code change, bug fix, or refactor be made while checked out on `main`.

### Mandatory Workflow
1. **Branch First:** Cut a dedicated branch from `origin/main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b <domain>/<name>
   ```
2. **Branch Naming Standard:**
   - Features / work packages: `<domain>/<feature-slug>` (e.g. `interview/job-aware-prompts-1`)
   - Bug fixes: `<domain>/<bug-slug>-fix` (e.g. `settings/model-reset-fix`)
   - Sequential fixups: `<domain>/<feature-slug>-fixup-<N>` where `<N>` = 1, 2, 3... 10... 100 (e.g. `interview/scoring-honesty-fixup-1`)
   - SPEC01 work orders use the branch names pre-assigned in `review/FIX_WORK_ORDERS.md`.
3. **Commit & Push Branch:**
   - Commit changes atomically on the branch with conventional commit messages.
   - Always push the branch to remote: `git push -u origin <branch-name>` so the diff is immediately inspectable.
4. **Merge to Main via `--no-ff`:**
   ```bash
   git checkout main
   git merge --no-ff <branch-name> -m "merge(<scope>): <description>"
   git push origin main
   ```
5. **Never Delete Branches:**
   - Keep all branches permanently, locally and on GitHub. Never run branch deletion commands.
6. **Never Force-Push Main:**
   - `--force-with-lease` is allowed ONLY on your own unmerged feature branch. Force-pushing `main` is completely prohibited.
   - *Incident record: this repo's history was force-pushed and rewritten on 2026-11-19/20 between audit pushes. The audited tree survived byte-identical only by luck. Do not repeat it.*
7. **Doc-only exception:** Documentation changes strictly inside `review/**`, `collab/**`, or root governance docs (`AGENTS.md`, `GEMINI.md`, `README.md`) may land directly on `main`. All code changes must follow the branch workflow.
