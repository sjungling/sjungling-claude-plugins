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

3. **Get vault path:**
   ```bash
   obsidian vault "<name>" info=path
   ```

## Overview

**Use `obsidian` for vault operations that touch links or structure.** For **iCloud-synced vaults** (path contains `Mobile Documents` — check with `obsidian vault "<name>" info=path`), the `Write` tool is not reliable: iCloud paths are TCC-protected, so direct filesystem writes can be blocked even with the sandbox disabled — only the Obsidian app (via the CLI) is guaranteed to land. For creating a note with substantial content (multi-line, frontmatter, code blocks), use `scripts/write-markdown-to-vault.js` in this skill — it chunks large payloads under the CLI's ~10KB IPC ceiling, filters banner noise, retries transient errors, and verifies the write by reading the note back. Run it **unsandboxed** (the CLI hangs under the command sandbox). For vaults on ordinary filesystem paths (not iCloud), the `Write` tool works directly and is simpler for one-off notes.

## Quick Reference

| Task | Command | Notes |
|------|---------|-------|
| List vaults | `obsidian vaults` | Always run first |
| Vault info | `obsidian vault "<name>"` | Name, path, file count |
| Vault path | `obsidian vault "<name>" info=path` | Path only, good for scripting |
| List folders | `obsidian "vault=<name>" folders` | Quote vault name if it has spaces |
| Read note | `obsidian "vault=<name>" read "<note name>"` | Reads by name (fuzzy) |
| Create note (large/iCloud) | `node scripts/write-markdown-to-vault.js --vault <name> --path <path> --input <file>` | Chunked, retried, verified — run unsandboxed |
| Create note (small, non-iCloud) | `obsidian "vault=<name>" create path="folder/name.md" content="$CONTENT"` | Use `printf` to build `$CONTENT` for multi-line |
| Overwrite note | `obsidian "vault=<name>" create path="..." content="$CONTENT" overwrite` | |
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

# Get full info (name, path, file count)
obsidian vault "<name>"

# Get just the path (useful for scripting)
VAULT_PATH=$(obsidian vault "<name>" info=path)
```

### Step 2 — Explore Structure

```bash
# List folders
obsidian "vault=<name>" folders

# Search for existing notes
obsidian "vault=<name>" search query="<topic>" path=<folder> format=json
```

### Step 3 — Create Notes with Rich Content

Use `printf` to build the content variable — this correctly handles newlines and multi-line content including frontmatter:

```bash
CONTENT=$(printf '---\ntags:\n  - til\nindex: "[[Today I learned]]"\n---\n## Heading\n\nContent here.')
obsidian "vault=<name>" create path="til/2026-04-27 My Note.md" content="$CONTENT"
```

**Look at an existing note first** to match local formatting conventions (tag names, frontmatter fields, `index` backlinks, etc.):
```bash
obsidian "vault=<name>" read "<existing note name>"
```

### Moving/Reorganizing Notes

```bash
# ✅ CORRECT: Auto-updates all links
obsidian "vault=<name>" move path="Random Notes/Design.md" newpath="Projects/Design.md"

# ❌ WRONG: Breaks all links to this note
mv "vault/Random Notes/Design.md" "vault/Projects/Design.md"
```

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Using `obsidian-cli` | That's a different npm package — the tool is `obsidian` | Use `obsidian` |
| Using `--flags` syntax | The CLI uses `key=value` positional args, not `--flags` | Use `key=value` format |
| `create` with `\n` in double-quoted string | Escapes get stripped, content truncated | Use `printf` to build a `$CONTENT` variable |
| Using `Write` on an iCloud vault path | TCC can silently block the write even with the sandbox disabled | Use `scripts/write-markdown-to-vault.js` instead |
| Content over ~10KB in one `create`/`append` call | Silent broken pipe (exit 0, nothing written) or a `NativeImage` error | Use `scripts/write-markdown-to-vault.js` — it chunks automatically |
| Using `mv` to move notes | Breaks all `[[wiki-links]]` to that note | Use `obsidian move` |
| Not checking existing note format | Each vault has different tagging/frontmatter conventions | Read an existing note first |
| Using absolute paths in wiki-links | Breaks when vault moves | Use vault-relative paths |

## When to Use Standard Tools

- **Bulk content editing**: Use `Edit` after reading with `obsidian read`
- **Complex search patterns**: Use `Grep` directly on the vault path (use `obsidian vault "<name>" info=path` to get it)

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
