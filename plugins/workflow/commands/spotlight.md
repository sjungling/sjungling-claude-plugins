---
description: Spotlight worktree changes into main worktree for testing (like Conductor Spotlight)
argument-hint: [on|off|refresh|status]
allowed-tools:
  - Bash(git:*)
---

Spotlight testing: merge worktree changes into the main worktree without committing,
so you can test in the main worktree's environment (build artifacts, node_modules, databases, etc.).

Parse `$ARGUMENTS` for the mode: `on` (default if empty), `off`, `refresh`, or `status`.

## Step 1: Detect Environment

Run these commands:

!`git rev-parse --show-toplevel`
!`git worktree list`
!`git branch --show-current`
!`git status --porcelain`

Determine:
- **Current worktree path** and **main worktree path** (first entry in `git worktree list`)
- **Is this a linked worktree?** — current directory is NOT the main worktree
- **Current branch name**
- **Has uncommitted changes?**

If NOT in a linked worktree, abort with:
> "Spotlight requires a linked worktree. Run this from a Claude Code worktree, not the main repo."

## Step 2: Execute Mode

### Mode: `on` (default)

1. **Check main worktree state:**
   - Run `git -C <main-worktree-path> status --porcelain`
   - If dirty, abort: "Main worktree has uncommitted changes. Commit or stash them first."
   - Check for active merge: look for MERGE_HEAD in the main worktree's git directory.
     For a standard (non-bare) main worktree, check `<main-worktree-path>/.git/MERGE_HEAD`.
     If an active merge exists, abort: "Main worktree already has an active merge. Run `/spotlight off` first."

2. **Checkpoint uncommitted changes (if any):**
   - If `git status --porcelain` shows changes:
     - `git add -A`
     - `git commit -m "spotlight: checkpoint"`
     - Remember we created a checkpoint commit (report this to user)
   - If no changes, skip this step

3. **Merge into main worktree:**
   - Get current branch name: `<branch>`
   - `git -C <main-worktree-path> merge --no-commit --no-ff <branch>`
   - The `--no-ff` ensures we get a proper staging even if fast-forward is possible

4. **Handle result:**
   - **Success**: Report that changes are now staged in main worktree. Remind user:
     - Test in main worktree at `<main-worktree-path>`
     - Run `/spotlight off` when done to clean up
   - **Conflicts**: Report conflicting files. User can resolve in main worktree or
     run `/spotlight off` to abort

### Mode: `refresh`

Re-spotlight the current branch's latest state into the main worktree. Useful after making new commits on the feature branch — avoids the `off` + `on` dance.

1. **Clear any existing spotlight in main:**
   - If main worktree has an active merge (MERGE_HEAD exists): `git -C <main-worktree-path> merge --abort`
   - Otherwise continue.

2. **Undo a prior checkpoint commit (if any):**
   - If current worktree HEAD subject is `spotlight: checkpoint`: `git reset --soft HEAD~1`.

3. **Re-run the `on` flow:** checkpoint any uncommitted changes, then
   `git -C <main-worktree-path> merge --no-commit --no-ff <branch>`.

4. **Report** the refreshed state (branch, main worktree path, whether a new checkpoint was created).

### Mode: `off`

1. **Abort merge in main worktree:**
   - Check if main worktree has an active merge (check for MERGE_HEAD as described above)
   - If yes: `git -C <main-worktree-path> merge --abort`
   - If no active merge: inform user "No active spotlight session found in main worktree"

2. **Undo checkpoint commit (if applicable):**
   - Check if HEAD commit message is "spotlight: checkpoint"
     via `git log -1 --format=%s`
   - If yes: `git reset --soft HEAD~1` to restore working state
   - If no: skip (user may have made additional commits)

3. **Report**: Confirm cleanup is complete

### Mode: `status`

1. Check main worktree for active merge (MERGE_HEAD)
2. Check if current worktree HEAD is a spotlight checkpoint
3. Report:
   - Whether spotlight is active
   - Which branch is spotlighted
   - Main worktree path
   - Whether a checkpoint commit exists
