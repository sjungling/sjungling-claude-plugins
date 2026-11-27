# obsidian CLI Caveats

General CLI syntax lives in the official `obsidian:obsidian-cli` skill and in `obsidian help`. This file keeps only what that skill doesn't cover: the active-vault trick, daily-note behavior, and iCloud/sandbox rules.

## Default / active vault

Run `vault` with no name to get the **active vault** — the one currently open in the
Obsidian app. This is the CLI's implicit default when `vault=<name>` is omitted:

```bash
# Active vault name, from the tab-separated output (grep '^name' also drops the banner)
VAULT=$(obsidian vault | grep '^name' | cut -f2-)
```

> **Banner on stdout:** every `obsidian` call prepends startup lines to stdout ("Loading
> updated app package…", an installer-out-of-date notice, an `obsidian.md` URL). When
> capturing output into a variable, filter it — prefer a *positive* match on the shape you
> want (`grep '^name'`, `grep '\.md$'`) over blocklisting the banner text.

Daily-note commands (below) resolve against the active vault; targeting a non-active vault
with `vault=<name>` may return empty for daily operations if that vault isn't open.

## Daily notes

These operate on today's daily note in the **active vault** and require the core **Daily
Notes** (or **Periodic Notes**) plugin to be enabled and configured. If daily commands
return nothing, that plugin is off or the vault isn't the active one.

### daily

Create or open today's daily note.

```bash
obsidian "vault=<name>" daily
```

### daily:path

Print the vault-relative path of today's daily note. Empty output means no daily note is
configured — don't fabricate a path.

```bash
DAILY=$(obsidian "vault=<name>" daily:path)   # e.g. "Daily Journal/2026-07-15.md"
```

### daily:append / daily:prepend

Append (or prepend) content to today's daily note, creating it if needed. Block mode adds
a surrounding newline; pass `inline` to append without one.

```bash
obsidian "vault=<name>" daily:append content="- **14:32** Quick capture text"
```

For multi-line content, build it with `printf` and pass it via a variable. This is the preferred way to capture short summaries into a
daily note (see the `/obsidian:add-to-daily-note` command).

### daily:read

Print the current contents of today's daily note.

## iCloud vaults & sandboxing

Caveats when scripting the CLI:

- **iCloud vaults are TCC-protected.** For vaults under
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>`, the `Write` tool
  cannot touch the files — only the Obsidian app can, via the `obsidian` CLI. Always go
  through the CLI (or the chunked `write-markdown-to-vault.js` script) for these vaults,
  never a direct file write.
- **Disable the command sandbox for CLI calls.** The `obsidian` CLI connects to the
  running app over a local socket the sandbox blocks; a sandboxed call hangs. Run
  `obsidian ...` invocations unsandboxed.
- **`\n` / `\t` are converted.** The CLI turns literal `\n`/`\t` two-character sequences in
  `content=` into real newlines/tabs and cannot distinguish them from intended escapes.
  If a capture legitimately contains those sequences (e.g. a code sample about escaping),
  spot-check the result.

