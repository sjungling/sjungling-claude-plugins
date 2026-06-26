---
description: Teleport the current Claude session into a new tmux window so you can close the original terminal
argument-hint: "[tmux-session-name]"
allowed-tools:
  - Bash
  - AskUserQuestion
---

Teleport **this** Claude conversation into a tmux window so the user can close
the terminal they accidentally started Claude in without losing the session.

macOS cannot move a live process's controlling terminal (no working `reptyr`),
so this does NOT move the running process. Instead it arms a new tmux window to
**resume** the current conversation from disk (`claude --resume <session-id>`)
the moment the old process exits. The conversation transcript is persisted per
turn, so everything committed transfers; only truly in-flight work is lost.

All the real work lives in `${CLAUDE_PLUGIN_ROOT}/scripts/teleport-tmux.sh`.
This command just runs it in two phases and relays the result.

> **IMPORTANT — run every bash block in this command with the sandbox
> DISABLED** (`dangerouslyDisableSandbox: true`). tmux talks to its server over
> a Unix socket (e.g. `/private/tmp/tmux-501/default`) that lives outside the
> default sandbox's writable allowlist. Under the sandbox, `tmux list-sessions`,
> `new-window`, and `send-keys` all fail with `error connecting to … (Operation
> not permitted)`. The script surfaces this as `ERROR_LISTING_SESSIONS` instead
> of silently hiding sessions — but it still cannot create the window unless the
> sandbox is off. The `command -v tmux` check passes either way (the binary
> exists), so the failure is easy to miss. Disable the sandbox up front.

Follow this workflow exactly.

## Step 1: Discover state

Run this (sandbox disabled) and read its output:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/teleport-tmux.sh" --discover
```

Capture from the output:
- `RESUME_SCRIPT` — path passed to `--arm` in Step 3.
- `AUTO` — `yes` if the old `claude` PID was detected, `no` otherwise.
- `INSIDE_TMUX` — `yes` if we're already inside tmux.
- The session list under `--- existing tmux sessions ---`.

If you see `ERROR_LISTING_SESSIONS`, the sandbox is still on (or the tmux socket
is otherwise blocked). Re-run the command with the sandbox disabled before
continuing — do NOT treat it as "no sessions."

## Step 2: Resolve the target session

- If the user passed an argument (`$ARGUMENTS`), use it as the target session name.
- Otherwise, look at the existing sessions from Step 1:
  - If there are existing sessions, use **AskUserQuestion** to let the user pick
    one, or choose "Create a new session". Offer a sensible default name for a
    new session based on the current directory: `claude-<basename of CWD>`.
  - If `<none>`, default to creating `claude-<basename of CWD>` (still confirm
    the name with AskUserQuestion if the user gave no argument).

Set `TARGET` to the chosen session name.

## Step 3: Create the window and arm the resume

Run this (sandbox disabled), substituting `__TARGET__` (chosen session),
`__SCRIPT__` (the `RESUME_SCRIPT` path from Step 1), and `__AUTO__` (`yes`/`no`
from Step 1):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/teleport-tmux.sh" --arm \
  --target '__TARGET__' --script '__SCRIPT__' --auto '__AUTO__'
```

The script prints `ARMED_AUTO_WAIT` (auto mode) or `ARMED_MANUAL` (PID not
detected). If it dies with a "tmux socket is blocked" message, the sandbox is
still on — re-run with it disabled.

## Step 4: Tell the user what to do

Based on the output:

- If **auto-wait** was armed (`ARMED_AUTO_WAIT`):
  1. If `INSIDE_TMUX` was `yes`: `tmux switch-client -t <TARGET>`
     Otherwise, from any terminal: `tmux attach -t <TARGET>`
  2. The new window shows "Waiting for the original Claude session to exit…".
  3. **Close / exit the original terminal** (or `Ctrl-C` then exit the old
     Claude). The new window will automatically launch `claude --resume` and
     pick the conversation back up.

- If **manual** was armed (`ARMED_MANUAL` — PID not detected):
  1. Attach/switch to `<TARGET>` as above.
  2. The resume command is pre-typed but not running.
  3. **First** close the original terminal, **then** press Enter in the new
     window to start the resumed session (this ordering avoids transcript
     corruption from two processes writing at once).

Keep the final message concise: the attach/switch command, and the reminder to
close the old terminal.
