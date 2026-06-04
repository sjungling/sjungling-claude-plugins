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
format (uncompressed). The `scripts/to-obsidian-md.js` helper builds that file.

```bash
# 1. Generate compact .excalidraw JSON (SINGLE-LINE labels only — see caveat)
node scripts/your-generator.js > /tmp/diagram.excalidraw

# 2. Wrap it as single-line .excalidraw.md note content
node scripts/to-obsidian-md.js /tmp/diagram.excalidraw > /tmp/note.txt

# 3. Write through the app (run UNSANDBOXED — see below)
obsidian create vault="My Vault" \
  path="Diagrams/my-diagram.excalidraw.md" \
  content="$(cat /tmp/note.txt)" overwrite

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

- **Run the CLI unsandboxed.** The `obsidian` CLI connects to the app over a
  local socket; the command sandbox blocks that and the call hangs. Run with the
  sandbox disabled and a timeout so a stuck call can't wedge the session.
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
