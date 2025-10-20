# Obsidian Markdown Syntax Reference

Complete reference for Obsidian-specific markdown syntax, including wiki-links, tags, frontmatter, and extended markdown features.

## Wiki-Links

Obsidian's primary linking syntax for internal note connections.

### Basic Wiki-Links

```markdown
[[Note Name]]
```

Links to a note named "Note Name.md" anywhere in the vault.

**Characteristics:**
- Case-sensitive
- Extension not required
- Searches entire vault by name
- Creates link even if note doesn't exist (shown in different color in Obsidian)

### Wiki-Links with Aliases

```markdown
[[Actual Note Name|Display Text]]
```

Display custom text while linking to the actual note.

**Examples:**
```markdown
See the [[Project Requirements|requirements]] for details.
Read [[Albert Einstein|Einstein's]] biography.
Check [[2024-01-15|yesterday's notes]].
```

### Wiki-Links to Headings

```markdown
[[Note Name#Heading]]
[[Note Name#Heading|Custom Text]]
```

Link to specific section within a note.

**Examples:**
```markdown
Review [[Meeting Notes#Action Items]]
See [[API Documentation#Authentication|auth docs]]
```

**Heading Link Rules:**
- Heading text must match exactly (case-sensitive)
- Use heading text without the `#` prefix
- Spaces in headings are preserved
- Works with any heading level

### Wiki-Links to Blocks

```markdown
[[Note Name#^block-id]]
```

Link to specific block within a note.

**Block ID Syntax:**
```markdown
This is a paragraph with an ID. ^block-123

- List item with ID ^item-456
```

**Example:**
```markdown
Reference: [[Research#^key-finding]]
```

### Wiki-Links with Paths

```markdown
[[folder/subfolder/Note Name]]
```

Specify path when multiple notes share the same name.

**Examples:**
```markdown
[[Work/Projects/Project Plan]]
[[Personal/Projects/Project Plan]]
```

### Embedding Notes

```markdown
![[Note Name]]
```

Embed the entire content of another note.

**Examples:**
```markdown
![[Meeting Template]]
![[Quote Collection#Favorite Quotes]]
```

### Embedding Images

```markdown
![[image.png]]
![[image.png|200]]
![[image.png|200x100]]
![[folder/image.png|Custom Alt Text|300]]
```

**Size Specifications:**
- `|width` - Set width, maintain aspect ratio
- `|widthxheight` - Set both dimensions
- Add alt text before dimensions

## Tags

Flexible categorization and filtering system.

### Basic Tags

```markdown
#tag
#tag-name
#tag_name
```

**Rules:**
- Start with `#`
- No spaces (use `-` or `_`)
- Alphanumeric characters
- Case-sensitive
- Can appear anywhere in note

**Examples:**
```markdown
#project #work #important

This note is about #machine-learning concepts.

Status: #in-progress
```

### Nested Tags

```markdown
#parent/child
#parent/child/grandchild
```

Creates tag hierarchy.

**Examples:**
```markdown
#project/work/client-a
#project/personal/side-hustle
#status/active
#status/archived
```

**In Obsidian UI:**
- Tags displayed as hierarchy
- Filter by parent shows all children
- Organize tags logically

### Inline Tags

Tags can appear anywhere in text:

```markdown
Discussed #meeting-notes with team about #q1-planning.

#review-required
```

### Multi-Word Tags

```markdown
#multi-word-tag
#multi_word_tag
```

Use hyphens or underscores, not spaces.

## Frontmatter (YAML)

Structured metadata at the start of notes.

### Basic Frontmatter

```markdown
---
title: Note Title
author: Author Name
date: 2024-01-15
---

# Note Content
```

**Rules:**
- Must be at very start of file
- Enclosed in `---` delimiters
- YAML syntax
- Key-value pairs

### Common Fields

```markdown
---
title: Document Title
date: 2024-01-15
tags:
  - tag1
  - tag2
aliases:
  - Alternative Name
  - Shorthand
author: John Doe
status: draft
---
```

### Array Values

```markdown
---
tags:
  - project
  - important
categories: [work, planning]
---
```

Both syntaxes work (YAML list or inline array).

### Nested Objects

```markdown
---
metadata:
  created: 2024-01-15
  modified: 2024-01-20
  version: 1.2
project:
  name: Project Alpha
  status: active
  team:
    - Alice
    - Bob
---
```

### Obsidian-Specific Fields

```markdown
---
aliases:
  - Alt Name 1
  - Alt Name 2
tags:
  - vault-tag
cssclasses:
  - custom-theme
  - wide-page
---
```

**Special Fields:**
- `aliases` - Alternative names for wiki-links
- `tags` - Tags (alternative to inline `#tags`)
- `cssclasses` - Custom CSS classes for styling

## Task Lists (Checkboxes)

Extended checkbox syntax beyond standard markdown.

### Standard Checkboxes

```markdown
- [ ] Unchecked task
- [x] Completed task
- [X] Completed task (capital X works too)
```

### Extended Checkbox Types

