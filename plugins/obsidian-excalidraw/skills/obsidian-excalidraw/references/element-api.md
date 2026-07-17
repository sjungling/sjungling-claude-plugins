# Excalidraw Element API Reference

## Common fields (all element types)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique within the document. Use short descriptive IDs. |
| `type` | string | `ellipse`, `rectangle`, `text`, `arrow` |
| `x`, `y` | number | Top-left corner of bounding box |
| `width`, `height` | number | Bounding box dimensions |
| `angle` | number | Rotation in radians. Use `0`. |
| `strokeColor` | string | Hex color for border/line |
| `backgroundColor` | string | Hex color for fill, or `"transparent"` |
| `fillStyle` | string | `"solid"` for filled shapes, `"hachure"` for arrows/text |
| `strokeWidth` | number | `1`–`4`. Use `2` for nodes, `1` for text. |
| `strokeStyle` | string | `"solid"` or `"dashed"` |
| `roughness` | number | `0` = clean, `1` = hand-drawn. Use `0`. |
| `opacity` | number | `0`–`100`. Use `100`. |
| `groupIds` | array | Leave `[]` unless grouping. |
| `roundness` | object | `{"type": 2}` for ellipses/arrows, `{"type": 3}` for rounded rects, `null` for sharp rects |
| `seed` | number | Any integer. Affects roughness rendering. |
| `version` | number | Use `1`. |
| `versionNonce` | number | Use same as `seed`. |
| `isDeleted` | boolean | Always `false`. |
| `boundElements` | array | For shapes: `[{"type": "text", "id": "text-id"}]`. For text bound to shape: `[]`. |
| `updated` | number | Unix timestamp ms. Use `Date.now()` or any fixed value. |
| `link` | null | Always `null`. |
| `locked` | boolean | Always `false`. |

## Ellipse

```json
{
  "type": "ellipse",
  "roundness": { "type": 2 },
  "boundElements": [{ "type": "text", "id": "node1__label" }]
}
```

## Rectangle

```json
{
  "type": "rectangle",
  "roundness": { "type": 3 },
  "boundElements": [{ "type": "text", "id": "box1__label" }]
}
```

Use `"roundness": null` for sharp corners.

**There is no `label` shorthand property in real Excalidraw JSON.** A labeled
shape is always TWO elements: the container (rectangle/ellipse/arrow) plus a
separate `text` element whose `containerId` points back at the container —
and the container's own `boundElements` must list that text element. Writing
a `label` field directly on the container is silently ignored by Excalidraw
(and by Obsidian's renderer): the shape draws with no visible text at all.

`node()`, `box()`, `annotationBox()`, and `arrow()` in `shapes.js` handle this
for you — pass a label string and they return `[shape, text]` (or `[arrow,
text]`) with the binding already wired. Always spread or push the full
return value; do not discard the second element.

## Text (floating or bound)

Additional fields:

| Field | Type | Notes |
|---|---|---|
| `text` | string | Use `\n` for line breaks |
| `originalText` | string | Same as `text` |
| `fontSize` | number | `11`–`22`. Use `13`–`14` for node labels. |
| `fontFamily` | number | `1` = Virgil (handwritten), `2` = Helvetica, `3` = Cascadia |
| `textAlign` | string | `"center"`, `"left"`, `"right"` |
| `verticalAlign` | string | `"middle"`, `"top"` |
| `baseline` | number | Set equal to `fontSize` |
| `containerId` | string\|null | ID of parent shape if bound, else `null` |

**Floating text**: set `containerId: null`. Use `floatingLabel()` in `shapes.js`.

**Bound text** (shape/arrow labels): `containerId` is the id of the shape or
arrow it labels. The container must list `{"type": "text", "id": <this id>}`
in its own `boundElements`. `shapes.js` computes an approximate `x/y/width/height`
for the bound text (centered in the container, or top-left for annotation
boxes) since there's no canvas available to measure real text metrics — good
enough for the embedded preview, but expect Excalidraw to reflow it slightly
once the file is opened and edited in the app.

## Arrow

Additional fields:

| Field | Type | Notes |
|---|---|---|
| `points` | array | `[[0,0], [dx, dy]]`. Relative to arrow `x,y`. |
| `startBinding` | object\|null | `{"elementId": "ID", "focus": 0, "gap": 6}` |
| `endBinding` | object\|null | Same shape |
| `startArrowhead` | string\|null | `null` for no arrowhead at start |
| `endArrowhead` | string | `"arrow"` for standard arrowhead |
| `elbowed` | boolean | `false` for curved/straight, `true` for right-angle elbows |
| `roundness` | object | `{"type": 2}` for curved arrows |

**`focus`**: `-1` to `1`. `0` = center of edge. Shift to control which part of the shape edge the arrow attaches to.

**`gap`**: pixels between arrowhead and shape edge. Use `5`–`8`.

**Arrow `x,y`**: place near the center of the source shape. The binding system overrides the exact start/end points.

### Binding is bidirectional (required for a real connection)

`startBinding`/`endBinding` on the arrow are only half of a connection. Each endpoint **shape** must also list the arrow in its `boundElements`:

```json
// arrow
{ "id": "a1", "type": "arrow", "startBinding": { "elementId": "m1", ... }, "endBinding": { "elementId": "g1", ... } }
// shape m1 — must reference the arrow back
{ "id": "m1", "type": "rectangle", "boundElements": [{ "type": "arrow", "id": "a1" }] }
```

Set only the arrow's start/endBinding and the line *looks* attached but won't follow the shape when it moves. `shapes.js` fills in the shape→arrow back-references for you in `document()` (via `linkBindings`); if you build elements by hand, add them yourself.

### Arrow label (inline)

Pass `opts.label` to `ex.arrow(...)` — it returns `[arrow, text]` with a
separate text element bound via `containerId`, positioned at the arrow's
midpoint:

```json
// arrow
{ "id": "a1", "type": "arrow", "boundElements": [{ "type": "text", "id": "a1__label" }], ... }
// bound text, positioned at the arrow midpoint
{ "id": "a1__label", "type": "text", "containerId": "a1", "text": "calls", "fontSize": 11, ... }
```

Keep labels to ~1–3 words — the line segment is short and long text overruns it.

## Annotation box pattern

A rectangle with left/top-aligned bound text — use for callout notes. `ex.annotationBox(id, x, y, w, h, text)` builds both elements for you:

```json
// container
{
  "id": "note",
  "type": "rectangle",
  "x": 40, "y": 600, "width": 600, "height": 120,
  "strokeColor": "#d1d5db",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roundness": { "type": 3 },
  "boundElements": [{ "type": "text", "id": "note__label" }]
}
// bound text, top-left aligned inside the container
{
  "id": "note__label",
  "type": "text",
  "containerId": "note",
  "text": "Line 1\nLine 2\nLine 3",
  "fontSize": 12,
  "textAlign": "left",
  "verticalAlign": "top"
}
```
