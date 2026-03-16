#!/bin/sh
set -eu

# generate-docs.sh — Build symbol graph documentation via xcodebuild docbuild
# Usage: generate-docs.sh [scheme]
#
# Outputs JSON-structured results per step for consumption by Claude Code commands.

SCHEME="${1:-}"

# --- Helpers ---
json_result() {
  printf '{"step":"%s","status":"%s","output":%s}\n' "$1" "$2" "$3"
}

escape_json() {
  python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))"
}

# --- Step 1: Preflight ---
if ! command -v xcodebuild >/dev/null 2>&1; then
  json_result "preflight" "error" '"xcodebuild not found. Install Xcode Command Line Tools: xcode-select --install"'
  exit 1
fi

# Find workspace or project
WORKSPACE=""
PROJECT=""
ws_match=$(ls -d *.xcworkspace 2>/dev/null | head -1)
proj_match=$(ls -d *.xcodeproj 2>/dev/null | head -1)
if [ -n "$ws_match" ]; then
  WORKSPACE="$ws_match"
  json_result "preflight" "ok" "$(echo "Found $WORKSPACE" | escape_json)"
elif [ -n "$proj_match" ]; then
  PROJECT="$proj_match"
  json_result "preflight" "ok" "$(echo "Found $PROJECT" | escape_json)"
else
  json_result "preflight" "error" '"No .xcworkspace or .xcodeproj found in current directory"'
  exit 1
fi

# --- Step 2: Scheme discovery ---
if [ -z "$SCHEME" ]; then
  list_json=$(xcodebuild -list -json 2>/dev/null) || {
    json_result "scheme" "error" '"Failed to list schemes. Is this a valid Xcode project?"'
    exit 1
  }

  # Extract schemes from JSON
  schemes=$(echo "$list_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
key = 'workspace' if 'workspace' in data else 'project'
schemes = data[key].get('schemes', [])
for s in schemes:
    print(s)
")

  scheme_count=$(echo "$schemes" | grep -c . || true)

  if [ "$scheme_count" -eq 0 ]; then
    json_result "scheme" "error" '"No schemes found in project"'
    exit 1
  elif [ "$scheme_count" -eq 1 ]; then
    SCHEME=$(echo "$schemes" | head -1)
  else
    json_result "scheme" "error" "$(echo "Multiple schemes found. Specify one: $schemes" | escape_json)"
    exit 1
  fi
fi

json_result "scheme" "ok" "$(echo "$SCHEME" | escape_json)"

# --- Step 3: Docbuild ---
BUILD_DIR=".build/docs"

if [ -n "$WORKSPACE" ]; then
  build_output=$(xcodebuild docbuild -workspace "$WORKSPACE" -scheme "$SCHEME" -derivedDataPath "$BUILD_DIR" -quiet 2>&1) || {
    json_result "docbuild" "error" "$(echo "$build_output" | tail -50 | escape_json)"
    exit 1
  }
else
  build_output=$(xcodebuild docbuild -project "$PROJECT" -scheme "$SCHEME" -derivedDataPath "$BUILD_DIR" -quiet 2>&1) || {
    json_result "docbuild" "error" "$(echo "$build_output" | tail -50 | escape_json)"
    exit 1
  }
fi

json_result "docbuild" "ok" '"Build succeeded"'

# --- Step 4: Extract symbol graphs to staging dir ---
STAGING_DIR=".build/symbol-graphs-raw"
mkdir -p "$STAGING_DIR"

# Use a temp file to track seen names (POSIX-compatible, no associative arrays)
seen_file=$(mktemp)
trap 'rm -f "$seen_file"' EXIT

find "$BUILD_DIR" -name "*.symbols.json" -type f 2>/dev/null | while IFS= read -r sg_file; do
  bname=$(basename "$sg_file")

  # Handle name collisions with numeric suffix
  if grep -qx "$bname" "$seen_file" 2>/dev/null; then
    counter=$(grep -c "^${bname}$" "$seen_file")
    dest_name="${bname%.symbols.json}.symbols.${counter}.json"
  else
    dest_name="$bname"
  fi

  echo "$bname" >> "$seen_file"
  cp "$sg_file" "$STAGING_DIR/$dest_name"
done

file_count=$(find "$STAGING_DIR" -name "*.symbols.json" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$file_count" -eq 0 ]; then
  json_result "extract" "warning" '"No symbol graph files found. Targets may lack public API or doc comments."'
  rm -rf "$BUILD_DIR" "$STAGING_DIR"
  exit 0
fi

json_result "extract" "ok" "$(echo "Extracted $file_count symbol graphs" | escape_json)"

# --- Step 5: Transform to structured CSVs ---
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
OUTPUT_DIR=".build/api-docs"

transform_output=$(python3 "$SCRIPT_DIR/generate-docs-transform.py" "$STAGING_DIR" "$OUTPUT_DIR" 2>&1) || {
  json_result "transform" "error" "$(echo "$transform_output" | escape_json)"
  rm -rf "$BUILD_DIR" "$STAGING_DIR"
  exit 1
}

json_result "transform" "ok" "$(echo "Generated api-surface.md, types.csv, methods.csv, relationships.csv" | escape_json)"

# --- Step 6: Cleanup ---
rm -rf "$BUILD_DIR" "$STAGING_DIR"

# --- Step 7: Summary ---
json_result "summary" "done" "$transform_output"
