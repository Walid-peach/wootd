---
name: pr-create
description: Creates or updates reviewer-friendly pull requests for WOOTD and similar git projects. Use when opening a PR, updating an existing PR, preparing PR title/body text, reviewing branch scope before a PR, or when the user asks to prepare a pull request.
---

# PR Create

Prepare or update one pull request for the current branch. Optimize for reviewers: accurate scope, clear title, concise description, explicit testing, and visible risks.

## Workflow

1. Detect PR state.
   - Check the current branch.
   - Detect whether a PR already exists for the branch using available GitHub tooling.
   - If a PR exists, update that PR instead of creating a new one.
   - Suggest a separate PR only when the branch purpose changed substantially, the base branch is wrong, or the user explicitly asks.

2. Identify the base branch.
   - Prefer the existing PR base branch.
   - Otherwise use the repository default branch or the intended target branch.
   - Do not assume `master`; verify whether the repo uses `main`, `master`, or another base.

3. Review the branch before drafting.
   - Run `git diff --stat <base>...HEAD` for scope.
   - Run `git diff <base>...HEAD` and inspect the full change set.
   - Review recent commits when useful to understand intent.
   - Check `git status --short` for untracked or unstaged files that should be included or excluded.

4. Apply a scope quality bar.
   - Confirm the branch has one coherent purpose.
   - Flag unrelated changes, debug code, temporary comments, generated noise, accidental edits, or broad mixed work.
   - Decide whether tests, docs, config updates, migrations, screenshots, or changelog notes are needed.
   - If the branch is too broad, recommend splitting before creating or heavily revising a PR.

5. Use WOOTD context when relevant.
   - Mention the current phase when it helps reviewers, for example `Phase 0 foundations`, `Phase 1 bronze ingestion`, or `Phase 3 API rule engine`.
   - For Phase 0, emphasize scaffolding, local setup, CI, `.env.example`, Docker Compose, tooling, and smoke tests.
   - For data changes, call out whether `make dbt-test` is applicable. If dbt models are still stubs, say that explicitly.
   - For API/data/web changes, prefer this validation set when applicable: `make lint`, `make test`, `cd web && npm run check`, `docker compose config`, and `make dev` if Docker and secrets are available.
   - Add a CI-readiness pass when workflows, setup, tooling, lockfiles, generated files, packaging, or tests changed.
   - Mention account/secrets work separately from code changes; do not imply secrets or hosted infrastructure are complete unless verified.

6. Run CI-readiness checks before creating the PR.
   - Inspect `.github/workflows/**` when CI config exists or setup/tooling changed.
   - Confirm files referenced by CI are committed and not ignored:
     - Lockfiles such as `uv.lock` and `package-lock.json`.
     - Generated type files such as `web/src/env.d.ts` when CI expects them.
     - Config files referenced by workflow cache keys.
   - If using `astral-sh/setup-uv`, do not pass `python-version`; use `actions/setup-python` separately.
   - If `setup-uv` cache is enabled, verify `uv.lock` exists in the repo or configure `cache-dependency-glob` to match a committed file.
   - Check for duplicate Python package names in test folders, especially multiple `tests/__init__.py` packages.
   - After local validation, mention whether GitHub Actions was observed green, pending, not yet run, or not checked.

7. Prepare a title.
   - Use a clear, action-oriented title.
   - Prefer `<area>: <change>`.
   - Examples for WOOTD:
     - `phase-0: harden local setup and smoke tests`
     - `data: add typed bronze ingestion helpers`
     - `api: add rule-engine recommendation smoke tests`
   - Avoid vague titles like `updates`, `fixes`, or `changes`.

8. Draft the PR description in `notes/pr_<sanitized-branch-name>.md`.
   - Replace `/` with `_`.
   - Lowercase the name.
   - Keep it concise and filesystem-safe.
   - Create `notes/` if it is missing.
   - Do not commit `notes/` unless the repository intentionally tracks PR notes.

9. Use this PR description structure:

```markdown
## What
One or two sentences describing what this PR changes.

## Why
Explain the problem, context, or reason the change is needed.

## Changes
- Group related changes together.
- Summarize meaningful implementation changes.
- Mention deleted, renamed, generated, or moved files when relevant.
- Focus on reviewer-relevant changes, not raw diff noise.

## Testing
- List automated tests run.
- List manual validation steps.
- If something could not be tested, say why.

## Risks / Notes
- Mention rollout concerns, edge cases, follow-ups, or reviewer attention points.

## Breaking Changes
None, or explain the impact clearly.
```

10. Update an existing PR carefully.
   - Read the existing PR title and description first.
   - Compare them with the current diff.
   - Update only inaccurate or missing parts.
   - Preserve useful reviewer context that remains true.
   - Do not rewrite a good description unnecessarily.

11. Check docs only when justified.
   - Update `README.md` only if setup, usage, config, examples, or user-facing behavior changed.
   - Update `AGENTS.md` or `CLAUDE.md` only if repo instructions, workflow rules, or agent guidance changed.
   - Do not add docs churn just to make a PR look larger.

12. Create or update the PR when asked.
   - Prefer the available GitHub connector/app for PR metadata and mutations.
   - If using GitHub CLI or git remotes, verify the repo and branch before pushing or creating a PR.
   - Never invent a PR URL. Report only URLs returned by the tool.

## Final Response

Return:
- Proposed or updated PR title.
- Path to the saved PR description.
- Short reviewer summary: what to review first and any known risks.
- Validation commands and results.
- PR URL if a PR was actually created or updated.
