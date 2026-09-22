---
name: obsidian-excalidraw
description: This skill should be used when the user asks to "create an excalidraw diagram", "generate a diagram in Obsidian", "add a diagram to my vault", "embed a diagram", "make a flowchart", "visualize relationships", "draw a network diagram", or wants to programmatically generate .excalidraw files for an Obsidian vault. Also use when the user asks to update or regenerate an existing diagram file.
---

# Obsidian Excalidraw

Generate `.excalidraw` files programmatically and embed them in Obsidian markdown notes.

## Quick start

Write a generator script to `$TMPDIR`, make it executable, and run it. The PEP 723
header pins the SDK and the shebang self-invokes through `uv` — no venv, no install.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["excaligen==0.11.14"]
# ///
import sys
sys.path.insert(0, "<absolute path to this skill>/scripts")

from obsidian_preset import new_scene, styled

scene = new_scene()
user = styled(scene.ellipse("User").center(0, 0), "active")
api = styled(scene.rectangle("API Gateway").center(340, 0), "active")
scene.arrow("request").bind(user, api)
print(scene.json())
```

```bash
chmod +x "$TMPDIR/gen-diagram.py"
"$TMPDIR/gen-diagram.py" > "$TMPDIR/diagram.excalidraw"
```

`bind()` computes edge-to-edge geometry, bidirectional bindings, and bound text
labels automatically. Pass shape objects to `bind()` — never coordinates.

**Labels must be single-line** with no `"`, tab or backslash characters: the
Obsidian CLI corrupts them. `obsidian_preset` raises `InvalidLabelError` at
construction rather than letting a corrupt write through. Put longer explanations
in a separate `scene.text(...)` near the shapes.

Full library API: https://milanpiskla.github.io/excaligen/

Embed in any Obsidian note:

```markdown
![[diagram.excalidraw]]
```

## How Obsidian stores Excalidraw files

**Write `.excalidraw` JSON → Obsidian converts it to `.excalidraw.md`.** The original `.excalidraw` disappears. The `.excalidraw.md` format wraps compressed JSON with a plaintext text-elements section (for Obsidian search/backlinks). On a filesystem-writable vault, no need to produce this format — write plain JSON and let the plugin convert.

> **iCloud vaults are the exception.** Vaults under `~/Library/Mobile Documents/` cannot be written on the filesystem (macOS blocks the process — see "Writing to the vault" below). There you must write the `.excalidraw.md` form through the Obsidian CLI.

`![[name.excalidraw]]` embeds resolve to `name.excalidraw.md` automatically.

A live scaffold example of the converted format is in `references/obsidian-file-format.md`.

See `references/obsidian-file-format.md` for the full format breakdown and decompression instructions.

### Updating a diagram — always update in place

**Do not delete a `.excalidraw.md` file and recreate it.** Write a new `.excalidraw` to the same base filename and Obsidian overwrites the existing `.excalidraw.md`:

```bash
# Correct: same base name → Obsidian converts and overwrites .excalidraw.md
./gen-diagram.py > /vault/FolderName/diagram.excalidraw

# Wrong: breaks iCloud sync tracking, loses undo history,
# and leaves dangling ![[diagram.excalidraw]] embeds in other notes
rm /vault/FolderName/diagram.excalidraw.md   # ❌
```

Use the `Write` tool when saving from Claude — it overwrites in place without deleting.

## Status color system

Use stroke color + style to show state. **Always keep fills white** — colored fills render dark in Obsidian's embedded preview regardless of the file content.

| State | strokeColor | backgroundColor | strokeWidth | strokeStyle |
|---|---|---|---|---|
| Active / normal | `#1d4ed8` (blue) | `#ffffff` | 2 | solid |
| Lapsed / cancelled | `#dc2626` (red) | `#ffffff` | 3 | solid |
| Secondary / decorative | `#6b7280` (gray) | `#ffffff` | 2 | dashed |
| Paused relationship | `#9ca3af` | transparent | 2 | dashed |
| Removed relationship | `#dc2626` | transparent | 2 | dashed |

`obsidian_preset.SHAPE`/`LINK` encode these; apply with `styled(element, "lapsed")`.

