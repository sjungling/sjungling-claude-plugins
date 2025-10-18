# Plugins and Marketplaces Guide

## Overview

Plugins are collections of Claude Code components (agents, commands, skills) packaged for distribution and installation. Plugin marketplaces enable discovery and installation of plugins from repositories.

**Official Documentation**:
- Plugins: https://docs.claude.com/en/docs/claude-code/plugins.md
- Marketplaces: https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md

## Plugin Structure

A plugin is a directory containing Claude Code components with a marketplace configuration:

```
plugin-name/
├── .claude-plugin/
│   └── marketplace.json    # Plugin metadata and component mapping
├── agents/                  # Optional: custom agents
│   ├── agent-one.md
│   └── agent-two.md
├── commands/                # Optional: slash commands
│   ├── command-one.md
│   └── command-two.md
├── skills/                  # Optional: skills
│   ├── skill-one/
│   │   └── SKILL.md
│   └── skill-two/
│       └── SKILL.md
├── SKILLS.md               # Required if skills/ exists
└── README.md               # Plugin documentation
```

## Plugin Metadata: plugin.json

Each plugin should include a `plugin.json` file in the `.claude-plugin/` directory:

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief description of what the plugin provides",
  "author": "Your Name",
  "repository": "https://github.com/username/repo",
  "keywords": ["swift", "ios", "mobile"],
  "category": "development"
}
```

### Fields

**`name`** (string, required)
- Unique identifier for the plugin
- Use kebab-case
- Example: `swift-engineer`, `technical-writer`

**`version`** (string, required)
- Semantic version number
- Format: `MAJOR.MINOR.PATCH`
- Example: `1.0.0`, `2.1.3`

**`description`** (string, required)
- Brief explanation of plugin purpose
- What components it provides
- Who should use it

**`author`** (string, optional)
- Plugin author name or organization

**`repository`** (string, optional)
- URL to source repository
- Enables users to browse code and contribute

**`keywords`** (array of strings, optional)
- Searchable tags
- Technologies, frameworks, use cases
- Example: `["swift", "ios", "xcode"]`

**`category`** (string, optional)
- Plugin category for organization
- Examples: `development`, `documentation`, `testing`, `deployment`

## Marketplace Configuration: marketplace.json

The `.claude-plugin/marketplace.json` file maps plugin components to their file locations:

```json
{
  "marketplaceName": "marketplace-name",
  "pluginRoot": "./plugins",
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "version": "1.0.0",
      "description": "Plugin description",
      "keywords": ["keyword1", "keyword2"],
      "category": "development",
      "agents": {
        "agent-name": "./agents/agent-name.md"
      },
      "commands": {
        "command-name": "./commands/command-name.md"
      },
      "skills": {
        "skill-name": "./skills/skill-name"
      }
    }
  ]
}
```

### Marketplace Fields

**`marketplaceName`** (string)
- Unique identifier for the marketplace
- Used in installation: `/plugin install name@marketplace-name`

**`pluginRoot`** (string)
- Relative path to directory containing all plugins
- Usually `"./plugins"`

**`plugins`** (array)
- List of all plugins in the marketplace
- Each plugin has metadata and component mappings

### Plugin Entry Fields

**`name`** (string, required)
- Plugin identifier
- Must match plugin.json name

**`source`** (string, required)
- Relative path from repository root to plugin directory
- **Must use `./` prefix**: `"./plugins/plugin-name"`
- This is critical for proper plugin discovery

**`version`** (string, required)
- Plugin version, should match plugin.json

**`description`** (string, required)
- Plugin description, should match plugin.json

**`keywords`** (array, optional)
- Searchable keywords

**`category`** (string, optional)
- Plugin category

**`agents`** (object, optional)
- Maps agent names to file paths
- Paths relative to plugin source directory
- Example: `{"ios-expert": "./agents/ios-expert.md"}`

**`commands`** (object, optional)
- Maps command names to file paths
- Paths relative to plugin source directory
- Example: `{"swift-lint": "./commands/swift-lint.md"}`

**`skills`** (object, optional)
- Maps skill names to directory paths
- Paths relative to plugin source directory
- Example: `{"ios-swift-expert": "./skills/ios-swift-expert"}`

### Path Requirements

**Critical**: All paths in marketplace.json must:
1. Be relative, not absolute
2. Use `./` prefix for the `source` field
3. Use forward slashes, even on Windows
4. Point to actual files/directories

**Good**:
```json
"source": "./plugins/swift-engineer"
"agents": {
  "ios-expert": "./agents/ios-expert.md"
}
```

**Bad**:
```json
"source": "plugins/swift-engineer"              // Missing ./
"source": "/absolute/path/to/plugin"           // Absolute path
"agents": {
  "ios-expert": "agents\\ios-expert.md"        // Backslashes
}
```

## Creating a Plugin

### 1. Plan Your Plugin

Determine:
- What problem does it solve?
- What components are needed (agents, commands, skills)?
- Who is the target audience?
- What tools and workflows will it provide?

### 2. Create Directory Structure

```bash
mkdir -p plugin-name/.claude-plugin
mkdir -p plugin-name/agents
mkdir -p plugin-name/commands
mkdir -p plugin-name/skills
```

### 3. Create plugin.json

```bash
cat > plugin-name/.claude-plugin/plugin.json << 'EOF'
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Your plugin description",
  "author": "Your Name",
  "keywords": ["tag1", "tag2"],
  "category": "development"
}
EOF
```

### 4. Add Components

Create agents, commands, and/or skills following their respective guides:
- See `subagents-guide.md` for agent creation
- See `slash-commands-guide.md` for command creation
- See `skills-guide.md` for skill creation

### 5. Create Documentation

**README.md**:
```markdown
# Plugin Name

