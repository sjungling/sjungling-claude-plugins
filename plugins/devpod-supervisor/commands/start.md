---
description: Become the devpod supervisor for this session (adopts state from STATE.md)
argument-hint: [--force]
allowed-tools: Bash, Read, Write, Edit, CronCreate, CronList, CronDelete
---

Start a devpod supervisor. Read `${CLAUDE_PLUGIN_ROOT}/references/playbook.md` and follow it.

1. Check `tmux`, `devpod`, `coder`, `gh`, `jq` and `$TMUX`; stop and name anything missing.
2. Create `$STATE/ledgers`.
3. If `heartbeat` is under 15 minutes old and `$ARGUMENTS` lacks `--force`, another supervisor is live; tell the user and stop.
4. `tmux select-pane -T supervisor`.
5. Adopt state: read `STATE.md` (or the older `HANDOFF.md`, renaming it), `stopped-by-user.txt`, `schedule.txt`. If `/tmp/devpod-ledgers` exists and `ledgers/` is empty, copy its small files.
6. `timeout 60 devpod ls`; rebuild panes for working pods.
7. `CronList`; if no "Devpod supervisor check" job exists, create one at `3-58/5 * * * *` (or the `schedule.txt` rung) with prompt `/devpod-supervisor:check`.
8. Write `heartbeat`, then run one check (`${CLAUDE_PLUGIN_ROOT}/commands/check.md`).
9. Report pods, pending user decisions from STATE.md, and the rung, briefly.
