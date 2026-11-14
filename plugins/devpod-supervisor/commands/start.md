---
description: Become the devpod supervisor for this session (adopts state from a handoff)
argument-hint: [--force]
allowed-tools: Bash, Read, Write, Edit, CronCreate, CronList, CronDelete
---

Start a devpod supervisor in this session. Read `${CLAUDE_PLUGIN_ROOT}/references/playbook.md` first and follow it for every rule below.

## Steps

1. Check tools: `tmux`, `devpod`, `coder`, `gh`, `jq` on PATH, and that you are inside tmux (`$TMUX`). Stop and say what is missing.
2. Create `~/.local/state/devpod-supervisor/ledgers` if needed.
3. Read `heartbeat`. If it is under 15 minutes old and `$ARGUMENTS` lacks `--force`, another supervisor is running (its cron jobs are invisible to this session). Tell the user and stop.
4. Title this tmux pane "supervisor" (`tmux select-pane -T supervisor`).
5. Adopt state: read `HANDOFF.md`, `stopped-by-user.txt` and `schedule.txt` if they exist. If the old `/tmp/devpod-ledgers` exists and `ledgers/` is empty, copy the small files over.
6. List the fleet with `timeout 60 devpod ls`. Rebuild any missing panes for working pods (attach only when the chat process exists).
7. `CronList`. If a "Devpod supervisor check" job exists, keep it; otherwise create exactly one cron job named "Devpod supervisor check" at `3-58/5 * * * *` (or the rung in `schedule.txt`) with the prompt `/devpod-supervisor:check`.
8. Write the epoch time to `heartbeat`, then run the first check by following `${CLAUDE_PLUGIN_ROOT}/commands/check.md`.
9. Report: pods and their jobs, pending user decisions from the handoff, and the cron rung. Keep it short.
