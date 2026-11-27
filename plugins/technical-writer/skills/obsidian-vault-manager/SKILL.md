---
name: obsidian-vault-manager
description: This skill should be used when writing notes into an Obsidian vault from Claude Code, especially an iCloud-synced vault, a note larger than a few KB, or a note that must match the vault's existing conventions. Covers the TCC and sandbox limits that break direct writes and the chunked, verified writer script. For general `obsidian` CLI syntax use the `obsidian:obsidian-cli` skill; for Obsidian markdown syntax use `obsidian:obsidian-markdown`.
---

# Obsidian Vault Manager

This skill sits on top of the official `obsidian:obsidian-cli` and `obsidian:obsidian-markdown` skills. Use those for CLI syntax and note syntax. This skill covers what they don't: writing reliably into vaults on macOS.

## Two limits that break writes

- **iCloud vaults are TCC-protected.** If the vault path contains `Mobile Documents` (check with `obsidian vault "<name>" info=path`), the `Write` tool can be blocked even with the sandbox off. Only the Obsidian app can write there, so go through the CLI.
- **The CLI hangs in the command sandbox.** It talks to the running app over a local socket the sandbox blocks. Run every `obsidian` call unsandboxed.

## Writing a note

| Note | How |
|------|-----|
| Small, single-line, any vault | `obsidian "vault=<name>" create path="folder/name.md" content="<text>"` |
| Multi-line, large, or iCloud | `node ${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-manager/scripts/write-markdown-to-vault.js --vault <name> --path <path> --input <file>` (unsandboxed) |
| Non-iCloud vault, one-off | `Write` tool on the vault path works and is simpler |

Use the script for anything substantial. A single `create`/`append` over ~10KB fails silently (exit 0, nothing written) or throws a `NativeImage` error. The script chunks under that limit, filters banner noise, retries transient errors, and reads the note back to verify.

The CLI turns every literal `\n` and `\t` in `content=` into a newline or tab, with no escape. Content with backslashes (LaTeX, Windows paths, escape examples) gets corrupted. Write it through the script from a file instead.

## Match the vault's conventions

Read an existing note in the target folder before creating one. Copy its tag names, frontmatter fields, backlink properties, and filename style:

```bash
obsidian "vault=<name>" read "<existing note name>"
```

## More

- [CLI caveats](./references/obsidian-cli-reference.md): active-vault detection, banner filtering, daily-note behavior, iCloud and sandbox notes.
- [Note templates](./assets/templates/): daily, project, and meeting templates.
