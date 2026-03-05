---
description: Create or update a comprehensive technical overview for the current project
argument-hint: [output-dir]
allowed-tools:
  - Agent
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

Create or update a comprehensive technical manual for this project. The output directory is `$ARGUMENTS` (default: `doc/technical-overview` if no path given).

**Before writing any content**, invoke the `technical-writer` skill to load the full technical writing style guide. All chapters must follow those conventions — in particular: sentence case for all headings (never title case), descriptive link text (never "click here"), and the standard content structure rules.

## Writing style

Write like **Beej's Guide to Network Programming** — colloquial, approachable, educational. The reader is a competent programmer but may not be an expert in this project's language or frameworks. Explain concepts as you go. Use code examples but keep them concise. Avoid dry reference-manual tone.

Good: "So what's actually happening when you call `beginTask()`? Think of it like a relay race — the navigation state hands the baton to the store, which sets up the worktree, and then signals the view to pick it up."

Bad: "The `beginTask()` method initiates task execution by delegating to the repository store."

## Process

### 1. Understand the project

Read CLAUDE.md, README, and key entry points to understand the architecture, frameworks, and major concepts. Identify:

- The main frameworks/packages/libraries the project has built (not third-party deps)
- Core workflows and data flows
- Key concepts a new developer needs to understand
- The language and platform conventions in use

### 2. Plan the chapters

Create a table of contents with individual chapters. Always include:

- **00-introduction.md** — What is this project? Who is it for? How to read this guide.
- One chapter per major framework/package/library the project has built
- One chapter per major workflow or concept (e.g., task execution, navigation, data persistence)
- **appendix-glossary.md** — Key terms and their definitions

Write the table of contents to `{output-dir}/README.md` first.

### 3. Write chapters in parallel using teammates

Launch one Agent (subagent_type: "general-purpose") per chapter. Each agent should:

- Read the relevant source code for their chapter
- Read any existing version of their chapter file (to update rather than rewrite from scratch)
- Write or update their chapter file in `{output-dir}/`
- Follow the writing style guidelines above
- Include real code snippets from the project (not invented examples)
- Explain the "why" not just the "what"
- Target ~500-1500 words per chapter (enough to be useful, short enough to stay focused)

Give each agent the full context: project name, language, the table of contents for cross-referencing, and the style guidelines.

### 4. Review and link

After all chapters are written, read through the output directory and:

- Ensure cross-references between chapters are correct and use relative markdown links
- Verify the README table of contents matches actual files
- Check that code examples reference real files/lines in the project

### 5. Generate PDF

Invoke the `pdf-generation` skill and run the generation script to produce a PDF book from the completed chapters. This gives the user a single shareable/printable artifact.

## Important rules

- If chapters already exist, UPDATE them rather than rewriting from scratch. Preserve good content, fix outdated content.
- Use filenames like `01-architecture.md`, `02-navigation.md`, etc. for ordering.
- Each chapter should stand alone — a reader should be able to jump to any chapter.
- Include a "What you'll learn" section at the top of each chapter.
- End each chapter with "Where to go next" pointing to related chapters.
- Do NOT invent code examples. Pull real snippets from the actual source files.
- Create the output directory if it doesn't exist.
- **Inter-document linking must be complete.** Every cross-reference between chapters must use relative markdown links (e.g., `[architecture overview](01-architecture.md)` or `[the store layer](03-data-layer.md#store)`). The final set of markdown files should be self-contained so they can be collated and converted to a single PDF without broken links.
