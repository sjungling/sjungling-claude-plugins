# OpenRewrite Author Plugin

A Claude Code plugin for creating production-quality OpenRewrite recipes, specializing in YAML transformations using test-first development.

## What This Skill Does

This skill guides you through creating OpenRewrite recipes for YAML manipulation using a structured TDD workflow:

1. **Write failing tests** (RED) with before/after examples
2. **Choose architecture** (declarative vs imperative)
3. **Implement minimally** (GREEN) to pass tests
4. **Apply OpenRewrite idioms** (REFACTOR) with traits and composition
5. **Document thoroughly** with markdown examples

## Features

- **Test-First Development**: Uses OpenRewrite's testing framework
- **YAML LST Navigation**: Work with Lossless Semantic Trees
- **JsonPath Matching**: Complex pattern matching for YAML structures
- **Java 8 Compatible**: All recipes use Java 8 syntax
- **OpenRewrite Traits**: Advanced semantic abstractions
- **Reference Guide**: Comprehensive traits implementation guide

## Installation

From your Claude Code marketplace:

```
/plugin install openrewrite-author@claude-plugins
```

## Usage

The skill is automatically invoked when you work on OpenRewrite YAML recipe tasks:

```
Create a recipe to update all uses of actions/checkout@v2 to v3
```

```
Write a search recipe to find all GitHub workflows using deprecated Node 12
```

```
Help me build a YAML transformation recipe for adding timeout-minutes to jobs
```

The skill automatically uses the OpenRewrite Traits reference guide when needed for advanced semantic abstractions.

## Examples

### Simple Search Recipe

```
Find all uses of actions/setup-node with Node.js 12
```

The skill will generate a complete OpenRewrite recipe using JsonPath matching and the visitor pattern.

### Transformation Recipe

```
Create a recipe to upgrade all actions/checkout from v2 to v4
```

The skill provides a working recipe with proper LST modifications using `withX()` methods.

### Trait-Based Recipe

```
Build an ActionStep trait that can identify and modify GitHub Actions steps
```

The skill references the traits guide and implements the full trait pattern with matcher.

## Key Capabilities

- **Java 8 Compatibility**: All recipes use Java 8 syntax (no modern features)
- **LST Preservation**: Recipes maintain YAML formatting and structure
- **JsonPath Matching**: Complex path expressions for precise targeting
- **Visitor Patterns**: Proper OpenRewrite visitor implementations
- **Trait Support**: Advanced semantic abstractions for complex recipes
- **License Headers**: Automatic detection and application of repository license headers

## Plugin Structure

```
openrewrite-author/
├── .claude-plugin/
│   └── plugin.json            # Plugin metadata
├── README.md                   # This file
└── skills/                     # Skills directory
    └── rewrite-yaml/           # The rewrite-yaml skill
        ├── SKILL.md            # Main skill definition
        └── references/         # Reference materials
            └── openrewrite-traits-guide.md
```

## How It Works

This plugin follows the Claude Code plugin skills pattern:

- **skills/**: Contains individual skills, each in its own directory
- **SKILL.md**: Each skill has YAML frontmatter and comprehensive instructions
- **references/**: Supporting documentation loaded as needed by Claude
- **Progressive disclosure**: Only loads what's needed for your specific task

## References

- [OpenRewrite Documentation](https://docs.openrewrite.org)
- [rewrite-yaml LST Structure](https://docs.openrewrite.org/concepts-explanations/lossless-semantic-trees)
- [Claude Code Skills](https://docs.claude.com/en/docs/claude-code/skills)
