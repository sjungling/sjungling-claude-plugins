# Obsidian Excalidraw File Format

## What Obsidian actually stores

When you write a `.excalidraw` JSON file to an Obsidian vault, the Excalidraw plugin converts it to `.excalidraw.md` format. The original `.excalidraw` file disappears.

**Example path:**
```
MyProject — Overview.excalidraw.md
```

## The `.excalidraw.md` structure

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data

## Text Elements
[All text content in the diagram, one block per text element]
Each element ends with a ^id anchor tag.

%%
## Drawing
```compressed-json
[zlib-compressed, base64-encoded Excalidraw JSON]
```
%%
```

The `## Text Elements` section is plaintext — Obsidian's search and backlinks index it. The `compressed-json` block is opaque; only the Excalidraw plugin reads it.

## The conversion workflow

```
You write:    name.excalidraw       (plain JSON)
Obsidian:     converts → name.excalidraw.md
              (original .excalidraw is removed)
You embed:    ![[name.excalidraw]]  (wikilink still resolves to .excalidraw.md)
```

## Embedding

Both extensions work in a wikilink:

```markdown
![[MyProject — Overview.excalidraw]]
![[MyProject — Overview.excalidraw.md]]
```

Obsidian resolves both to the same file.

## Updating a diagram — MUST update in place

**Never delete a `.excalidraw.md` file and recreate it.** Always update by writing a new `.excalidraw` to the same base filename:

```bash
# Correct: write new JSON with the same base name
node helpers/example.js > /path/to/vault/diagram.excalidraw
# Obsidian converts it → diagram.excalidraw.md (overwrites existing)
# All ![[diagram.excalidraw]] embeds continue to resolve

# Wrong: deleting first breaks iCloud sync tracking and
# can leave dangling embed references in notes
rm /path/to/vault/diagram.excalidraw.md  # ❌ don't do this
```

**Why this matters:**
- Obsidian tracks files by path; delete+recreate can confuse iCloud sync
- Other notes that embed `![[diagram.excalidraw]]` reference the filename — renaming breaks them
- The Excalidraw plugin may lose undo history and version state on the file

## Decompressing for inspection

To see the raw JSON inside a `.excalidraw.md` file:

In Obsidian: open the file → Command Palette → "Decompress current Excalidraw file"

This replaces the `compressed-json` block with the raw JSON temporarily. Save it back to re-compress.
