---
description: Monitor open PRs — review changes, post comments, resolve conflicts, surface new feedback
model: haiku
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
  - Agent
  - Skill
---

Monitor all open pull requests in the current repository. Designed for recurring use with `/loop` or as a one-shot check.

This command runs on haiku for the main orchestration loop. Expensive review work is delegated to specialized skills that use their own models.

## Setup

Determine the repository owner and name:

```bash
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
```

Fetch all open PRs authored by the current user:

```bash
gh pr list --author "@me" --state open --json number,title,headRefName,updatedAt,mergeable
```

If no open PRs are found, report that to the user and stop.

## Step 1: Identify PRs Needing Review

Track review state using a timestamp file at `/tmp/monitor-prs-last-run-{repo-slug}.txt`. If the file exists, read the ISO 8601 timestamp from it. If it does not exist, treat all PRs as needing review.

Partition the PRs into two lists:

- **Needs review**: PRs whose `updatedAt` is newer than the last-run timestamp (or all PRs on the first run)
- **Unchanged**: PRs that have not been updated since the last run

## Step 2: Review New or Updated PRs

For each PR that needs review, invoke the `/pr-review-toolkit:review-pr` skill using the `Skill` tool:

```
Skill: "pr-review-toolkit:review-pr"
Args: "{number}"
```

This delegates the full code review (diff analysis, finding issues, confidence scoring, validation) to the specialized review toolkit, which uses its own model and agent pipeline.

Wait for the review to complete before proceeding. The skill will produce validated review findings.

## Step 3: Post Review Comments

If the review from Step 2 produced any findings, use the `/workflow:post-pr-comments` skill to post them on the PR:

```
Skill: "workflow:post-pr-comments"
```

Invoke the skill once per PR that has findings. The skill handles formatting comments, resolving line numbers, and posting via the GitHub API.

If no findings were produced, skip to Step 4.

## Step 4: Check for Merge Conflicts

For each open PR, check the `mergeable` field from the PR list query:

- `MERGEABLE` — no action needed
- `CONFLICTING` — resolve the conflict
- `UNKNOWN` — re-fetch: `gh pr view {number} --json mergeable -q '.mergeable'`

For each PR with merge conflicts, dispatch a teammate agent in a worktree to resolve them:

Use the `Agent` tool with `isolation: "worktree"` to:

1. Check out the PR branch
2. Attempt to rebase onto the base branch (usually `main`)
3. Resolve any conflicts
4. Push the resolved branch to update the PR

```
Agent prompt: "Check out branch '{headRefName}', rebase it onto 'main', resolve any merge conflicts, and push the result. The repo is {REPO}. PR #{number}: {title}"
```

If conflict resolution fails, note it for the summary but do not block the rest of the workflow.

## Step 5: Surface New Review Comments

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
- **No changes**: if nothing required attention, say so briefly
