---
description: Create a pull request with conventional commits formatting
preapprovedTools:
  - Bash(git:*)
  - Bash(gh:*)
  - Read(**/*.*)
  - Grep
  - Glob
  - TodoWrite
---

You are tasked with creating a pull request following these strict requirements:

# Branch Management
1. Check the current branch using `git branch --show-current`
2. Get the default branch using `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'`
3. If we're on the main/default branch:
   - Analyze the changes to determine the appropriate conventional commit type
   - Create a new branch using the format: `{type}/{short-description}` (e.g., `fix/auth-token-validation`, `feat/add-dark-mode`)
   - The short-description should be kebab-case and descriptive
   - Check out the new branch

# Conventional Commit Types
Use these standard types for commits and branch names:
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

# Commit Creation
1. Review all staged and unstaged changes using `git status` and `git diff`
2. Review recent commit messages for style consistency using `git log -5 --oneline`
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
4. Create commits with:
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

# Pull Request Creation
1. Push the branch to remote with tracking: `git push -u origin {branch-name}`
2. Create PR using `gh pr create` with:
   - **PR Title**: Same format as commit title - `{type}({scope}): {short description}`
   - **PR Description**: Use Problem & Solution format with heredoc:

```bash
gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
## Problem
[Describe the problem being solved, why this change is needed, or what gap this fills]

## Solution
[Explain the approach taken to solve the problem]
[Include specific implementation details]
[Note any important technical decisions]

## Testing
[How to test these changes]

## Related Issues
[Link any related issues if applicable]
EOF
)"
```

3. Return the PR URL to the user

# Important Rules
- NEVER add "Co-Authored-By: Claude" or any AI attribution to commits or PRs
- NEVER push directly to main/default branch
- NEVER use `git add .` or `git add -A` - always stage files selectively
- Always use conventional commit format
- Keep commit titles concise and descriptive (max 72 chars)
- Include meaningful extended descriptions for context
- Ensure commits are atomic and focused
- Use Problem & Solution format for all PR descriptions
- STOP and ask user if potentially sensitive files are detected in changes

# Workflow Summary
1. Check current branch → create feature branch if on main
2. Review changes with `git status` and `git diff` → determine commit type
3. **Selectively stage files** (review each file, exclude sensitive/generated files)
4. Create conventional commit with extended description
5. Push branch → create PR with Problem & Solution format
6. Return PR URL

Proceed with creating the pull request following these guidelines.
