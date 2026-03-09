#!/bin/bash
set -euo pipefail

# SessionStart hook: capture the active model and persist it for later hooks
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
cat > "$tmpfile"

model=$(jq -r '.model // empty' "$tmpfile")

if [ -n "$model" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export TOKEN_TRACKER_MODEL=\"$model\"" >> "$CLAUDE_ENV_FILE"
fi
