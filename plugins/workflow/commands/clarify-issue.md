---
allowed-tools: Bash(gh issue view:*),
  Bash(gh issue edit:*),
  Bash(git status:*),
  AskUserQuestion,
  Read(**/*.md),
  Write(**/*.md),
  Edit(**/*.md),
  mcp__use_browser,
  mcp__plugin_ui-engineering_figma-mcp__*
argument-hint: [issue-url]
description: Clarify ambiguities in a GitHub issue through structured questioning
---

Clarify ambiguities in GitHub issue: $ARGUMENTS

## Argument Validation

- Ensure an issue URL or number was provided and prompt the user if not.
- Extract the issue number from the URL if a full URL was provided.

## Context Gathering

Fetch the issue details using `gh`:

```bash
gh issue view "$ISSUE_NUMBER" --json number,title,body,url,labels,state
```

Parse the issue title and body to understand the current specification.

## Ambiguity Detection

Analyze the issue against these nine categories to identify gaps:

1. **Functional Scope & Behavior**
   - What specific capabilities must be delivered?
   - What's explicitly out of scope?
   - How should the feature behave in normal conditions?

2. **Domain & Data Model**
   - What entities, attributes, and relationships are involved?
   - What validation rules apply?
   - Are there existing data structures to extend or new ones to create?

3. **Interaction & UX Flow**
   - What's the user journey or workflow?
   - What inputs are required and what outputs are produced?
   - How should errors or feedback be communicated to users?

4. **Non-Functional Quality Attributes**
   - What are the performance, security, or accessibility requirements?
   - What scale or load must be supported?
   - Are there compliance or regulatory constraints?

5. **Integration & External Dependencies**
   - What APIs, services, or systems must integrate?
   - What data formats or protocols are required?
   - Are there authentication or authorization requirements?

6. **Edge Cases & Failure Handling**
   - What happens with invalid, missing, or malformed input?
   - How should timeouts, network failures, or unavailable services be handled?
   - What error states need graceful degradation?

7. **Constraints & Tradeoffs**
   - What technical or business constraints exist?
   - What tradeoffs between speed, quality, scope are acceptable?
   - What's the priority if resources are limited?

8. **Terminology & Consistency**
   - Are terms used consistently throughout the spec?
   - Do any terms need clear definitions?
   - Are there naming conventions to follow?

9. **Completion Signals**
   - What defines "done" for this feature?
   - What testing is required?
   - What documentation must be updated?

For each category, assign a status:
- **Clear**: Well-defined and actionable
- **Partial**: Some information present but gaps remain
- **Missing**: No information or critically incomplete

## Question Generation

Generate up to 5 targeted clarification questions that:
- Address the highest-impact ambiguities (Partial or Missing categories)
- Materially affect architecture, data modeling, testing, UX, operations, or compliance
- Exclude trivial stylistic preferences
- Can be answered with either:
  - Multiple-choice (2-4 options with clear descriptions)
  - Short-phrase responses

For each question:
- Clearly state what's ambiguous and why it matters
- If multiple-choice, identify and explain the recommended option
- Ensure answers will directly inform implementation decisions

## Interactive Clarification

Use the `AskUserQuestion` tool to present clarifications:

1. Present questions one at a time (or in small batches if related)
2. For multiple-choice questions:
   - Set the recommended option based on best practices or issue context
   - Provide clear descriptions for each option explaining tradeoffs
   - Use `multiSelect: false` for mutually exclusive choices
3. For open-ended questions:
   - Provide example options with an "Other" choice
   - Keep option descriptions concise but informative

Example AskUserQuestion usage:
```
{
  "questions": [
    {
      "question": "What should happen when a user tries to perform this action without authentication?",
      "header": "Auth handling",
      "multiSelect": false,
      "options": [
        {
          "label": "Redirect to login",
          "description": "Send user to login page with return URL. Standard web app pattern."
        },
        {
          "label": "Show 401 error",
          "description": "Return 401 status. Better for API endpoints."
        },
        {
          "label": "Graceful degradation",
          "description": "Show limited functionality without auth. Good for public features."
        }
      ]
    }
  ]
}
```

## Answer Integration

After receiving answers from the user:

1. **Create clarifications file** (if it doesn't exist):
   - Write to `/tmp/claude/issue-$ISSUE_NUMBER-clarifications.md`
   - Format with:
     ```markdown
     # Clarifications for Issue #$ISSUE_NUMBER

     ## Date: YYYY-MM-DD

     ### [Category Name]

     **Q:** [Question text]
     **A:** [User's answer with reasoning if applicable]

     ---
     ```

2. **Update existing clarifications** (if file exists):
   - Use Read tool to load existing content
   - Use Edit tool to append new Q&A under today's date
   - Ensure no duplicate questions

3. **Update the GitHub issue**:
   - Write updated issue body to `/tmp/claude/issue-$ISSUE_NUMBER-body.md`
   - Add or update a `## Clarifications` section at the end
   - Include date-stamped Q&A entries
   - Use Read tool to verify content
   - Update issue: `gh issue edit $ISSUE_NUMBER --body-file /tmp/claude/issue-$ISSUE_NUMBER-body.md`

4. **Validate**:
   - Check for contradictions with previous answers
   - Ensure terminology consistency
   - Verify formatting is preserved

## Session Management

- Maximum 10 questions per session (stop earlier if all critical gaps addressed)
- Allow user to signal completion with "done", "stop", or "skip"
- If quota exhausted, report any remaining high-impact items

## Completion Report

After clarification session ends, provide:

```markdown
## Clarification Summary

**Questions asked:** X
**Questions answered:** Y
**Issue updated:** #$ISSUE_NUMBER

**Coverage by Category:**
| Category | Status | Notes |
|----------|--------|-------|
| Functional Scope | Clear/Partial/Missing | ... |
| Domain Model | Clear/Partial/Missing | ... |
| ... | ... | ... |

**Next Steps:**
- [Suggested action based on coverage]
- [Any remaining ambiguities to address]
- [Ready to proceed with implementation? Yes/No]
```

## Important Rules

- NEVER ask trivial or stylistic questions that don't affect implementation
- NEVER speculate about tech stack unless blocking functional clarity
- ALWAYS respect "done"/"stop" signals
- ALWAYS update the issue incrementally after each answer to prevent data loss
- ALWAYS provide reasoning for recommended options in multiple-choice questions
- Keep questions focused and actionable
- Prioritize questions by implementation impact

## Workflow Summary

1. Fetch issue with `gh issue view` → extract title and body
2. Analyze against 9-category taxonomy → identify ambiguities
3. Generate up to 5 high-impact clarification questions
4. Use `AskUserQuestion` tool → collect structured responses
5. Write clarifications to temp file → update issue with `gh issue edit --body-file`
6. Validate for consistency and contradictions
7. Provide coverage summary and next steps

Proceed with clarifying the issue following these guidelines.
