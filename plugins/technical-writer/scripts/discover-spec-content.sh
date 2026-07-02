#!/usr/bin/env bash
# discover-spec-content.sh
#
# Discovers the best content source for saving a spec/design doc to Obsidian
# from the current Claude Code session. Outputs JSON to stdout.
#
# Adapted from the workflow plugin's discover-issue-content.sh, stripped of
# GitHub-specific bits (no gh, no label/repo detection) — this command has no
# explicit-file argument slot (its two positional args are vault and topic),
# so the waterfall starts at superpowers specs/plans.
#
# Output JSON shape:
#   {
#     "source": "superpowers" | "claude-plan" | "summary",
#     "primary": "/path/to/file.md" | "",
#     "secondary": "/path/to/file.md" | "",
#     "candidates": { "specs": [...], "plans": [...] }
#   }
#
# Exit codes:
#   0 — success (check "source" field for what was found)
#   1 — not in a git repo

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"

# --- Helpers ---

json_output() {
  local source="$1" primary="$2" secondary="${3:-}" specs_json="${4:-[]}" plans_json="${5:-[]}"
  jq -n \
    --arg source "$source" \
    --arg primary "$primary" \
    --arg secondary "$secondary" \
    --argjson specs "$specs_json" \
    --argjson plans "$plans_json" \
    '{
      source: $source,
      primary: $primary,
      secondary: $secondary,
      candidates: { specs: $specs, plans: $plans }
    }'
}

# Collect file paths into a JSON array
files_to_json_array() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    local files
    files=$(find "$dir" -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort -r)
    if [[ -n "$files" ]]; then
      echo "$files" | jq -R . | jq -s .
      return
    fi
  fi
  echo "[]"
}

# --- Pre-checks ---

if ! command -v jq &>/dev/null; then
  echo '{"error": "jq not installed"}' >&2
  exit 1
fi

if [[ -z "$REPO_ROOT" ]]; then
  echo '{"error": "not in a git repository"}' >&2
  exit 1
fi

# --- Waterfall ---

# 1. Superpowers specs/plans
SPECS_DIR="$REPO_ROOT/docs/superpowers/specs"
PLANS_DIR="$REPO_ROOT/docs/superpowers/plans"

SPECS_JSON=$(files_to_json_array "$SPECS_DIR")
PLANS_JSON=$(files_to_json_array "$PLANS_DIR")

SPEC_COUNT=$(echo "$SPECS_JSON" | jq 'length')
PLAN_COUNT=$(echo "$PLANS_JSON" | jq 'length')

if [[ "$SPEC_COUNT" -gt 0 || "$PLAN_COUNT" -gt 0 ]]; then
  PRIMARY=""
  SECONDARY=""

  if [[ "$SPEC_COUNT" -eq 1 ]]; then
    PRIMARY=$(echo "$SPECS_JSON" | jq -r '.[0]')
  elif [[ "$SPEC_COUNT" -gt 1 ]]; then
    # Multiple specs — leave primary empty, let caller disambiguate from candidates
    PRIMARY=""
  fi

  if [[ "$PLAN_COUNT" -ge 1 && -n "$PRIMARY" ]]; then
    # Spec is primary, most recent plan is secondary
    SECONDARY=$(echo "$PLANS_JSON" | jq -r '.[0]')
  elif [[ "$SPEC_COUNT" -eq 0 && "$PLAN_COUNT" -eq 1 ]]; then
    # No specs, single plan is primary
    PRIMARY=$(echo "$PLANS_JSON" | jq -r '.[0]')
  elif [[ "$SPEC_COUNT" -eq 0 && "$PLAN_COUNT" -gt 1 ]]; then
    # No specs, multiple plans — let caller disambiguate
    PRIMARY=""
  fi

  json_output "superpowers" "$PRIMARY" "$SECONDARY" "$SPECS_JSON" "$PLANS_JSON"
  exit 0
fi

# 2. Claude plan file via session metadata
#
# $PPID inside a script points to the intermediate shell, not Claude Code.
# Instead, find the session file matching the current working directory by
# scanning all active session files.
CLAUDE_DIR="$HOME/.claude"
CURRENT_CWD="$(pwd)"
SESSION_ID=""

for sf in "$CLAUDE_DIR/sessions/"*.json; do
  [[ -f "$sf" ]] || continue
  sf_cwd=$(jq -r '.cwd // empty' "$sf" 2>/dev/null || echo "")
  if [[ "$sf_cwd" == "$CURRENT_CWD" ]]; then
    SESSION_ID=$(jq -r '.sessionId // empty' "$sf" 2>/dev/null || echo "")
    break
  fi
done

if [[ -n "$SESSION_ID" ]]; then
  ENCODED_CWD=$(echo "$CURRENT_CWD" | tr '/.' '-')
  JSONL="$CLAUDE_DIR/projects/${ENCODED_CWD}/${SESSION_ID}.jsonl"

  if [[ -f "$JSONL" ]]; then
    SLUG=$(grep -o '"slug":"[^"]*"' "$JSONL" 2>/dev/null | head -1 | cut -d'"' -f4 || echo "")

    if [[ -n "$SLUG" ]]; then
      PLAN_FILE="$CLAUDE_DIR/plans/${SLUG}.md"

      if [[ -s "$PLAN_FILE" ]]; then
        json_output "claude-plan" "$PLAN_FILE" "" "[]" "[]"
        exit 0
      fi
    fi
  fi
fi

# 3. Nothing found — caller should generate a summary
json_output "summary" "" "" "[]" "[]"
exit 0
