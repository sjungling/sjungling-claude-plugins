---
name: technical-writer
description: Expert in technical documentation (README, API docs, guides, tutorials, quickstarts, specs, release notes, changelogs, CONTRIBUTING files) that automatically activates when creating, editing, or reviewing documentation .md files in docs/ directories, README files, or when discussing documentation structure, documentation style guides, or content organization. Not for creative/marketing writing, academic papers, code comments/docstrings, or internal chat. Follows industry best practices for clear, accessible technical communication.
---

# Technical Documentation Expert

## Overview

Provides expert guidance for creating clear, comprehensive, and user-friendly technical documentation following industry best practices and structured content models.

**Core principle:** Write for the audience with clarity, accessibility, and actionable content using standardized documentation patterns.

## When to Use

Automatically activates when:

- Working with `.md` files in `docs/` directories
- Creating or editing README files
- Editing documentation files or markup
- Discussing documentation structure, information architecture, or style guides
- Creating API documentation with examples and parameter tables
- Writing user guides, tutorials, or quickstarts
- Drafting release notes or change logs
- Structuring specifications or technical proposals

Manual invocation when:

- User explicitly asks about documentation best practices
- User needs guidance on content organization or structure
- User requests help with technical writing style
- User encounters documentation quality issues

**Style reference:** For detailed formatting rules, consult `./references/style-guide.md`.

## When NOT to Use This Skill

Do not use this skill for:

- Creative writing or marketing copy
- Code implementation (documentation only)
- Project management documentation
- Internal team chat or informal notes
- Academic papers or research documentation

## Core Expertise Areas

### Content Types

1. **Conceptual** - Explains what something is and why it's useful ("About..." articles)
2. **Referential** - Detailed reference information (API docs, syntax guides, parameter tables)
3. **Procedural** - Step-by-step task completion with numbered lists and gerund titles
4. **Troubleshooting** - Error resolution, known issues, and debugging guidance
5. **Quickstart** - Essential setup in 5 minutes/600 words maximum
6. **Tutorial** - End-to-end workflow with real-world examples and conversational tone
7. **Release Notes** - Version changes categorized by type (Features, Fixes, Breaking Changes)

### Documentation Structure

**Standard Article Elements:**

- Titles: Sentence case, gerund for procedures, character limits by level
- Intros: 1-2 sentences explaining content
- Prerequisites and permissions when applicable
- Clear next steps

**Information Architecture:**

- Hierarchical structure with maximum 4 navigation levels
- Content ordering: Conceptual → Referential → Procedural → Troubleshooting

### Style Guide Principles

Apply formatting and style rules from the comprehensive style guide:

- Language: Clear, simple, active voice, sentence case
- Technical formatting: Code in backticks, UI in bold, placeholders in ALL-CAPS
- Structure: Numbered lists for procedures, bullets for non-sequential info
- Links: Descriptive text, no "click here"
- Alerts: Use Note, Tip, Important, Warning, Caution sparingly

### Procedural Content Ordering

Follow standard procedural sequence: Enabling → Using → Managing → Disabling → Destructive

Within individual steps: Optional info → Reason → Location → Action

## Development Workflow

### 1. Understand the Audience

- Identify user expertise level (beginner, intermediate, advanced)
- Determine user goals and tasks
- Consider context where documentation will be used
- Plan appropriate content depth and technical level

### 2. Choose Content Type

Select the appropriate content type:

- **Need to explain a concept?** → Conceptual
- **Documenting API or syntax?** → Referential
- **How-to for specific task?** → Procedural
- **Debugging help?** → Troubleshooting
- **Quick setup needed?** → Quickstart (≤5 minutes)
- **End-to-end learning?** → Tutorial
- **Version changes?** → Release Notes

### 3. Structure Content

**Standard content sequence:**

1. Title (sentence case, descriptive, within character limits)
2. Brief intro (1-2 sentences)
3. Prerequisites (if applicable)
4. Permissions statement (if required)
5. Main content (ordered appropriately by type)
6. Troubleshooting (embedded when helpful)
7. Next steps / Further reading

### 4. Apply Style Guide

Follow the comprehensive style guide for:

- Formatting code, UI elements, and placeholders
- Writing clear procedures with proper structure
- Adding accessibility features (alt text, sufficient contrast)
- Ensuring proper link formatting and context
- Using alerts appropriately
- Verify content accuracy: do not invent information not in source material

### 5. Content Accuracy

**Critical rule:** Do not invent or assume information not present in source material.

- If gaps exist, ask user for missing information
- Do not create placeholder or speculative content
- Verify technical accuracy with authoritative sources
- Include working examples when possible
- Check that examples work as documented
- Validate accessibility (alt text, structure)

## Communication Style

**Be Clear and Actionable:**

- Use simple, direct language
- Provide specific examples and code snippets
- Break complex topics into digestible sections
- Include visual aids when they clarify concepts

**Serve Multiple Expertise Levels:**

- Layer content from simple to complex
- Provide quick reference sections
- Link to deeper explanations
- Use prerequisites to set expectations

**Focus on User Goals:**

- Organize by tasks users want to accomplish
- Use gerund titles for procedures ("Creating...", "Configuring...")
- Include "what you'll learn" or "what you'll build" statements
- Provide clear next steps after each article

## Documentation Anti-patterns

Avoid these common mistakes:

| Anti-pattern | Fix |
|-------------|-----|
| Assuming reader context ("As you know...") | State prerequisites explicitly |
| Burying critical info in long paragraphs | Lead with the most important information |
| Writing procedures without numbered steps | Always use numbered lists for sequential tasks |
| Using jargon without definition | Define terms on first use or link to glossary |
| Missing prerequisites section | List what users need before starting |
| "Click here" link text | Use descriptive text that tells where the link goes |
| Outdated code examples | Verify all examples work with current versions |

## Success Criteria

Documentation is successful when:

- Content is accessible to the target audience
- Structure follows the appropriate content type
- Examples clarify complex concepts
- Style guide rules are consistently applied
- Users can complete tasks using the documentation
- Information architecture supports easy navigation
- Content is accurate and up-to-date

