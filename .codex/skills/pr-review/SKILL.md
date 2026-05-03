---
name: pr-review
description: Reviews a branch or pull request like a careful reviewer before or during code review. Use when the user asks for a PR review, review readiness check, pre-merge review, or feedback before merging.
---

# PR Review

Review one branch or pull request with a reviewer-first lens. Prioritize correctness, scope, safety, testing, and reviewer clarity over style nits.

## Workflow

1. Identify the review target.
   - Prefer an existing PR for the current branch when one exists.
   - Otherwise review the current branch against the intended base branch.
   - Use the PR base branch or repository default branch when available.
   - Do not assume the base branch is always `master`.

2. Review the actual change set.
   - Run `git diff --stat <base>...HEAD` for a high-level summary.
   - Run `git diff <base>...HEAD` for the full changes.
   - Review recent commits when they clarify intent or change history.
   - Check `git status --short` for unstaged, untracked, accidental, or generated files.

3. Understand the purpose before judging details.
   - Infer the main objective from the diff, PR title, PR description, commits, and project context.
   - Identify whether the implementation matches the stated or implied goal.
   - If the scope is unclear, say so explicitly.

4. Apply WOOTD context when relevant.
   - For Phase 0 changes, check local setup, `.env.example`, Docker Compose, CI, lockfiles, tooling, and smoke tests.
   - For Phase 1 ingestion changes, check provider contracts, typed parsing, R2 bronze paths, retry/backoff, fixtures, and no live network calls in CI.
   - For Phase 2 dbt changes, check seeds, canonical silver schema, dedup keys, gold outputs, and dbt tests.
   - For Phase 3 API/rule-engine changes, check request/response shape, no live R2 calls in tests, Supabase migration alignment, and explicit rule thresholds.
   - For web changes, check whether UI behavior and setup commands changed, and whether `cd web && npm run check` is relevant.
   - Do not imply hosted accounts, secrets, deployed services, or scheduled workflows are ready unless verified.

5. Evaluate the PR.
   - Correctness: Does the implementation solve the intended problem? Are there logic errors, broken assumptions, incomplete paths, or runtime failures?
   - Scope: Is the PR focused on one coherent purpose? Are unrelated changes mixed in?
   - Readability: Is the code understandable and consistent with existing patterns?
   - Maintainability: Does it avoid unnecessary complexity, brittle logic, duplicated patterns, and unexplained hardcoding?
   - Safety: Are migration, deployment, rollback, data, secrets, config, or operational risks handled?
   - Testing: Are tests present where needed? Are automated and manual validation steps enough?
   - Documentation: Should `README.md`, docs, `AGENTS.md`, or `CLAUDE.md` change because setup, usage, config, or workflow changed?

6. Distinguish severity.
   - Must Fix: likely bug, broken behavior, unsafe change, serious missing validation, or serious merge blocker.
   - Should Fix: important quality, maintainability, clarity, or coverage issue that should ideally be addressed before merge.
   - Nice to Have: non-blocking cleanup, follow-up, or polish.

7. Stay precise and evidence-based.
   - Reference concrete files, functions, config, commands, or behaviors.
   - Explain why something is risky, confusing, or incorrect.
   - Avoid vague comments like “this looks bad” or “maybe improve this”.
   - Avoid low-value style comments unless they affect readability or violate project conventions.

8. Check PR title and description when available.
   - Compare the PR description against the actual diff.
   - Call out mismatches, missing important changes, inaccurate testing claims, or stale risk notes.
   - Suggest title or description updates when they would help reviewers.

9. Flag messy or mixed branches.
   - Recommend splitting unrelated work.
   - Call out accidental edits, debug code, commented-out code, temporary files, local notes, generated noise, or unrelated lockfile churn.

## Review Format

Use this exact structure:

```markdown
## Summary
Two to four sentences summarizing what the PR does and the overall review outcome.

## Must Fix
- Blocking issues that should be resolved before merge.
- State `None` if there are no blocking issues.

## Should Fix
- Important non-blocking improvements.
- State `None` if there are no important improvements.

## Nice to Have
- Optional improvements or follow-ups.
- State `None` if there are no optional suggestions.

## Testing / Validation Gaps
- Missing or weak validation.
- State `None` if validation looks sufficient.

## Documentation / Reviewer Notes
- Needed docs changes, rollout notes, or areas reviewers should pay attention to.
- State `None` if nothing special is needed.

## Verdict
One of:
- Ready to merge
- Ready with minor changes
- Needs changes before merge
- Scope should be reduced or split
```

## Posting The Review

If the user asks to post the review, post it directly to the PR after generating the structured review.

Prefer available GitHub app tooling:
- Use `mcp__codex_apps__github._add_review_to_pr` with `action: "COMMENT"`, the PR number, repo full name, and the structured review body.

Fallbacks:
- If the GitHub app is unavailable, use `gh pr review <number> --comment -b <review-file>`.
- If neither posting path is available, return the review body and explain that posting was not possible.

Do not invent a PR URL, PR number, or posting result.

## Final Response

Return:
- Whether the review was posted or only drafted.
- The structured review body or a concise summary if it was posted.
- Any validation commands run and their results.
- The verdict.
