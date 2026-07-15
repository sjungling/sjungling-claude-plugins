---
description: Quick-capture a short summary into today's Obsidian daily note via the native CLI
argument-hint: [summary text] (optional leading vault=<name> to override the default vault)
allowed-tools:
  - Bash
  - AskUserQuestion
  - Skill
---

Capture `$ARGUMENTS` into today's daily note in Obsidian.

The full CLI surface and every caveat live in the shared reference: the
`technical-writer:obsidian-vault-manager` skill →
`references/obsidian-cli-reference.md` (see the **Default / active vault**, **Daily
notes**, and **iCloud vaults & sandboxing** sections). Consult it if any step is unclear.

**Run every `obsidian` CLI call with the sandbox disabled.** The CLI talks to the running
Obsidian app over a local socket the command sandbox blocks, so a sandboxed call hangs.

## Step 1 — Resolve the target vault

Default to the CLI's active vault — this is "the default vault":

```bash
VAULT=$(obsidian vault | awk -F'\t' '$1=="name"{print $2}')
```

If `$ARGUMENTS` begins with a `vault=<name>` token, use that name instead and strip the
token from the summary text. Validate an override with `obsidian vault "<name>"`; if it
errors, show `obsidian vaults` and stop (name typo).

## Step 2 — Resolve today's daily note

```bash
DAILY=$(obsidian "vault=$VAULT" daily:path)
```

If `$DAILY` is empty, the vault has no Daily Notes / Periodic Notes plugin configured (or
it isn't the active vault — daily commands target the active vault). Report that and stop;
do not fabricate a path.

## Step 3 — Decide short vs. long

Judge the capture text (`$ARGUMENTS` minus any `vault=` token):

- **Short** — a few sentences / one small paragraph, no headings or large code blocks.
  Append it inline (Step 4a).
- **Long** — multiple sections, headings, or code blocks. It doesn't belong inline in a
  daily note. Ask with `AskUserQuestion`: *inline anyway* (Step 4a) or *create a linked
  note* (Step 4b).

## Step 4a — Append inline

Append a single timestamped bullet (block mode supplies the newline):

```bash
obsidian "vault=$VAULT" daily:append content="- **$(date +%H:%M)** <summary text>"
```

For multi-line captures, build the content with `printf` and pass it via a variable — the
CLI strips `\n` from plain double-quoted strings but honors `printf`-produced newlines.

## Step 4b — Create a linked note

1. Derive a concise title from the content; confirm the target `folder/Title.md` with the
   user if it's not obvious.
2. Create the note (`printf` for multi-line bodies):
   ```bash
   obsidian "vault=$VAULT" create path="<folder>/<Title>.md" content="$BODY"
   ```
   For a body beyond the CLI's ~10KB IPC ceiling, invoke the
   `technical-writer:obsidian-vault-manager` skill and use its chunked, verified
   `scripts/write-markdown-to-vault.js` instead.
3. Link it from the daily note:
   ```bash
   obsidian "vault=$VAULT" daily:append content="- [[<Title>]] — <one-line gist>"
   ```

## Step 5 — Report

Report the vault, the daily note path, whether the capture went inline or into a linked
note (with its path), and the exact line(s) added. If the capture text contained literal
`\n`/`\t` sequences, flag it — the CLI converts them to real newlines/tabs (a known CLI
limitation, not something this command can prevent).
