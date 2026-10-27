# Excalidraw element shape

What a diagram's JSON has to look like, so you can size, check and hand-edit one
with confidence. Verified against excaligen 0.11.14's output and Excalidraw
0.18.x, and consistent with the element format of the Excalidraw MCP servers.
`obsidian_preset` and excaligen already produce all of this; read it when output
looks wrong, or when you post-process JSON by hand.

## Bound text: both sides record the link

A label on a shape or arrow is a separate `text` element:

- the text has `containerId` set to the shape's id, `textAlign: "center"` and `verticalAlign: "middle"`;
- the shape lists it in `boundElements`: `{ "type": "text", "id": "<text id>" }`.

Dropping either side leaves an orphan text that Excalidraw draws unattached.

## Arrow bindings

An arrow's `startBinding` / `endBinding` name the shape it touches, and the shape
lists the arrow in `boundElements` (`{ "type": "arrow", "id": ... }`). That is what
keeps an arrow attached when someone drags a shape.

- Plain arrows bind as `{ "elementId", "focus": 0, "gap": 1 }`. This is what excaligen writes.
- `fixedPoint` (`[1, 0.5]` is the right edge, `[0, 0.5]` the left) belongs to elbow arrows and newer Excalidraw builds; the MCP format uses it. On 0.18.x emit `focus` and `gap` as well.
- Always pass shape objects to `bind()` rather than coordinates; it writes both sides.

## Arrow geometry: sizes are positive, direction lives in `points`

`width` and `height` are the arrow's bounding box and are never negative.
`points` are offsets from `x`, `y`, and carry the direction. An arrow that runs
up and left has `width: 210, height: 123` and `points: [[0, 0], [-210, -123]]`.
Hand-built JSON with a negative `width` or `height` renders wrongly, and the
Excalidraw whiteboards service rejects it.

## Text size

Excalidraw's fonts measure close to 0.6 × `fontSize` per character, with a line
height of 1.25 × `fontSize`. excaligen records exactly this, and neither wraps
text nor grows a shape, so a label wider than its shape overflows it:

| | |
|---|---|
| text width | longest line × `fontSize` × 0.6 |
| text height | lines × `fontSize` × 1.25 |
| shape width | text width + 40 (ellipses and diamonds: × 1.41) |
| shape height | text height + 24 (ellipses and diamonds: × 1.41) |

`obsidian_preset.fit(label)` does this and floors the result at 120×60. A
multi-line label is not available here (the Obsidian CLI corrupts `\n`), so only
the single-line row applies.

## Layout and readability

- `fontsize` 16 or more for labels, 20 or more for titles, never below 14.
- 20 to 30 px between shapes. Fewer, larger shapes read better than many small ones.
- Draw order is z-order: create a container before what sits inside it, and arrows after the shapes they join.
- Text on white no lighter than `#757575`; the status palette in `SKILL.md` already complies.
- No emoji in labels: they do not render the same for everyone.
- To group shapes, put a dashed gray (`secondary`) rectangle behind them, created first, with a white fill. Colored zones render dark in embeds.

## Quick check of a generated file

```bash
# every arrow size is positive
jq '[.elements[] | select(.type=="arrow") | select(.width < 0 or .height < 0)] | length' d.excalidraw
# every label fits its shape (arrow labels sit on the arrow, so only shapes count)
jq '[.elements as $all | $all[] | select(.type=="text" and .containerId) as $t
     | $all[] | select(.id == $t.containerId and .type != "arrow" and .width < $t.width)] | length' d.excalidraw
```

Both should print `0`.
