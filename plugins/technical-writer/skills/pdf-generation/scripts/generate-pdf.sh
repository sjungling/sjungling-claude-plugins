#!/usr/bin/env bash
set -euo pipefail

# Generate a single PDF from a directory of ordered markdown chapters.
# Uses pandoc (markdown -> HTML) + weasyprint (HTML -> PDF).
#
# Usage: generate-pdf.sh <input-dir> [output.pdf]
#
# If output.pdf is not specified, writes to <input-dir>/technical-overview.pdf

INPUT_DIR="${1:?Usage: generate-pdf.sh <input-dir> [output.pdf]}"
INPUT_DIR="${INPUT_DIR%/}"

if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: directory '$INPUT_DIR' does not exist" >&2
  exit 1
fi

OUTPUT_PDF="${2:-${INPUT_DIR}/technical-overview.pdf}"

# --- Check dependencies ---
for cmd in pandoc weasyprint; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: '$cmd' is not installed." >&2
    if [ "$cmd" = "pandoc" ]; then
      echo "  Install with: brew install pandoc" >&2
    else
      echo "  Install with: uv tool install weasyprint" >&2
      echo "  Also requires pango: brew install pango" >&2
    fi
    exit 1
  fi
done

# --- Collect markdown files in order ---
# README first, then numbered chapters (00-*, 01-*, ...), then appendix-*
FILES=()
[ -f "$INPUT_DIR/README.md" ] && FILES+=("$INPUT_DIR/README.md")

for f in "$INPUT_DIR"/[0-9][0-9]-*.md; do
  [ -f "$f" ] && FILES+=("$f")
done

for f in "$INPUT_DIR"/appendix-*.md; do
  [ -f "$f" ] && FILES+=("$f")
done

if [ ${#FILES[@]} -eq 0 ]; then
  echo "Error: no markdown files found in '$INPUT_DIR'" >&2
  exit 1
fi

echo "Collecting ${#FILES[@]} chapters from $INPUT_DIR"

# --- Derive title from README or directory name ---
TITLE="Technical Overview"
if [ -f "$INPUT_DIR/README.md" ]; then
  first_heading=$(head -5 "$INPUT_DIR/README.md" | grep '^# ' | head -1 | sed 's/^# //')
  [ -n "$first_heading" ] && TITLE="$first_heading"
fi

# --- Create temp files ---
TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

HTML_RAW="$TMPDIR_WORK/raw.html"
HTML_FIXED="$TMPDIR_WORK/fixed.html"
CSS_FILE="$TMPDIR_WORK/print.css"

# --- Print stylesheet ---
cat > "$CSS_FILE" << 'CSS'
@page {
  size: letter;
  margin: 1in 0.75in;
  @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #1a1a1a;
  max-width: 100%;
}
h1 { font-size: 22pt; margin-top: 2em; page-break-before: always; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 16pt; margin-top: 1.5em; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
h3 { font-size: 13pt; margin-top: 1.2em; }
code { font-family: "SF Mono", "Fira Code", Menlo, monospace; font-size: 9.5pt; background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 12px; font-size: 9pt; line-height: 1.45; overflow-wrap: break-word; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10pt; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
th { background: #f0f0f0; font-weight: 600; }
tr:nth-child(even) { background: #fafafa; }
blockquote { border-left: 4px solid #ddd; margin-left: 0; padding-left: 1em; color: #555; }
a { color: #0366d6; text-decoration: none; }
nav#TOC { page-break-after: always; }
nav#TOC h2 { font-size: 18pt; }
nav#TOC ul { list-style: none; padding-left: 0; }
nav#TOC li { margin: 0.3em 0; }
nav#TOC ul ul { padding-left: 1.5em; }
CSS

# --- Step 1: Markdown -> HTML with pandoc ---
echo "Converting markdown to HTML..."
pandoc "${FILES[@]}" \
  -f gfm \
  -t html5 \
  --standalone \
  --metadata title="$TITLE" \
  --toc \
  --toc-depth=2 \
  --css="$CSS_FILE" \
  -o "$HTML_RAW"

# --- Step 2: Fix inter-chapter links ---
# In the stitched HTML, links like href="01-architecture.md" need to become
# internal anchor links (href="#heading-id"). We extract all h1 id attributes
# from the generated HTML, then match each source file's first heading to
# find the correct anchor — no need to reimplement pandoc's ID algorithm.
echo "Fixing inter-chapter links..."

SED_SCRIPT="$TMPDIR_WORK/fix-links.sed"
> "$SED_SCRIPT"

# Extract all h1 ids from the HTML (format: one id per line)
H1_IDS="$TMPDIR_WORK/h1-ids.txt"
grep '<h1 id="' "$HTML_RAW" | sed 's/.*<h1 id="//;s/".*//' > "$H1_IDS"

for f in "${FILES[@]}"; do
  basename=$(basename "$f")
  # Extract the first h1 heading text from the markdown
  heading=$(grep '^# ' "$f" | head -1 | sed 's/^# //')
  [ -z "$heading" ] && continue

  # Convert heading to a grep-friendly pattern: lowercase, collapse whitespace,
  # replace non-alphanumeric chars with flexible matchers
  search_pattern=$(echo "$heading" | \
    tr '[:upper:]' '[:lower:]' | \
    sed 's/[^a-z0-9]/-*/g' | \
    sed 's/-\*-\*/-*/g')

  # Find the matching h1 id
  anchor=$(grep -m1 "$search_pattern" "$H1_IDS" 2>/dev/null || true)

  if [ -n "$anchor" ]; then
    escaped_basename=$(echo "$basename" | sed 's/\./\\./g')
    echo "s|href=\"\\(\\./\\)\\{0,1\\}${escaped_basename}\"|href=\"#${anchor}\"|g" >> "$SED_SCRIPT"
  else
    echo "  Warning: could not find anchor for '$basename' (heading: '$heading')" >&2
  fi
done

if [ -s "$SED_SCRIPT" ]; then
  sed -f "$SED_SCRIPT" "$HTML_RAW" > "$HTML_FIXED"
else
  cp "$HTML_RAW" "$HTML_FIXED"
fi

# Report any remaining .md links
remaining=$(grep -c 'href="[^#][^"]*\.md"' "$HTML_FIXED" 2>/dev/null || true)
if [ "$remaining" -gt 0 ]; then
  echo "  Warning: $remaining .md links could not be resolved to anchors" >&2
fi

# --- Step 3: HTML -> PDF with weasyprint ---
echo "Generating PDF..."
DYLD_FALLBACK_LIBRARY_PATH="${DYLD_FALLBACK_LIBRARY_PATH:-}:/opt/homebrew/lib" \
  weasyprint "$HTML_FIXED" "$OUTPUT_PDF" 2>&1 | grep -v '^WARNING:' || true

echo "Done: $OUTPUT_PDF ($(du -h "$OUTPUT_PDF" | cut -f1 | xargs))"
