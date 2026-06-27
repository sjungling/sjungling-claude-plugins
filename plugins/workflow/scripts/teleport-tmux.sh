#!/bin/bash
# Teleport the current Claude session into a tmux window.
#
# macOS cannot move a live process's controlling terminal (no working reptyr),
# so this does NOT move the running process. Instead it arms a new tmux window
# to RESUME the current conversation from disk (claude --resume <session-id>)
# once the old process exits. The transcript is persisted per turn, so
# everything committed transfers; only truly in-flight work is lost.
#
# Two modes:
#   teleport-tmux.sh --discover
#       Detect the old claude PID, write the resume script, and print state +
#       the existing tmux session list. Distinguishes "no tmux server running"
#       from a real error (e.g. a sandbox blocking the tmux socket) instead of
#       silently reporting "<none>".
#
#   teleport-tmux.sh --arm --target <session> --script <path> [--auto yes|no]
#       Create a 'claude' window in <session> (creating the session if needed)
#       and arm it to run <path>. With --auto yes the resume runs immediately
#       (it waits for the old PID internally); with --auto no it is pre-typed
#       but not executed, so the user can close the old terminal first.
#
# IMPORTANT (sandbox): tmux talks to its server over a Unix socket (e.g.
# /private/tmp/tmux-501/default) that lives outside the default Claude Code
# sandbox's writable allowlist. Run this script with the sandbox DISABLED, or
# allowlist the tmux socket directory — otherwise every tmux call fails with
# "error connecting to ... (Operation not permitted)".

set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Shared preconditions
# ---------------------------------------------------------------------------
require_tmux() {
  command -v tmux >/dev/null 2>&1 \
    || die "tmux is not installed. Install it with: brew install tmux"
}

# Query the tmux server once and classify the result, so a sandbox/permission
# failure surfaces clearly rather than masquerading as "no sessions". Sets two
# globals (bash's idiom for returning more than one value):
#   TMUX_STATUS = ok | no-server | blocked
#   TMUX_OUT    = raw output — session names when ok, error detail when blocked
probe_tmux() {
  # Assign inside the `if` condition: this both captures the command
  # substitution's exit status directly and exempts it from `set -e` (a bare
  # `var=$(failing)` would abort the script under errexit).
  if TMUX_OUT="$(tmux list-sessions -F '#{session_name}' 2>&1)"; then
    TMUX_STATUS=ok
  elif [[ "$TMUX_OUT" == *"no server running"* || "$TMUX_OUT" == *"No such file or directory"* ]]; then
    # No server started yet. tmux's wording varies by platform/version:
    #   Linux / older tmux: "no server running on <socket>"
    #   macOS tmux 3.x:     "error connecting to <socket> (No such file or directory)"
    # `tmux new-session` starts one on demand, so this is benign — not a block.
    TMUX_STATUS=no-server
  else
    # Anything else — notably "(Operation not permitted)" from a sandbox
    # blocking the socket — is a real connection failure we must surface.
    TMUX_STATUS=blocked
  fi
}

