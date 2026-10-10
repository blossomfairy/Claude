#!/usr/bin/env bash
# Install this repo's token-efficiency skills and rules into ~/.claude so they apply to every Claude Code session.
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$dest/skills"
cp -r "$src/.claude/skills/token-efficiency" "$src/.claude/skills/lean-code" "$dest/skills/"
marker="<!-- token-efficiency-rules -->"
if ! grep -qF "$marker" "$dest/CLAUDE.md" 2>/dev/null; then
  { echo; echo "$marker"; sed 's#`\.claude/skills/#`~/.claude/skills/#g' "$src/CLAUDE.md"; } >> "$dest/CLAUDE.md"
fi
echo "Installed to $dest"