## Finding the Obsidian vault path

```bash
# Current active vault's path on disk
obsidian vault info=path

# All known vaults with paths
obsidian vaults verbose
```

## Writing to the vault — pick the route by vault type

There are two ways to get a diagram into a vault. **Check which applies before writing.**

```bash
VAULT=$(obsidian vault info=path)
ls "$VAULT" >/dev/null 2>&1 && echo "filesystem-writable" || echo "blocked — use CLI route"
```

### Route A — filesystem-writable vault (default)

Ordinary paths (e.g. `~/Work/knowledge-base`). Write the raw `.excalidraw` and let the plugin convert:

```bash
./examples/example.py > "$VAULT/Diagrams/my-diagram.excalidraw"
obsidian create path="Diagrams/overview.md" content="![[my-diagram.excalidraw]]"
obsidian open path="Diagrams/overview.md"
```

### Route B — iCloud vault (filesystem blocked)

Paths under `~/Library/Mobile Documents/...` return `Operation not permitted` on read/write — only the Obsidian app can touch them. Use the `scripts/write_to_vault.py` helper: it builds the `.excalidraw.md` form, chunks it under the CLI's ~10KB payload limit, streams it via `create`+`append`, retries transient errors, and verifies the result by reading it back. **Run it unsandboxed** (the CLI hangs under the sandbox) and use single-line labels (no `\n`, no `"`):

```bash
./scripts/your-generator.py > "$TMPDIR/diagram.excalidraw"   # compact, single-line labels
./scripts/write_to_vault.py \
  --vault "My Vault" \
  --path  "Diagrams/my-diagram.excalidraw.md" \
  --input "$TMPDIR/diagram.excalidraw"
obsidian open vault="My Vault" path="Diagrams/my-diagram.excalidraw.md"
```

Key gotchas (all handled by the script): the CLI's per-call payload limit is ~10KB and oversized writes **fail silently**; the `Created:`/`Appended to:` confirmation line is omitted for larger successful writes, so success is gated by a read-back element count, not that line; and `overwrite` **no-ops on a note that's currently open** in Obsidian — close it first. Use `$TMPDIR`, never `/tmp` (sandbox blocks `/tmp`).

See `references/icloud-vaults.md` for the full rationale and verification steps.

## Pitfalls

The most common issues:

1. **Colored fills render dark in Obsidian embeds** — keep backgrounds white; convey state via stroke color/style only.
2. **Very long text overflows shape bounds** — shapes don't auto-grow to fit text; size for the label or keep it short.
3. **iCloud vaults can't be written on the filesystem** — `~/Library/Mobile Documents/...` is blocked by macOS; use the CLI route (Route B above) via `scripts/write_to_vault.py`. Single-line labels only, and no `"` characters in label text.
4. **CLI-written labels must not contain `"`** — `obsidian_preset` raises `InvalidLabelError` before you get a corrupt write.

See `references/pitfalls.md` for all 5 pitfalls with examples.

## Additional Resources

### Reference Files

- **`references/obsidian-file-format.md`** — How Obsidian converts `.excalidraw` to `.excalidraw.md`, the scaffold structure, update-in-place rules, and decompression instructions
- **`references/icloud-vaults.md`** — Writing diagrams into iCloud-synced vaults (filesystem blocked) via the Obsidian CLI, with the format/escape constraints and verification steps
- **`references/pitfalls.md`** — 5 common mistakes with before/after examples
- **excaligen API docs** — https://milanpiskla.github.io/excaligen/

### Scripts

- **`scripts/obsidian_preset.py`** — `new_scene()` (Obsidian-safe defaults), `styled(el, status)`, and the `SHAPE`/`LINK` palettes. Rejects multi-line labels.
- **`scripts/write_to_vault.py`** — the writer for all vaults. Takes `--vault`, `--path`, `--input`; chunks under the CLI ~10KB limit, streams via `create`+`append` with retries, and verifies by read-back. Run unsandboxed.

### Examples

- **`examples/example.py`** — Runnable service-overview diagram; run it and pipe to a `.excalidraw` file to verify output
