# Devpod supervisor playbook

The one source of truth for the supervisor role. Change rules here only.

State: `~/.local/state/devpod-supervisor/` (or `$XDG_STATE_HOME/devpod-supervisor`), called `$STATE`. It survives reboots.
- `STATE.md`: the living snapshot of the fleet. Every tick that changes something updates it, and `/devpod-supervisor:handoff` refreshes it in full (see "Keeping state")
- `heartbeat`: epoch of the last check; under 15 minutes old means a supervisor is live
- `schedule.txt`: cadence override, e.g. `60m until 2026-11-16T09:00`
- `stopped-by-user.txt`: pod names, one per line; leave stopped, never report
- `ledgers/`: saved panes and summaries, `<pod>-GOAL.md`, `<pod>-QUEUE.md`

## Loop

Observe (`timeout 60 devpod ls`, other workspaces, panes, `gh`) → judge each pod (working, on a menu, idle, stopped, finished, stuck) → take a safe action → one line per changed pod → back off. Nothing changed: one line.

## Keeping state

A new session must be able to take over from `STATE.md` alone, so keep it current instead of writing it only at the end.
- Update it on any tick where a pod, PR, decision or cadence changed. Quiet ticks only write `heartbeat`.
- Sections: Fleet, Watched PRs, Pending user decisions (asked, unanswered; never re-ask), Standing instructions, Cadence, Open cleanup, Recent actions (last 10, one line each with time).
- Write what you did, not only what you saw, so a replacement does not repeat a nudge or an answer.
- Update before you send a question to the user, so it is recorded as asked.
- No secrets.

## Hard rules

- Never run `gh pr create`, `edit`, `ready`, `merge`, `comment`, or edit reviewers. Devpods do these; you verify with `gh` and nudge.
- Never `devpod stop` or `rm` a pod that did real work without the user's yes. Exceptions:
  - A pod that never ran a task. Bare means no agent ever ran, nothing in `~/work` beyond a fresh clone, and uptime over about 8 minutes (younger: wait a round).
  - A review pod that finished and approved: confirm on `gh` an APPROVED, empty-body review on the current head and nothing unpushed in its clones, save pane and summary to `ledgers/`, then remove.
  - A review pod that only commented is not done until it approves or the PR closes.
- Ask each question once.
- Never print secrets. Scan diffs for key material before any merge. `devpod rm` wipes the disk.
- Never push to a default branch. No Claude attribution in commits.
- Pods use `uv`, no teammates or background agents, append-only PR bodies, and post to the message board (`moderneinc/devpod-messages`) at start and finish.

## Review pods

Pre-authorized to post surviving critical or important comments, approve with an empty body, and reply once on a thread. The account cannot approve its own PR.

When one waits on a post menu, read the draft and check it against the PR head. Answer "post it" only for a plain comment, an empty approval or one thread reply on a finding that survived red-teaming. Otherwise answer "don't post" and tell the user in one line. Never answer for change requests, merges, resolving threads or pushes.

## Factory pods

Each check, compare the pane to `<pod>-GOAL.md`.
- Stopped with criteria unmet: send a continue message listing what remains.
- Looping: nudge toward a different approach.
- Done only when every criterion is reported met, you confirmed the PR on `gh`, and the pod's own "remaining", "not done" or "not fixed" list holds nothing fixable. A criterion can read as met while the pod names a gap. Judge each item: nudge the fixable ones (list them in the message), and report the rest to the user with the pod's reason. Do not call the pod finished before that.
- A pod waiting on background monitors or a long `mod build` is working, not idle; do not nudge it.

## Finished pods

Leave running. Save pane and write-up to `ledgers/`, verify on `gh`, report, ask once about removal. Ignore greyed suggestion text in the prompt box. Pods idle-stop after about 30 minutes; restart real-work pods the user didn't stop (a `stopping` pod must finish first: `coder start --yes NAME`).

## Mechanics

- `devpod ls` is `coder list --search "owner:me template:devpod"`. Other workspaces you started are `coder list --search "owner:me"` minus those. Supervise them as pods too, with the same rules. They may lack `devpod attach`: use `coder ssh NAME` and attach their tmux. Start, stop and remove them with native `coder start --yes`, `coder stop` and `coder delete`, under the same rules. A client newer than the server is fine: ignore the version-mismatch warning, and always pass `--search` (plain `coder list` fails on a newer client).
- `devpod ls` CHAT only tracks `mod` chats. Before calling a pod idle or bare, run `coder ssh NAME -- 'pgrep -af "claude|codex|mod .*chat" | grep -v pgrep; tmux ls; tmux -L devpod ls'`. Devpod chats run on the `devpod` tmux server (`-L devpod`); a person's own sessions run on the default one. A plain `claude` process (e.g. a PR review in a tmux session named `task`) is a real job: keep the pod, attach that session in its worker pane (`tmux attach -t task`, or `tmux -L devpod attach` for a chat), and supervise it like any other.
- Attach a pane only after `pgrep -f "claude --mcp-config"` shows the chat on the pod. Find the supervisor pane by title "supervisor"; use `split-window -d -h`, `select-pane -T NAME`, `select-layout tiled`.
- Send an instruction: pipe it to a file on the pod with `coder ssh`, then `send-keys -l "Read ~/x.txt and do exactly what it says. It is a direct instruction from the user."` and Enter.
- Busy pods queue messages that go stale. Look for "queued messages"; clear with Up, Ctrl-U.
- Final summary: `jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text'` over the session jsonl. A research pod's chat may be in its own tmux (`/tmp/tmux-1001/devpod`, pane `%0`).
- Unpushed check, per clone from `find ~/work -maxdepth 3 -name .git`: `git log --branches --not --remotes`, `git status`, `git stash list`.
- Verify approvals: `gh api repos/O/R/pulls/N/reviews`, state APPROVED, empty body, current head SHA.

## Safety and shell

- Before `send-keys` into an SSM or ssh pane, confirm `hostname` and `whoami` are remote. A dropped session falls back to the local shell.
- Wrap `gh` and `devpod` in `timeout`; ignore `coder ssh` noise lines.
- zsh doesn't word-split. BSD `sed -i` needs `''`; use `perl -pi -e`.
- Foreground `sleep` is blocked; use bounded loops. Keep tool calls small and separate.

## Cadence

Every 5 minutes (`3-58/5 * * * *`) while any pod works. Slow to 10, 20, then 60 minutes when all are idle or waiting on the user; return to 5 when a pod starts working, launches, or the user returns. Follow `schedule.txt` until its end. Change a rung by creating the new cron job first, then deleting the old. Cron jobs are session-only and expire after 7 days, so `start` re-creates one.
