---
name: obsidian-vault-manager
description: This skill should be used when the user asks to "manage Obsidian vault", "create a daily note", "move notes without breaking links", "search vault content", or "organize Obsidian notes". Automatically activates when working with Obsidian vaults, markdown notes with [[wiki-links]], daily notes, templates, or tags. Not for general markdown editing outside Obsidian vaults.
---

# Obsidian Vault Manager

## Prerequisites

Before performing vault operations:

1. **Verify obsidian CLI is installed:**
   ```bash
   obsidian --version
   ```
   The CLI is the native `obsidian` binary that ships with the Obsidian desktop app — not a separate npm package.

2. **List available vaults:**
   ```bash
   obsidian vaults
   ```

3. **Find vault path on disk** (needed for direct file writes):
   ```bash
   grep -o '"path":"[^"]*<vault-name>[^"]*"' ~/Library/Application\ Support/obsidian/obsidian.json
   ```

## Overview

**Use `obsidian` for vault operations that touch links or structure.** For creating notes with substantial content (multi-line, frontmatter, etc.), use the `Write` tool directly after locating the vault path — the CLI's `create` command strips multi-line content when `\n` escapes are used.

## Quick Reference

| Task | Command | Notes |
|------|---------|-------|
| List vaults | `obsidian vaults` | Always run first |
| List folders | `obsidian "vault=<name>" folders` | Quote vault name if it has spaces |
| Read note | `obsidian "vault=<name>" read "<note name>"` | Reads by name (fuzzy) |
| Create note (simple) | `obsidian "vault=<name>" create path="folder/name.md" content="<text>"` | Single-line content only |
| Create note (rich) | Write directly to vault path on disk | Use for multi-line/frontmatter content |
| Append to note | `obsidian "vault=<name>" append path="<path>" content="<text>"` | |
| Move note | `obsidian "vault=<name>" move path="old.md" newpath="new.md"` | **Auto-updates all links** |
| Search content | `obsidian "vault=<name>" search query="<term>" [path=<folder>] [format=json]` | |
| Daily note | `obsidian "vault=<name>" daily` | Create/open today's note |

**See also:**
- [Complete obsidian Command Reference](./references/obsidian-cli-reference.md) - All commands with flags and advanced usage
- [Obsidian Syntax Reference](./references/obsidian-syntax.md) - Wiki-links, tags, frontmatter, and markdown syntax
- [Note Templates](./assets/templates/) - Daily note, project, and meeting templates

## Core Workflows

### Step 1 — Find the Vault

```bash
# List vaults to confirm the name
obsidian vaults

# Get the disk path for direct writes
grep -o '"path":"[^"]*<vault-name>[^"]*"' ~/Library/Application\ Support/obsidian/obsidian.json
# Example output: "path":"/Users/me/Library/Mobile Documents/iCloud~md~obsidian/Documents/my vault"
```

### Step 2 — Explore Structure

```bash
# List folders
obsidian "vault=my vault" folders

# Search for existing notes
obsidian "vault=my vault" search query="devcenter" path=til format=json
```

### Step 3 — Create Notes with Rich Content

The CLI `create` command works for simple single-line content. For notes with frontmatter and multiple paragraphs, **write directly to the vault path**:

```bash
# Get vault path
VAULT_PATH="/Users/me/Library/Mobile Documents/iCloud~md~obsidian/Documents/my vault"

# Write note directly (preserves all content, newlines, frontmatter)
# Use the Write tool with the full path: $VAULT_PATH/til/2026-04-27 My TIL.md
```

**Look at an existing note first** to match local formatting conventions (tag names, frontmatter fields, `index` backlinks, etc.):
```bash
obsidian "vault=my vault" read "some existing note"
```

### Moving/Reorganizing Notes

```bash
# ✅ CORRECT: Auto-updates all links
obsidian "vault=my vault" move path="Random Notes/Design.md" newpath="Projects/Design.md"

# ❌ WRONG: Breaks all links to this note
mv "vault/Random Notes/Design.md" "vault/Projects/Design.md"
```

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Using `obsidian-cli` | That's a different npm package — the tool is `obsidian` | Use `obsidian` |
| Using `--flags` syntax | The CLI uses `key=value` positional args, not `--flags` | Use `key=value` format |
| `create` with `\n` content | Multi-line content gets stripped to frontmatter only | Write directly to vault path |
| Using `mv` to move notes | Breaks all `[[wiki-links]]` to that note | Use `obsidian move` |
| Not checking existing note format | Each vault has different tagging/frontmatter conventions | Read an existing note first |
| Using absolute paths in wiki-links | Breaks when vault moves | Use vault-relative paths |

## When to Use Standard Tools

- **Rich note creation**: Use `Write` tool with the full disk path (faster, no content truncation)
- **Bulk content editing**: Use `Edit` after reading with `obsidian read`
- **Complex search patterns**: Use `Grep` directly on the vault path

**Always preserve:**
- Frontmatter (YAML between `---`)
- Obsidian link syntax `[[Note]]`
- Tag syntax `#tag-name`
- Markdown structure

## Success Criteria

Vault operations succeed when:
- All `[[wiki-links]]` remain valid after moves
- Notes created in correct vault location with full content intact
- Formatting matches existing notes in the same folder
- No broken links or orphaned notes