Brief description of what the plugin does.

## Components

### Agents
- **agent-name**: Description of agent

### Commands
- **/command-name**: Description of command

### Skills
- **skill-name**: Description of skill

## Installation

Add the marketplace:
\`\`\`
/plugin marketplace add <repository-url>
\`\`\`

Install the plugin:
\`\`\`
/plugin install plugin-name@marketplace-name
\`\`\`

## Usage

[Usage examples and documentation]
```

**SKILLS.md** (if plugin includes skills):
```markdown
# Plugin Skills

## skill-name

Description of what the skill does and when it activates.

### What It Provides
- Capability 1
- Capability 2

### Example Usage
[Brief example]
```

### 6. Register in Marketplace

Add plugin entry to marketplace.json:

```json
{
  "marketplaceName": "your-marketplace",
  "pluginRoot": "./plugins",
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "version": "1.0.0",
      "description": "Your plugin description",
      "keywords": ["tag1", "tag2"],
      "category": "development",
      "agents": {
        "agent-name": "./agents/agent-name.md"
      },
      "commands": {
        "command-name": "./commands/command-name.md"
      },
      "skills": {
        "skill-name": "./skills/skill-name"
      }
    }
  ]
}
```

## Installing Plugins

### Add Marketplace

```bash
/plugin marketplace add /path/to/marketplace
# or
/plugin marketplace add https://github.com/user/marketplace
```

### List Available Plugins

```bash
/plugin list marketplace-name
```

### Install Plugin

```bash
/plugin install plugin-name@marketplace-name
```

### Verify Installation

Check that agents, commands, and skills are available:
- Agents: Use Task tool with subagent_type
- Commands: Type `/command-name`
- Skills: Should activate automatically based on context

## Best Practices

### Plugin Design

**Do:**
- Focus on a specific domain or use case
- Provide comprehensive documentation
- Include usage examples
- Follow semantic versioning
- Test all components before publishing

**Don't:**
- Create overly broad, unfocused plugins
- Duplicate existing functionality
- Include untested components
- Use absolute paths in configurations

### Component Organization

**Agents**: Use when delegatable workflows need isolation
**Commands**: Use for keyboard shortcuts and parameterized tasks
**Skills**: Use for automatic, context-aware guidance

Most plugins should favor **skills** over agents for better UX (automatic activation).

### Documentation

Include in README:
- What problem the plugin solves
- Complete component listing
- Installation instructions
- Usage examples
- Common workflows
- Troubleshooting

Include in SKILLS.md:
- Detailed skill descriptions
- Activation triggers
- What capabilities each skill provides
- Usage examples

### Versioning

Follow semantic versioning:
- **MAJOR**: Breaking changes, incompatible updates
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Update version in both:
- `plugin.json`
- `marketplace.json` plugin entry

### Testing

Before publishing:

1. **Validate JSON**:
   ```bash
   cat .claude-plugin/marketplace.json | python -m json.tool
   cat .claude-plugin/plugin.json | python -m json.tool
   ```

2. **Test installation**:
   ```bash
   /plugin marketplace add /path/to/your/repo
   /plugin install plugin-name@marketplace-name
   ```

3. **Test components**:
   - Invoke each agent
   - Run each command
   - Trigger each skill
   - Verify all work as expected

4. **Verify paths**:
   - All files referenced in marketplace.json exist
   - Paths are relative with proper `./` prefix
   - No broken links in documentation

## Common Patterns

### Single-Purpose Plugin

Plugin with one focused capability:

```
swift-engineer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── ios-swift-expert/
│       └── SKILL.md
├── commands/
│   └── swift-lint.md
├── SKILLS.md
└── README.md
```

### Multi-Component Plugin

Plugin with multiple related capabilities:

```
web-development/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── react-expert.md
│   └── api-designer.md
├── commands/
│   ├── create-component.md
│   └── run-dev-server.md
├── skills/
│   ├── react-patterns/
│   │   └── SKILL.md
│   └── api-testing/
│       └── SKILL.md
├── SKILLS.md
└── README.md
```

### Plugin Collection Marketplace

