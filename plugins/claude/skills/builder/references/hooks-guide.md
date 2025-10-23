# Hooks Guide

## Overview

Hooks are scripts that run in response to Claude Code events, enabling validation, automation, and control over tool execution. Plugins can define hooks to ensure prerequisites are met before operations execute.

**Official Documentation**:
- Hooks: https://docs.claude.com/en/docs/claude-code/hooks
- Plugin Hooks: https://docs.claude.com/en/docs/claude-code/hooks#plugin-hooks

## Hook Types

### PreToolUse

Executes **after** Claude creates tool parameters but **before** the tool actually runs. This allows you to:
- Validate prerequisites (dependencies installed, config set)
- Control tool execution (allow, deny, ask for confirmation)
- Provide context to Claude about environment state
- Block operations that would fail due to missing setup

**Common Use Cases**:
- Check MCP server installation before MCP tool calls
- Verify API keys/credentials before external service calls
- Validate file paths before destructive operations
- Enforce project-specific constraints
- Provide setup guidance when prerequisites are missing

### Other Hook Types

See official documentation for:
- `SessionStart`: Runs when session begins
- `UserPromptSubmit`: Runs when user submits a message
- `BeforeToolUse`: Additional validation before tool execution
- `AfterToolUse`: Post-execution actions

## Directory Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── hooks.json          # Hook configuration (required location)
├── scripts/                # Hook scripts (recommended location)
│   ├── check-setup.sh
│   └── validate-config.py
└── README.md
```

**Key Points**:
- `hooks/hooks.json` must be in the `hooks/` directory (or specify custom path in plugin.json)
- Scripts can be anywhere, commonly in `scripts/` directory
- Use `${CLAUDE_PLUGIN_ROOT}` to reference plugin root path in hooks

## Hook Configuration

### hooks.json

```json
{
  "PreToolUse": [
    {
      "matcher": "mcp__plugin_name_server__*",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh"
    }
  ]
}
```

### Matcher Patterns

**Exact match**:
```json
"matcher": "Write"
```
Matches only the Write tool.

**Regex pattern**:
```json
"matcher": "Edit|Write|MultiEdit"
```
Matches multiple specific tools.

**Wildcard**:
```json
"matcher": "*"
```
Matches all tools (use cautiously).

**MCP tools**:
```json
"matcher": "mcp__*"                              // All MCP tools
"matcher": "mcp__server__*"                      // All tools from a server
"matcher": "mcp__server__specific_tool"          // Specific MCP tool
```

**Tool name patterns**:
- Built-in: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Task`, `WebFetch`, `WebSearch`
- Notebooks: `NotebookEdit`, `NotebookExecute`
- MCP: `mcp__<server>__<tool>`

### Command Field

Use `${CLAUDE_PLUGIN_ROOT}` to reference scripts:
```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh"
```

This ensures the hook works regardless of where the plugin is installed.

## Writing PreToolUse Hook Scripts

### Input

Your script receives JSON via **stdin**:

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "mcp__grafana__create_incident",
  "tool_input": {
    "title": "Production outage",
    "severity": "critical",
    "roomPrefix": "incident"
  },
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.md",
  "cwd": "/current/working/directory"
}
```

**Fields**:
- `hook_event_name`: Always "PreToolUse"
- `tool_name`: Name of the tool being called
- `tool_input`: Parameters Claude wants to pass to the tool (schema varies by tool)
- `session_id`: Unique session identifier
- `transcript_path`: Path to session transcript
- `cwd`: Current working directory

### Output

Your script must output JSON via **stdout**:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Why this decision was made",
    "additionalContext": "Optional message shown to Claude"
  }
}
```

**Required Fields**:

**`permissionDecision`** (string, required):
- `"allow"`: Auto-approve tool execution, bypass normal permissions
- `"deny"`: Block tool execution entirely
- `"ask"`: Prompt user for confirmation in UI

**`permissionDecisionReason`** (string, required):
- Brief explanation of why this decision was made
- Shown in logs/UI
- Examples: "Setup verified", "Missing API key", "User confirmation required"

**Optional Fields**:

**`additionalContext`** (string, optional):
- Additional information shown to Claude
- Use for detailed error messages, warnings, setup instructions
- Supports formatted text (newlines, bullets, etc.)

### Exit Codes

**`0` - Success**:
- Hook executed successfully
- Permission decision should be respected

**`2` - Blocking Error**:
- Hook failed, block tool execution
- stderr shown to Claude
- Use for critical validation failures

**Other codes**:
- Treated as errors, behavior may vary

### Best Practices

**1. Always return permission decision**:
```bash
# BAD: Missing permissionDecision
{
  "hookSpecificOutput": {
    "additionalContext": "Some message"
  }
}

# GOOD: Includes required fields
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Setup verified"
  }
}
```

