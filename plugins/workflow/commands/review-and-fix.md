---
description: Review a PR, apply high-confidence fixes, verify build, and push
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
---

Run a review-and-fix cycle on a pull request. The PR must already exist. If a PR number is provided as an argument, use it; otherwise use the PR associated with the current branch.

## Step 1: Resolve PR Context

Determine which PR to work on:

```bash
# If $ARGUMENTS is set, use it as the PR number; otherwise resolve from current branch
PR_NUMBER="${ARGUMENTS:-}"
if [ -z "$PR_NUMBER" ]; then
    PR_NUMBER=$(gh pr view --json number -q '.number' 2>/dev/null || echo "")
fi
```

If no PR can be resolved, tell the user and stop. Do not try to open a PR — this command is fix-only.

Fetch PR metadata to confirm the target:

```bash
gh pr view "$PR_NUMBER" --json number,title,headRefName,baseRefName,state,mergeable
```

Confirm the PR is open. If it is merged or closed, stop and report.

Check that the current working tree matches the PR's `headRefName`. If not, tell the user and stop — do not switch branches automatically, since the user may have unsaved work or be in a specific worktree. Tell them the command required branch and let them switch.

## Step 2: Dispatch Review Subagent

Use the `Agent` tool to run a code review in a subagent. This keeps the raw diff output out of the main context and isolates the review findings.

Agent prompt template:

```
Review PR #<number> in the current repository. The head branch is <headRefName>
and the base is <baseRefName>.

1. Get the diff with: gh pr diff <number>
2. Analyze every changed hunk for:
   - Bugs and logic errors
   - Missing error handling on system-boundary calls
   - Style violations against project conventions (read CLAUDE.md if present)
   - Missing tests for new behavior
   - Performance regressions on hot paths
   - Accessibility issues in view code (if the project has accessibility rules)
3. For each finding, return a JSON object:
   {
     "path": "relative/path.ext",
     "line": 42,
     "confidence": 0-100,
     "category": "bug|style|test|perf|a11y|other",
     "description": "What is wrong",
     "suggested_fix": "Concrete change to make (code snippet or instruction)"
   }
4. Return a JSON array of findings. If nothing is wrong, return [].

Be strict about confidence scoring. Only score >= 80 for issues you are certain
are real bugs or clear policy violations. Score 60-79 for likely-but-not-certain
issues. Score below 60 for subjective preferences — these will be discarded.
```

Capture the agent's returned JSON array as `$FINDINGS`.

## Step 3: Filter and Report

Parse `$FINDINGS` and split into three buckets:

- **Auto-fix**: confidence >= 80 — will be fixed in Step 4
- **Ask user**: confidence 60-79 — report to user for a decision, do not auto-fix
- **Discard**: confidence < 60 — ignore silently

If the auto-fix bucket is empty:

- If the ask-user bucket is also empty, report "No actionable findings" and stop.
- Otherwise, report the ask-user findings and stop — wait for the user to tell you which to address.

## Step 4: Apply Fixes

For each auto-fix finding, apply the suggested change using Edit or Write. After each fix:

1. Re-read the file to confirm the edit landed correctly
2. Keep a running list of `(path, description)` pairs for the commit message

Do NOT batch edits — apply one finding at a time so failures are isolated.

## Step 5: Build Verification

Before committing, run the project's build. This step is **mandatory** — do not skip it even if the changes seem trivial.

Find the build command:

1. Read `CLAUDE.md` in the project root, if present, for a documented build command
2. If not documented, check for common build systems in this order:
   - `Package.swift` → `swift build`
   - `*.xcodeproj` → `xcodebuild -scheme $(ls -1 *.xcodeproj | head -1 | sed 's/.xcodeproj$//') -quiet build`
   - `package.json` with a `build` script → `npm run build`
   - `Cargo.toml` → `cargo build`
   - `Makefile` with a `build` target → `make build`
3. If none match, ask the user for the build command

Run the build. If it fails:

1. Show the error output to the user
2. Do NOT attempt to fix the build failure automatically — the fix may require reverting a finding
3. Stop and wait for user guidance

If the build passes, continue.

## Step 6: Confirmation Checkpoint

Before committing and pushing, show the user:

- The PR number and title
- The list of fixes applied (path + description for each)
- The build verification result (passed)
- The pending commit message draft

Ask the user to confirm before proceeding. Do NOT commit or push without explicit confirmation. If the user declines, leave the working tree as-is (fixes applied but uncommitted) so they can adjust.

## Step 7: Commit and Push

On confirmation:

```bash
git add -A
git commit -m "$(cat <<'EOF'
review: address findings from /review-and-fix

<bulleted list of fixes, one per line>
EOF
)"
git push
```

Do not use `--no-verify`. If a pre-commit hook fails, stop and report — do not bypass.

## Step 8: Report Summary

Report to the user:

- **PR**: `#<number> <title>`
- **Fixes applied**: count and bullet list
- **Ask-user findings**: count and bullet list (if any were surfaced in Step 3)
- **Build**: passed
- **Commit**: SHA and push status
- **Next step**: suggest running `/monitor-prs` or viewing the PR to confirm CI is green
