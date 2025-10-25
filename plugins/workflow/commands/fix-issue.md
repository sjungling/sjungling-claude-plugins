---
allowed-tools: Bash(gh issue view:*),
  Bash(gh issue comment:*),
  Bash(gh pr create:*),
  Bash(gh pr list:*),
  Bash(git status:*),
  Bash(git branch:*),
  Bash(git switch:*),
  Bash(git checkout:*),
  Bash(git add:*),
  Bash(git commit:*),
  Bash(git push:*),
  Bash(lsof:*)
argument-hint: [issue-number]
description: Analyze and fix a GitHub issue end-to-end with plan, branch, tests, and draft PR
---

Analyze and fix GitHub issue #$ARGUMENTS.

## Argument validation

- Ensure an issue number was provided and prompt the user if not.

## Context

- Issue (JSON): `gh issue view "$ARGUMENTS" --json number,title,body,url,labels,assignees,state,author,createdAt,updatedAt`
- Issue (human): `gh issue view "$ARGUMENTS"`
- Current branch: `git branch --show-current`
- Git status: `git status -sb`
- Open PRs referencing #$ARGUMENTS: `gh pr list --state open --search "$ARGUMENTS in:title,body" --json number,title,url,headRefName,author`

## Inputs

- $ARGUMENTS = issue number (required)
- Type and branch slug are auto-inferred from the issue (no additional args).

## Your task

1. Analysis

   - Summarize the problem, acceptance criteria, scope, and risks from the issue details.
   - If unclear, ask clarifying questions on edge cases or missing requirements.

2. Plan (propose and wait for confirmation)

   - Propose a minimal, testable plan (files to change, tests to add, migration notes if any).
   - Post the proposed plan to the issue:
     - Run: gh issue comment $ARGUMENTS --body "<concise plan summary>"
   - Wait for user confirmation before making repo changes.

3. Branch management

   - If on main or default branch, create a branch:
     - Type: infer from labels/title (fix|feat|chore|docs|refactor). Default: fix.
     - Slug: derive from issue title (kebab-case, <=50 chars). Fallback: "issue-$ARGUMENTS".
     - Branch name: {type}/issue-$ARGUMENTS-{slug}
   - Commands to use (after approval):
     - git switch -c {branch} OR git checkout -b {branch}

4. Code search and implementation

   - Identify impacted modules and cross-cutting concerns.
   - Implement the fix/feature with small, logical commits.

5. Tests and local verification

   - Prefer unit tests. If integration tests needed, call that out.
   - Heuristics:
     - If `package.json` exists: run `npm run check:all` and `npm test` if available.
     - If a Python project: run `uvx pytest` and `ruff` if configured.
     - If Go: run `go test ./...`.
   - Ensure dev server on port 3000 is not already running before starting any local server.

6. Quality gates

   - Ensure code passes linting, formatting, and type checks available in the repo.
   - Keep changes minimal and well-scoped.

7. Commit

   - Use a conventional commit message; include issue reference.
   - Example: "<type>: <scope>: <subject> (#$ARGUMENTS)" (type inferred)
   - Do NOT attribute to Claude in the commit message.

8. PR (draft) with Problem/Solution format

   - Push branch and create a draft PR that links the issue:
     - Body should include:
       - Problem: what's broken or missing
       - Solution: what changed and why
       - Fixes #$ARGUMENTS
     - Command:
       - gh pr create --draft --fill --title "<type>: <scope>: <subject> (#$ARGUMENTS)" --body "Problem\n\n<text>\n\nSolution\n\n<text>\n\n<text>\n\nFixes #$ARGUMENTS"

## Notes

- Use GitHub CLI (gh) for all GitHub operations.
- Keep interactions idempotent and ask for confirmation before pushing or creating PRs.
- If repo tooling is unclear, ask whether to enable/add tests or linters for this fix.
