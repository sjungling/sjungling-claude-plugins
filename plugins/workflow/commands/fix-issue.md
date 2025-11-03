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

1. Analysis and Clarification (use subagent)

   - Launch a general-purpose subagent to analyze the issue and gather requirements
   - The subagent should:
     - Read and summarize the issue: problem, acceptance criteria, scope, and risks
     - Identify any ambiguities or missing information
     - **Use the AskUserQuestion tool** to ask structured clarifying questions about:
       - Edge cases and error handling requirements
       - Scope boundaries (what's in/out of scope)
       - Implementation approach preferences
       - Testing expectations and coverage requirements
       - Any missing acceptance criteria
       - Breaking changes or migration concerns
     - Return a comprehensive summary including user responses
   - Wait for the subagent to complete and review the analysis before proceeding

2. Plan (propose and wait for confirmation)

   - Based on the analysis and clarification responses, propose a minimal, testable plan (files to change, tests to add, migration notes if any).
   - Post the proposed plan to the issue:
     - Create temp file: `gh issue comment $ARGUMENTS --edit-last --body-file /dev/null 2>/dev/null || true` (to get template if available)
     - Write plan to temp file: Use Write tool to create `/tmp/claude/issue-comment-$ARGUMENTS.md` with the concise plan summary
     - Use Read tool to verify the content if needed
     - Post comment: `gh issue comment $ARGUMENTS --body-file /tmp/claude/issue-comment-$ARGUMENTS.md`
   - **Wait for user confirmation before making repo changes.**

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
     - Write PR body to temp file using Write tool at `/tmp/claude/pr-body-issue-$ARGUMENTS.md`:
       ```markdown
       ## Problem

       [Describe what's broken or missing]

       ## Solution

       [Explain what changed and why]

       ## Testing

       [How to test these changes]

       Fixes #$ARGUMENTS
       ```
     - Use Edit tool to update the temp file with actual problem/solution descriptions
     - Use Read tool to verify the content before creating PR
     - Create PR: `gh pr create --draft --title "<type>(<scope>): <subject> (#$ARGUMENTS)" --body-file /tmp/claude/pr-body-issue-$ARGUMENTS.md`

## Notes

- Use GitHub CLI (gh) for all GitHub operations.
- Keep interactions idempotent and ask for confirmation before pushing or creating PRs.
- If repo tooling is unclear, ask whether to enable/add tests or linters for this fix.
