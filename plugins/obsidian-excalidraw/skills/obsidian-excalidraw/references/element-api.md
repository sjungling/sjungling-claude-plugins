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
  "boundElements": [],
  "label": { "text": "Node label", "fontSize": 13 }
}
```

## Rectangle

```json
{
  "type": "rectangle",
  "roundness": { "type": 3 },
  "boundElements": [],
  "label": { "text": "Box label", "fontSize": 13 }
}
```

Use `"roundness": null` for sharp corners. The `label` property is optional — omit it for unlabeled shapes. Excalidraw auto-centers the label and auto-resizes the container to fit.

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

Shape and arrow labels are set via the `label` property on the element itself — not via separate text elements.

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

Use the `label` property directly on the arrow element. Excalidraw pins it to the arrow midpoint:

```json
{ "id": "a1", "type": "arrow", "label": { "text": "calls", "fontSize": 11 }, ... }
```

Keep labels to ~1–3 words — the line segment is short and long text overruns it.

## Annotation box pattern

A rectangle with an inline `label` — use for callout notes:

```json
{
  "id": "note",
  "type": "rectangle",
  "x": 40, "y": 600, "width": 600, "height": 120,
  "strokeColor": "#d1d5db",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roundness": { "type": 3 },
  "boundElements": [],
  "label": { "text": "Line 1\nLine 2\nLine 3", "fontSize": 12, "textAlign": "left", "verticalAlign": "top" }
}
```
