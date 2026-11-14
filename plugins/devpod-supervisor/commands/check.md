---
description: One supervisor tick over all devpods (the cron job runs this)
allowed-tools: Bash, Read, Write, Edit, CronCreate, CronList, CronDelete
---

Run one check. Follow `${CLAUDE_PLUGIN_ROOT}/references/playbook.md`. Keep tool calls small and separate.

1. Write `heartbeat`. Read `schedule.txt` and `stopped-by-user.txt`; if an override ended, restore the 5-minute rung.
2. `timeout 60 devpod ls`, plus `timeout 60 coder list --search "owner:me"` for non-devpod workspaces. Skip stopped-by-user pods.
3. Judge each other pod from its pane; restart stopped real-work pods.
4. Act per the playbook: answer fitting review menus, nudge, clear stale queued messages, verify finished work on `gh`.
5. Check each watched PR in `HANDOFF.md` on `gh`; report changes only.
6. One line per changed pod, or one line total if nothing changed.
7. Adjust the rung per "Cadence". Ask the user only real decisions, once.
