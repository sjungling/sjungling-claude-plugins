# Excalidraw in Obsidian — Pitfalls

## 1. Colored fills render dark in Obsidian embeds

**Symptom:** Shapes with colored `backgroundColor` (e.g. `#bfdbfe`) look dark or unreadable when the diagram is embedded with `![[...]]` in a note.

**Cause:** The Excalidraw plugin applies Obsidian's active theme to embedded previews. In dark mode, colored fills get inverted or dimmed.

**Fix:** Always use `backgroundColor: "#ffffff"` for all shapes. Convey state through `strokeColor` and `strokeStyle` only.

```js
// ❌ Will look wrong in dark mode Obsidian embeds
ex.node('alice', 100, 80, 180, 70, 'Alice', { backgroundColor: '#bfdbfe' })

// ✅ Reads fine in any theme
ex.node('alice', 100, 80, 180, 70, 'Alice', { strokeColor: '#1d4ed8', strokeWidth: 2 })
```

**If fills are required:** Go to Obsidian Settings → Excalidraw → Embed & Export and disable "Match Obsidian theme", or add `|light` to the embed: `![[diagram.excalidraw|light]]`.

---

## 2. `node()` and `box()` return arrays — must spread

**Symptom:** Diagram renders with shapes but no labels, or labels appear in wrong positions.

**Cause:** `node()` returns `[ellipse, text]` — two elements. If not spread, the array itself gets added as a single element, which is invalid.

```js
// ❌ Wrong — wraps the array in another array
const elements = [ex.node('a', ...), ex.arrow(...)];

// ✅ Correct — spreads both elements into the flat array
const elements = [...ex.node('a', ...), ex.arrow(...)];
```

---

## 3. Arrow points are relative to arrow x,y

**Symptom:** Arrow appears at wrong position or doesn't connect to shapes.

**Cause:** Arrow `points` are relative offsets from the arrow's own `x,y`, not absolute canvas coordinates. `points[0]` must always be `[0, 0]`.

```js
// ❌ Wrong — using absolute coordinates
{ x: 100, y: 200, points: [[100, 200], [400, 300]] }

// ✅ Correct — using relative offset
{ x: 100, y: 200, points: [[0, 0], [300, 100]] }
```

The `shapes.js` helper handles this automatically when you pass `fromCenter` and `toCenter`.

---

## 4. Bound text containerId must match shape id exactly

**Symptom:** Text appears as floating text, not inside the shape; or shape has no label.

**Cause:** `containerId` on the text element must exactly match the shape's `id`. The shape's `boundElements` must include `{"type": "text", "id": "TEXT_ID"}`.

```json
// Shape
{ "id": "alice", "boundElements": [{ "type": "text", "id": "alice_t" }] }

// Text — containerId must match shape id
{ "id": "alice_t", "containerId": "alice" }
```

---

## 5. All element IDs must be unique

**Symptom:** Shapes disappear or overlap unexpectedly.

**Cause:** Duplicate IDs cause Excalidraw to silently drop or merge elements.

The `shapes.js` helper uses a monotonic counter for IDs when you pass explicit IDs, but if you generate IDs manually, ensure uniqueness across the full `elements` array.

---

## 6. Arrow `startBinding`/`endBinding` elementIds must reference existing elements

**Symptom:** Arrows float disconnected from shapes.

**Cause:** If the referenced element ID doesn't exist in the document, Excalidraw treats the binding as invalid and falls back to the arrow's raw coordinates.

Always add shapes to the elements array before (or in the same batch as) the arrows that reference them.

---

## 7. Very long text overflows ellipse bounds

**Symptom:** Text is clipped or overflows outside the shape.

**Cause:** Ellipses don't auto-grow to fit text. The text element height must fit within the shape's height.

**Fix:** Use `fontSize: 12` or `13` for 3-line labels in an 80px-tall shape. Or increase `height` of the shape. Rule of thumb: `height >= lineCount * (fontSize * 1.4)`.

---

## 8. iCloud vaults can't be written on the filesystem

**Symptom:** `Operation not permitted` when reading or writing any file under `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>` — even with the sandbox disabled. The diagram never appears.

**Cause:** macOS privacy (TCC) restricts the iCloud Drive directory to apps with the entitlement. Claude Code's process doesn't have it; the Obsidian app does. So `Write`/`node > file` simply cannot reach the vault.

**Fix:** Write through the Obsidian CLI, which proxies to the running app. Build the `.excalidraw.md` form with `scripts/to-obsidian-md.js` and `obsidian create … content=…`. Run the CLI **unsandboxed** (it hangs under the sandbox) and use **single-line labels** (the CLI corrupts `\n` in content).

```bash
node scripts/your-generator.js > /tmp/d.excalidraw          # single-line labels
node scripts/to-obsidian-md.js /tmp/d.excalidraw > /tmp/note.txt
obsidian create vault="My Vault" path="Diagrams/d.excalidraw.md" \
  content="$(cat /tmp/note.txt)" overwrite
```

See `icloud-vaults.md` for the complete workflow and why each constraint exists.
