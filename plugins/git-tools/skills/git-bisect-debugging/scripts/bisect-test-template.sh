#!/bin/bash
# Git bisect test script template
# Exit codes: 0 = good (issue absent), 1 = bad (issue present), 125 = skip (can't test)
#
# Usage: git bisect run ./bisect-test.sh
#
# Customize the SETUP and TEST sections below for the specific regression.

set -euo pipefail

# --- SETUP (required for each commit) ---
# Install dependencies, build project, etc.
# Use `exit 125` if setup fails (commit is untestable).
#
# Example for Node.js:
#   npm install --silent 2>/dev/null || exit 125
#
# Example for Python:
#   pip install -e . 2>/dev/null || exit 125
#
# Example for compiled languages:
#   make clean && make 2>/dev/null || exit 125

npm install --silent 2>/dev/null || exit 125

# --- TEST ---
# Run the specific test that reproduces the issue.
# Exit 0 if the issue is ABSENT (good), exit 1 if PRESENT (bad).
#
# Guidelines:
# - Make it deterministic (no random data, use fixed seeds)
# - Make it fast (this runs ~log2(N) times)
# - Test ONE specific thing, not the entire suite
# - Make it read-only (no data modification)
#
# Example: Run a specific test file
#   npm test -- path/to/specific-test.js
#
# Example: Check for a specific error
#   node app.js 2>&1 | grep -q "ERROR" && exit 1 || exit 0
#
# Example: Check performance threshold
#   DURATION=$(npm run benchmark 2>&1 | grep "time:" | awk '{print $2}')
#   [ "$(echo "$DURATION > 5.0" | bc)" -eq 1 ] && exit 1 || exit 0

npm test -- path/to/specific-test.js
exit $?
