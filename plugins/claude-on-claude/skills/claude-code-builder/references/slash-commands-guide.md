# Slash Commands Creation Guide

## Overview

Slash commands are custom shortcuts that execute specific workflows or expand into prompts. They provide quick access to common operations and can accept arguments for dynamic behavior.

**Official Documentation**: https://docs.claude.com/en/docs/claude-code/slash-commands.md

## When to Create a Slash Command

Create a slash command when you need:
- Quick keyboard shortcuts for common tasks
- Parameterized workflows with user input
- Simple, linear execution flows
- Convenience wrappers around common operations
- Reusable prompts with argument substitution

## File Structure

Slash commands are markdown files that can optionally include YAML frontmatter:

```markdown
---
description: Clear one-line description of what this command does
allowed-tools:
  - Bash(npm run build:*)
  - Bash(npm test:*)
args:
  - name: target
    description: The build target to compile
---

[Command prompt content with instructions and optional argument placeholders]
```

### Location
- Personal: `~/.claude/commands/`
- Plugin: `<plugin-root>/commands/`
- Project: `.claude/commands/`

### Naming
- Use **kebab-case** for command file names
- File name becomes the command name
- `format-code.md` → `/format-code`
- `run-tests.md` → `/run-tests`

## YAML Frontmatter

Frontmatter is **optional** but recommended for:
- Documenting command purpose
- Preapproving tools and bash commands
- Defining expected arguments

### Fields

**`description`** (string, optional)
- One-line explanation of command purpose
- Shown in command lists and help
- Example: `Format and lint Swift code using swift-format`

**`allowed-tools`** (array, optional)
- Preapprove bash commands and tools for execution
- Uses glob patterns for flexibility
- Reduces user approval friction
- Example:
  ```yaml
  allowed-tools:
    - Bash(echo:*)
    - Bash(git:*)
    - Bash(npm run build:*)
    - Bash(swift-format:*)
  ```

**`args`** (array of objects, optional)
- Document expected command arguments
- Each arg has `name` and `description`
- For documentation only - doesn't enforce validation
- Example:
  ```yaml
  args:
    - name: environment
      description: Target environment (dev, staging, prod)
    - name: version
      description: Version tag to deploy
  ```

## Tool Preapprovals

The `allowed-tools` field uses specific syntax:

### Bash Commands

```yaml
allowed-tools:
  - Bash(command:*)  # Allow command with any arguments
  - Bash(git:*)      # Allow all git commands
  - Bash(npm run build:*)  # Allow npm run build variants
  - Bash(echo:*)     # Allow echo
  - Bash(find:*)     # Allow find
```

### Other Tools

You can also preapprove Claude Code tools:

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(*)          # Allow all bash commands (use carefully)
```

### Best Practices

**Do:**
- Be specific with command patterns
- Use wildcards for argument flexibility
- Include only necessary commands
- Consider security implications

**Don't:**
- Preapprove dangerous commands (rm -rf, etc.) unless absolutely necessary
- Use `Bash(*)` unless you fully trust the command
- Preapprove commands not used by the workflow

## Argument Handling

Commands can accept and use arguments through placeholders:

### Argument Placeholders

- `$ARGUMENTS` - All arguments as a single string
- `$1`, `$2`, `$3`, etc. - Individual positional arguments
- `$N` - Nth argument (1-indexed)

### Example: Parameterized Command

```markdown
---
description: Deploy application to specified environment
allowed-tools:
  - Bash(git:*)
  - Bash(npm run deploy:*)
args:
  - name: environment
    description: Target environment (dev, staging, prod)
---

Deploy the application to the $1 environment.

Steps:
1. Verify the git branch is clean
2. Run the deployment script for $1
3. Verify deployment succeeded
4. Update deployment tracking

Use: /deploy prod
```

Usage: `/deploy staging` → `$1` becomes `staging`

### Example: Multiple Arguments

```markdown
---
description: Create a new feature branch
allowed-tools:
  - Bash(git:*)
args:
  - name: branch-name
    description: Name of the feature branch
  - name: base-branch
    description: Base branch to branch from (default: main)
---

Create a new feature branch named "$1" from base branch "$2".

1. Checkout the base branch: $2
2. Pull latest changes
3. Create and checkout new branch: $1
4. Push the new branch to remote

