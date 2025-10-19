---
description: Create a conventional commit and push to current branch
args:
  - name: pre-commit-action
    description: Optional action to perform before committing (e.g., "run tests", "update version", "lint code")
preapprovedTools:
  - Bash(git:*)
  - Read(**/*.*)
  - Grep
  - Glob
  - TodoWrite
---

You are tasked with creating a conventional commit and pushing to the current branch following these strict requirements:

# Pre-Commit Action

If the user provided a pre-commit action argument ($1), perform that action FIRST before proceeding with the commit workflow:
- Read and understand what action is requested
- Execute the requested action (e.g., run tests, update version numbers, run linters)
- Verify the action completed successfully
- If the action fails, STOP and report the error - do not proceed with commit
- If the action succeeds, continue with the commit workflow below

If no pre-commit action was specified, proceed directly to the commit workflow.

# Conventional Commit Types
Use these standard types for commits:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling
- `ci`: CI/CD configuration changes
- `revert`: Reverting previous commits

# Commit Creation Workflow

1. **Review changes**:
   - Run `git status` to see all changed files
   - Run `git diff` to see unstaged changes
   - Run `git diff --staged` to see already-staged changes

2. **Review commit style**:
   - Run `git log -5 --oneline` to understand the project's commit message style

3. **Selectively stage files** (NEVER use `git add .` or `git add -A`):
   - Review the output of `git status` carefully
   - Stage files individually using `git add <file1> <file2> ...`
   - **EXCLUDE these file patterns** (never stage):
     - Secret/credential files: `.env`, `.env.*`, `credentials.json`, `secrets.*`, `*.key`, `*.pem`
     - IDE configs: `.vscode/`, `.idea/`, `*.swp`, `*.swo`, `.DS_Store`
     - Build artifacts: `node_modules/`, `dist/`, `build/`, `target/`, `*.log`
     - Temporary files: `tmp/`, `temp/`, `*.tmp`, `*.cache`
     - Personal configs: `.env.local`, `config.local.*`
   - If you detect any of these patterns in changed files, **STOP and ask the user** before proceeding
   - Only stage files that are directly related to the changes being committed

4. **Create conventional commit**:
   - **Title format**: `{type}({scope}): {short description}` or `{type}: {short description}`
   - Title should be max 72 characters
   - Use imperative mood ("add feature" not "added feature")
   - **Extended description**: Multi-line explanation of:
     - What changed and why
     - Any breaking changes or important notes
     - Related issues or tickets
   - NEVER include co-authorship credit to Claude or any AI agent
   - Format: Use git commit with heredoc for proper multi-line formatting

Example commit:
```bash
git commit -m "$(cat <<'EOF'
feat(auth): add user authentication system

Implements JWT-based authentication with refresh tokens.
Includes middleware for protected routes and token validation.
Adds login, logout, and token refresh endpoints.

Breaking change: API now requires Authorization header for protected routes.
EOF
)"
```

5. **Push changes**:
   - Get current branch name: `git branch --show-current`
   - Push only the current branch: `git push origin {current-branch}`
   - If the branch doesn't exist on remote, use: `git push -u origin {current-branch}`

# Important Rules
- NEVER add "Co-Authored-By: Claude" or any AI attribution to commits
- NEVER use `git add .` or `git add -A` - always stage files selectively
- Always use conventional commit format
- Keep commit titles concise and descriptive (max 72 chars)
- Include meaningful extended descriptions for context
- Ensure commits are atomic and focused
- STOP and ask user if potentially sensitive files are detected in changes
- Only push the current branch (no tags, no other branches)

# Workflow Summary
1. Review changes → `git status`, `git diff`
2. Review recent commits → `git log -5 --oneline`
3. **Selectively stage files** (review each file, exclude sensitive/generated files)
4. Create conventional commit with extended description using heredoc
5. Push current branch to remote

Proceed with creating the commit and pushing following these guidelines.
