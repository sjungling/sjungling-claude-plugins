---
description: Enrich a GitHub issue with codebase triage, pinned code permalinks, and an optional Mermaid sequence diagram
argument-hint: "<issue-number>"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
---

Enrich a GitHub issue with codebase analysis: triage which area of the code owns the problem, add GitHub permalinks pinned to the `origin/main` HEAD SHA, and optionally include a Mermaid sequence diagram illustrating where the flow breaks down.

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
COMMIT_URL="https://github.com/$REPO/commit/$SHA"
SHORT_SHA="${SHA:0:7}"
```

If `git rev-parse origin/main` fails (no remote), use `HEAD` and note the fallback in the enrichment footer so readers know the snapshot may not be `main`.

## Step 3: Dispatch Research Subagent

Dispatch a fresh `Agent` to search the codebase and map the issue to specific code locations. This keeps raw search output out of the main context.

Fill in `<number>`, `<title>`, `<body>`, `<repo>`, `<sha>`, and `<permalink_base>` from the values resolved above before dispatching.

Agent prompt:

```
You are analyzing GitHub issue #<number>: "<title>"

Issue body:
<body>

Repository: <repo>
Permalink base (pinned to origin/main HEAD <sha>): <permalink_base>

Map this issue to the codebase. Do NOT prescribe solutions — only describe what currently exists and where the problem manifests. Do not use language like "should", "fix by", "change X to Y", or "the solution is".

## 1. TRIAGE THE CODEBASE

- Identify which files, modules, or services the issue touches
- Search for relevant symbols, error messages, configuration keys, or API paths mentioned in the issue using Grep, Glob, and Read
- Trace the execution path or data flow relevant to this issue
- Note the blast radius: which other areas are likely affected even if not the primary location

Write a 2-4 sentence triage summary that names the specific subsystem or layer that owns the problem. Be concrete — name real files or packages, not generic descriptions like "the backend" or "the frontend".

## 2. COLLECT CODE REFERENCES

For each relevant code location found:
- Verify the file exists: `test -f <path> && echo exists || echo MISSING` — skip any path that does not exist
- Record the exact file path (relative to repo root)
- Record the specific line range (start to end), confirmed against actual file content
- Write one sentence describing why this location is relevant to the issue — no prescriptions

Prefer narrower line ranges (5-20 lines) that isolate the specific logic, not entire files.

Return as a JSON array where every entry has been verified to exist on disk:
[
  { "file": "src/auth/middleware.ts", "start": 42, "end": 58, "relevance": "Session token is written here without expiry enforcement" }
]

## 3. ASSESS DIAGRAM VALUE

Decide whether a Mermaid sequence diagram would materially help a reader understand WHERE the issue occurs:
- Include if: the issue involves a sequence of calls, events, or interactions across multiple components or services
- Omit if: the issue is contained within a single function or is a pure data/type bug

If including, generate a `sequenceDiagram` using real component, function, and service names verified to exist in the codebase. Show ONLY the actual current flow. Use a `Note` annotation to mark the failure point. Do NOT add branches, dashed lines, or annotations showing a corrected or desired flow — the diagram must describe what happens now, not what should happen. Never invent names that don't appear in the code.

Mermaid syntax constraints to ensure valid rendering on GitHub:
- Participant aliases must be short identifiers with no spaces, parentheses, or special characters (use `as` to give them a display label: `participant W as WorkerService`)
- `Note` text must be a single line and kept concise (under 80 characters) — no colons or semicolons in the note text
- Do not use `activate`/`deactivate` blocks

## RETURN

Return a single JSON object:
{
  "triage_summary": "...",
  "code_refs": [
    { "file": "...", "start": N, "end": N, "relevance": "..." }
  ],
  "diagram": "sequenceDiagram\n  ..." or null,
  "diagram_rationale": "one sentence: why included or omitted"
}
```

Capture the agent's returned JSON as `$RESEARCH`.

## Step 4: Build Enrichment Body

Construct the enrichment markdown from `$RESEARCH` and write it to a temp file:

```bash
ENRICHMENT_FILE=$(mktemp /tmp/gh-enrich-XXXXXX.md)
```

### Triage section

Write to `$ENRICHMENT_FILE`:

```
## Issue Triage

<triage_summary>
```

### Code references

For each entry in `code_refs`, build the permalink:

```
<PERMALINK_BASE>/<file>#L<start>-L<end>
```

Append a block like the following to `$ENRICHMENT_FILE` — each reference gets a bold label line followed by the bare URL on its own line. GitHub automatically expands bare permalink URLs into inline code snippet previews. Do NOT wrap the URL in `[]()` markdown link syntax.

```
### Relevant Code