**2. Use exit code 2 for blocking**:
```bash
# BAD: Using exit 1
if [ ${#ERRORS[@]} -gt 0 ]; then
    echo '{"hookSpecificOutput": {"permissionDecision": "deny", ...}}'
    exit 1  # Wrong exit code
fi

# GOOD: Using exit 2
if [ ${#ERRORS[@]} -gt 0 ]; then
    echo '{"hookSpecificOutput": {"permissionDecision": "deny", ...}}'
    exit 2  # Correct blocking exit code
fi
```

**3. Provide helpful error messages**:
```bash
# GOOD: Actionable error message
"additionalContext": "❌ Setup Issues:\n\n  • mcp-server not installed\n  • Install from: https://example.com/install\n  • Set API_KEY environment variable\n\nPlease resolve these issues to continue."
```

**4. Silent success is OK**:
```bash
# When everything is fine, minimal output is acceptable
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Setup verified"
  }
}
# No additionalContext needed
```

**5. Use warnings for non-critical issues**:
```bash
# Allow execution but inform about warnings
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Setup verified with warnings",
    "additionalContext": "⚠️  Warnings:\n\n  • Connection slow\n  • Using fallback config"
  }
}
```

## Example: MCP Setup Validation

### hooks/hooks.json

```json
{
  "PreToolUse": [
    {
      "matcher": "mcp__grafana__*",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/check-grafana-setup.sh"
    }
  ]
}
```

### scripts/check-grafana-setup.sh

```bash
#!/bin/bash
set -e

ERRORS=()
WARNINGS=()

# Check if mcp-grafana is installed
if ! command -v mcp-grafana &> /dev/null; then
    ERRORS+=("mcp-grafana is not installed. Install from: https://github.com/grafana/mcp-grafana")
fi

# Check if API key is set
if [ -z "${GRAFANA_API_KEY}" ]; then
    ERRORS+=("GRAFANA_API_KEY environment variable is not set. Add to ~/.zshrc: export GRAFANA_API_KEY='your-key'")
fi

# Check connectivity (optional, warns but doesn't block)
GRAFANA_URL="${GRAFANA_URL:-https://grafana.example.com}"
if [ -n "${GRAFANA_API_KEY}" ]; then
    if ! curl -sf -H "Authorization: Bearer ${GRAFANA_API_KEY}" "${GRAFANA_URL}/api/health" &> /dev/null; then
        WARNINGS+=("Unable to connect to Grafana at ${GRAFANA_URL}")
    fi
fi

# Build output message
OUTPUT=""

if [ ${#ERRORS[@]} -gt 0 ]; then
    OUTPUT="❌ Grafana Plugin Setup Issues:\n\n"
    for error in "${ERRORS[@]}"; do
        OUTPUT+="  • ${error}\n"
    done
    OUTPUT+="\nPlease resolve these issues to use Grafana features.\n"
elif [ ${#WARNINGS[@]} -gt 0 ]; then
    OUTPUT="⚠️  Grafana Plugin Warnings:\n\n"
    for warning in "${WARNINGS[@]}"; do
        OUTPUT+="  • ${warning}\n"
    done
fi

# Return JSON with permission decision
if [ ${#ERRORS[@]} -gt 0 ]; then
    cat << EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "Grafana plugin setup is incomplete",
    "additionalContext": "$(echo -e "$OUTPUT")"
  }
}
EOF
    exit 2
elif [ ${#WARNINGS[@]} -gt 0 ]; then
    cat << EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Setup verified with warnings",
    "additionalContext": "$(echo -e "$OUTPUT")"
  }
}
EOF
    exit 0
else
    cat << EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Grafana plugin setup verified"
  }
}
EOF
    exit 0
fi
```

### What This Hook Does

1. **Blocks tool execution** if:
   - `mcp-grafana` command not found
   - `GRAFANA_API_KEY` environment variable not set

2. **Allows with warnings** if:
   - Setup is complete but connectivity check fails

3. **Allows silently** if:
   - All checks pass

4. **Provides guidance** when blocked:
   - Installation instructions
   - Configuration steps
   - Clear error messages

## Testing Hooks

### Manual Testing

Create a test input file:

```bash
cat > test-input.json << 'EOF'
{
  "hook_event_name": "PreToolUse",
  "tool_name": "mcp__grafana__create_incident",
  "tool_input": {
    "title": "Test",
    "severity": "critical"
  },
  "session_id": "test",
  "transcript_path": "/tmp/test.md",
  "cwd": "/tmp"
}
EOF
```

Test the hook script:

```bash
# Test without setup (should deny)
cat test-input.json | ./scripts/check-setup.sh
echo "Exit code: $?"

# Test with setup (should allow)
export GRAFANA_API_KEY="test-key"
cat test-input.json | ./scripts/check-setup.sh
echo "Exit code: $?"
```

### Validation Checklist

- [ ] Script is executable (`chmod +x`)
- [ ] Returns valid JSON to stdout
- [ ] Includes `permissionDecision` field
- [ ] Includes `permissionDecisionReason` field
- [ ] Uses exit code 2 for blocking errors
- [ ] Uses exit code 0 for success/warnings
- [ ] Error messages are actionable
- [ ] Script handles missing environment variables
- [ ] Matcher pattern is correct in hooks.json
- [ ] Command path uses `${CLAUDE_PLUGIN_ROOT}`

