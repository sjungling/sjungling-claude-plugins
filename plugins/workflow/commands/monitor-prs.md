---
description: Monitor open PRs — review changes, post comments, resolve conflicts, surface new feedback
model: haiku
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
  - Edit
  - Agent
  - Skill
---

Monitor all open pull requests in the current repository. Designed for recurring use with `/loop` or as a one-shot check.

This command runs on haiku for the main orchestration loop. All per-PR work (reviews, conflict resolution) is performed in isolated worktrees to keep the main worktree clean.

## Setup

Determine the repository owner and name:

```bash
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
```

Fetch all open PRs authored by the current user:

```bash
gh pr list --author "@me" --state open --json number,title,headRefName,baseRefName,updatedAt,mergeable
```

If no open PRs are found, report that to the user and stop.

## Step 1: Identify PRs Needing Review

Track review state using a timestamp file at `/tmp/monitor-prs-last-run-{repo-slug}.txt`. If the file exists, read the ISO 8601 timestamp from it. If it does not exist, treat all PRs as needing review.

Filter to PRs whose `updatedAt` is newer than the last-run timestamp (or all PRs on the first run). Skip unchanged PRs for review, but still include them in conflict and comment checks (Steps 3-4).

## Step 2: Review and Comment on New or Updated PRs

For each PR that needs review, dispatch an `Agent` with `isolation: "worktree"` to perform the review from an isolated copy of the repository. The agent checks out the PR branch and runs the full review pipeline from that worktree.

```
Agent:
  isolation: "worktree"
  prompt: |
    You are reviewing PR #{number}: {title} in {REPO}.

    1. Check out branch '{headRefName}'
    2. Run the /pr-review-toolkit:review-pr skill with args "{number}" to perform the code review
    3. If the review produced findings, run the /workflow:post-pr-comments skill to post them on the PR
    4. Report what you found and what comments (if any) were posted
```

This delegates the full code review (diff analysis, finding issues, confidence scoring, validation, and comment posting) to an isolated worktree. The worktree is automatically cleaned up when the agent completes since no changes are made to the repo.

If multiple PRs need review, dispatch agents in parallel when possible.

## Step 3: Check for Merge Conflicts

For each open PR, check the `mergeable` field from the PR list query:

- `MERGEABLE` — no action needed
- `CONFLICTING` — resolve the conflict
- `UNKNOWN` — re-fetch: `gh pr view {number} --json mergeable -q '.mergeable'`

For each PR with merge conflicts, dispatch an `Agent` with `isolation: "worktree"` to resolve them:

```
Agent:
  isolation: "worktree"
  prompt: |
    Check out branch '{headRefName}', rebase it onto '{baseRefName}',
    resolve any merge conflicts, and push the result.
    The repo is {REPO}. PR #{number}: {title}
```

If conflict resolution fails, note it for the summary but do not block the rest of the workflow.

## Step 4: Surface New Review Comments

For each open PR, fetch review comments posted since the last monitoring cycle:

```bash
gh api repos/{REPO}/pulls/{number}/comments --jq '[.[] | select(.created_at > "{last_run_timestamp}")] | length'
```

If there are new comments, fetch their details:

```bash
gh api repos/{REPO}/pulls/{number}/comments --jq '[.[] | select(.created_at > "{last_run_timestamp}")] | .[] | {user: .user.login, path: .path, line: .line, body: .body}'
```

Also check for PR review comments (top-level review bodies):

```bash
gh api repos/{REPO}/pulls/{number}/reviews --jq '[.[] | select(.submitted_at > "{last_run_timestamp}" and .state != "PENDING")] | .[] | {user: .user.login, state: .state, body: .body}'
```

Summarize any new comments for the user, grouped by PR.

## Step 5: Clean Up Stale Worktrees

Check for any lingering worktrees from previous monitoring runs whose PRs have since been merged or closed:

```bash
git worktree list --porcelain
```

For each worktree that is not the main worktree, check if its branch corresponds to a PR that is no longer open:

```bash
gh pr list --head "{branch}" --state open --json number -q '.[0].number'
```

If the query returns empty (no open PR for that branch), remove the worktree:

```bash
git worktree remove --force "{worktree_path}"
```

Only clean up worktrees that appear to be agent-created (located in the `.claude/worktrees/` directory). Do not touch worktrees outside that directory.

## Finalize

Update the last-run timestamp file:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > /tmp/monitor-prs-last-run-{repo-slug}.txt
```

Report a summary to the user:

- **PRs reviewed**: count and PR numbers
- **Comments posted**: count per PR
- **Conflicts resolved**: which PRs, success/failure
- **New reviewer feedback**: summary of comments per PR
- **Worktrees cleaned**: count of stale worktrees removed
- **No changes**: if nothing required attention, say so briefly
