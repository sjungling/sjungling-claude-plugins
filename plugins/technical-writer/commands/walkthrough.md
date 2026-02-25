---
description: Generate a code walkthrough using showboat
argument-hint: [path-to-source]
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

Read the source at `$ARGUMENTS` (or the current working directory if no path is given) and then plan a linear walkthrough of the code that explains how it all works in detail.

Then run `uvx showboat --help` to learn showboat - use showboat to create a `walkthrough.md` file in the repo and build the walkthrough in there, using `showboat note` for commentary and `showboat exec` plus `sed` or `grep` or `cat` or whatever you need to include snippets of code you are talking about.
