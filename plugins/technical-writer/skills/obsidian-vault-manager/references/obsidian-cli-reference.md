# obsidian-cli Command Reference

Complete reference for `obsidian-cli` commands and advanced usage patterns.

## Installation

```bash
npm install -g @johnlindquist/obsidian-cli
```

Verify installation:
```bash
obsidian-cli --version
```

## Core Commands

### print-default

Display current vault information.

```bash
obsidian-cli print-default
```

**Flags:**
- `--path-only` - Output only the vault path (useful for scripting)

**Output:**
- Vault name
- Vault path
- Vault status

**Usage:**
```bash
# Get vault info
obsidian-cli print-default

# Get path for scripts
VAULT_PATH=$(obsidian-cli print-default --path-only)
echo "Vault location: $VAULT_PATH"
```

### print

Read note contents by name or path.

```bash
obsidian-cli print "Note Name"
obsidian-cli print "folder/Note Name"
```

**Behavior:**
- Searches by note name first (without path)
- Falls back to path-based lookup
- Returns full note contents including frontmatter
- Case-sensitive matching

**Examples:**
```bash
# Read by name
obsidian-cli print "Project Plan"

# Read by path
obsidian-cli print "Work/Projects/Project Plan"

# Pipe to other tools
obsidian-cli print "Note" | grep "TODO"
```

### create

Create new notes or update existing ones.

```bash
obsidian-cli create "Note Name" --content "content"
```

**Required Flags:**
- `--content "text"` - Note content (supports `\n` for newlines)

**Optional Flags:**
- `--append` - Add content to end of existing note (safe for existing files)
- `--overwrite` - Replace entire note (destructive)
- `--open` - Open note in Obsidian after creation

**Content Syntax:**
- Use `\n` for newlines
- Include Obsidian syntax: `[[wiki-links]]`, `#tags`, `- [ ]` checkboxes
- Frontmatter can be included in content

**Examples:**
```bash
# Create new note
obsidian-cli create "Meeting Notes" --content "# Meeting\n\nAttendees: [[John]], [[Sarah]]"

# Append to existing
obsidian-cli create "Daily Log" --content "\n## 3pm Update\n- Completed task" --append

# Replace existing (caution!)
obsidian-cli create "Draft" --content "# New Draft\n\nStarting over" --overwrite

# Create and open in Obsidian
obsidian-cli create "Quick Note" --content "# Note" --open
```

**Frontmatter Example:**
```bash
obsidian-cli create "Book Review" --content "---\ntitle: Book Title\nauthor: Author Name\nrating: 5\n---\n\n# Review\n\nExcellent book about [[Topic]]"
```

### move

Move or rename notes while preserving all wiki-links.

```bash
obsidian-cli move "old/path" "new/path"
```

**Behavior:**
- Automatically updates ALL links to moved note throughout entire vault
- Updates bidirectional links
- Maintains frontmatter and note content
- Creates destination folder if needed

**Path Formats:**
- Vault-relative paths (no leading `/`)
- With or without `.md` extension
- Folder paths for organizing

**Examples:**
```bash
# Move note to different folder
obsidian-cli move "Inbox/Idea" "Projects/New Idea"

# Rename note
obsidian-cli move "Draft Title" "Final Title"

# Reorganize with folders
obsidian-cli move "Random/Design Doc" "Projects/Mobile/Design Doc"

# Move with .md extension (works the same)
obsidian-cli move "note.md" "folder/note.md"
```

**Critical:** This is the ONLY safe way to move notes. Using `mv`, `Write`, or file operations will break all links.

### search-content

Search note contents for text.

```bash
obsidian-cli search-content "search term"
```

**Behavior:**
- Full-text search across all notes
- Returns matching note paths
- Case-insensitive by default
- Searches note content, not just titles

**Examples:**
```bash
# Find notes about a topic
obsidian-cli search-content "API design"

# Find todos
obsidian-cli search-content "- [ ]"

# Find tagged notes
obsidian-cli search-content "#important"

# Combine with other commands
for note in $(obsidian-cli search-content "refactor"); do
  echo "Found in: $note"
  obsidian-cli print "$note"
done
```

### search

Interactive fuzzy search for note names.

```bash
obsidian-cli search
```

**Behavior:**
- Opens interactive picker
- Fuzzy matching on note names
- Navigate with arrow keys
- Press Enter to select

**Usage:**
- Run command
- Type to filter notes
- Select note with Enter
- Use selected note path in scripts

**Note:** This is interactive and may not work in all automation contexts. Use `search-content` for scripting.

