---
description: Rebase current branch with main, handling worktrees and stashing
allowed-tools:
  - Bash(git:*)
---

Rebase the current branch against main. Follow this workflow exactly:

## Step 1: Detect Environment

Run these commands to determine context:

!`git rev-parse --show-toplevel`
!`git worktree list`
!`git branch --show-current`
!`git status --porcelain`

From these results, determine:
- **Current branch name** (from `git branch --show-current`)
- **Is this a worktree?** — If `git worktree list` shows more than one entry AND the current working directory is NOT the first (main) worktree listed, then we are in a linked worktree
- **Has uncommitted changes?** — If `git status --porcelain` produces output
- **Main worktree path** — The first entry in `git worktree list` (the bare/main worktree)

## Step 2: Stash if needed

If there are uncommitted changes (staged or unstaged):
1. Run `git stash push -m "rebase-main: auto-stash before rebase"`
2. Remember that we stashed so we can pop later

## Step 3: Rebase based on context

### Case A: In a worktree
The main worktree has the authoritative copy of main. Fetch from the main worktree path:
1. Get the main worktree path (first entry from `git worktree list`)
2. Run `git fetch <main-worktree-path> main:main` to update the local main ref from the main worktree
3. Run `git rebase main`

### Case B: Not in a worktree, ON main branch
We're on main itself — rebase against origin:
1. Run `git fetch origin main`
2. Run `git rebase origin/main`

### Case C: Not in a worktree, on a NON-main branch
Rebase against the local main branch:
1. Run `git rebase main`

## Step 4: Handle rebase conflicts

If the rebase fails due to conflicts:
1. Report the conflicting files to the user
2. Ask the user how they want to proceed: resolve conflicts, or abort with `git rebase --abort`
3. Do NOT automatically resolve conflicts — wait for user guidance

## Step 5: Restore stash

If we stashed changes in Step 2:
1. Run `git stash pop`
2. If the stash pop has conflicts, report them to the user

## Step 6: Report results

Summarize what happened:
- Which rebase case was used (worktree/main/branch)
- Whether changes were stashed and restored
- Current branch status after rebase
