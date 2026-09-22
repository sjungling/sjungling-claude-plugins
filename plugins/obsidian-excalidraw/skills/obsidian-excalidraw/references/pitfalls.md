# Excalidraw in Obsidian — Pitfalls

## 1. Colored fills render dark in Obsidian embeds

**Symptom:** Shapes with colored `backgroundColor` (e.g. `#bfdbfe`) look dark or unreadable when the diagram is embedded with `![[...]]` in a note.

**Cause:** The Excalidraw plugin applies Obsidian's active theme to embedded previews. In dark mode, colored fills get inverted or dimmed.

**Fix:** Always keep `background("#ffffff")`. Convey state through stroke color and style only.

**If fills are required:** Go to Obsidian Settings → Excalidraw → Embed & Export and disable "Match Obsidian theme", or add `|light` to the embed: `![[diagram.excalidraw|light]]`.

---

## 2. Very long text overflows ellipse bounds

**Symptom:** Text is clipped or overflows outside the shape.

**Cause:** Ellipses don't auto-grow to fit text. The text element height must fit within the shape's height.

**Fix:** Use a smaller `fontsize` for multi-line labels in a short shape, or increase the shape's height. Rule of thumb: `height >= lineCount * (fontsize * 1.4)`.

---

## 3. iCloud vaults can't be written on the filesystem

**Symptom:** `Operation not permitted` when reading or writing any file under `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>` — even with the sandbox disabled. The diagram never appears.

**Cause:** macOS privacy (TCC) restricts the iCloud Drive directory to apps with the entitlement. Claude Code's process doesn't have it; the Obsidian app does. So `Write`/direct file writes simply cannot reach the vault.

**Fix:** Write through the Obsidian CLI with `scripts/write_to_vault.py`, which proxies to the running app. Run the CLI **unsandboxed** (it hangs under the sandbox) and use **single-line labels** (the CLI corrupts `\n` in content).

```bash
./scripts/your-generator.py > "$TMPDIR/d.excalidraw"      # single-line labels, no " chars
./scripts/write_to_vault.py --vault "My Vault" \
  --path "Diagrams/d.excalidraw.md" --input "$TMPDIR/d.excalidraw"
```

Three traps the script handles for you, and you must respect if writing the CLI by hand:
- **~10KB per-call payload limit** — a larger `content=` fails silently (broken pipe, nothing written) or errors with `Argument must be a file path or a NativeImage`. Split the JSON into sub-limit chunks via `append` (between elements, so it stays valid JSON).
- **The `Created:`/`Appended to:` confirmation line is omitted for larger successful writes** — don't gate on it; verify by reading the note back and counting `elements`.
- **`overwrite` no-ops on a note that's currently open in Obsidian** — close it first.

Use `$TMPDIR`, never `/tmp` (the sandbox blocks `/tmp`). See `icloud-vaults.md` for the complete workflow and why each constraint exists.

---

## 4. CLI-written labels must not contain `"` (double-quote) characters

**Symptom:** `write_to_vault.py` aborts with "drawing JSON contains escaped characters", or a hand-written CLI `create` produces a corrupt note.

**Cause:** A `"` inside a text value is serialized by JSON encoding as `\"` — a backslash. The Obsidian CLI's `content=` interprets backslash escapes (`\n`, `\t`, `\\`), so any backslash in the drawing JSON gets corrupted on write. `obsidian_preset` raises `InvalidLabelError` at construction rather than letting a corrupt write through.

This only applies to the iCloud CLI route. Filesystem-writable vaults (raw `.excalidraw` written directly) have no such restriction.

---

## 5. Compressed diagrams can't be read back for updates

excaligen is write-only — no decoder — so updating an existing diagram means reading its JSON back out of the `.excalidraw.md`. Whether that is possible depends on how the diagram got there:

- **Route A** (write a raw `.excalidraw`, let Obsidian convert it): the `## Drawing` block is `compressed-json` from the moment of conversion. Not readable, even untouched.
- **Route B** (`write_to_vault.py`): a plain ```json block, readable — until a human opens and edits it in Obsidian, which re-saves it compressed.

On hitting a `compressed-json` block, ask the user to run Obsidian's "Decompress current Excalidraw file" command, or rebuild the diagram from its description. Do not fail silently.