**`<file>:<start>-<end>`** — <relevance>
<PERMALINK_BASE>/<file>#L<start>-L<end>

**`<file2>:<start>-<end>`** — <relevance>
<PERMALINK_BASE>/<file2>#L<start>-L<end>
```

If `code_refs` is empty, write a note that no specific code locations were identified and the issue may need more detail.

### Mermaid diagram (conditional)

If `diagram` is non-null, append a `### Flow Diagram` heading followed by a fenced `mermaid` code block to `$ENRICHMENT_FILE`. Write the block exactly as:

    ### Flow Diagram

    ```mermaid
    <diagram content here>
    ```

## Step 5: Dispatch Review Subagent

Before posting anything, dispatch a fresh `Agent` to review the enrichment. The review subagent has access to Bash, Grep, Glob, and Read tools and must use them — this is an active code check, not a literary review.

Fill in `<number>`, `<title>`, `<body>`, and the full contents of `$ENRICHMENT_FILE` before dispatching.

Agent prompt:

```
Review this GitHub issue enrichment for quality and accuracy before it is posted. You have Bash, Grep, Glob, and Read tools — use them to verify claims rather than guessing.

Original issue #<number>: "<title>"

Issue body:
<body>

Proposed enrichment:
<enrichment_body>

Perform these checks:

1. FILE EXISTENCE: For every file path in the code references, run:
   test -f <path> && echo "OK: <path>" || echo "MISSING: <path>"
   Fail any reference where the file does not exist on disk.

2. LINE RANGE VALIDITY: For each existing file, confirm the referenced line range is within the file's actual line count:
   wc -l < <path>
   Flag any range where end > line count.

3. NO SOLUTIONS: Does the enrichment describe what exists WITHOUT prescribing what should change? Flag any language like "should", "fix by", "change X to Y", or "the solution is".

4. DIAGRAM NAMES: If a Mermaid diagram is present, grep for each component or service name used in the diagram to confirm it appears in the codebase. Flag any name not found.

5. TRIAGE SPECIFICITY: Does the triage summary name real files or subsystems (not generic terms like "the backend")?

6. GAPS: Search for related symbols or paths not covered in the code references. List any obvious locations that seem relevant to the issue but are absent.

Return JSON:
{
  "approved": true or false,
  "issues": ["specific problems found, empty if none"],
  "missed_areas": ["file paths or symbols that appear relevant but are absent from the enrichment"]
}
```

If `approved` is false or `missed_areas` is non-empty:
- Revise `$ENRICHMENT_FILE` to address the flagged issues
- For missed areas, perform targeted searches and append additional code refs
- Re-run Step 5 if significant changes were made

Only proceed to Step 6 once the review passes or all identified issues have been addressed.

## Step 6: Choose Update Method

Use `AskUserQuestion` to ask how to apply the enrichment:

- **Post as a comment** — preserves the original description unchanged, adds context as a new comment
- **Append to description** — adds the enrichment as a new section at the bottom of the existing issue body

## Step 7: Post Enrichment

### If comment:

```bash
gh issue comment "$ISSUE_NUMBER" --body-file "$ENRICHMENT_FILE"
```

### If append to description:

Fetch the current body (re-fetch to avoid overwriting edits made since Step 2):

```bash
BODY_FILE=$(mktemp /tmp/gh-body-XXXXXX.md)
gh issue view "$ISSUE_NUMBER" --json body -q '.body' > "$BODY_FILE"
printf '\n\n---\n\n' >> "$BODY_FILE"
cat "$ENRICHMENT_FILE" >> "$BODY_FILE"
gh issue edit "$ISSUE_NUMBER" --body-file "$BODY_FILE"
rm -f "$BODY_FILE"
```

Clean up the enrichment temp file and report the issue URL to the user.

## Step 8: Optional Title and Description Refinement

Use `AskUserQuestion` to ask:

> Based on the codebase research, would you like me to suggest a more precise title or description for this issue?

If yes:
- Propose a revised title that reflects the actual subsystem and observed behavior (e.g., "Auth middleware drops session expiry on token refresh" rather than "Login sometimes fails")
- Propose an optional one-paragraph clarification to prepend to the description that references the triaged code location

Present suggestions clearly and ask for explicit confirmation before applying any changes:

```bash
gh issue edit "$ISSUE_NUMBER" --title "<revised_title>"
```

Do not apply title or description changes without the user's explicit confirmation.

## Notes

- Never prescribe solutions — describe what exists, not what should change
- All code links must use the `origin/main` HEAD SHA, not the branch name (which can move)
- If the issue references multiple repositories, note this in the triage summary and focus on the current repo; mention the other repos by name for the implementer's reference
- Clean up all temp files created by this command, whether the command succeeds or is cancelled
