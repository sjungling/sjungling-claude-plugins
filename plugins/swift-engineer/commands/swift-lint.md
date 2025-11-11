---
description: Format and lint Swift code using swift-format
allowed-tools:
  - Task
  - Bash
  - Glob
  - AskUserQuestion
---

To keep the codebase clean, execute the following workflow:

## Step 1: Check for Periphery

Before formatting and linting, check if Periphery (unused code detector) is available:

1. Run `which periphery` to check if periphery is installed
2. If installed, check if the project is configured by looking for:
   - `.periphery.yml` configuration file in the project root, OR
   - An Xcode project/workspace file (`.xcodeproj` or `.xcworkspace`)

3. If periphery is installed AND the project has either a `.periphery.yml` config or Xcode project files, use AskUserQuestion to prompt:
   - Question: "Periphery is available for detecting unused code. Would you like to run it before formatting and linting?"
   - Header: "Run Periphery"
   - Options:
     - "Yes" - "Run periphery scan first to identify unused code"
     - "No" - "Skip periphery and proceed with formatting/linting"

4. If user selects "Yes", launch a general-purpose subagent to run `periphery scan` and report findings. Wait for it to complete before proceeding.

## Step 2: Format and Lint with swift-format

Execute the following workflow using subagents for context isolation:

**IMPORTANT**: Launch TWO separate subagents sequentially. Do NOT run them in parallel. Formatting often fixes issues that would be flagged by the linter, so linting must happen AFTER formatting is complete.

1. First, launch a general-purpose subagent to run `swift-format format --in-place --recursive` to format all Swift code. Wait for it to complete.

2. Then, launch a second general-purpose subagent to run `swift-format lint --recursive` on the project and resolve all remaining lint issues until clean.

Use the Task tool for all subagent steps to keep output isolated from the main agent context.

Report a brief summary of results after all steps are complete.
