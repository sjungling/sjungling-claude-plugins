---
description: Create a GitHub issue from session context (specs, plans, or conversation summary)
argument-hint: "[file-path]"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

Create a GitHub issue using the best available content from the current session.

Parse `$ARGUMENTS` for an optional file path override.

## Step 1: Discover Content

Run the discovery script to find the best content source. The script is located relative to this command file:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd || echo "")"
```

If `$SCRIPT_DIR` is empty or the script does not exist, compute the path from the plugin root. The script lives at `plugins/workflow/scripts/discover-issue-content.sh` relative to the marketplace root. As a fallback, use `${CLAUDE_PLUGIN_ROOT}/scripts/discover-issue-content.sh` if that variable is available.

Run the script, passing `$ARGUMENTS` if non-empty:

```bash
DISCOVERY=$(bash "$SCRIPT_DIR/discover-issue-content.sh" $ARGUMENTS 2>&1)
```

If the script exits non-zero, check stderr for `{"error": "..."}` and report the error to the user. Common errors:
- `gh CLI not installed` — tell user to install GitHub CLI
- `jq not installed` — tell user to install jq
- `not in a git repository` — abort
- `file not found: <path>` — abort with the missing file path

Parse the JSON output:

```bash
SOURCE=$(echo "$DISCOVERY" | jq -r '.source')
PRIMARY=$(echo "$DISCOVERY" | jq -r '.primary')
SECONDARY=$(echo "$DISCOVERY" | jq -r '.secondary')
LABEL=$(echo "$DISCOVERY" | jq -r '.label')
REPO=$(echo "$DISCOVERY" | jq -r '.repo')
SPECS=$(echo "$DISCOVERY" | jq -r '.candidates.specs[]' 2>/dev/null)
PLANS=$(echo "$DISCOVERY" | jq -r '.candidates.plans[]' 2>/dev/null)
```

## Step 2: Resolve Content

Based on the `SOURCE` value:

### `explicit` or `claude-plan`
`PRIMARY` already points to the file. Use it directly as `$BODY_FILE`.

### `superpowers`
If `PRIMARY` is non-empty, use it as `$BODY_FILE`.

If `PRIMARY` is empty, there are multiple candidates that need disambiguation. Use `AskUserQuestion` to present the candidates from `SPECS` and/or `PLANS` and ask which file to use as the issue body. Set `$BODY_FILE` to the chosen file.

If `SECONDARY` is non-empty, it will be posted as a comment after issue creation.

### `summary`
No content files were found. Write a markdown summary of the current conversation covering:
- **Problem statement** — what prompted the session
- **Approach discussed** — key technical decisions and alternatives considered
- **Current status** — what was accomplished, what remains
- **Open questions** — anything unresolved

Write the summary to a temp file:
```bash
BODY_FILE=$(mktemp /tmp/gh-issue-body-XXXXXX.md)
```

## Step 3: Validate Content Size

Check the byte count of `$BODY_FILE`:
```bash
wc -c < "$BODY_FILE"
```

If it exceeds 60000 bytes:
1. Read the file and find the last markdown heading (`## ` or `### `) boundary before the 60000 byte mark
2. Truncate at that boundary
3. Append: `\n\n---\n_Content truncated due to GitHub size limits. Full document: \`<original-path>\`_`
4. Write the truncated version to a new temp file and use that instead

Apply the same size check to `$SECONDARY` if it is non-empty.

## Step 4: Suggest and Confirm Title

Extract a title suggestion from `$BODY_FILE`:
- Look for the first `# ` (H1) heading in the file
- If no H1, use the first non-empty, non-frontmatter line
- Strip any markdown formatting from the title

Use `AskUserQuestion` to present:
- Which content source was detected (`SOURCE` value)
- The file path being used
- The suggested title
- Ask the user to confirm the title or provide a different one

## Step 5: Create the Issue

Build the label flag from the discovery output:
- If `LABEL` is non-empty, use `--label "$LABEL"`
- Otherwise, omit `--label`

```bash
gh issue create --title "<confirmed-title>" --body-file "$BODY_FILE" --label "$LABEL"
```

Capture the output — `gh` prints the issue URL on success.

## Step 6: Post Secondary Content

If `SECONDARY` is non-empty:

1. Extract the issue number from the URL: `echo "$ISSUE_URL" | grep -o '[0-9]*$'`
2. Post the secondary content as a comment:
   ```bash
   gh issue comment "$ISSUE_NUMBER" --body-file "$SECONDARY"
   ```

## Step 7: Cleanup and Report

Remove any temp files that were created (do NOT remove the original source files).

Report to the user:
- The issue URL (as a clickable link)
- Which content source was used (`SOURCE`)
- Which label was applied (if any)
- Whether secondary content was added as a comment
