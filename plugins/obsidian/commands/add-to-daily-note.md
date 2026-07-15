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

Two things that will bite you if ignored:

- **Run every `obsidian` CLI call with the sandbox disabled.** The CLI talks to the
  running Obsidian app over a local socket the command sandbox blocks, so a sandboxed
  call hangs.
- **The CLI prepends a startup banner to stdout on every call** ("Loading updated app
  package…", installer-out-of-date, an `obsidian.md` URL). Always filter it when
  capturing output into a variable — the snippets below do this positionally
  (`grep '^name'`, `grep '\.md$'`).

If the capture text (`$ARGUMENTS`) is empty, ask the user what to capture — don't append
an empty bullet.

**This command acts; it does not gate.** Appending to a daily note is trivial and
reversible. Do **not** enter plan mode, write a plan file, or call `ExitPlanMode` for it —
the session's own permission prompt on the `daily:append` call is the only checkpoint you
need. Ask a clarifying question only for the one genuine fork below (long content), and
prefer a sensible default over asking.

## Step 1 — Resolve the target vault

Default to the CLI's active vault — this is "the default vault":

```bash
VAULT=$(obsidian vault | grep '^name' | cut -f2-)
```

If `$ARGUMENTS` begins with a `vault=<name>` token, use that name instead and strip the
token from the summary text. Validate an override with `obsidian vault "<name>"`; if it
errors, show `obsidian vaults` and stop (name typo).

## Step 2 — Resolve today's daily note

```bash
DAILY=$(obsidian "vault=$VAULT" daily:path | grep -E '\.md$' | head -n1)
```

If `$DAILY` is empty, the vault has no Daily Notes / Periodic Notes plugin configured (or
it isn't the active vault — daily commands target the active vault). Report that and stop;
do not fabricate a path.

## Step 3 — Right-size the capture

Judge the capture text (`$ARGUMENTS` minus any `vault=` token) and act — don't ask:

- **Short** — a few sentences / one small paragraph. Append it as-is (Step 4a).
- **Long** — multiple sections, headings, or code blocks. Don't dump it inline and don't
  stop to ask. **Condense it** to a few key bullets plus any action items, then append
  that under a heading (Step 4a). The daily note stays scannable; that's the default.

Only take the linked-note branch (Step 4b) when the user explicitly wants the full text
preserved verbatim, or the content is clearly a standalone document. If it's genuinely
ambiguous, ask **one** short `AskUserQuestion` (condense inline vs. linked note) — never a
plan or approval gate.

## Step 4a — Append under a new heading

Give each capture its own `###` (H3) heading so entries stay scannable. Derive a concise
topic (3–6 words) from the content for the heading, then put the summary beneath it:

```bash
TOPIC="<concise topic — e.g. Obsidian daily-note command>"
BLOCK=$(printf '\n### %s\n\n%s' "$TOPIC" "<summary text>")
obsidian "vault=$VAULT" daily:append content="$BLOCK"
```

Build the block with `printf`, not a plain double-quoted string — the CLI strips literal
`\n` from `content=` values but honors `printf`-produced newlines. The leading `\n`
separates the new heading from earlier content.

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
3. Link it from the daily note under its own H3 heading (same shape as Step 4a):
   ```bash
   BLOCK=$(printf '\n### %s\n\n- [[%s]] — %s' "<Topic>" "<Title>" "<one-line gist>")
   obsidian "vault=$VAULT" daily:append content="$BLOCK"
   ```

## Step 5 — Report

Report the vault, the daily note path, whether the capture went inline or into a linked
note (with its path), and the exact line(s) added. If the capture text contained literal
`\n`/`\t` sequences, flag it — the CLI converts them to real newlines/tabs (a known CLI
limitation, not something this command can prevent).
