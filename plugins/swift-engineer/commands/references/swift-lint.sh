#!/usr/bin/env bash
set -euo pipefail

# swift-lint.sh — Format and lint Swift code, optionally run Periphery
# Usage: swift-lint.sh [path] [--periphery] [--format-only] [--lint-only]
#
# Outputs JSON-structured results per step for consumption by Claude Code commands.

TARGET="${1:-.}"
RUN_PERIPHERY=false
FORMAT_ONLY=false
LINT_ONLY=false

# Parse flags (can appear anywhere after target)
shift || true
for arg in "$@"; do
  case "$arg" in
    --periphery)    RUN_PERIPHERY=true ;;
    --format-only)  FORMAT_ONLY=true ;;
    --lint-only)    LINT_ONLY=true ;;
  esac
done

# --- Helpers ---
json_result() {
  local step="$1" status="$2" output="$3"
  printf '{"step":"%s","status":"%s","output":%s}\n' "$step" "$status" "$output"
}

escape_json() {
  python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))"
}

# --- Check tools ---
if ! command -v swift-format &>/dev/null; then
  json_result "preflight" "error" '"swift-format not found. Install via: brew install swift-format"'
  exit 1
fi

# --- Step 1: Periphery (optional) ---
if [[ "$RUN_PERIPHERY" == true ]]; then
  if ! command -v periphery &>/dev/null; then
    json_result "periphery" "skipped" '"periphery not installed"'
  elif [[ ! -f ".periphery.yml" ]] && ! compgen -G "*.xcodeproj" &>/dev/null && ! compgen -G "*.xcworkspace" &>/dev/null; then
    json_result "periphery" "skipped" '"no .periphery.yml or Xcode project found"'
  else
    periphery_output=$(periphery scan 2>&1 | tail -100) || true
    json_result "periphery" "done" "$(echo "$periphery_output" | escape_json)"
  fi
fi

# --- Step 2: Format ---
if [[ "$LINT_ONLY" != true ]]; then
  format_output=$(swift-format format --in-place --recursive "$TARGET" 2>&1) || true
  json_result "format" "done" "$(echo "$format_output" | escape_json)"
fi

# --- Step 3: Lint ---
if [[ "$FORMAT_ONLY" != true ]]; then
  lint_output=$(swift-format lint --recursive "$TARGET" 2>&1) || true
  lint_exit=${PIPESTATUS[0]:-$?}

  if [[ -z "$lint_output" ]]; then
    json_result "lint" "clean" '""'
  else
    json_result "lint" "issues" "$(echo "$lint_output" | escape_json)"
  fi
fi
