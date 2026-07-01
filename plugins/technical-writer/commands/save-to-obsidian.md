---
description: Save the current spec/plan/session summary to Obsidian as a design note
argument-hint: [vault] [topic]
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

Save the best available content from the current session into an Obsidian vault as a design note.

Parse `$1` as an optional **vault** override and `$2` as an optional **topic** override (both optional — see resolution rules below). `$1`/`$2` are name/topic strings, not file paths — this command never takes an explicit source file; content is always auto-discovered from the session.

**Vaults on iCloud storage cannot be written with the `Write` tool** — `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>` is TCC-protected; only the Obsidian app (via the `obsidian` CLI) can touch it, even with the sandbox disabled. **Step 5 below always writes through the CLI — never write directly to a resolved vault path with the `Write` tool, even for a small note.** (`Write` is only used in this command to stage the note in a scratch temp file before handing it to the CLI script.)

## Step 1: Discover content

Run the discovery script, resolved relative to the plugin root:

```bash
DISCOVERY=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/discover-spec-content.sh" 2>&1)
```

If it exits non-zero, check stderr for `{"error": "..."}` and report the error (`jq not installed`, `not in a git repository`).

Parse the JSON output:
```bash
SOURCE=$(echo "$DISCOVERY" | jq -r '.source')
PRIMARY=$(echo "$DISCOVERY" | jq -r '.primary')
SECONDARY=$(echo "$DISCOVERY" | jq -r '.secondary')
SPECS=$(echo "$DISCOVERY" | jq -r '.candidates.specs[]' 2>/dev/null)
PLANS=$(echo "$DISCOVERY" | jq -r '.candidates.plans[]' 2>/dev/null)
```

### `superpowers`
If `PRIMARY` is non-empty, read it as `$BODY`.

If `PRIMARY` is empty, multiple candidates need disambiguation — use `AskUserQuestion` with the `SPECS`/`PLANS` candidates to pick the file. Read the chosen file as `$BODY`.

If `SECONDARY` is non-empty (a related plan), you may append a short "Implementation plan: `<path>`" reference line to the note rather than inlining the whole plan.

### `claude-plan`
`PRIMARY` already points to the plan file. Read it as `$BODY`.

### `summary`
No spec/plan files found. Write a markdown summary of the current conversation covering:
- **Problem** — what prompted the session
- **Decisions & rationale** — key choices made and why (this is the part worth keeping; skip anything derivable from re-reading the code)
- **Approach** — architecture/implementation shape agreed on
- **Open questions** — anything unresolved

Use this as `$BODY`.

## Step 2: Resolve the vault

```bash
obsidian vaults
```

- If `$1` was given, validate it: `obsidian vault "$1"`. If that errors, report the failure (name typo — show the list from `obsidian vaults`) and stop.
- If `$1` was omitted and there is exactly one vault, use it silently.
- If `$1` was omitted and there are multiple vaults, use `AskUserQuestion` to pick one.

## Step 3: Resolve topic → folder + tag conventions

```bash
obsidian "vault=$VAULT" folders
```

- If `$2` was given, case-insensitively match it against the folder list (e.g. topic `fraudfront` matches folder `FraudFront`). Use the matching folder.
- If `$2` was given but nothing matches, use `AskUserQuestion`: create a new top-level folder named after the topic, or pick an existing folder instead.
- If `$2` was omitted, infer a topic guess from the current repo/project name (e.g. `git rev-parse --show-toplevel` basename, or the project name in `CLAUDE.md`) and propose it via `AskUserQuestion` alongside "pick a different existing folder" and "type a topic".

Once the folder is resolved, learn its formatting conventions rather than inventing your own:
```bash
# List existing note filenames in the folder (folders command doesn't list files — use find on the vault path)
VAULT_PATH=$(obsidian vault "$VAULT" info=path)
ls "$VAULT_PATH/$FOLDER" 2>/dev/null
```
If notes exist, `obsidian "vault=$VAULT" read "<one existing note>"` and match its frontmatter shape (tag names, whether it uses `date`/`status` fields, filename separator style — e.g. em dash + " Design" suffix). If the folder is empty, default to: tags = `[<topic-slug>, design]` plus any specific keyword tag drawn from the note's own title, frontmatter fields `tags`/`date`/`status: draft`.

## Step 4: Build the note

- Title: the first `# ` (H1) heading in `$BODY`, or the first non-empty non-frontmatter line if there's no H1.
- Filename: match the existing folder's naming convention from Step 3; if none observed, use `<Title>.md`.
- Frontmatter: the tags/fields resolved in Step 3, `date: <today, YYYY-MM-DD>`, `status: draft`.
- Body: `$BODY` as-is below the frontmatter (don't re-summarize or truncate — the write script in Step 5 chunks automatically, so there's no size limit to work around here, unlike posting to GitHub).

Stage it with the `Write` tool at a scratch path (`mktemp "${TMPDIR:-/tmp}/obsidian-note-XXXXXX.md"`) — **not** in the vault.

## Step 5: Write through the CLI

Check whether a note already exists at the target path first:
```bash
obsidian "vault=$VAULT" read "path=$FOLDER/$FILENAME"
```
If it returns real content (not a "not found" error), use `AskUserQuestion`: overwrite, save under a new dated variant (append ` — <date>` to the filename), or abort.

Then write via the dedicated script — **this MUST run unsandboxed** (the `obsidian` CLI connects to the running app over a local socket that the command sandbox blocks and hangs on):
```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-manager/scripts/write-markdown-to-vault.js" \
  --vault "$VAULT" \
  --path "$FOLDER/$FILENAME" \
  --input "$NOTE_FILE" \
  --overwrite   # only if Step 5's collision check confirmed overwrite
```
The script chunks large notes automatically, retries transient CLI errors, and verifies the write by reading the note back — treat a non-zero exit as a real failure, not a warning. It also warns (on stderr) if the source content contains literal `\n`/`\t` two-character sequences (e.g. a code sample describing escape sequences) — the `obsidian` CLI cannot distinguish these from real newline/tab escapes and will silently convert them, which is a CLI limitation, not something this command can fix. If that warning fires, mention it in your report so the user knows to spot-check that section of the note.

## Step 6: Report

Report to the user:
- Vault name and note path
- Tags applied
- Whether this created a new note or overwrote an existing one
- Any `\n`/`\t` literal-escape warning from Step 5