Use: /create-branch my-feature main
```

Usage: `/create-branch user-auth develop` → `$1` = `user-auth`, `$2` = `develop`

## Command Content

The markdown content after frontmatter is the command's prompt/instructions:

### Simple Commands

Direct instructions that execute immediately:

```markdown
---
description: Run the test suite
allowed-tools:
  - Bash(npm test:*)
---

Run the complete test suite using npm test. Report any failures with details.
```

### Workflow Commands

Multi-step processes with clear guidance:

```markdown
---
description: Prepare a release
allowed-tools:
  - Bash(git:*)
  - Bash(npm:*)
args:
  - name: version
    description: Semantic version for the release (e.g., 1.2.3)
---

Prepare a new release version $1:

1. Update version in package.json to $1
2. Update CHANGELOG.md with version $1 and today's date
3. Commit changes with message "chore: prepare release $1"
4. Create git tag v$1
5. Build the project
6. Ask user if ready to push tag and publish

Use: /prepare-release 1.2.3
```

### Commands with Subagents

Delegate complex work to specialized agents:

```markdown
---
description: Write comprehensive API documentation
allowed-tools:
  - Task
---

Use the technical-writer agent to create comprehensive API documentation for the current project.

The documentation should include:
- API overview and getting started
- Authentication guide
- Endpoint reference with examples
- Error handling
- Rate limiting
- Code examples in multiple languages

Analyze the codebase first, then delegate to the technical-writer agent.
```

## Common Patterns

### Code Quality Commands

```markdown
---
description: Format and lint Swift code
allowed-tools:
  - Bash(swift-format:*)
  - Bash(find:*)
---

Format and lint all Swift code in the project:

1. Find all .swift files
2. Run swift-format on each file
3. Report any formatting issues
4. Fix issues automatically where possible
```

### Git Workflow Commands

```markdown
---
description: Create a conventional commit
allowed-tools:
  - Bash(git:*)
---

Create a conventional commit following the format:

type(scope): description

Where type is one of: feat, fix, docs, style, refactor, test, chore

1. Show current git status
2. Ask user for commit type and scope
3. Ask for commit description
4. Create commit with conventional format
5. Include Claude Code co-author
```

### Project Setup Commands

```markdown
---
description: Initialize a new TypeScript project
allowed-tools:
  - Bash(npm:*)
  - Bash(mkdir:*)
  - Write
---

Initialize a new TypeScript project with best practices:

1. Create directory structure (src/, tests/, dist/)
2. Initialize npm package
3. Install TypeScript and development dependencies
4. Create tsconfig.json with strict settings
5. Create initial src/index.ts
6. Set up test framework
7. Create README.md

Ask user for project name and description first.
```

### Deployment Commands

```markdown
---
description: Deploy to production
allowed-tools:
  - Bash(git:*)
  - Bash(npm run build:*)
  - Bash(gh:*)
args:
  - name: version
    description: Version to deploy (defaults to current)
---

Deploy version $1 to production:

⚠️  WARNING: This will deploy to PRODUCTION

1. Confirm with user before proceeding
2. Verify git branch is main
3. Verify working directory is clean
4. Run production build
5. Run smoke tests
6. Create GitHub release
7. Trigger deployment pipeline
8. Monitor deployment status

Use: /deploy-prod 1.2.3
```

## Testing Your Command

1. **Invoke the command**:
   ```
   /your-command arg1 arg2
   ```

2. **Verify behavior**:
   - Do arguments substitute correctly?
   - Are tools preapproved appropriately?
   - Does the workflow execute as expected?

3. **Test edge cases**:
   - Missing arguments
   - Invalid arguments
   - Error conditions

4. **Refine**:
   - Update allowed-tools if approval prompts appear
   - Clarify instructions if behavior is unexpected
   - Add error handling guidance

## Commands vs Skills vs Subagents

**Use Commands when:**
- Workflow is straightforward and linear
- You want a quick keyboard shortcut
- Users will invoke explicitly
- Arguments customize behavior
- Example: /format-code, /run-tests, /deploy

**Use Skills when:**
- Guidance should activate automatically
- Pattern applies across contexts
- Always-available best practices
- No explicit invocation needed
- Example: Code style patterns, debugging workflows

**Use Subagents when:**
- Complex decision-making required
- Context isolation needed
- Delegatable, self-contained workflows
- Specialized tool restrictions
- Example: Code reviews, technical writing

## Plugin Integration

When including commands in plugins:

1. Place command markdown files in `commands/` subdirectory
2. Register in `.claude-plugin/marketplace.json`:
   ```json
   {
     "commands": {
       "command-name": "./commands/command-name.md"
     }
   }
   ```
3. Document in plugin README.md
4. Test command installation and execution

## Example: Complete Command

```markdown
---
description: Create a new React component with tests and storybook
allowed-tools:
  - Bash(mkdir:*)
  - Write
  - Edit
