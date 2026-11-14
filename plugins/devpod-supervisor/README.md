# devpod-supervisor

Turn a Claude session into the supervisor for your devpods. It checks them on a timer, nudges stuck ones, answers review prompts that fit the rules, and verifies results on GitHub with `gh`.

## Commands

- `/devpod-supervisor:devpod` launches a review, research or factory devpod.
- `/devpod-supervisor:start` makes this session the supervisor. It sets up the schedule and picks up state from a handoff.
- `/devpod-supervisor:check` runs one check. The schedule calls this for you.
- `/devpod-supervisor:handoff` saves the fleet, watched PRs and open questions so a new session can take over.

The `devpod-inspector` agent is a read-only helper. It summarizes one pod and checks for unpushed work before a removal.

## Why commands and not one agent

A subagent runs once and returns. The supervisor needs to own a tmux pane, keep a cron job alive, and talk to you across turns. That has to live in the main session.

## Taking over

Run `/devpod-supervisor:handoff` in the old session. In the new one, run `/devpod-supervisor:start`. Start refuses if a supervisor ran in the last 15 minutes. Use `--force` to override.

State lives in `~/.local/state/devpod-supervisor/`. The rules live in `references/playbook.md`. Change them there.

## Needs

`tmux`, `devpod`, `coder`, `gh` and `jq`, and a session running inside tmux. Cron jobs belong to the session and expire after seven days, so `start` creates a fresh one.
