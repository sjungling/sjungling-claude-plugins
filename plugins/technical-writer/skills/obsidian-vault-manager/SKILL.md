---
name: obsidian-vault-manager
description: Use when working with Obsidian vaults, managing markdown notes with wiki-links, or needing to preserve internal link integrity during file operations - provides obsidian-cli workflows for reading, writing, searching, moving, and organizing notes while maintaining vault structure
---

# Obsidian Vault Manager

## Overview

**Use `obsidian-cli` for all Obsidian vault operations.** Standard file tools (mv, Write, Edit) break internal links and ignore vault structure. The `obsidian-cli` tool automatically preserves `[[wiki-links]]` and maintains vault integrity.

## When to Use

Use this skill when:
- Working with Obsidian vaults (`.md` files with `[[wiki-links]]`)
- Moving/renaming notes (links must stay valid)
- Creating notes with Obsidian-specific syntax (wiki-links, checkboxes, tags)
- Searching vault content or note names
- Organizing multiple notes across folders

**Don't use for:**
- General markdown editing outside Obsidian vaults
- Static documentation (no internal links)
- Single-file markdown operations

## Quick Reference

| Task | Command | Notes |
|------|---------|-------|
| Check vault | `obsidian-cli print-default` | Always run first |
| Read note | `obsidian-cli print "Note Name"` | Reads by name or path |
| Create note | `obsidian-cli create "Name" --content "text"` | Add `--open` to launch Obsidian |
| Update note | `obsidian-cli create "Name" --content "text" --append` | Use `--overwrite` to replace |
| Move note | `obsidian-cli move "old/path" "new/path"` | **Auto-updates all links** |
| Search content | `obsidian-cli search-content "term"` | Searches note contents |
| Search names | `obsidian-cli search` | Fuzzy search (interactive) |
| Daily note | `obsidian-cli daily` | Create/open today's note |

## Core Workflows

### Always Check Vault First

```bash
# REQUIRED before any operation
obsidian-cli print-default

# Get path for direct file operations if needed
VAULT_PATH=$(obsidian-cli print-default --path-only)
```

**Why:** Paths are vault-relative, not repository-relative. Creating files in wrong location breaks vault structure.

### Moving/Reorganizing Notes

```bash
# ✅ CORRECT: Auto-updates all links
obsidian-cli move "Random Notes/Design" "Projects/Design"

# ❌ WRONG: Breaks all links to this note
mv "vault/Random Notes/Design.md" "vault/Projects/Design.md"
```

**Critical:** `obsidian-cli move` updates every link in the vault automatically. Using `mv` or file operations breaks internal references.

### Creating/Updating Notes

```bash
# Create new note
obsidian-cli create "Projects/Mobile App" --content "# Mobile App\n\n## Tasks\n- [ ] Task 1"

# Append to existing (safe if file exists)
obsidian-cli create "Daily Log" --content "\n## Update\n- New entry" --append

# Replace existing (use cautiously)
obsidian-cli create "Draft" --content "# Fresh content" --overwrite
```

**Obsidian syntax in `--content`:**
- Wiki-links: `[[Note Name]]`
- Tags: `#project`
- Checkboxes: `- [ ] Task`
- Newlines: `\n`

### Searching and Organizing

```bash
# Find notes mentioning topic
obsidian-cli search-content "API design"

# Read found note
obsidian-cli print "Backend/API Design"

# Reorganize (preserves all links)
obsidian-cli move "Backend/API Design" "Projects/Backend/API Design"
```

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Using `mv` to move notes | Breaks all `[[wiki-links]]` to that note | Use `obsidian-cli move` |
| Using `Write` tool for notes | Creates files outside vault or wrong location | Use `obsidian-cli create --content` |
| Using `Read` for vault notes | Misses vault context, no search integration | Use `obsidian-cli print` |
| Not checking vault first | Operations fail or create files in wrong place | Always run `print-default` first |
| Manual link updating with sed | Error-prone, misses bidirectional links | `obsidian-cli move` handles automatically |
| Using absolute paths | Breaks when vault moves | Use vault-relative paths |

## When to Use Standard Tools

**Use `obsidian-cli` first.** Only use standard tools when:
- Bulk editing note contents (use `Edit` after `obsidian-cli print`)
- Complex search patterns (use `Grep` with vault path)
- File pattern matching (use `Glob` on `$VAULT_PATH/**/*.md`)

**Always preserve:**
- Frontmatter (YAML between `---`)
- Obsidian link syntax `[[Note]]`
- Tag syntax `#tag-name`
- Markdown structure

## Integration Pattern

```bash
# 1. Check vault
obsidian-cli print-default

# 2. Use obsidian-cli for vault operations
obsidian-cli search-content "search term"
obsidian-cli print "Found Note"

# 3. Use standard tools ONLY when needed
# (e.g., complex editing after reading with obsidian-cli)
```

## Success Criteria

Your vault operations succeed when:
- All `[[wiki-links]]` remain valid after moves
- Notes created in correct vault location
- Markdown and frontmatter preserved
- Search returns accurate results
- No broken links or orphaned notes