args:
  - name: component-name
    description: Name of the component (PascalCase)
  - name: component-type
    description: Type of component (functional or class, defaults to functional)
---

# Create React Component: $1

Create a new React component named $1 as a $2 component.

## Steps

1. **Create component directory**:
   ```
   src/components/$1/
   ```

2. **Create component file**: `src/components/$1/$1.tsx`
   ```tsx
   import React from 'react';
   import styles from './$1.module.css';

   interface ${1}Props {
     // TODO: Define props
   }

   export const $1: React.FC<${1}Props> = (props) => {
     return (
       <div className={styles.container}>
         <h2>$1</h2>
       </div>
     );
   };
   ```

3. **Create styles**: `src/components/$1/$1.module.css`
   ```css
   .container {
     /* Component styles */
   }
   ```

4. **Create test file**: `src/components/$1/$1.test.tsx`
   ```tsx
   import { render, screen } from '@testing-library/react';
   import { $1 } from './$1';

   describe('$1', () => {
     it('renders without crashing', () => {
       render(<$1 />);
       expect(screen.getByText('$1')).toBeInTheDocument();
     });
   });
   ```

5. **Create Storybook story**: `src/components/$1/$1.stories.tsx`
   ```tsx
   import type { Meta, StoryObj } from '@storybook/react';
   import { $1 } from './$1';

   const meta: Meta<typeof $1> = {
     title: 'Components/$1',
     component: $1,
   };

   export default meta;
   type Story = StoryObj<typeof $1>;

   export const Default: Story = {
     args: {},
   };
   ```

6. **Create index file**: `src/components/$1/index.ts`
   ```ts
   export { $1 } from './$1';
   export type { ${1}Props } from './$1';
   ```

7. **Update main components index**: Add to `src/components/index.ts`:
   ```ts
   export { $1 } from './$1';
   ```

## Usage Examples

```bash
# Create functional component (default)
/create-component Button

# Create class component
/create-component Modal class
```

## Next Steps

After creating the component:
1. Define the component props interface
2. Implement component logic
3. Add styles
4. Write comprehensive tests
5. Create Storybook stories for different states
6. Update documentation
```

## Advanced Techniques

### Conditional Logic

Guide Claude to make decisions based on arguments:

```markdown
If $1 is "production":
  - Use production configuration
  - Require manual confirmation
  - Enable extra validation

If $1 is "development":
  - Use development configuration
  - Skip confirmation
  - Allow warnings
```

### Error Handling

Include guidance for error scenarios:

```markdown
If the build fails:
1. Show the error output
2. Suggest common fixes
3. Ask user if they want to retry

If tests fail:
1. Report which tests failed
2. Show failure details
3. Ask if user wants to run only failed tests
```

### Checklists

Provide systematic validation:

```markdown
Before deploying:
- [ ] All tests pass
- [ ] Build succeeds
- [ ] Version updated
- [ ] CHANGELOG updated
- [ ] Git working directory clean
- [ ] On correct branch
```

## Security Considerations

**Be careful with:**
- Commands that modify production systems
- Commands that delete files or data
- Commands with elevated privileges
- Commands that expose secrets

**Best practices:**
- Require confirmation for destructive operations
- Validate inputs before execution
- Limit preapproved commands to minimum necessary
- Document security implications
- Consider using read-only operations where possible

## Discoverability

Users discover commands through:
- `/help` command output
- Plugin documentation
- Tab completion in Claude Code
- README files

Make commands discoverable by:
- Using clear, descriptive names
- Writing good descriptions in frontmatter
- Documenting in plugin README
- Using conventional naming patterns
