# Writing diagrams to iCloud-synced vaults

The default workflow — write a `.excalidraw` file to disk and let the Excalidraw
plugin convert it — only works when the vault is on a **filesystem-writable**
path. It fails for **iCloud-synced vaults**.

## The problem

Vaults under `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<name>`
are protected by macOS privacy (TCC). Claude Code's process gets
`Operation not permitted` on read **and** write — even with the sandbox
disabled. Only the Obsidian app itself has the entitlement to touch iCloud
Drive. So you cannot `Write`/`node > file` into these vaults at all.

Detect this case up front:

```bash
# iCloud vault paths contain "Mobile Documents"
case "$VAULT" in *"Mobile Documents"*) echo "iCloud — use the CLI route";; esac
# Or just probe: a failing `ls` means go through the app.
ls "$VAULT" >/dev/null 2>&1 || echo "blocked — use the CLI route"
```

## The fix: write through the Obsidian CLI

The `obsidian` CLI proxies to the running app, which *does* have iCloud access.
Use it to write the diagram as the Excalidraw plugin's native `.excalidraw.md`
format (uncompressed).

### Recommended: the `write-to-vault.js` helper

`scripts/write-to-vault.js` does the whole dance — wrapper build, chunked
`create`+`append`, banner filtering, transient-error retries, and a read-back
verify — given a vault, a path, and an `.excalidraw` file. Use it for any
diagram; it is the only safe path once a diagram is more than a few KB (see the
size limit below).

```bash
# Generate compact .excalidraw JSON (SINGLE-LINE labels only — see caveat)
node scripts/your-generator.js > "$TMPDIR/diagram.excalidraw"

# Write it (run UNSANDBOXED — the CLI hangs under the sandbox)
node scripts/write-to-vault.js \
  --vault "My Vault" \
  --path  "Diagrams/my-diagram.excalidraw.md" \
  --input "$TMPDIR/diagram.excalidraw"

# Then open it
obsidian open vault="My Vault" path="Diagrams/my-diagram.excalidraw.md"
```

The script exits non-zero with a specific reason if the write didn't fully land
(target note open in Obsidian, a chunk over the IPC limit, app wedged, etc.).

### Manual route (small diagrams, or to understand the mechanics)

For a small diagram you can build the note in one shot with `to-obsidian-md.js`
and a single `create`. **This only works while the whole note stays under the
IPC size limit (~10KB)** — above that, use the script above.

```bash
# 1. Generate compact .excalidraw JSON (SINGLE-LINE labels only)
node scripts/your-generator.js > "$TMPDIR/diagram.excalidraw"

# 2. Wrap it as single-line .excalidraw.md note content
node scripts/to-obsidian-md.js "$TMPDIR/diagram.excalidraw" > "$TMPDIR/note.txt"

# 3. Write through the app (run UNSANDBOXED — see below)
obsidian create vault="My Vault" \
  path="Diagrams/my-diagram.excalidraw.md" \
  content="$(cat "$TMPDIR/note.txt")" overwrite

# 4. Verify it round-tripped to valid JSON
obsidian read vault="My Vault" path="Diagrams/my-diagram.excalidraw.md" 2>/dev/null \
  | grep -v -E 'Loading updated app package|installer is out of date' \
  | sed 's/\\n/\n/g' \
  | awk '/^```json$/{f=1;next} /^```$/{f=0} f' | jq -e .

# 5. Open it
obsidian open vault="My Vault" path="Diagrams/my-diagram.excalidraw.md"
```

## Why each constraint exists

These are the non-obvious rules the helper and steps above encode:

- **There is a ~10KB payload ceiling per CLI call.** The CLI forwards each
  command to the already-running app over a process-singleton socket. A
  `content=` value past ~10–11KB fails — either a *silent* broken pipe
  (`write() failed: Broken pipe`, exit 0, nothing written) or an
  `Argument must be a file path or a NativeImage` error. This is why a whole
  >10KB note can't be written in one `create`; `write-to-vault.js` splits the
  drawing JSON into sub-limit chunks streamed with `append`. Splitting is safe
  **between elements** (after `},` outside any string) — the reassembled
  multi-line JSON is still valid, which is exactly why single-line labels matter.
- **The confirmation line is unreliable — verify by read-back instead.** The CLI
  prints `Created:`/`Overwrote:`/`Appended to:` for small payloads but OMITS it
  for larger ones that nonetheless succeed (a ~9KB append writes fine yet echoes
  nothing). Never gate success on that line. The authoritative check is reading
  the note back and counting `elements`, which `write-to-vault.js` does.
- **Don't write a note that's currently OPEN in Obsidian.** `create … overwrite`
  silently no-ops when the target note is open in the active editor. Close it (or
  write a fresh path) first; the read-back verify will flag the stale state.
- **Use `$TMPDIR`, not `/tmp`.** Under the command sandbox, `/tmp` writes return
  `Operation not permitted`. Stage generator output and note files in `$TMPDIR`.
- **Run the CLI unsandboxed.** The `obsidian` CLI connects to the app over a
  local socket; the command sandbox blocks that and the call hangs. Run with the
  sandbox disabled and a timeout so a stuck call can't wedge the session. An
  oversized payload can wedge the app's CLI handler (subsequent calls time out) —
  if that happens, restart Obsidian.
- **Filter the banner.** The CLI prints `Loading updated app package …` and
  `Your Obsidian installer is out of date …` to stdout. Strip those lines before
  parsing any output (`grep -v -E '…'`).
- **`obsidian create` only writes `.md`.** A `path=…something.excalidraw` is
  renamed to `…something.md`. A `path=…something.excalidraw.md` is preserved — so
  write the `.excalidraw.md` form directly. You cannot produce a raw
  `.excalidraw` file this way.
- **`content=` interprets escapes.** The CLI turns `\n`→newline, `\t`→tab,
  `\\`→`\`. The helper exploits this: the markdown wrapper is emitted as ONE
  physical line with literal `\n` markers, which the CLI expands into real lines.
- **The drawing JSON must be compact and plain.** Compact `JSON.stringify`
  (no indentation) has no structural newlines. Use **single-line labels** so no
  text value contains `\n` — otherwise the escape would corrupt the JSON.
  Double-escaping (`\\n`) does NOT round-trip cleanly. `to-obsidian-md.js`
  refuses to run if the JSON contains any escaped character.
- **Pass content via a variable, not an inline literal.** `content="$(cat note.txt)"`
  expands the file's bytes literally — the backticks of the ```json fence inside
  it are NOT command-substituted. Writing the fences inline in the script source
  would trigger substitution.

## The `.excalidraw.md` format produced

`to-obsidian-md.js` emits the uncompressed variant the plugin reads natively:

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data

## Text Elements
<one "text ^id" line per text element — indexes for search>

%%
## Drawing
```json
<compact excalidraw JSON, one line>
```
%%
```

The plugin renders from the `## Drawing` JSON; the `## Text Elements` section is
for Obsidian search/backlinks and is regenerated on save.

## Filesystem-writable vaults

Vaults on ordinary paths (e.g. `~/Work/knowledge-base`) need none of this —
write the raw `.excalidraw` file directly with the `Write` tool or `node > file`
and let the plugin convert it. See `obsidian-file-format.md`.
