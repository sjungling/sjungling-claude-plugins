# Workflow Plugin

Automates Git workflows with conventional commits, proper branch management, and structured pull requests.

## Overview

The `workflow` plugin streamlines your Git workflow by providing intelligent commands that handle commits and pull requests with best practices built in.

## Features

- **Conventional Commits**: Automatically formats commits following the conventional commits specification
- **Smart Branch Management**: Creates feature branches when needed, prevents commits to main
- **Structured Pull Requests**: Uses Problem & Solution format for clear communication
- **Consistent Formatting**: Enforces commit message style and PR descriptions
- **No AI Attribution**: Never adds co-authorship credit to AI tools

## Components

### Commands

**`/pr`** - Create a pull request with conventional commits

This command:
- Analyzes your changes to determine the appropriate commit type
- Creates a feature branch if you're on main/default branch
- Generates succinct commit titles with extended descriptions
- Creates structured PR with Problem & Solution format
- Handles all git operations (staging, committing, pushing, PR creation)

**`/commit-and-push`** - Create a conventional commit and push to current branch

This command:
- Reviews all staged and unstaged changes
- Selectively stages files (excludes secrets, IDE configs, build artifacts)
- Creates conventional commits with extended descriptions
- Pushes only the current branch to remote
- No branch creation or PR - just commit and push

## Installation

First, add the marketplace to Claude Code (if not already added):

```bash
/plugin marketplace add /Users/scott.jungling/Work/claude-plugins
```

Then install this plugin:

```bash
/plugin install workflow@claude-plugins
```

## Usage

### Creating a Pull Request

Simply run:

```
/pr
```

The command will:
1. Check if you're on the main/default branch
2. If so, create a new branch like `feat/new-feature` or `fix/bug-name`
3. Review all your changes
4. Create commits with conventional commit format:
   - Title: `type(scope): description`
   - Extended description with context
5. Push to remote
6. Create a PR with Problem & Solution format

### Commit and Push Without PR

To commit and push to your current branch without creating a PR:

```
/commit-and-push
```

The command will:
1. Review all changed files
2. Selectively stage files (excludes secrets, IDE configs, build artifacts)
3. Create conventional commit with extended description
4. Push to the current branch

Use this when:
- You're working on an existing PR and want to add more commits
- You want to commit and push without creating a PR yet
- You're pushing to a feature branch that already has a PR open

### Conventional Commit Types

The plugin uses these standard types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build/tooling changes
- `ci`: CI/CD configuration
- `revert`: Reverting changes

### Example Workflow

```
# Make your changes
git add .

# Create a PR - this handles everything
/pr
```

The command will:
- Create branch: `feat/add-user-authentication`
- Commit: `feat(auth): add user authentication system`
- Extended description explaining the implementation
- PR with Problem & Solution sections
- Return the PR URL

## Pull Request Format

PRs created by this plugin follow this structure:

```markdown
## Problem
[Description of the problem being solved or feature being added]

## Solution
[Explanation of the approach taken]
[Implementation details]
[Technical decisions]

## Testing
[How to test these changes]

## Related Issues
[Links to related issues if applicable]
```

## Best Practices

The plugin enforces these conventions:

1. **Branch Naming**: `{type}/{kebab-case-description}`
2. **Commit Titles**: Max 72 characters, imperative mood
3. **Commit Scope**: Optional, use when changes are scoped to a specific area
4. **No AI Attribution**: Never includes co-authorship credit to AI
5. **Atomic Commits**: Focused, single-purpose commits
6. **Protected Branches**: Never commits directly to main/default

## Tips

- Run `/pr` when you're ready to create a pull request
- The command will analyze your changes to pick the right commit type
- It reviews recent commits to match your project's style
- All git operations are handled automatically
- The PR is created and you get the URL back

## Examples

### Creating a New Feature PR

```
/pr
```

Creates:
- Branch: `feat/dark-mode-toggle`
- Commit: `feat(ui): add dark mode toggle to settings`
- PR: "Problem: Users requested dark mode. Solution: Added theme toggle..."

### Fixing a Bug with PR

```
/pr
```

Creates:
- Branch: `fix/login-validation`
- Commit: `fix(auth): validate email format on login`
- PR: "Problem: Login accepted invalid emails. Solution: Added email validation..."

### Adding Documentation with PR

```
/pr
```

Creates:
- Branch: `docs/api-endpoints`
- Commit: `docs(api): document REST endpoints`
- PR: "Problem: API endpoints were undocumented. Solution: Added comprehensive docs..."

### Commit and Push to Existing Branch

```
/commit-and-push
```

On branch `feat/dark-mode-toggle`:
- Reviews changes
- Stages: `src/components/ThemeToggle.tsx`, `src/styles/themes.css`
- Excludes: `.DS_Store`, `node_modules/`
- Commit: `feat(ui): add theme persistence with localStorage`
- Push to: `origin feat/dark-mode-toggle`

## Contributing

This plugin is part of a personal plugin collection. Feel free to adapt it for your own use.

## License

MIT
