---
description: Enrich a GitHub issue with codebase triage, inline code permalinks, and an optional Mermaid sequence diagram
argument-hint: "<issue-number>"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
---

Enrich a GitHub issue with codebase analysis: write narrative prose that traces the problem through the code with inline identifier hyperlinks, and optionally include a Mermaid sequence diagram that is render-validated before posting.

## Step 1: Resolve Issue Number

Parse `$ARGUMENTS` for the issue number. If it is empty, use `AskUserQuestion` to ask the user for the issue number before proceeding.

```bash
ISSUE_NUMBER="$ARGUMENTS"
if [ -z "$ISSUE_NUMBER" ]; then
  # Use AskUserQuestion to collect the issue number, then set ISSUE_NUMBER
  exit 0
fi
```

## Step 2: Fetch Issue and Permalink Base

Fetch the full issue details:

```bash
gh issue view "$ISSUE_NUMBER" --json number,title,body,labels,comments,url
```

If `gh issue view` returns a 404, tell the user the issue was not found in the current repository. Suggest they verify the issue number or pass `--repo owner/repo` to `gh issue view` manually and retry.

Resolve the permalink base pinned to `origin/main` HEAD:

```bash
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
SHA=$(git rev-parse origin/main 2>/dev/null || git rev-parse HEAD)
PERMALINK_BASE="https://github.com/$REPO/blob/$SHA"
```

If `git rev-parse origin/main` fails (no remote), use `HEAD` and note the fallback at the end of the triage prose.

## Step 3: Dispatch Research Subagent

Dispatch a fresh `Agent` to search the codebase. Fill in `<number>`, `<title>`, `<body>`, `<repo>`, `<sha>`, and `<permalink_base>` before dispatching.

Agent prompt:

```
You are analyzing GitHub issue #<number>: "<title>"

Issue body:
<body>

Repository: <repo>
Permalink base (pinned to origin/main HEAD <sha>): <permalink_base>

Map this issue to the codebase. Do NOT prescribe solutions. Do not use language like "should", "fix by", "change X to Y", or "the solution is".

## 1. TRIAGE THE CODEBASE

- Search for relevant symbols, error messages, config keys, or API paths from the issue using Grep, Glob, and Read
- Trace the execution path or data flow from entry point to failure
- Note blast radius: other areas affected even if not the root cause

Write triage prose — 3-6 sentences of narrative that traces the call chain from where the problem enters to where it manifests. Every code identifier you name (class name, method name, field name) must be a markdown hyperlink whose link text IS the identifier itself, not the file path. Build each permalink as:
  <permalink_base>/<file>#L<start>-L<end>

Format: [`ClassName.methodName`](permalink) or [`fieldName`](permalink)
Do NOT show raw file paths as visible link text. Do NOT write a separate table or list of code references.

Verify every file exists with `test -f <path>` before building its permalink. Skip any file that does not exist.

Example (not real — illustrative only):
  The issue originates in [`TokenRefreshFilter.doFilter`](https://github.com/org/repo/blob/SHA/path/Filter.java#L42-L67) where the session is re-issued without copying the expiry timestamp. The new token object is assembled in [`SessionFactory.build`](permalink) and written by [`SessionStore.persist`](permalink), which receives no expiry argument.

## 2. CODE REFS (for verification only — not displayed directly)

Return a separate machine-readable list of the code locations embedded in the prose above. These are used for post-hoc verification only and are NOT rendered in the output.

[
  { "file": "relative/path/from/repo/root.java", "start": 42, "end": 67 }
]

## 3. ASSESS DIAGRAM VALUE

Decide whether a Mermaid sequenceDiagram would materially help a reader understand WHERE the issue occurs:
- Include if: the issue involves interactions across multiple components or services
- Omit if: it is contained within a single function or class

If including, use real component names verified to exist in the code. Show ONLY the actual current flow. Use a `Note` annotation to mark the failure point. Do NOT show a corrected or desired flow.

Critical Mermaid syntax rules — violations will cause the diagram to fail rendering:
- Participant aliases: short identifiers only, NO spaces, parentheses, or special characters
  Good: `participant W as WorkerService`   Bad: `participant WorkerService (recipe-worker)`
- Message labels (arrows): NO semicolons. Semicolons are statement terminators in Mermaid — use a dash or comma instead
  Good: `W->>R: readUpgradesAndMigrations - returns empty`   Bad: `W->>R: reads CSV; returns empty`
- Note text: single line, under 80 characters, no colons or semicolons
- Do not use activate/deactivate blocks

## RETURN

{
  "triage_prose": "narrative with inline [`Identifier`](permalink) links...",
  "code_refs": [{ "file": "...", "start": N, "end": N }],
  "diagram": "sequenceDiagram\n  ..." or null,
  "diagram_rationale": "one sentence"
}
```

Capture the result as `$RESEARCH`.

## Step 4: Build Enrichment Body

Write the enrichment to a temp file:

```bash
ENRICHMENT_FILE=$(mktemp /tmp/gh-enrich-XXXXXX.md)
```

Write `triage_prose` as the entire body under a heading:

```
## Issue Triage

<triage_prose>
```

If `diagram` is non-null, append a `### Flow Diagram` heading followed by a fenced mermaid block. Use 4-space indentation here to avoid nested-fence ambiguity when writing the command file itself — when writing the actual enrichment file, use literal triple-backtick fences:

    ### Flow Diagram

    ```mermaid
    <diagram content>
    ```

## Step 5: Render-validate the Mermaid Diagram

If a diagram was included, validate it renders before posting. A diagram that fails to parse is worse than no diagram.

