---
name: token-efficiency
description: Minimize token use in every session (chat, terminal, code) without lowering work quality. Applies always — load at session start and before any multi-step task, file exploration, search, tool use, or long reply.
---

# Token Efficiency

Goal: fewest input + output tokens for the same correct result. Never trade correctness, verification, or completeness of the deliverable for brevity.

## Output (what you write)
- Answer first. No greetings, preambles, restating the question, or closing offers.
- Bullets/tables over prose. One line per fact.
- Report conclusions, not process. No "I'll now…", "Let me…", step narration.
- Never echo tool output, logs, or file contents back. Cite `path:line` instead.
- Show diffs/changed lines only, never whole files the user already has.
- Status reports: Status · ID · URL. Omit timings, SHAs, duplicate links unless asked.
- One recommendation, not a survey of options. Skip caveats that don't change the decision.
- Code comments only where logic is non-obvious; match surrounding density.

## Input (what you read)
- Search before reading: `Grep`/`Glob` to locate, then `Read` with `offset`/`limit` on the relevant range only.
- Never re-read a file you just wrote/edited or already have in context.
- Pipe noisy commands: `| tail -n 40`, `| head`, `grep -E 'error|fail'`, `--quiet`, `-q`, `--no-pager`, `--oneline`, `--stat`.
- Prefer machine-readable minimal flags: `git status -sb`, `git diff --stat`, `ls -1`, `wc -l`, `jq '.field'`.
- Skip binaries, lockfiles, generated/minified/vendor dirs (`node_modules`, `dist`, `build`, `*.min.js`) unless the task targets them.
- MCP/API calls: request minimal fields, small page sizes (`minimal_output: true`, `limit`, `fields=`).
- Delegate broad multi-file exploration to a subagent (`Explore`) so only its summary enters context.

## Tool calls
- Batch independent calls in one turn (parallel reads, searches, commands).
- Chain dependent shell steps with `&&` in one call instead of several round trips.
- Use `Edit` (diff) over `Write` (full file) for changes to existing files.
- Don't load skills, docs, or tool schemas that the task doesn't need.
- Act when you have enough information; don't re-derive established facts or re-verify what a tool already confirmed.

## Quality guardrails (never cut)
- Still run tests/lint/build that prove the change works; just filter their output.
- Still read enough code to understand the change's blast radius.
- Still state errors, failures, and skipped steps explicitly.
- If brevity would make an answer ambiguous, add the minimum words to remove the ambiguity.
