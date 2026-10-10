---
name: lean-code
description: Token-lean workflow for coding tasks (debugging, features, refactors, reviews, CI fixes). Use with token-efficiency whenever code is read, written, built, or tested.
---

# Lean Code Workflow

## Locate
1. `Grep` for the symbol/error string → `files_with_matches` mode first, then `content` with `-n` and small `-C`.
2. `Read` only the matched range (`offset`/`limit`). Expand only if the range is insufficient.
3. For unfamiliar repos: read `README`/`CLAUDE.md`/manifest (`package.json`, `pyproject.toml`) once; skip the rest until needed.

## Change
- Smallest diff that fully solves the task. No drive-by refactors, renames, or reformatting.
- `Edit` with tight unique `old_string`; `replace_all` for repeated renames.
- No new files unless required; no docs/README updates unless asked.

## Verify (filtered, never skipped)
- Run only the affected tests: `pytest path::test -q`, `npm test -- path`, `go test ./pkg/...`.
- Filter output: `2>&1 | tail -n 30` or `| grep -E 'FAIL|Error|error:'`.
- Builds/lint: `--quiet`/`-s`; show only failures.
- Re-run once after a fix; don't re-run passing suites.

## Git
- `git status -sb`, `git diff --stat`, `git log --oneline -5`.
- Inspect a specific hunk with `git diff -- path` only when needed.

## Report
- Changed: `path:line` — one-line what/why.
- Verified: command → pass/fail.
- Open issues: only if any.
