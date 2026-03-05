---
name: pdf-generation
description: Generate a PDF book from a directory of ordered markdown chapters using pandoc and weasyprint. Automatically activates when the user wants to produce a PDF from markdown documentation, convert a technical overview to PDF, or create a printable book from a set of chapter files. Not for single-file markdown-to-PDF conversion or non-documentation use cases.
---

# PDF book generation

## Overview

Converts a directory of ordered markdown chapters into a single, styled PDF book with table of contents, page numbers, and resolved inter-chapter links.

**Core principle:** The markdown files are the source of truth. The PDF is a derived artifact — never edit the PDF directly.

## When to use

Automatically activates when:

- User asks to generate a PDF from markdown chapters
- A `technical-overview` or similar multi-chapter doc set is ready for export
- User wants a printable or shareable version of documentation

## Prerequisites

Two tools must be installed:

| Tool | Install command | Purpose |
|------|----------------|---------|
| `pandoc` | `brew install pandoc` | Markdown to HTML conversion |
| `weasyprint` | `uv tool install weasyprint` | HTML to PDF rendering |
| `pango` | `brew install pango` | Text layout (weasyprint dependency) |

## How it works

The generation pipeline has three stages:

1. **Collect** — Gather markdown files in order: `README.md` first, then `00-*.md` through `99-*.md`, then `appendix-*.md`
2. **Convert** — Pandoc stitches all files into a single HTML document with a generated table of contents
3. **Fix links** — Inter-chapter `.md` links (e.g., `[architecture](01-architecture.md)`) are rewritten to internal `#anchor` links so they work within the single document
4. **Render** — Weasyprint converts the styled HTML to PDF with print-optimized CSS

## Usage

Run the generation script:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/pdf-generation/scripts/generate-pdf.sh <input-dir> [output.pdf]
```

- `input-dir` — Directory containing the ordered markdown chapters
- `output.pdf` — Optional output path (defaults to `<input-dir>/technical-overview.pdf`)

## Inter-document linking requirements

For the PDF to have working internal links, the source markdown must follow these rules:

- Use relative links between chapters: `[architecture overview](01-architecture.md)`
- Section links with anchors work too: `[the store layer](03-data-layer.md#store)`
- Every chapter should have exactly one `# ` heading — this is used to resolve link targets
- The script warns about any `.md` links it cannot resolve

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Error: 'pandoc' is not installed" | Missing dependency | `brew install pandoc` |
| "Error: 'weasyprint' is not installed" | Missing dependency | `uv tool install weasyprint && brew install pango` |
| Warning about unresolved `.md` links | Chapter heading doesn't match filename pattern | Ensure each chapter has a `# ` heading and the link target filename is correct |
| PDF renders but fonts look wrong | Missing system fonts | weasyprint uses system fonts; install desired fonts via Font Book |
