---
description: One supervisor tick over all devpods (the cron job runs this)
allowed-tools: Bash, Read, Write, Edit, CronCreate, CronList, CronDelete
---

Run one supervisor check. Read `${CLAUDE_PLUGIN_ROOT}/references/playbook.md` and follow its rules exactly. Keep tool calls small and separate.

## Steps

1. Write the epoch time to `~/.local/state/devpod-supervisor/heartbeat`.
2. Read `schedule.txt` and `stopped-by-user.txt`. If a schedule override has ended, move the cron job back to the default rung (create the new job first, then delete the old one).
3. `timeout 60 devpod ls`. Skip pods in `stopped-by-user.txt` entirely.
4. For each other pod, look at its pane (or restart a stopped real-work pod) and judge it: working, waiting on a menu, idle, finished, stuck.
5. Act within the playbook: answer review menus that fit the rules, send continue or nudge messages, clear stale queued messages, and verify finished work with `gh`.
6. For each watched PR in `HANDOFF.md`, check state with `gh` (draft, review decision, checks, merged). Report only changes.
7. Report one short line per pod that changed. If nothing changed, print one line and stop.
8. Adjust the cron rung per "Cadence" in the playbook. Ask the user only about real decisions, and only once.
