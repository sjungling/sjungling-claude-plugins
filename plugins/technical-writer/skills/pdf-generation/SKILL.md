---
name: pdf-generation
description: This skill should be used when the user asks to "generate a PDF from markdown", "create a printable book", "convert documentation to PDF", or "export chapters as a PDF". Automatically activates when producing a PDF from a directory of ordered markdown chapters using pandoc and weasyprint. Not for single-file markdown-to-PDF conversion or non-documentation use cases.
---

# PDF Book Generation

## Overview

Converts a directory of ordered markdown chapters into a single, styled PDF book with table of contents, page numbers, and resolved inter-chapter links.

**Core principle:** The markdown files are the source of truth. The PDF is a derived artifact -- never edit the PDF directly.

## When to Use

Automatically activates when:

- A request to generate a PDF from markdown chapters is made
- A `technical-overview` or similar multi-chapter doc set is ready for export
- A printable or shareable version of documentation is needed

## Prerequisites

Three tools must be installed before generation can proceed:

| Tool | Install command | Purpose |
|------|----------------|---------|
| `pandoc` | `brew install pandoc` | Markdown to HTML conversion |
| `weasyprint` | `uv tool install weasyprint` | HTML to PDF rendering |
| `pango` | `brew install pango` | Text layout (weasyprint dependency) |

Before running the script, verify availability:

```bash
command -v pandoc >/dev/null 2>&1 || echo "Missing: pandoc (brew install pandoc)"
command -v weasyprint >/dev/null 2>&1 || echo "Missing: weasyprint (uv tool install weasyprint)"
```

If either tool is missing, install it and retry. The script itself checks for dependencies and exits with a clear error message.

## How It Works

The generation pipeline has four stages:

1. **Collect** -- Gather markdown files in order: `README.md` first, then `00-*.md` through `99-*.md`, then `appendix-*.md`
2. **Convert** -- Pandoc stitches all files into a single HTML document with a generated table of contents
3. **Fix links** -- Inter-chapter `.md` links (e.g., `[architecture](01-architecture.md)`) are rewritten to internal `#anchor` links so they work within the single document
4. **Render** -- Weasyprint converts the styled HTML to PDF with print-optimized CSS

## Usage

Run the generation script using `$CLAUDE_PLUGIN_ROOT`:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/pdf-generation/scripts/generate-pdf.sh <input-dir> [output.pdf]
```

- `input-dir` -- Directory containing the ordered markdown chapters
- `output.pdf` -- Optional output path (defaults to `<input-dir>/technical-overview.pdf`)

### Handling Missing CLAUDE_PLUGIN_ROOT

If `$CLAUDE_PLUGIN_ROOT` is not set (e.g., running outside a plugin context), locate the script manually:

```bash
# Fallback: find the script in the plugin installation directory
SCRIPT_PATH=$(find ~/.claude/plugins -path "*/pdf-generation/scripts/generate-pdf.sh" 2>/dev/null | head -1)
if [ -z "$SCRIPT_PATH" ]; then
  echo "Error: generate-pdf.sh not found. Ensure the technical-writer plugin is installed."
  exit 1
fi
"$SCRIPT_PATH" <input-dir> [output.pdf]
```

## Expected Directory Structure

The input directory must contain ordered markdown files following this naming convention:

```
docs/technical-overview/
├── README.md              # Title page and introduction (always first)
├── 00-getting-started.md  # Numbered chapters in sequence
├── 01-architecture.md
├── 02-data-model.md
├── 03-api-reference.md
├── 04-deployment.md
├── appendix-a-glossary.md # Appendices after numbered chapters
└── appendix-b-faq.md
```

**Expected output:**

```
docs/technical-overview/
├── ... (source files unchanged)
└── technical-overview.pdf  # Generated PDF (default output location)
```

The PDF includes:
- A title derived from the first `# ` heading in `README.md` (or the directory name as fallback)
- A generated table of contents with depth 2 (h1 and h2 headings)
- Page numbers centered at the bottom of each page
- Chapter breaks (each h1 starts on a new page)
- Resolved inter-chapter links as internal anchors

## Inter-Document Linking Requirements

For the PDF to have working internal links, the source markdown must follow these rules:

- Use relative links between chapters: `[architecture overview](01-architecture.md)`
- Section links with anchors work too: `[the store layer](03-data-layer.md#store)`
- Every chapter should have exactly one `# ` heading -- this is used to resolve link targets
- The script warns about any `.md` links it cannot resolve

**Common linking mistakes:**

| Mistake | Fix |
|---------|-----|
| Absolute paths (`/docs/01-arch.md`) | Use relative paths (`01-arch.md`) |
| Missing `# ` heading in chapter | Add exactly one h1 heading per chapter |
| Link to file not in input directory | Ensure all linked files are in the same directory |

## Styling and Customization

The script embeds a print-optimized CSS stylesheet with sensible defaults:

- **Page size:** US Letter with 1-inch top/bottom margins
- **Fonts:** System font stack (Apple system fonts, Segoe UI, Helvetica, Arial)
- **Code blocks:** Light gray background with monospace font at 9pt
- **Tables:** Bordered with alternating row colors
- **Chapter breaks:** Each h1 heading starts on a new page

For detailed CSS customization options (fonts, colors, page sizes, themes), see `./references/css-customization.md`.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Error: 'pandoc' is not installed" | Missing dependency | `brew install pandoc` |
| "Error: 'weasyprint' is not installed" | Missing dependency | `uv tool install weasyprint && brew install pango` |
| Warning about unresolved `.md` links | Chapter heading does not match filename pattern | Ensure each chapter has a `# ` heading and the link target filename is correct |
| PDF renders but fonts look wrong | Missing system fonts | weasyprint uses system fonts; install desired fonts via Font Book |
| Empty PDF or no chapters found | Files not matching naming convention | Verify files follow `README.md`, `00-*.md` through `99-*.md`, `appendix-*.md` pattern |
| `CLAUDE_PLUGIN_ROOT` is empty | Running outside plugin context | Use the fallback script discovery method described above |
| Long code blocks overflow margins | Default CSS handles this | Verify `overflow-wrap: break-word` and `white-space: pre-wrap` in CSS |

## Additional Resources

- **`./references/css-customization.md`** -- Detailed CSS customization options for fonts, page sizes, colors, and themes
- **`./scripts/generate-pdf.sh`** -- The generation script (inspect for advanced modification)
