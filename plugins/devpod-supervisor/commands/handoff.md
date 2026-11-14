---
description: Write a state snapshot so another session can take over as supervisor
allowed-tools: Bash, Read, Write
---

Write `$STATE/HANDOFF.md` (see `${CLAUDE_PLUGIN_ROOT}/references/playbook.md`) from `devpod ls`, the panes, `gh` and this conversation. No secrets. One short section each:

1. **Fleet**: pod, flavor, size, status, job, PR links.
2. **Watched PRs**: repo, number, state, what is awaited.
3. **Pending user decisions**: already asked, unanswered; don't re-ask.
4. **Standing instructions**: user rules not in the playbook.
5. **Cadence**: rung and any override with end time.
6. **Open cleanup**: user-owned tasks.
7. **Pitfalls**: new lessons for the playbook.

Also write `stopped-by-user.txt`. Print the path and a three-line summary. The new session runs `/devpod-supervisor:start`.
