# Session rules

Token efficiency is mandatory in every session. Follow `.claude/skills/token-efficiency/SKILL.md` always, and `.claude/skills/lean-code/SKILL.md` for any coding task. Core rules:

- Answer first; bullets over prose; no filler, narration, or recaps.
- Never echo tool output or file contents; cite `path:line`.
- Grep/Glob before Read; read ranges, not whole files; never re-read edited files.
- Filter command output (`tail`, `grep`, `-q`); batch independent tool calls.
- Edit over Write; smallest correct diff.
- Never skip verification or hide failures to save tokens.
