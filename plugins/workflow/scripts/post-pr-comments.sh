#!/usr/bin/env bash
# post-pr-comments.sh
#
# Posts inline review comments on a GitHub PR using the Pull Request Reviews API.
#
# Usage: post-pr-comments.sh <comments-json-file>
#
# Input: A JSON file containing an array of comment objects:
#   [
#     {
#       "path": "src/foo.swift",
#       "line": 42,
#       "side": "RIGHT",
#       "body": "Comment text"
#     }
#   ]
#
# Optional fields per comment: start_line, start_side (for multi-line ranges)
#
# Output (stdout): JSON object with review_url and comment_count on success,
#                  or error field on failure.
#
# Exit codes:
#   0 — success
#   1 — prereq or validation failure
#   2 — API failure

set -euo pipefail

# --- Helpers ---

error_json() {
  local msg="$1"
  local exit_code="${2:-1}"
  echo "{\"error\": \"$msg\"}"
  exit "$exit_code"
}

# --- Pre-checks ---

command -v gh &>/dev/null || error_json "gh CLI not installed"
command -v jq &>/dev/null || error_json "jq not installed"
git rev-parse --show-toplevel &>/dev/null || error_json "not in a git repository"

# --- Argument validation ---

[[ $# -ge 1 ]] || error_json "usage: post-pr-comments.sh <comments-json-file>"

COMMENTS_FILE="$1"

[[ -f "$COMMENTS_FILE" ]] || error_json "comments file not found: $COMMENTS_FILE"

COMMENT_COUNT=$(jq 'if type == "array" then length else -1 end' "$COMMENTS_FILE" 2>/dev/null || echo "-1")

[[ "$COMMENT_COUNT" -gt 0 ]] || error_json "comments file must contain a non-empty JSON array"

jq -e '.[] | has("path") and has("line") and has("side") and has("body")' "$COMMENTS_FILE" >/dev/null 2>&1 || \
  error_json "each comment must have path, line, side, and body fields"

# --- Get PR metadata ---

PR_DATA=$(gh pr view --json number,headRefOid 2>/dev/null) || error_json "no PR found for current branch"
PR_NUMBER=$(echo "$PR_DATA" | jq -r '.number')
HEAD_SHA=$(echo "$PR_DATA" | jq -r '.headRefOid')

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || echo "")
[[ -n "$REPO" ]] || error_json "could not determine repository"

# --- Build review payload ---

PAYLOAD_FILE=$(mktemp /tmp/pr-review-payload-XXXXXX.json)

jq -n \
  --arg commit_id "$HEAD_SHA" \
  --slurpfile comments "$COMMENTS_FILE" \
  '{
    commit_id: $commit_id,
    event: "COMMENT",
    body: "",
    comments: $comments[0]
  }' > "$PAYLOAD_FILE"

# --- Post review ---

RESPONSE=$(gh api "repos/$REPO/pulls/$PR_NUMBER/reviews" --input "$PAYLOAD_FILE" 2>&1) || {
  rm -f "$PAYLOAD_FILE"
  API_ERROR=$(echo "$RESPONSE" | jq -r '.message // .errors[0].message // "unknown API error"' 2>/dev/null || echo "$RESPONSE")
  error_json "API request failed: $API_ERROR" 2
}

rm -f "$PAYLOAD_FILE"

# --- Extract result ---

REVIEW_URL=$(echo "$RESPONSE" | jq -r '.html_url // empty' 2>/dev/null || echo "")

if [[ -n "$REVIEW_URL" ]]; then
  jq -n \
    --arg review_url "$REVIEW_URL" \
    --argjson comment_count "$COMMENT_COUNT" \
    '{ review_url: $review_url, comment_count: $comment_count }'
else
  error_json "review posted but could not extract URL from response"
fi
