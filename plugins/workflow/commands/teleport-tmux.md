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

Follow this workflow exactly.

## Step 1: Gather state and write the resume script

Run this single block and read its output. It detects the old `claude` process
and writes a self-contained resume script to a temp file — building the script
in a real shell (with proper `printf %q` quoting) avoids any fragile text
substitution or `tmux send-keys` quoting problems later.

```bash
set -euo pipefail

# tmux must be installed
if ! command -v tmux >/dev/null 2>&1; then
  echo "ERROR: tmux is not installed. Install it with: brew install tmux"
  exit 1
fi

# CLAUDE_CODE_SESSION_ID is an internal Claude Code env var (not shown in
# `claude --help`); it holds the current session ID we resume. Fail loudly if
# it ever stops being exported.
SID="${CLAUDE_CODE_SESSION_ID:-}"
if [ -z "$SID" ]; then
  echo "ERROR: CLAUDE_CODE_SESSION_ID is not set; cannot determine which session to resume."
  exit 1
fi

CWD="$PWD"
CLAUDE_BIN="$(command -v claude || echo claude)"

# Walk up the process tree to find the ancestor 'claude' process. Match the
# basename EXACTLY so we don't match unrelated processes like 'claude-helper'.
# kill -0 (used inside the resume script) only needs signal permission, so the
# *wait* is reliable even where ps is restricted; this detection is best-effort.
OLD_PID=""
pid="$PPID"
guard=0
while [ -n "$pid" ] && [ "$pid" -gt 1 ] && [ "$guard" -lt 25 ]; do
  comm="$(ps -o comm= -p "$pid" 2>/dev/null || true)"
  case "${comm##*/}" in
    claude) OLD_PID="$pid"; break ;;
  esac
  pid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
  guard=$((guard + 1))
done

# Write the resume script the new tmux window will run. It is always invoked as
# `bash <script>`, so no shebang is needed.
SCRIPT="${CLAUDE_TMPDIR:-${TMPDIR:-/tmp}}/teleport-resume-${SID}.sh"
{
  if [ -n "$OLD_PID" ]; then
    printf 'echo "Waiting for the original Claude session (PID %s) to exit, then resuming here..."\n' "$OLD_PID"
    printf 'while kill -0 %s 2>/dev/null; do sleep 0.5; done\n' "$OLD_PID"
    # Brief pause narrows the PID-reuse / TOCTOU window before we start writing
    # to the same transcript the old process just released.
    printf 'sleep 1\n'
  fi
  printf 'cd %q || exit 1\n' "$CWD"
  # No `exec`: keep the pane open if resume fails so the error is visible.
  printf '%q --resume %q\n' "$CLAUDE_BIN" "$SID"
  printf 'ec=$?\n'
  printf '[ "$ec" -ne 0 ] && { echo "claude --resume exited with $ec. Press Enter to close."; read -r _; }\n'
} > "$SCRIPT"
chmod +x "$SCRIPT"

echo "SESSION_ID=$SID"
echo "OLD_PID=${OLD_PID:-<not-detected>}"
echo "RESUME_SCRIPT=$SCRIPT"
echo "INSIDE_TMUX=${TMUX:+yes}"
echo "--- existing tmux sessions ---"
tmux list-sessions -F '#{session_name}' 2>/dev/null || echo "<none>"
```

Capture from the output: `RESUME_SCRIPT` (path), whether `OLD_PID` was detected
(`AUTO=yes` if it is a number, `AUTO=no` if `<not-detected>`), whether we're
`INSIDE_TMUX`, and the list of existing sessions.

## Step 2: Resolve the target session

- If the user passed an argument (`$ARGUMENTS`), use it as the target session name.
- Otherwise, look at the existing sessions from Step 1:
  - If there are existing sessions, use **AskUserQuestion** to let the user pick
    one, or choose "Create a new session". Offer a sensible default name for a
    new session based on the current directory: `claude-<basename of CWD>`.
  - If there are no sessions at all, default to creating `claude-<basename of CWD>`
    (still confirm the name with AskUserQuestion if the user gave no argument).

Set `TARGET` to the chosen session name.

## Step 3: Create the window and arm the resume

Run this block, substituting only these simple, low-risk values: `__TARGET__`
(the session name), `__SCRIPT__` (the `RESUME_SCRIPT` path from Step 1), and
`__AUTO__` (`yes` or `no` from Step 1). The window's working directory is set by
the resume script's own `cd`, so no path needs substituting here.

```bash
set -euo pipefail
TARGET='__TARGET__'
SCRIPT='__SCRIPT__'
AUTO='__AUTO__'

# Create the window and capture its index so send-keys targets THIS window,
# not whatever window happens to be active in the session.
if tmux has-session -t "$TARGET" 2>/dev/null; then
  WIN="$(tmux new-window -t "$TARGET" -n claude -P -F '#{window_index}')"
else
  tmux new-session -d -s "$TARGET" -n claude
  WIN="$(tmux list-windows -t "$TARGET" -F '#{window_index}' | head -n1)"
fi
PANE="${TARGET}:${WIN}"

if [ "$AUTO" = yes ]; then
  # Auto-wait: the script waits for the old process to exit, then resumes. This
  # prevents two processes appending to the same transcript .jsonl at once.
  tmux send-keys -t "$PANE" "bash $(printf %q "$SCRIPT")" C-m
  echo "ARMED_AUTO_WAIT pane=$PANE"
else
  # Graceful degradation (PID not detected): pre-type the launch but do NOT run
  # it, so the user can close the old terminal first, then press Enter.
  tmux send-keys -t "$PANE" "bash $(printf %q "$SCRIPT")"
  echo "ARMED_MANUAL pane=$PANE"
fi
```

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
