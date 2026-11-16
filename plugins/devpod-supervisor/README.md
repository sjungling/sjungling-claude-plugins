# devpod-supervisor

Makes a Claude session the supervisor for your devpods: it checks them on a timer, nudges stuck ones, answers review prompts that fit the rules, and verifies results with `gh`.

## Commands

- `/devpod-supervisor:devpod` launches a review, research, factory or Dependabot-sweep devpod.
- `/devpod-supervisor:start` makes this session the supervisor and adopts a handoff.
- `/devpod-supervisor:check` runs one check; the schedule calls it.
- `/devpod-supervisor:handoff` refreshes `STATE.md` in full, with what only this conversation knows.

The `devpod-inspector` agent is a read-only helper: it summarizes one pod and checks for unpushed work.

## Why commands, not an agent

The supervisor must own a tmux pane, keep a cron job alive and talk to you across turns, so it lives in the main session.

## Taking over

`STATE.md` is updated on every check that changes something, so a new session can usually just run `start`. Run `handoff` first when you can, to add standing instructions from the conversation. `start` refuses if a supervisor ran in the last 15 minutes; use `--force` to override.

State lives in `~/.local/state/devpod-supervisor/`. Rules live in `references/playbook.md`.

Needs `tmux`, `devpod`, `coder`, `gh` and `jq`, and a session inside tmux. Cron jobs expire after seven days, so `start` makes a fresh one.
