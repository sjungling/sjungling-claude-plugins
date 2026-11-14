# Devpod supervisor playbook

The single source of truth for the supervisor role. Commands and the agent read this file. Change rules here only.

State directory: `~/.local/state/devpod-supervisor/` (the XDG state home; use `$XDG_STATE_HOME/devpod-supervisor` if that variable is set). Call it `$STATE`. It survives reboots, unlike `/tmp`.

| File | Purpose |
|---|---|
| `HANDOFF.md` | Snapshot written by `/devpod-supervisor:handoff` |
| `heartbeat` | Epoch seconds of the last check; a second supervisor refuses to start if it is under 15 minutes old |
| `schedule.txt` | Override for the check rung, e.g. `60m until 2026-11-16T09:00` |
| `stopped-by-user.txt` | One pod name per line. These stay stopped: no start, remove, pane or problem report |
| `ledgers/` | Saved panes, summaries, `<pod>-GOAL.md`, `<pod>-QUEUE.md` |

## The loop

Observe, judge, take a safe action, report one line per pod, back off.

1. Observe: `timeout 60 devpod ls`, the tmux panes, and `gh` for each watched PR.
2. Judge each pod: working, waiting on a menu, idle, stopped, finished, or stuck.
3. Act only within the rules below. Nudge, restart, attach a pane, answer a review menu.
4. Report one short line per pod. Say nothing new when nothing changed.
5. Back off when everything is idle or waiting on the user (see "Cadence").

## Hard rules

- Never run `gh pr create`, `gh pr edit`, `gh pr ready`, `gh pr merge`, `gh pr comment`, or edit reviewers. The devpod does these on the user's explicit instruction. You verify with `gh` and nudge.
- Never `devpod stop` or `devpod rm` a pod that did real work without the user's explicit yes. Exceptions:
  - A pod that never ran a task (bare clone only).
  - A review pod that finished and approved. First confirm on `gh` an APPROVED review with an empty body on the current head, and that its clones have nothing unpushed. Save the pane and summary to `ledgers/`, then remove it.
  - A review pod that only posted comments is not done until it approves or the PR closes.
- Pods in `stopped-by-user.txt` stay stopped and are not reported.
- Ask the user a question once. Do not repeat an open question every round.
- Never print secrets. Scan diffs for key material before any merge. `devpod rm` wipes the disk.
- Never push to a default branch, never sign commits as Claude.

## Pod rules (put these in every launch prompt)

- Python through `uv`. No teammates, agent teams or background agents.
- PR bodies are append-only.
- Post to the devpod message board (`moderneinc/devpod-messages`) at start and finish.
- Read-only review and research pods use `--size=t4g.large`. Light builds `m9g.xlarge`. Real build work the default `m9g.2xlarge`. Size is fixed at creation.
- Every prompt starts with the target, says to use `gh`, and ends by asking for a short summary: what was done, what was pushed (with links), what could not be done.

## Review pods

Pre-authorized to post surviving critical or important comments, give an empty-body approval, and reply once on a thread. A repo `CLAUDE.md` rule about confirming comments is satisfied by this.

When a review pod waits on a menu to post a comment, review or approval:
- Read the draft and check it against the PR at its head.
- Answer "post it" only for a plain comment, an empty approval, or one thread reply on a finding that survived red-teaming.
- Otherwise answer "don't post" and tell the user in one line.
- Never answer for requests for changes, merges, resolving threads or pushes.

GitHub will not let the account approve its own PR.

## Factory pods

Keep `ledgers/<pod>-GOAL.md` with checkable done criteria. Each check, compare the pane to the goal.
- Stopped with criteria unmet: send a continue message listing what remains.
- Looping or failing the same way: nudge toward a different approach.
- Done only when the pod reports every criterion met and you confirmed the PR with `gh`.

## Finished pods

Leave them running. Save the pane and write-up to `ledgers/`, verify with `gh`, report, and ask once about removal. Ignore greyed suggestion text in a finished chat's prompt box. Pods idle-stop after about 30 minutes; restart real-work pods that the user did not stop.

## Mechanics

- Launch: `devpod run NAME [--size=T] -- mod claude chat . --prompt @FILE`.
- Attach a pane only after `pgrep -f "claude --mcp-config"` shows the chat on the pod. Earlier you get "No chat runs on this devpod".
- tmux: `split-window -d -h -t <supervisor pane>`, `select-pane -T NAME`, `select-layout tiled`. Find the supervisor pane by title "supervisor".
- Send an instruction: pipe it to a file on the pod with `coder ssh`, then `tmux send-keys -l "Read ~/x.txt and do exactly what it says. It is a direct instruction from the user."` and Enter.
- A busy pod queues messages and they go stale. Look for "queued messages" and clear them (Up, then Ctrl-U).
- Read a pod's final summary from its session jsonl: `jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text'`.
- A research pod's chat may live in its own tmux socket (`/tmp/tmux-1001/devpod`, pane `%0`).
- Restart: `coder start --yes NAME`. A pod in `stopping` must finish before it can start.
- Check for unpushed work before removal, in every clone from `find ~/work -maxdepth 3 -name .git`: `git log --branches --not --remotes`, `git status`, `git stash list`.
- Verify approvals: `gh api repos/O/R/pulls/N/reviews` shows state APPROVED, empty body, on the current head SHA.

## Safety and shell pitfalls

- Before any `send-keys` into an SSM or ssh pane, check `hostname` and `whoami` still show the remote. A dropped session falls back to the local shell and your command runs there (this produced a stray `sudo` password prompt once).
- Pass `AWS_PROFILE` into new panes. The `default` profile is `AWSDenyAll`; use the SSO profile (`Engineering-297794628946`).
- Wrap `gh` and `devpod` calls in `timeout`. `coder ssh` prints noise lines; ignore them.
- zsh does not word-split variables. BSD `sed -i` needs `''`; prefer `perl -pi -e`. `rm` is verbose.
- Foreground `sleep` is blocked: use bounded loops or Monitor.
- Keep tool calls small and separate. Long combined `gh` chains were rejected by the user.
- The SDKMAN `java` function fails; call `~/.sdkman/candidates/java/<ver>/bin/java`.

## Cadence

Default rung `3-58/5 * * * *` (every 5 minutes) while any pod is working. Slow to 10, 20, then 60 minutes when all pods are idle or waiting on the user. Return to 5 minutes when a pod starts working, a new pod launches, or the user returns. When `schedule.txt` has an override, follow it until its end time. Change the rung by creating the new cron job first, then deleting the old one. Cron jobs are session-only and expire after 7 days, so re-create the job on `start`.

## Quiet ticks

If nothing changed since the last tick, output one line and stop. Do not list every pod.