```markdown
- [ ] To do
- [x] Done
- [>] Forwarded/Rescheduled
- [<] Scheduled
- [-] Cancelled
- [?] Question
- [!] Important
- [*] Star
- ["] Quote
- [l] Location
- [b] Bookmark
- [i] Information
- [S] Amount/Money
- [I] Idea
- [p] Pro
- [c] Con
- [f] Fire
- [k] Key
- [w] Win
- [u] Up
- [d] Down
```

**Note:** Extended types require Obsidian or plugins. Rendered specially in Obsidian UI.

### Nested Tasks

```markdown
- [ ] Parent task
  - [ ] Subtask 1
  - [x] Subtask 2
  - [ ] Subtask 3
    - [ ] Sub-subtask
```

## Callouts (Admonitions)

Styled information blocks.

### Basic Callout

```markdown
> [!note]
> This is a note callout.

> [!info]
> This is an info callout.
```

### Callout Types

```markdown
> [!note]
> Note content

> [!abstract] / [!summary] / [!tldr]
> Summary content

> [!info] / [!todo]
> Information

> [!tip] / [!hint] / [!important]
> Helpful tip

> [!success] / [!check] / [!done]
> Success message

> [!question] / [!help] / [!faq]
> Question content

> [!warning] / [!caution] / [!attention]
> Warning message

> [!failure] / [!fail] / [!missing]
> Error message

> [!danger] / [!error]
> Danger warning

> [!bug]
> Bug report

> [!example]
> Example content

> [!quote] / [!cite]
> Quoted text
```

### Callout with Title

```markdown
> [!note] Custom Title
> Content goes here.

> [!warning] Important Warning
> This is critical information.
```

### Foldable Callouts

```markdown
> [!note]- Collapsed by default
> Content hidden initially.

> [!note]+ Expanded by default
> Content visible initially.
```

### Nested Callouts

```markdown
> [!info] Outer callout
> Information here.
>
> > [!warning] Nested callout
> > Nested warning.
```

## Code Blocks

### Basic Code Blocks

````markdown
```
Plain code block
```

```javascript
console.log("JavaScript code");
```

```python
print("Python code")
```
````

### With Line Numbers

Obsidian doesn't natively support line numbers, but some plugins do.

## Tables

### Basic Tables

```markdown
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Row 1    | Data     | Data     |
| Row 2    | Data     | Data     |
```

### Alignment

```markdown
| Left | Center | Right |
| :--- | :----: | ----: |
| L1   | C1     | R1    |
| L2   | C2     | R2    |
```

### Tables with Links

```markdown
| Project | Status | Notes |
| ------- | ------ | ----- |
| [[Project A]] | #active | See [[Notes]] |
| [[Project B]] | #done | Complete |
```

## Comments

```markdown
%%
This is a comment.
Multi-line comments are supported.
%%

Regular text. %% Inline comment %%
```

**Rules:**
- Enclosed in `%%`
- Not rendered in reading view
- Can be inline or multi-line

## Footnotes

```markdown
Here's a sentence with a footnote[^1].

[^1]: This is the footnote content.

Another reference[^note].

[^note]: Named footnotes work too.
```

## Obsidian URI

Link to open notes in Obsidian app:

```markdown
obsidian://open?vault=VaultName&file=NoteName

[Open Note](obsidian://open?vault=MyVault&file=folder/note)
```

## Combining Syntax

### Complex Examples

```markdown
---
title: Project Plan
tags:
  - project
  - planning
status: active
---

# [[Projects|Project]]: Mobile App Redesign

## Overview

This project focuses on #ui-ux improvements. See [[Design System]] for details.

## Tasks

- [ ] Review [[Requirements#Functional|functional requirements]]
- [x] Create [[Wireframes]]
- [>] Schedule meeting with #stakeholders
- [ ] Update [[Project Timeline]]

## References

![[Design Principles#Core Values]]

> [!tip] Best Practice
> Always link to [[Style Guide]] when implementing designs.

## Related

- [[Previous Projects#Mobile|Past mobile work]]
- [[Team Members|Team]]

#project/mobile #status/in-progress
```

## Best Practices

1. **Use wiki-links liberally** - Create connections between related notes
2. **Consistent tag hierarchy** - Use nested tags for organization (`#project/work/client`)
3. **Frontmatter for metadata** - Structure data that's queried frequently
4. **Aliases for flexibility** - Add aliases for common alternative names
5. **Descriptive link text** - Use aliases when natural reading flow matters
6. **Block links sparingly** - For specific references within longer notes
7. **Comments for drafts** - Use `%%` for notes to self that shouldn't be published
8. **Callouts for emphasis** - Highlight important information visually

## Compatibility Notes

- Standard markdown works everywhere
- Wiki-links are Obsidian-specific (convert to regular links for export)
- Extended checkboxes may need plugins outside Obsidian
- Callouts are Obsidian-specific (render as blockquotes elsewhere)
- Frontmatter is standard YAML (works in most markdown processors)
- Comments (`%%`) are Obsidian-specific
- Tags work in Obsidian; may be ignored elsewhere

## See Also

- [obsidian-cli Reference](./obsidian-cli-reference.md) - Command-line vault operations
- [Note Templates](../assets/templates/) - Ready-to-use note structures
