---
name: obsidian-excalidraw
description: This skill should be used when the user asks to "create an excalidraw diagram", "generate a diagram in Obsidian", "add a diagram to my vault", "embed a diagram", "make a flowchart", "visualize relationships", "draw a network diagram", or wants to programmatically generate .excalidraw files for an Obsidian vault. Also use when the user asks to update or regenerate an existing diagram file.
---

# Obsidian Excalidraw

Generate `.excalidraw` files programmatically and embed them in Obsidian markdown notes.

## Quick start

Use the helper module in `scripts/shapes.js` — it generates valid Excalidraw JSON with no dependencies:

```bash
# Run the working example to generate a diagram
node examples/example.js > my-diagram.excalidraw

# Inspect or validate generated JSON with jq (never python)
node examples/example.js | jq '.elements | length'
node examples/example.js | jq '.elements[] | select(.type == "arrow") | .id'
```

Or require it in your own script:

```js
const ex = require('./scripts/shapes');

const elements = [
  ...ex.node('alpha', 100, 80,  180, 70, 'Alpha\n(primary)'),
  ...ex.node('beta',  400, 80,  180, 70, 'Beta\n(secondary)', { strokeStyle: 'dashed', strokeColor: '#6b7280' }),
  ex.arrow('a1', 'beta', 'alpha', [490, 115], [190, 115]),
  ex.floatingLabel('l1', 290, 90, 'depends on'),
];

require('fs').writeFileSync('diagram.excalidraw', JSON.stringify(ex.document(elements), null, 2));
// shapes.js lives in scripts/ — adjust the relative path if requiring from elsewhere
```

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
node myscript.js > /vault/FolderName/diagram.excalidraw

# Wrong: breaks iCloud sync tracking, loses undo history,
# and leaves dangling ![[diagram.excalidraw]] embeds in other notes
rm /vault/FolderName/diagram.excalidraw.md   # ❌
```

Use the `Write` tool when saving from Claude — it overwrites in place without deleting.

## File format (what you write)

Every `.excalidraw` file you generate is JSON with this structure:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [ ... ],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

`elements` is the only array you need to populate. See `references/element-api.md` for all fields.

## Shape helpers — what's available

| Function | Generates |
|---|---|
| `ex.node(id, x, y, w, h, label, opts?)` | Ellipse + bound text (returns array of 2 elements) |
| `ex.box(id, x, y, w, h, label, opts?)` | Rectangle + bound text (returns array of 2 elements) |
| `ex.arrow(id, fromId, toId, fromPt, toPt, opts?)` | Connected arrow between two shapes; `opts.label` rides *on* the line |
| `ex.floatingLabel(id, x, y, text, opts?)` | Standalone text element |
| `ex.annotationBox(id, x, y, w, h, text, opts?)` | Note/annotation box with text |
| `ex.document(elements, opts?)` | Wraps element array in valid Excalidraw JSON (and wires up bindings) |
| `ex.rectEdge(rx, ry, rw, rh, tx, ty)` | Point on a rect boundary toward (tx,ty) — use as arrow fromPt/toPt |
| `ex.ellipseEdge(cx, cy, a, b, tx, ty)` | Point on an ellipse boundary toward (tx,ty) — use as arrow fromPt/toPt |

Spread node/box results into the elements array: `[...ex.node(...), ...ex.node(...), ex.arrow(...)]`

## Connecting shapes with arrows (binding)

**Use `ex.arrow(id, fromId, toId, ...)` for any arrow that represents a relationship between two shapes** — a flow, a dependency, a call. A bound arrow stays attached when either shape is moved or resized in Excalidraw, which is what makes a diagram editable rather than a brittle set of free-floating lines.

Connection in Excalidraw is **bidirectional** and both directions are required:
- the arrow names its endpoints via `startBinding`/`endBinding` (the factory sets these from the two shape IDs you pass), **and**
- each endpoint shape must list the arrow in its own `boundElements`.

You do **not** wire the second direction by hand — `ex.document(...)` runs a reconcile pass (`linkBindings`) that adds the shape→arrow back-references (and text→container links) automatically and idempotently. Just pass the shape IDs to `ex.arrow` and the labels' `containerId`s are handled for you. If you assemble raw element objects without `ex.document`, call `ex.linkBindings(flatArray)` yourself before wrapping, or the arrows will look connected but won't move with their shapes.

When **not** to bind: a caption, legend, title, or note that isn't anchored to a specific shape edge is a `floatingLabel`/`annotationBox`, not an arrow label. Don't fake a connector with a floating line.

### Always use edge-to-edge points — NOT center-to-center

**Obsidian's embedded preview renders the raw `points` array without applying Excalidraw's live binding calculation.** If you pass shape centers as `fromPt`/`toPt`, every arrow will pass straight through the shapes and converge at their centers in the embedded view.

**Always pass boundary intersection points** using the edge helpers:

```js
// For an arrow from a node (ellipse) to a box (rectangle):
const from = ex.ellipseEdge(u.cx, u.cy, u.w/2, u.h/2,  box.cx, box.cy);
const to   = ex.rectEdge(box.x, box.y, box.w, box.h,    u.cx,   u.cy);
ex.arrow('a1', 'user', 'api', from, to, { strokeColor: '#1d4ed8', gap: 0 });

