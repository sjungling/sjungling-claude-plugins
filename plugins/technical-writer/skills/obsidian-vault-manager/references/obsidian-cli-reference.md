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

### daily

Create or open today's daily note.

```bash
obsidian "vault=<name>" daily
```

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
