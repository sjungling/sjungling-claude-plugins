---
name: obsidian-excalidraw
description: Use when creating, editing, or embedding Excalidraw diagrams inside an Obsidian vault. Use when generating network diagrams, flowcharts, state machines, or relationship maps programmatically and saving them as .excalidraw files. Use when asked to visualize entities and their relationships, show state changes across diagrams, or embed diagrams in Obsidian markdown notes.
---

# Obsidian Excalidraw

Generate `.excalidraw` files programmatically and embed them in Obsidian markdown notes.

## Quick start

Use the helper module in `helpers/shapes.js` — it generates valid Excalidraw JSON with no dependencies:

```bash
# Run example to generate a diagram
node helpers/example.js > my-diagram.excalidraw
```

Or require it in your own script:

```js
const ex = require('./helpers/shapes');

const elements = [
  ...ex.node('alpha', 100, 80,  180, 70, 'Alpha\n(primary)'),
  ...ex.node('beta',  400, 80,  180, 70, 'Beta\n(secondary)', { strokeStyle: 'dashed', strokeColor: '#6b7280' }),
  ex.arrow('a1', 'beta', 'alpha', [490, 115], [190, 115]),
  ex.floatingLabel('l1', 290, 90, 'depends on'),
];

require('fs').writeFileSync('diagram.excalidraw', JSON.stringify(ex.document(elements), null, 2));
```

Embed in any Obsidian note:

```markdown
![[diagram.excalidraw]]
```

## How Obsidian stores Excalidraw files

**Write `.excalidraw` JSON → Obsidian converts it to `.excalidraw.md`.** The original `.excalidraw` disappears. The `.excalidraw.md` format wraps compressed JSON with a plaintext text-elements section (for Obsidian search/backlinks). You do not need to produce this format — write plain JSON and let the plugin convert.

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
| `ex.arrow(id, fromId, toId, fromCenter, toCenter, opts?)` | Bound arrow between two shapes |
| `ex.floatingLabel(id, x, y, text, opts?)` | Standalone text element |
| `ex.annotationBox(id, x, y, w, h, text, opts?)` | Note/annotation box with text |
| `ex.document(elements, opts?)` | Wraps element array in valid Excalidraw JSON |

Spread node/box results into the elements array: `[...ex.node(...), ...ex.node(...), ex.arrow(...)]`

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

Use the path to construct where to write diagram files:

```bash
VAULT=$(obsidian vault info=path)
node helpers/example.js > "$VAULT/Diagrams/my-diagram.excalidraw"
```

Then embed in a note:

```bash
obsidian create path="Diagrams/overview.md" content="![[my-diagram.excalidraw]]"
obsidian open path="Diagrams/overview.md"
```

## Pitfalls

See `references/pitfalls.md` for the full list. The three that matter most:

1. **Colored fills render dark in Obsidian embeds** — use `backgroundColor: "#ffffff"` always; convey state via stroke color/style only.
2. **`node()` and `box()` return arrays** — spread them: `[...ex.node(...), ex.arrow(...)]` not `[ex.node(...), ex.arrow(...)]`.
3. **Arrow `points` are relative to arrow `x,y`** — the helper handles this; if writing arrows manually, `points[0]` is always `[0,0]`.