// For an arrow between two rectangles:
const from = ex.rectEdge(src.x, src.y, src.w, src.h,  dst.cx, dst.cy);
const to   = ex.rectEdge(dst.x, dst.y, dst.w, dst.h,  src.cx, src.cy);
ex.arrow('a2', 'src', 'dst', from, to, { gap: 0 });
```

Use `gap: 0` alongside edge points — the default `gap: 6` is designed for center-to-center arrows and adds unnecessary offset when points are already on the boundary.

The `startBinding`/`endBinding` are still set automatically and keep arrows magnetically attached when shapes are moved in the Excalidraw editor.

### Arrow labels: bound and terse

`opts.label` creates a text element **bound to the arrow** (`containerId` = arrow id), so it renders on the line with a gap and moves with it — not a caption sitting beside it. **Keep arrow labels to ~1–3 words** (`"act-as hdr"`, `"signed email"`, `"verbatim"`); the label sits on a short line segment and long text overruns it and collides with the shapes. Put any longer explanation in an `annotationBox` near the shapes instead.

```js
// edge-to-edge, with a terse on-line label — back-references added by document()
const from = ex.rectEdge(src.x, src.y, src.w, src.h, dst.cx, dst.cy);
const to   = ex.rectEdge(dst.x, dst.y, dst.w, dst.h, src.cx, src.cy);
ex.arrow('a1', 'src', 'dst', from, to, { label: 'calls', strokeColor: '#dc2626', gap: 0 })
```

## Status color system

Use stroke color + style to show state. **Always keep fills white** — colored fills render dark in Obsidian's embedded preview regardless of the file content.

| State | strokeColor | backgroundColor | strokeWidth | strokeStyle |
|---|---|---|---|---|
| Active / normal | `#1d4ed8` (blue) | `#ffffff` | 2 | solid |
| Lapsed / cancelled | `#dc2626` (red) | `#ffffff` | 3 | solid |
| Secondary / decorative | `#6b7280` (gray) | `#ffffff` | 2 | dashed |
| Paused relationship | `#9ca3af` | transparent | 2 | dashed |
| Removed relationship | `#dc2626` | transparent | 2 | dashed |

Pass these as `opts`: `ex.node('id', x, y, w, h, 'Label', { strokeColor: '#dc2626', strokeWidth: 3 })`

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
node examples/example.js > "$VAULT/Diagrams/my-diagram.excalidraw"
obsidian create path="Diagrams/overview.md" content="![[my-diagram.excalidraw]]"
obsidian open path="Diagrams/overview.md"
```

### Route B — iCloud vault (filesystem blocked)

Paths under `~/Library/Mobile Documents/...` return `Operation not permitted` on read/write — only the Obsidian app can touch them. Use the `scripts/write-to-vault.js` helper: it builds the `.excalidraw.md` form, chunks it under the CLI's ~10KB payload limit, streams it via `create`+`append`, retries transient errors, and verifies the result by reading it back. **Run it unsandboxed** (the CLI hangs under the sandbox) and use single-line labels (no `\n`, no `"`):

```bash
node scripts/your-generator.js > "$TMPDIR/diagram.excalidraw"   # compact, single-line labels
node scripts/write-to-vault.js \
  --vault "My Vault" \
  --path  "Diagrams/my-diagram.excalidraw.md" \
  --input "$TMPDIR/diagram.excalidraw"
obsidian open vault="My Vault" path="Diagrams/my-diagram.excalidraw.md"
```

Key gotchas (all handled by the script): the CLI's per-call payload limit is ~10KB and oversized writes **fail silently**; the `Created:`/`Appended to:` confirmation line is omitted for larger successful writes, so success is gated by a read-back element count, not that line; and `overwrite` **no-ops on a note that's currently open** in Obsidian — close it first. Use `$TMPDIR`, never `/tmp` (sandbox blocks `/tmp`).

See `references/icloud-vaults.md` for the full rationale, the manual single-`create` route for tiny diagrams, and verification steps.

## Pitfalls

The most common issues:

1. **Colored fills render dark in Obsidian embeds** — use `backgroundColor: "#ffffff"` always; convey state via stroke color/style only.
2. **`node()` and `box()` return arrays** — spread them: `[...ex.node(...), ex.arrow(...)]` not `[ex.node(...), ex.arrow(...)]`.
3. **Arrow `points` are relative to arrow `x,y`** — the helper handles this; if writing arrows manually, `points[0]` is always `[0,0]`.
4. **iCloud vaults can't be written on the filesystem** — `~/Library/Mobile Documents/...` is blocked by macOS; use the CLI route (Route B above) via `scripts/write-to-vault.js`. Single-line labels only, and no `"` characters in label text.

See `references/pitfalls.md` for all 9 pitfalls with examples.

## Additional Resources

### Reference Files

- **`references/element-api.md`** — Full field reference for all element types (ellipse, rectangle, text, arrow), including every required field and valid values
- **`references/obsidian-file-format.md`** — How Obsidian converts `.excalidraw` to `.excalidraw.md`, the scaffold structure, update-in-place rules, and decompression instructions
- **`references/icloud-vaults.md`** — Writing diagrams into iCloud-synced vaults (filesystem blocked) via the Obsidian CLI, with the format/escape constraints and verification steps
- **`references/pitfalls.md`** — 9 common mistakes with before/after examples

### Scripts

- **`scripts/shapes.js`** — Zero-dependency factory module: `node()`, `box()`, `arrow()`, `annotationBox()`, `floatingLabel()`, `document()`
- **`scripts/write-to-vault.js`** — Recommended writer for iCloud vaults (Route B). Takes `--vault`, `--path`, `--input` (or stdin); builds the `.excalidraw.md`, chunks under the CLI ~10KB limit, streams via `create`+`append` with retries, and verifies by read-back. Run unsandboxed.
- **`scripts/to-obsidian-md.js`** — Lower-level helper: wrap compact `.excalidraw` JSON into single-line `.excalidraw.md` content for a single manual `create` (tiny diagrams only). Guards against escape-sequence corruption.

### Examples

- **`examples/example.js`** — Runnable org-chart diagram; pipe to a `.excalidraw` file and drop into an Obsidian vault to verify output
