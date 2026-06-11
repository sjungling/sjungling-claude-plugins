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
  "boundElements": [{ "type": "text", "id": "TEXTID" }]
}
```

## Rectangle

```json
{
  "type": "rectangle",
  "roundness": { "type": 3 },
  "boundElements": [{ "type": "text", "id": "TEXTID" }]
}
```

Use `"roundness": null` for sharp corners.

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

**Bound text** (label inside a shape): set `containerId` to the shape's ID; set `boundElements: []`; set the shape's `boundElements` to include this text's ID.

**Floating text**: set `containerId: null`.

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
{ "id": "m1", "type": "rectangle", "boundElements": [{ "type": "text", "id": "m1_t" }, { "type": "arrow", "id": "a1" }] }
```

Set only the arrow's start/endBinding and the line *looks* attached but won't follow the shape when it moves. `shapes.js` fills in the shape→arrow back-references for you in `document()` (via `linkBindings`); if you build elements by hand, add them yourself.

### Bound arrow label (label on the line)

A label that rides on the arrow is a `text` element with `containerId` set to the **arrow's** id, plus the arrow listing it in `boundElements`. Excalidraw pins it to the arrow midpoint and paints a gap over the line:

```json
{ "id": "a1", "type": "arrow", "boundElements": [{ "type": "text", "id": "a1_lbl" }], ... }
{ "id": "a1_lbl", "type": "text", "containerId": "a1", "text": "email arg", "textAlign": "center", "verticalAlign": "middle", ... }
```

Keep these labels to ~1–3 words — the line segment is short and long text overruns it. This differs from a floating caption (`containerId: null`), which is not attached to anything.

## Annotation box pattern

A rectangle with a text element bound to it — use for callout notes:

```json
[
  {
    "id": "note",
    "type": "rectangle",
    "x": 40, "y": 600, "width": 600, "height": 120,
    "strokeColor": "#d1d5db",
    "backgroundColor": "#ffffff",
    "fillStyle": "solid",
    "strokeWidth": 1,
    "roundness": { "type": 3 },
    "boundElements": [{ "type": "text", "id": "note_t" }],
    ...
  },
  {
    "id": "note_t",
    "type": "text",
    "x": 55, "y": 615, "width": 570, "height": 90,
    "text": "Line 1\nLine 2\nLine 3",
    "fontSize": 12,
    "textAlign": "left",
    "verticalAlign": "top",
    "containerId": "note",
    ...
  }
]
```