### daily

Create or open daily note.

```bash
obsidian-cli daily
```

**Behavior:**
- Creates note with today's date (YYYY-MM-DD format by default)
- Opens in Obsidian if it already exists
- Uses vault's daily note template if configured

**Examples:**
```bash
# Open today's note
obsidian-cli daily

# Create with custom content
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d)" --content "\n## Evening Review\n- Accomplishments" --append
```

## Advanced Usage Patterns

### Scripting with obsidian-cli

```bash
#!/bin/bash

# Get vault path for reference
VAULT_PATH=$(obsidian-cli print-default --path-only)

# Search and process notes
obsidian-cli search-content "TODO" | while read -r note; do
  echo "Processing: $note"
  content=$(obsidian-cli print "$note")
  # Process content...
done

# Bulk reorganization
for note in $(obsidian-cli search-content "#archive"); do
  obsidian-cli move "$note" "Archive/$note"
done
```

### Combining with Standard Tools

```bash
# Use obsidian-cli for vault operations, then standard tools for processing
obsidian-cli print "Note" > /tmp/note.md
# Edit with standard tools
sed -i 's/old/new/g' /tmp/note.md
# Write back to vault
obsidian-cli create "Note" --content "$(cat /tmp/note.md)" --overwrite
```

### Template-Based Note Creation

```bash
# Read template
TEMPLATE=$(cat templates/project-template.md)

# Create note with template
obsidian-cli create "New Project" --content "$TEMPLATE"

# Create with substitutions
TEMPLATE=$(cat templates/meeting-template.md | sed "s/DATE/$(date +%Y-%m-%d)/g")
obsidian-cli create "Meeting - Team Sync" --content "$TEMPLATE"
```

### Batch Operations

```bash
# Rename multiple notes with pattern
for note in Project-*; do
  new_name=$(echo "$note" | sed 's/Project-/Archived-Project-/')
  obsidian-cli move "$note" "Archive/$new_name"
done

# Add tag to multiple notes
obsidian-cli search-content "machine learning" | while read -r note; do
  content=$(obsidian-cli print "$note")
  obsidian-cli create "$note" --content "$content\n\n#machine-learning" --append
done
```

### Working with Frontmatter

```bash
# Create note with complex frontmatter
obsidian-cli create "Article" --content "---
title: Article Title
date: $(date +%Y-%m-%d)
tags:
  - article
  - published
author: John Doe
---

# Article Title

Content here with [[Wiki Links]]"
```

### Link Integrity Verification

```bash
# After bulk operations, verify links
# (obsidian-cli handles this automatically, but for validation:)
VAULT_PATH=$(obsidian-cli print-default --path-only)

# Use standard tools to find broken links
grep -r "\[\[.*\]\]" "$VAULT_PATH" | while read -r line; do
  # Check if target exists
  # obsidian-cli move ensures this isn't needed
done
```

## Troubleshooting

### Command Not Found

```bash
# Install globally
npm install -g @johnlindquist/obsidian-cli

# Or use npx
npx @johnlindquist/obsidian-cli print-default
```

### No Default Vault

Error: "No default vault set"

**Solution:**
- Open Obsidian application
- Vault must be opened at least once
- obsidian-cli reads from Obsidian's configuration

### Path Issues

**Problem:** Note not found by name

**Solution:**
```bash
# Use full path
obsidian-cli print "folder/subfolder/Note Name"

# Or search first
obsidian-cli search-content "unique phrase in note"
```

### Newlines Not Working

**Problem:** `\n` appears literally in notes

**Solution:**
```bash
# Use echo with -e flag
obsidian-cli create "Note" --content "$(echo -e "Line 1\nLine 2")"

# Or use $'...' syntax
obsidian-cli create "Note" --content $'Line 1\nLine 2'
```

## Best Practices

1. **Always check vault first:** Run `print-default` before operations
2. **Use obsidian-cli move exclusively:** Never use `mv` for notes
3. **Preserve Obsidian syntax:** Maintain `[[links]]`, `#tags`, frontmatter
4. **Test on copies:** For bulk operations, test on duplicate notes first
5. **Use --append safely:** Append is safe for existing files, overwrite is destructive
6. **Script defensively:** Check command success before proceeding
7. **Backup regularly:** obsidian-cli is safe, but backups prevent mistakes

## See Also

- [Obsidian Syntax Reference](./obsidian-syntax.md) - Wiki-link and markdown syntax
- [Note Templates](../assets/templates/) - Ready-to-use note templates