# ---------------------------------------------------------------------------
# --discover
# ---------------------------------------------------------------------------
do_discover() {
  require_tmux

  # CLAUDE_CODE_SESSION_ID is an internal Claude Code env var (not in
  # `claude --help`); it holds the session ID we resume. Fail loudly if it ever
  # stops being exported.
  local SID="${CLAUDE_CODE_SESSION_ID:-}"
  [ -n "$SID" ] || die "CLAUDE_CODE_SESSION_ID is not set; cannot determine which session to resume."

  local CWD="$PWD"
  local CLAUDE_BIN
  CLAUDE_BIN="$(command -v claude || echo claude)"

  # Walk up the process tree to find the ancestor 'claude' process. Match the
  # basename EXACTLY so we don't match 'claude-helper' etc. kill -0 (used in the
  # resume script) only needs signal permission, so the *wait* is reliable even
  # where ps is restricted; this detection is best-effort.
  local OLD_PID="" pid="$PPID" guard=0 comm
  while [ -n "$pid" ] && [ "$pid" -gt 1 ] && [ "$guard" -lt 25 ]; do
    comm="$(ps -o comm= -p "$pid" 2>/dev/null || true)"
    case "${comm##*/}" in
      claude) OLD_PID="$pid"; break ;;
    esac
    pid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
    guard=$((guard + 1))
  done

  # Write the resume script the new tmux window will run. Always invoked as
  # `bash <script>`, so no shebang is needed.
  local SCRIPT="${CLAUDE_TMPDIR:-${TMPDIR:-/tmp}}/teleport-resume-${SID}.sh"
  {
    if [ -n "$OLD_PID" ]; then
      printf 'echo "Waiting for the original Claude session (PID %s) to exit, then resuming here..."\n' "$OLD_PID"
      printf 'while kill -0 %s 2>/dev/null; do sleep 0.5; done\n' "$OLD_PID"
      # Brief pause narrows the PID-reuse / TOCTOU window before we start
      # writing to the same transcript the old process just released.
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
  if [ -n "$OLD_PID" ]; then
    echo "OLD_PID=$OLD_PID"
    echo "AUTO=yes"
  else
    echo "OLD_PID=<not-detected>"
    echo "AUTO=no"
  fi
  echo "RESUME_SCRIPT=$SCRIPT"
  echo "INSIDE_TMUX=${TMUX:+yes}"
  echo "--- existing tmux sessions ---"

  probe_tmux
  case "$TMUX_STATUS" in
    ok)
      [ -n "$TMUX_OUT" ] && printf '%s\n' "$TMUX_OUT" || true
      ;;
    no-server)
      echo "<none>"
      ;;
    blocked)
      echo "ERROR_LISTING_SESSIONS: $TMUX_OUT"
      echo "(This usually means the sandbox is blocking the tmux socket. Re-run"
      echo " with the sandbox disabled, or allowlist the tmux socket directory.)"
      ;;
  esac
}

# ---------------------------------------------------------------------------
# --arm
# ---------------------------------------------------------------------------
do_arm() {
  local TARGET="" SCRIPT="" AUTO="no"
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --target) TARGET="${2:-}"; shift 2 ;;
      --script) SCRIPT="${2:-}"; shift 2 ;;
      --auto)   AUTO="${2:-no}"; shift 2 ;;
      *) die "unknown --arm argument: $1" ;;
    esac
  done

  require_tmux
  [ -n "$TARGET" ] || die "--arm requires --target <session>"
  [ -n "$SCRIPT" ] || die "--arm requires --script <path>"
  [ -f "$SCRIPT" ] || die "resume script not found: $SCRIPT"

  # Surface a blocked socket before we try to create windows, so the failure is
  # legible instead of an opaque tmux error mid-way.
  probe_tmux
  if [ "$TMUX_STATUS" = blocked ]; then
    die "tmux socket is blocked ($TMUX_OUT). Re-run with the sandbox disabled, or allowlist the tmux socket directory."
  fi

  # Create the window and capture its index so send-keys targets THIS window,
  # not whatever window happens to be active in the session.
  local WIN PANE
  if tmux has-session -t "$TARGET" 2>/dev/null; then
    WIN="$(tmux new-window -t "$TARGET" -n claude -P -F '#{window_index}')"
  else
    tmux new-session -d -s "$TARGET" -n claude
    WIN="$(tmux list-windows -t "$TARGET" -F '#{window_index}' | head -n1)"
  fi
  PANE="${TARGET}:${WIN}"

  if [ "$AUTO" = yes ]; then
    # Auto-wait: the resume script waits for the old process to exit, then
    # resumes. Prevents two processes appending to the same transcript at once.
    tmux send-keys -t "$PANE" "bash $(printf %q "$SCRIPT")" C-m
    echo "ARMED_AUTO_WAIT pane=$PANE"
  else
    # Graceful degradation (PID not detected): pre-type the launch but do NOT
    # run it, so the user can close the old terminal first, then press Enter.
    tmux send-keys -t "$PANE" "bash $(printf %q "$SCRIPT")"
    echo "ARMED_MANUAL pane=$PANE"
  fi
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
case "${1:-}" in
  --discover) shift; do_discover "$@" ;;
  --arm)      shift; do_arm "$@" ;;
  *) die "usage: teleport-tmux.sh --discover | --arm --target <session> --script <path> [--auto yes|no]" ;;
esac
