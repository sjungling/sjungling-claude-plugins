---
description: Write a state snapshot so another session can take over as supervisor
allowed-tools: Bash, Read, Write
---

Write `~/.local/state/devpod-supervisor/HANDOFF.md`. Read `${CLAUDE_PLUGIN_ROOT}/references/playbook.md` for the state layout. Gather facts from `devpod ls`, the panes, `gh` and this conversation. Do not copy secrets.

Sections, each short:

1. **Fleet**: one line per pod: name, flavor, size, status, its job, PR links.
2. **Watched PRs**: repo, number, state, what is awaited.
3. **Pending user decisions**: questions already asked and not yet answered (do not re-ask them).
4. **Standing instructions**: rules the user gave this session that are not in the playbook (for example "keep pod X until PR Y merges").
5. **Cadence**: current rung and any override with its end time.
6. **Open cleanup**: tasks the user owns, such as local key files to delete or pipelines to sync.
7. **Pitfalls hit**: new lessons worth adding to the playbook.

Also write the stopped-by-user pods to `stopped-by-user.txt`. Print the file path and a three-line summary. To resume, the new session runs `/devpod-supervisor:start`.