Multiple related plugins in one marketplace:

```
marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    ├── plugin-one/
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── [components]
    ├── plugin-two/
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── [components]
    └── plugin-three/
        ├── .claude-plugin/
        │   └── plugin.json
        └── [components]
```

## Marketplace Management

### Adding New Plugins

1. Create plugin directory in `plugins/`
2. Add plugin metadata to `.claude-plugin/plugin.json`
3. Create components
4. Register in `.claude-plugin/marketplace.json`
5. Update main README
6. Test installation

### Updating Plugins

1. Make changes to plugin components
2. Update version in `plugin.json`
3. Update version in `marketplace.json`
4. Document changes in plugin README
5. Test updated plugin
6. Commit and push

### Deprecating Plugins

1. Mark as deprecated in description
2. Add deprecation notice to README
3. Suggest alternative plugins
4. Keep available for backward compatibility
5. Eventually remove from marketplace

## Distribution

### Local Distribution

Share repository path:
```bash
/plugin marketplace add /path/to/marketplace
```

### Git Repository

Host on GitHub/GitLab:
```bash
/plugin marketplace add https://github.com/user/marketplace
```

### Documentation

Provide clear instructions:
1. How to add the marketplace
2. How to install plugins
3. What each plugin provides
4. Usage examples
5. Troubleshooting

## Troubleshooting

### Plugin Not Found

**Issue**: `/plugin install plugin-name@marketplace-name` fails

**Solutions**:
- Verify marketplace is added: `/plugin marketplace list`
- Check plugin name matches marketplace.json
- Ensure marketplace.json is valid JSON
- Verify `source` path has `./` prefix

### Components Not Available

**Issue**: Installed plugin components don't appear

**Solutions**:
- Check component paths in marketplace.json
- Verify files exist at specified paths
- Ensure YAML frontmatter is valid (agents, skills)
- Restart Claude Code session

### Invalid Marketplace JSON

**Issue**: Marketplace JSON validation fails

**Solutions**:
- Validate with JSON linter
- Check for trailing commas
- Verify all paths use forward slashes
- Ensure proper quote escaping

### Skill Not Activating

**Issue**: Skill doesn't trigger in expected contexts

**Solutions**:
- Review skill description for trigger keywords
- Add more specific context triggers
- Verify SKILL.md has valid frontmatter
- Check skill is registered in marketplace.json

## Example: Complete Plugin

**Directory structure**:
```
swift-engineer/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── ios-swift-expert.md
├── commands/
│   └── swift-lint.md
├── skills/
│   └── ios-swift-expert/
│       ├── SKILL.md
│       └── references/
│           └── swift-style-guide.md
├── SKILLS.md
└── README.md
```

**plugin.json**:
```json
{
  "name": "swift-engineer",
  "version": "1.0.0",
  "description": "iOS and macOS development expertise with Swift tooling",
  "author": "Scott Jungling",
  "repository": "https://github.com/username/claude-plugins",
  "keywords": ["swift", "ios", "macos", "xcode", "swiftui"],
  "category": "development"
}
```

**marketplace.json entry**:
```json
{
  "name": "swift-engineer",
  "source": "./plugins/swift-engineer",
  "version": "1.0.0",
  "description": "iOS and macOS development expertise with Swift tooling",
  "keywords": ["swift", "ios", "macos", "xcode", "swiftui"],
  "category": "development",
  "agents": {
    "ios-swift-expert": "./agents/ios-swift-expert.md"
  },
  "commands": {
    "swift-lint": "./commands/swift-lint.md"
  },
  "skills": {
    "ios-swift-expert": "./skills/ios-swift-expert"
  }
}
```

**README.md**:
```markdown
# Swift Engineer Plugin

Expert iOS and macOS development assistance with Swift tooling.

## Components

### Skills

**ios-swift-expert**: Automatically activates when working with Swift, SwiftUI, UIKit, Xcode projects, or Apple frameworks. Provides expert guidance on iOS/macOS development.

### Commands

**/swift-lint**: Format and lint Swift code using swift-format

### Agents

**ios-swift-expert**: Delegatable iOS/macOS development expert (prefer using the skill for automatic activation)

## Installation

Add the marketplace:
\`\`\`
/plugin marketplace add https://github.com/username/claude-plugins
\`\`\`

Install the plugin:
\`\`\`
/plugin install swift-engineer@claude-plugins
\`\`\`

## Usage

The ios-swift-expert skill activates automatically when working with Swift code. For example:

- Opening .swift files
- Discussing SwiftUI layouts
- Debugging iOS apps
- Configuring Xcode projects

Use the `/swift-lint` command to format code:
\`\`\`
/swift-lint
\`\`\`

## Requirements

- swift-format installed for linting command
- Xcode for iOS/macOS development

## License

MIT
```

This comprehensive setup provides users with automatic expertise (skill), convenient shortcuts (command), and delegatable workflows (agent).
