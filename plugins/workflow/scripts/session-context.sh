#!/bin/bash
# Emit git worktree context at session start so Claude (and any subagents
# it dispatches) always know which working tree they are operating in.
#
# Prevents the "subagent edited the main repo instead of the worktree"
# failure mode by making the current worktree path explicit up front.

set -u

CWD=$(pwd)

if ! command -v git >/dev/null 2>&1; then
    echo "Session context: git not available, skipping worktree detection."
    echo "Working directory: $CWD"
    exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Session context: not inside a git repository."
    echo "Working directory: $CWD"
    exit 0
fi

TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null || echo "$CWD")
BRANCH=$(git branch --show-current 2>/dev/null || echo "(detached)")
COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || echo "")
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null || echo "")

if [ -n "$COMMON_DIR" ] && [ -n "$GIT_DIR" ]; then
    ABS_COMMON=$(cd "$COMMON_DIR" 2>/dev/null && pwd || echo "$COMMON_DIR")
    ABS_GIT=$(cd "$GIT_DIR" 2>/dev/null && pwd || echo "$GIT_DIR")
    if [ "$ABS_COMMON" != "$ABS_GIT" ]; then
        IS_WORKTREE=1
    else
        IS_WORKTREE=0
    fi
else
    IS_WORKTREE=0
fi

echo "Session context:"
echo "- Working directory: $CWD"
echo "- Git toplevel:      $TOPLEVEL"
echo "- Current branch:    $BRANCH"

if [ "$IS_WORKTREE" = "1" ]; then
    MAIN_REPO=$(dirname "$ABS_COMMON" 2>/dev/null || echo "unknown")
    echo "- Worktree:          YES (linked from $MAIN_REPO)"
    echo ""
    echo "IMPORTANT: You are in a git worktree. All edits and builds must"
    echo "stay within $TOPLEVEL. Do NOT 'cd' to the main repo at $MAIN_REPO."
    echo "When dispatching subagents, pass the worktree path explicitly."
else
    echo "- Worktree:          no (main checkout)"
fi
