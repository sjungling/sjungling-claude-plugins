#!/bin/bash
set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PRICING_FILE="$PLUGIN_ROOT/pricing.json"

# Read hook input from stdin into a temp file (stdin may contain control chars that break echo)
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
cat > "$tmpfile"

# Bail out gracefully if input isn't valid JSON
if ! jq empty "$tmpfile" 2>/dev/null; then
  exit 0
fi

tool_name=$(jq -r '.tool_name // "unknown"' "$tmpfile")

# Get character lengths of input and result
input_chars=$(jq -r '.tool_input // "" | tostring | length' "$tmpfile")
result_chars=$(jq -r '.tool_response // "" | tostring | length' "$tmpfile")

# Estimate tokens (~4 chars per token is a rough heuristic)
input_tokens=$(( input_chars / 4 ))
output_tokens=$(( result_chars / 4 ))
total_tokens=$(( input_tokens + output_tokens ))

# Resolve model: env var set by SessionStart hook, or fall back to pricing.json default
model="${TOKEN_TRACKER_MODEL:-}"

if [ -z "$model" ] && [ -f "$PRICING_FILE" ]; then
  model=$(jq -r '.default' "$PRICING_FILE")
fi

# Look up pricing from pricing.json
if [ -f "$PRICING_FILE" ] && jq -e ".models[\"$model\"]" "$PRICING_FILE" > /dev/null 2>&1; then
  model_label=$(jq -r ".models[\"$model\"].label" "$PRICING_FILE")
  input_cost_per_m=$(jq -r ".models[\"$model\"].input_per_mtok" "$PRICING_FILE")
  output_cost_per_m=$(jq -r ".models[\"$model\"].output_per_mtok" "$PRICING_FILE")
else
  # Fallback if pricing.json missing or model not found
  model_label="${model:-unknown}"
  input_cost_per_m=15.00
  output_cost_per_m=75.00
fi

# Calculate cost in dollars
cost=$(awk "BEGIN {
  input_cost = ($input_tokens / 1000000) * $input_cost_per_m
  output_cost = ($output_tokens / 1000000) * $output_cost_per_m
  total = input_cost + output_cost
  printf \"%.6f\", total
}")

# Format cost for display
cost_display=$(awk "BEGIN {
  c = $cost
  if (c < 0.001) printf \"<\$0.001\"
  else if (c < 0.01) printf \"\$%.4f\", c
  else printf \"\$%.3f\", c
}")

# Format token counts with commas
format_num() {
  printf "%'d" "$1" 2>/dev/null || printf "%d" "$1"
}

message="Token estimate for $tool_name [$model_label]: ~$(format_num $input_tokens) in / ~$(format_num $output_tokens) out ($(format_num $total_tokens) total) | Cost: $cost_display"

# Output as JSON with systemMessage so it appears in the conversation
jq -n --arg msg "$message" '{"systemMessage": $msg}'
