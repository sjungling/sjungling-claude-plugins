#!/usr/bin/env bash
#
# License Header Script
#
# Adds or updates license headers in Java source files based on the project's
# license template file (gradle/licenseHeader.txt).
#
# Usage:
#   ./add_license_header.sh <java-file>
#   ./add_license_header.sh src/main/java/com/example/MyRecipe.java
#
# Features:
# - Checks for gradle/licenseHeader.txt in repository root
# - Substitutes ${year} with current year
# - Preserves existing package/import statements
# - Skips files that already have the correct header
#
# Exit codes:
#   0 - Success (header added or already present)
#   1 - License template file not found
#   2 - Invalid arguments or file not found

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current year
CURRENT_YEAR=$(date +%Y)

# Function to find repository root
find_repo_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]] || [[ -f "$dir/build.gradle" ]] || [[ -f "$dir/build.gradle.kts" ]]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    echo "$PWD"
    return 1
}

# Function to show usage
usage() {
    echo "Usage: $0 <java-file>"
    echo ""
    echo "Add or update license header in a Java source file."
    echo ""
    echo "Example:"
    echo "  $0 src/main/java/com/example/MyRecipe.java"
    exit 2
}

# Check arguments
if [[ $# -ne 1 ]]; then
    usage
fi

JAVA_FILE="$1"

# Validate Java file exists
if [[ ! -f "$JAVA_FILE" ]]; then
    echo -e "${RED}Error: File not found: $JAVA_FILE${NC}" >&2
    exit 2
fi

# Validate it's a Java file
if [[ ! "$JAVA_FILE" =~ \.java$ ]]; then
    echo -e "${RED}Error: Not a Java file: $JAVA_FILE${NC}" >&2
    exit 2
fi

# Find repository root and license header file
REPO_ROOT=$(find_repo_root)
LICENSE_HEADER_FILE="$REPO_ROOT/gradle/licenseHeader.txt"

# Check if license header template exists
if [[ ! -f "$LICENSE_HEADER_FILE" ]]; then
    echo -e "${YELLOW}Warning: License header template not found at: $LICENSE_HEADER_FILE${NC}" >&2
    echo -e "${YELLOW}Skipping license header addition.${NC}" >&2
    exit 1
fi

# Read license header template and substitute ${year}
LICENSE_HEADER=$(sed "s/\${year}/$CURRENT_YEAR/g" "$LICENSE_HEADER_FILE")

# Create a temporary file for the new content
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

# Check if file already has a license header (starts with /* or //)
FIRST_LINE=$(head -n 1 "$JAVA_FILE")

if [[ "$FIRST_LINE" =~ ^/\* ]] || [[ "$FIRST_LINE" =~ ^// ]]; then
    # File has some kind of header comment
    # Extract everything after the header comment

    # Find the end of the comment block
    if [[ "$FIRST_LINE" =~ ^/\* ]]; then
        # Multi-line comment - find the closing */
        LINE_NUM=$(grep -n "\*/" "$JAVA_FILE" | head -n 1 | cut -d: -f1)
        if [[ -n "$LINE_NUM" ]]; then
            # Extract content after the comment block
            tail -n +$((LINE_NUM + 1)) "$JAVA_FILE" > "$TEMP_FILE.body"
        else
            # No closing found, treat whole file as body
            cp "$JAVA_FILE" "$TEMP_FILE.body"
        fi
    else
        # Single-line comments - skip all leading // lines
        LINE_NUM=$(grep -n -m 1 "^[^/]" "$JAVA_FILE" | head -n 1 | cut -d: -f1)
        if [[ -n "$LINE_NUM" ]]; then
            tail -n +$LINE_NUM "$JAVA_FILE" > "$TEMP_FILE.body"
        else
            # All lines are comments, preserve the file
            cp "$JAVA_FILE" "$TEMP_FILE.body"
        fi
    fi

    # Write new header + body
    echo "$LICENSE_HEADER" > "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"  # Add blank line after header
    cat "$TEMP_FILE.body" >> "$TEMP_FILE"
    rm -f "$TEMP_FILE.body"

    echo -e "${GREEN}✓ Updated license header in: $JAVA_FILE${NC}"
else
    # No header comment found, prepend the license header
    echo "$LICENSE_HEADER" > "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"  # Add blank line after header
    cat "$JAVA_FILE" >> "$TEMP_FILE"

    echo -e "${GREEN}✓ Added license header to: $JAVA_FILE${NC}"
fi

# Replace original file with new content
mv "$TEMP_FILE" "$JAVA_FILE"

exit 0