## Common Patterns

### Environment Validation

```bash
# Check required environment variables
REQUIRED_VARS=("API_KEY" "API_URL" "PROJECT_ID")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        ERRORS+=("$var environment variable not set")
    fi
done
```

### Command Availability

```bash
# Check if command exists
REQUIRED_COMMANDS=("docker" "kubectl" "helm")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        ERRORS+=("$cmd is not installed")
    fi
done
```

### File/Directory Existence

```bash
# Check if required files exist
if [ ! -f "config.yaml" ]; then
    ERRORS+=("config.yaml not found")
fi

if [ ! -d ".git" ]; then
    ERRORS+=("Not in a git repository")
fi
```

### API Connectivity

```bash
# Check if API is reachable (warning, not error)
if ! curl -sf "${API_URL}/health" &> /dev/null; then
    WARNINGS+=("API at ${API_URL} is not reachable")
fi
```

### Conditional Blocking

```bash
# Block only specific tools
if [[ "$tool_name" == *"create_incident"* ]]; then
    # Strict validation for incident creation
    if [ -z "${ONCALL_SCHEDULE}" ]; then
        ERRORS+=("ONCALL_SCHEDULE required for incident creation")
    fi
fi
```

## Troubleshooting

### Hook Not Running

**Check**:
- `hooks/hooks.json` exists in correct location
- JSON is valid (`cat hooks/hooks.json | python -m json.tool`)
- Matcher pattern matches the tool name
- Script path is correct and uses `${CLAUDE_PLUGIN_ROOT}`

### Invalid JSON Output

**Check**:
- Script outputs to stdout (not stderr)
- JSON is properly formatted
- No extra output before/after JSON
- Special characters are escaped in strings

### Exit Code Issues

**Remember**:
- Use `exit 2` for blocking (not `exit 1`)
- Use `exit 0` for success
- Check exit code: `echo $?` after running script

### Permission Decision Not Respected

**Ensure**:
- `permissionDecision` field is present
- Value is exactly `"allow"`, `"deny"`, or `"ask"`
- Exit code is 0 or 2 (not other values)

## Best Practices Summary

1. **Always validate** before allowing operations
2. **Provide helpful errors** with clear resolution steps
3. **Use exit code 2** for blocking errors
4. **Return proper JSON** with required fields
5. **Test thoroughly** with and without prerequisites
6. **Make scripts executable** (`chmod +x`)
7. **Use environment variables** for configuration
8. **Handle missing dependencies** gracefully
9. **Warn don't block** for non-critical issues
10. **Keep hooks fast** (< 1 second when possible)

## Security Considerations

### Input Validation

Hooks receive tool parameters from Claude. Be cautious with:
- File paths (could be outside expected directories)
- Command arguments (could contain injection attempts)
- URLs (could point to unexpected destinations)

### Credential Handling

Never:
- Log credentials or API keys
- Include credentials in error messages
- Write credentials to files

Always:
- Read from environment variables
- Validate credential format before use
- Fail safely if credentials are missing

### Least Privilege

Hooks run with user's permissions. Ensure:
- Scripts don't require sudo
- File operations are scoped appropriately
- Network calls are to expected endpoints only

## Advanced Patterns

### Multi-Stage Validation

```bash
# Stage 1: Critical requirements (block if missing)
check_critical_requirements

# Stage 2: Optional requirements (warn if missing)
check_optional_requirements

# Stage 3: Connectivity (warn if unreachable)
check_connectivity
```

### Caching Validation Results

```bash
# Cache validation for performance
CACHE_FILE="/tmp/plugin-validation-cache"
CACHE_TTL=300  # 5 minutes

if [ -f "$CACHE_FILE" ]; then
    CACHE_AGE=$(($(date +%s) - $(stat -f %m "$CACHE_FILE")))
    if [ $CACHE_AGE -lt $CACHE_TTL ]; then
        cat "$CACHE_FILE"
        exit 0
    fi
fi

# Run validation and cache result
validate > "$CACHE_FILE"
cat "$CACHE_FILE"
```

### Tool-Specific Validation

```bash
# Read tool_name from stdin
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

case "$TOOL_NAME" in
    "mcp__server__read_only")
        # Light validation for read operations
        ;;
    "mcp__server__write")
        # Strict validation for write operations
        ;;
    "mcp__server__delete")
        # Extra confirmation for destructive operations
        echo '{"hookSpecificOutput": {"permissionDecision": "ask", ...}}'
        ;;
esac
```

## References

- Official Hooks Documentation: https://docs.claude.com/en/docs/claude-code/hooks
- Plugin Hooks: https://docs.claude.com/en/docs/claude-code/hooks#plugin-hooks
- JSON Specification: https://www.json.org/
- Bash Best Practices: https://google.github.io/styleguide/shellguide.html
