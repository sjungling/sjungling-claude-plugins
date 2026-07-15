# obsidian CLI Command Reference

Complete reference for the `obsidian` CLI. This is the **native Obsidian binary**, not an npm package.

## Installation

The `obsidian` CLI ships with the Obsidian desktop app. Verify it's on your PATH:

```bash
obsidian --version
```

## Vault Targeting

All vault commands use `vault=<name>` as a positional key=value argument. Quote it when the vault name has spaces:

```bash
obsidian "vault=my vault" <command>
```

### Default / active vault

Run `vault` with no name to get the **active vault** — the one currently open in the
Obsidian app. This is the CLI's implicit default when `vault=<name>` is omitted:

```bash
# Active vault name, from the tab-separated output (grep '^name' also drops the banner)
VAULT=$(obsidian vault | grep '^name' | cut -f2-)
```

> **Banner on stdout:** every `obsidian` call prepends startup lines to stdout ("Loading
> updated app package…", an installer-out-of-date notice, an `obsidian.md` URL). When
> capturing output into a variable, filter it — prefer a *positive* match on the shape you
> want (`grep '^name'`, `grep '\.md$'`) over blocklisting the banner text.

Daily-note commands (below) resolve against the active vault; targeting a non-active vault
with `vault=<name>` may return empty for daily operations if that vault isn't open.

## Core Commands

### vault

Get info about a specific vault by name.

```bash
obsidian vault "<name>"
```

**Output:** name, path, file count, folder count, size.

**Flags:**
- `info=path` — return only the disk path (useful for scripting)

**Examples:**
```bash
# Full vault info
obsidian vault "my vault"

# Get path for scripting
VAULT_PATH=$(obsidian vault "my vault" info=path)
```

### vaults

List all vaults Obsidian knows about.

```bash
obsidian vaults
```

Use this to confirm vault names before targeting them.

### folders

List all folders in a vault.

```bash
obsidian "vault=<name>" folders
```

### read

Read note contents by name or path.

```bash
obsidian "vault=<name>" read "<note name or path>"
```

**Behavior:**
- Fuzzy search by name (no path needed for unique names)
- Returns full note contents including frontmatter

**Examples:**
```bash
obsidian "vault=my vault" read "2024-03-21 Some Note Title"
obsidian "vault=my vault" read "til/2024-03-21 Some Note Title.md"
```

### create

Create a new note.

```bash
obsidian "vault=<name>" create path="folder/note.md" content="$CONTENT"
```

**Multi-line content:** Pass content via a `printf`-built variable — `\n` escapes inside double-quoted strings get stripped, but `printf` handles them correctly:

```bash
CONTENT=$(printf '---\ntags:\n  - til\nindex: "[[Today I learned]]"\n---\n## Heading\n\nFull content here, multiple paragraphs, frontmatter all preserved.')
obsidian "vault=<name>" create path="til/2026-04-27 My Note.md" content="$CONTENT"
```

**Flags:**
- `overwrite` — replace file if it already exists
- `template=<name>` — apply a vault template

### append

Append content to an existing note.

```bash
obsidian "vault=<name>" append path="folder/note.md" content="<text>"
```

### move

Move or rename notes while preserving all wiki-links.

```bash
obsidian "vault=<name>" move path="old/path.md" newpath="new/path.md"
```

**Behavior:**
- Automatically updates ALL links to moved note throughout entire vault
- Creates destination folder if needed

**This is the only safe way to move notes.** Using `mv` or file operations will break all links.

### search

Search note contents.

```bash
obsidian "vault=<name>" search query="<term>" [path=<folder>] [limit=<n>] [format=text|json]
```

**Examples:**
```bash
# Search entire vault
obsidian "vault=my vault" search query="API design"

# Search within a folder, return JSON paths
obsidian "vault=my vault" search query="setup" path=til format=json
```

## Daily notes

These operate on today's daily note in the **active vault** and require the core **Daily
Notes** (or **Periodic Notes**) plugin to be enabled and configured. If daily commands
return nothing, that plugin is off or the vault isn't the active one.

### daily

Create or open today's daily note.

```bash
obsidian "vault=<name>" daily
```

### daily:path

Print the vault-relative path of today's daily note. Empty output means no daily note is
configured — don't fabricate a path.

```bash
DAILY=$(obsidian "vault=<name>" daily:path)   # e.g. "Daily Journal/2026-07-15.md"
```

### daily:append / daily:prepend

Append (or prepend) content to today's daily note, creating it if needed. Block mode adds
a surrounding newline; pass `inline` to append without one.

```bash
obsidian "vault=<name>" daily:append content="- **14:32** Quick capture text"
```

For multi-line content, build it with `printf` and pass via a variable — see the escaping
note under [create](#create). This is the preferred way to capture short summaries into a
daily note (see the `/obsidian:add-to-daily-note` command).

### daily:read

Print the current contents of today's daily note.

## iCloud vaults & sandboxing

Two operational caveats when scripting the CLI:

- **iCloud vaults are TCC-protected.** For vaults under
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>`, the `Write` tool
  cannot touch the files — only the Obsidian app can, via the `obsidian` CLI. Always go
  through the CLI (or the chunked `write-markdown-to-vault.js` script) for these vaults,
  never a direct file write.
- **Disable the command sandbox for CLI calls.** The `obsidian` CLI connects to the
  running app over a local socket the sandbox blocks; a sandboxed call hangs. Run
  `obsidian ...` invocations unsandboxed.
- **`\n` / `\t` are converted.** The CLI turns literal `\n`/`\t` two-character sequences in
  `content=` into real newlines/tabs and cannot distinguish them from intended escapes.
  If a capture legitimately contains those sequences (e.g. a code sample about escaping),
  spot-check the result.

## Finding the Vault Path on Disk

Use the CLI directly:

```bash
# Full info including path
obsidian vault "<name>"

# Path only (for scripting)
VAULT_PATH=$(obsidian vault "<name>" info=path)
```

## Troubleshooting

### Command not found
The `obsidian` binary is not on PATH. Open Obsidian.app at least once — the binary is bundled with the app.

### Content gets stripped on create
Multi-line content with `\n` escapes doesn't survive the CLI's argument parsing. Use the `Write` tool to write directly to the vault path on disk instead.

### Note not found by name
Use the full vault-relative path, or run `search` first to find the exact path:
```bash
obsidian "vault=<name>" search query="unique phrase" format=json
```

## See Also

- [Obsidian Syntax Reference](./obsidian-syntax.md) - Wiki-link and markdown syntax
- [Note Templates](../assets/templates/) - Ready-to-use note templates
