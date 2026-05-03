---
name: pr-review-fix
description: Applies narrow fixes to a pull request based on existing PR review feedback. Use when the user asks to address PR review comments, fix a PR from review feedback, resolve Must Fix or Should Fix items, or update a branch based on reviewer feedback.
---

# PR Review Fix

Apply only the fixes requested by PR review feedback. Keep the branch narrow, review-driven, and aligned with the original PR purpose.

## Workflow

1. Start from the actual review feedback.
   - Read the PR review comment, review thread, or user-provided feedback carefully before editing.
   - Extract only explicit requested fixes.
   - If there is no review comment or no clear fix request, stop and ask for the PR comment or a clear list of fixes.
   - If using GitHub tooling, prefer unresolved review threads and requested-changes reviews over general discussion.

2. Determine what is in scope.
   - Always address explicit `Must Fix` items.
   - Address explicit `Should Fix` items unless the user says otherwise.
   - Ignore `Nice to Have` items unless the user explicitly asks for them.
   - Do not implement optional cleanup, refactors, polish, or adjacent improvements just because they seem useful.

3. Preserve PR scope.
   - Understand the original PR purpose from the diff, PR title/description, and relevant files.
   - Inspect only the files needed to implement the requested fixes.
   - Avoid changing behavior outside the review feedback.
   - Do not broaden the PR beyond its current phase or objective.

4. Apply targeted fixes.
   - Make the smallest useful changes that fully resolve the requested feedback.
   - Prefer local edits over broad rewrites.
   - Maintain existing project patterns, typing, formatting, and test style.
   - Do not revert unrelated user changes.

5. Apply WOOTD-specific validation when relevant.
   - For Python/API/data fixes, run `make lint` and `make test` when feasible.
   - For web fixes, run `cd web && npm run check` and formatting checks when relevant.
   - For Docker/local setup fixes, run `docker compose config`; run `make dev` only when Docker and needed env values are available.
   - For dbt/pipeline fixes, run `make dbt-test` or state clearly if dbt models/tests are still stubs.
   - If validation cannot run because of missing secrets, unavailable Docker, or external services, say so explicitly.

6. Update PR metadata or docs only when justified.
   - Update the PR description only if the fixes materially change the PR summary, testing, or risks.
   - Update `README.md` only if setup, usage, configuration, examples, or user-facing behavior changed.
   - Update `AGENTS.md` or `CLAUDE.md` only if repo workflow or agent guidance changed.
   - Do not add docs churn for unrelated reasons.

7. Confirm each requested fix.
   - Re-read the original feedback after editing.
   - Map each `Must Fix` and `Should Fix` item to a concrete change or a clear explanation for why it was not fixed.
   - Leave `Nice to Have` items untouched unless explicitly requested.

## Summary Format

Use this structure when reporting back:

```markdown
## Fixed
- List all Must Fix items addressed.
- List all Should Fix items addressed.

## Not Fixed
- List any requested item that could not be implemented and why.
- Write `None` if everything in scope was addressed.

## Validation
- List tests, checks, or manual validation performed.
- If none, state that explicitly.

## Notes
- Mention whether the PR description or docs were updated.
- Mention follow-up the reviewer or author should know.
- Write `None` if there is nothing extra to note.
```

## Stop Conditions

Stop and ask for clarification when:
- No PR review comment, review thread, or clear list of fixes is available.
- The feedback is ambiguous enough that a reasonable implementation would be risky.
- A requested Must Fix appears incorrect, unsafe, or impossible.
- Fixing the feedback would require broad unrelated work or splitting the PR.

## Final Behavior

Read the review feedback, fix all explicit Must Fix items, fix all explicit Should Fix items, ignore Nice to Have items unless requested, validate the result, and summarize exactly what changed.
