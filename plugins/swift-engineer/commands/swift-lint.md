---
description: Format and lint Swift code using swift-format
allowed-tools:
  - Bash(swift-format:*)
  - Bash(swift build)
  - Bash(swift:*)
  - Bash(xcodebuild:*)
  - Bash(xcrun simctl boot:*)
  - Bash(xcrun simctl list:*)
  - Bash(echo:*)
  - Bash(tee:*)
---

To keep the codebase clean, execute the following workflow using subagents:

1. Launch a subagent to run `swift-format format --in-place --recursive` and report back when complete
2. Launch a subagent to run `swift-format lint --recursive` on this project and resolve all issues until it's clean, then report back when complete

Wait for both subagents to complete and report their results before finishing.
