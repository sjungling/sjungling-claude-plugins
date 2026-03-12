#!/bin/bash
set -euo pipefail

# Syncs pricing data from litellm's model_prices_and_context_window.json
# and generates pricing.json with Anthropic API model IDs.
#
# Source: https://github.com/BerriAI/litellm
#
# Usage: bash scripts/sync-pricing.sh

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRICING_FILE="$PLUGIN_ROOT/pricing.json"
LITELLM_URL="https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

echo "Fetching pricing from litellm..."
raw=$(curl -sL "$LITELLM_URL")

# Extract Bedrock Anthropic entries and convert to Anthropic API IDs.
# Strips "anthropic." prefix and Bedrock version suffixes (-v1:0, -v2:0).
# Filters out legacy non-Claude models (claude-instant, claude-v1/v2) and
# Vertex-style IDs (containing @).
models=$(echo "$raw" | jq '[
  to_entries[]
  | select(.key | startswith("anthropic.claude-"))
  | select(.key | test("claude-instant|claude-v[0-9]") | not)
  | {
      api_id: (.key | sub("^anthropic\\."; "") | sub("-v[0-9]+(:[0-9]+)?$"; "")),
      input_per_mtok: ((.value.input_cost_per_token // 0) * 1000000),
      output_per_mtok: ((.value.output_cost_per_token // 0) * 1000000)
    }
  | select(.input_per_mtok > 0)
  | select(.api_id | contains("@") | not)
] | unique_by(.api_id) | sort_by(.api_id)')

# Build pricing.json with labels and aliases
pricing=$(echo "$models" | jq '{
  models: (reduce .[] as $m ({};
    # Generate label from API ID
    # claude-3-5-sonnet-20241022 -> "Sonnet 3.5"
    # claude-opus-4-6 -> "Opus 4.6"
    # claude-haiku-4-5-20251001 -> "Haiku 4.5"
    ($m.api_id
      | sub("^claude-"; "")
      | sub("-[0-9]{8}$"; "")
      | if test("^[0-9]+-[0-9]+-") then
          # Claude 3.x: "3-5-sonnet" -> "Sonnet 3.5"
          capture("^(?<major>[0-9]+)-(?<minor>[0-9]+)-(?<name>.+)$")
          | "\(.name | explode | [.[0] - 32] + .[1:] | implode) \(.major).\(.minor)"
        elif test("^[0-9]+-") then
          # Claude 3: "3-opus" -> "Opus 3"
          capture("^(?<major>[0-9]+)-(?<name>.+)$")
          | "\(.name | explode | [.[0] - 32] + .[1:] | implode) \(.major)"
        else
          # Claude 4+: "opus-4-6" -> "Opus 4.6", "haiku-4-5" -> "Haiku 4.5"
          split("-")
          | [(.[0] | explode | [.[0] - 32] + .[1:] | implode)] + .[1:]
          | if length >= 3 then "\(.[0]) \(.[1]).\(.[2])"
            elif length == 2 then "\(.[0]) \(.[1])"
            else join(" ")
            end
        end
    ) as $label

    # Round pricing to avoid floating point artifacts
    | ($m.input_per_mtok * 100 | round / 100) as $in_price
    | ($m.output_per_mtok * 100 | round / 100) as $out_price

    # Add the full dated ID
    | . + { ($m.api_id): { label: $label, input_per_mtok: $in_price, output_per_mtok: $out_price } }

    # Add aliases for dated IDs:
    # claude-opus-4-20250514 -> claude-opus-4-0 (numbered alias)
    # claude-haiku-4-5-20251001 -> claude-haiku-4-5 (short alias)
    | if ($m.api_id | test("-[0-9]{8}$")) then
        ($m.api_id | sub("-[0-9]{8}$"; "-0")) as $numbered
        | ($m.api_id | sub("-[0-9]{8}$"; "")) as $short
        | . + { ($numbered): { label: $label, input_per_mtok: $in_price, output_per_mtok: $out_price } }
        | . + { ($short): { label: $label, input_per_mtok: $in_price, output_per_mtok: $out_price } }
      else . end
  )),
  default: "claude-opus-4-6"
}')

echo "$pricing" | jq '.' > "$PRICING_FILE"

count=$(echo "$pricing" | jq '.models | length')
echo "Wrote $count model entries to $PRICING_FILE"
echo ""
echo "Models:"
echo "$pricing" | jq -r '.models | to_entries[] | "  \(.value.label | . + " " * (20 - length))  \(.key | . + " " * (30 - length))  $\(.value.input_per_mtok) / $\(.value.output_per_mtok)"'