```bash
# Extract the mermaid block content from the enrichment file
MMD_FILE=$(mktemp /tmp/gh-diagram-XXXXXX.mmd)
sed -n '/^```mermaid$/,/^```$/{ /^```/d; p }' "$ENRICHMENT_FILE" > "$MMD_FILE"

# Create puppeteer config pointing at system Chrome (default puppeteer Chrome not installed)
PUPPETEER_CFG=$(mktemp /tmp/puppeteer-XXXXXX.json)
cat > "$PUPPETEER_CFG" <<'JSON'
{
  "args": ["--no-sandbox"],
  "executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
}
JSON

# Resolve mmdc
if command -v mmdc &>/dev/null; then
  MMDC_CMD="mmdc"
else
  MMDC_CMD="npx --yes @mermaid-js/mermaid-cli"
fi

OUT_PNG=$(mktemp /tmp/gh-diagram-XXXXXX.png)
MMDC_OUTPUT=$($MMDC_CMD -i "$MMD_FILE" -o "$OUT_PNG" --puppeteerConfigFile "$PUPPETEER_CFG" 2>&1)
MMDC_EXIT=$?
rm -f "$OUT_PNG" "$PUPPETEER_CFG"
```

If `$MMDC_EXIT` is non-zero:
1. Show `$MMDC_OUTPUT` to the user
2. Pass the error and the failing diagram back to a fresh `Agent` with this prompt:

```
This Mermaid sequenceDiagram failed to render. Fix ONLY the syntax — do not change the diagram's meaning.

Error from mmdc:
<MMDC_OUTPUT>

Failing diagram:
<MMD content>

Rules:
- No semicolons anywhere in message labels or Note text — they are statement terminators in Mermaid
- Participant aliases must be short identifiers with no spaces or parentheses
- Note text must be a single line under 80 characters with no colons or semicolons
- Return only the corrected diagram content (no fences, no explanation)
```

Replace the diagram block in `$ENRICHMENT_FILE` with the corrected diagram and re-run the mmdc validation. Repeat until the diagram renders cleanly or the agent cannot fix it (in which case, remove the diagram from the enrichment and note the failure to the user).

Clean up `$MMD_FILE`.

## Step 6: Dispatch Review Subagent

Dispatch a fresh `Agent` to review the enrichment. Fill in `<number>`, `<title>`, `<body>`, and the contents of `$ENRICHMENT_FILE`.

Agent prompt:

```
Review this GitHub issue enrichment before it is posted. Use Bash, Grep, Glob, and Read to verify — do not guess.

Issue #<number>: "<title>"
Body: <body>

Enrichment:
<enrichment_body>

Checks:

1. FILE EXISTENCE: For every permalink in the enrichment, extract the file path and run:
   test -f <path> && echo "OK" || echo "MISSING: <path>"
   Fail any reference pointing to a nonexistent file.

2. LINE RANGE VALIDITY: For each file, confirm referenced lines are within the file:
   wc -l < <path>

3. LINK STYLE: Every code identifier link must use the identifier as link text — never a raw file path.
   Good: [`ClassName.methodName`](url)   Bad: [`path/to/File.java:42-58`](url)
   Flag any link where the visible text is a file path rather than an identifier name.

4. NO SOLUTIONS: Flag any language like "should", "fix by", "change X to Y", or "the solution is".

5. TRIAGE SPECIFICITY: Does the prose name real identifiers from the codebase, not generic descriptions?

6. DIAGRAM: The diagram has already been validated by mmdc. Confirm that each participant alias
   and component name in the diagram grep-matches to an actual name in the codebase.

Return JSON:
{
  "approved": true or false,
  "issues": ["specific problems"],
  "missed_areas": ["relevant symbols or paths absent from the enrichment"]
}
```

If `approved` is false or `missed_areas` is non-empty:
- Address flagged issues in `$ENRICHMENT_FILE`
- For missed areas, search and incorporate additional inline references in the prose
- Re-run this step if significant changes were made

## Step 7: Choose Update Method

Use `AskUserQuestion` to ask how to apply the enrichment:

- **Post as a comment** — preserves the original description, adds context below
- **Append to description** — adds the enrichment as a new section at the bottom

## Step 8: Post Enrichment

### If comment:

```bash
gh issue comment "$ISSUE_NUMBER" --body-file "$ENRICHMENT_FILE"
```

### If append to description:

Re-fetch the current body to avoid overwriting any edits made during this workflow:

```bash
BODY_FILE=$(mktemp /tmp/gh-body-XXXXXX.md)
gh issue view "$ISSUE_NUMBER" --json body -q '.body' > "$BODY_FILE"
printf '\n\n---\n\n' >> "$BODY_FILE"
cat "$ENRICHMENT_FILE" >> "$BODY_FILE"
gh issue edit "$ISSUE_NUMBER" --body-file "$BODY_FILE"
rm -f "$BODY_FILE"
```

Clean up `$ENRICHMENT_FILE` and report the issue URL to the user.

## Step 9: Optional Title and Description Refinement

Use `AskUserQuestion` to ask:

> Based on the codebase research, would you like me to suggest a more precise title or description for this issue?

If yes:
- Propose a revised title that names the actual component and observed behavior
- Propose an optional one-paragraph clarification that references the triaged identifiers

Ask for explicit confirmation before applying:

```bash
gh issue edit "$ISSUE_NUMBER" --title "<revised_title>"
```

## Notes

- Never prescribe solutions — describe what exists, not what should change
- All permalinks use the `origin/main` HEAD SHA, never the branch name
- If the issue spans multiple repositories, name all of them in the triage prose and focus research on the current repo
- Clean up all temp files whether the command succeeds or is cancelled
