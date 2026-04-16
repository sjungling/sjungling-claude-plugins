---
description: Post code review comments from conversation onto the current branch's PR
allowed-tools:
  - Bash
  - Read
  - Write
---

Post inline code review comments on the GitHub PR associated with the current branch.

## Step 1: Gather Findings

Collect all code review findings, issues, or suggestions from the current conversation. For each finding, determine:

- **File path** — relative to the repo root
- **Line number(s)** — the specific line or line range in the current version of the file
- **Comment body** — a clear, actionable description of the issue in markdown

If there are no review findings in the conversation, tell the user and stop.

## Step 2: Resolve Line Numbers

For each finding, verify the line numbers are accurate:

1. Read the file to confirm the code at the referenced line matches what was discussed
2. If the line has shifted (e.g., due to edits since the review), find the correct current line
3. For issues spanning multiple lines, use `start_line` and `line` to define the range

## Step 3: Write Comments JSON

Write a JSON file containing the comments array:

```bash
COMMENTS_FILE=$(mktemp /tmp/pr-review-comments-XXXXXX.json)
```

Each comment object must have:
- `path` (string) — file path relative to repo root
- `line` (number) — the line number (or end line for ranges)
- `side` (string) — always `"RIGHT"`
- `body` (string) — markdown comment body

For multi-line ranges, also include:
- `start_line` (number) — first line of the range
- `start_side` (string) — always `"RIGHT"`

Example:
```json
[
  {
    "path": "src/foo.swift",
    "line": 42,
    "side": "RIGHT",
    "body": "**Raw spacing literal**\n\nUse `CortinaSpacing.lg` instead of `12`."
  },
  {
    "path": "src/bar.swift",
    "start_line": 10,
    "start_side": "RIGHT",
    "line": 15,
    "side": "RIGHT",
    "body": "This block should use the shared helper."
  }
]
```

Write the array to `$COMMENTS_FILE`.

## Step 4: Post the Review

Run the posting script. The script is located relative to this command file:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd || echo "")"
```

If `$SCRIPT_DIR` is empty or the script does not exist, use `${CLAUDE_PLUGIN_ROOT}/scripts/post-pr-comments.sh` as a fallback.

```bash
RESULT=$(bash "$SCRIPT_DIR/post-pr-comments.sh" "$COMMENTS_FILE" 2>&1)
```

## Step 5: Cleanup and Report

Remove the comments temp file:
```bash
rm -f "$COMMENTS_FILE"
```

Parse `$RESULT` as JSON:
- If it contains `review_url`: report the URL and comment count to the user
- If it contains `error`: report the error message to the user
