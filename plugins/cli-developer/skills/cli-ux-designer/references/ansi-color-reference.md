# ANSI Color Reference for CLI Design

This reference provides comprehensive ANSI color codes for terminal styling in CLI applications.

## Basic 16 Colors (3/4-bit)

### Standard Colors

| Color   | Foreground | Background | Use Cases                              |
|---------|-----------|-----------|----------------------------------------|
| Black   | `\033[30m` | `\033[40m` | Default text, dividers                |
| Red     | `\033[31m` | `\033[41m` | Errors, failures, closed states       |
| Green   | `\033[32m` | `\033[42m` | Success, open states, confirmations   |
| Yellow  | `\033[33m` | `\033[43m` | Warnings, draft states, caution       |
| Blue    | `\033[34m` | `\033[44m` | Information, links, metadata          |
| Magenta | `\033[35m` | `\033[45m` | Special highlights, tags              |
| Cyan    | `\033[36m` | `\033[46m` | Branch names, identifiers, emphasis   |
| White   | `\033[37m` | `\033[47m` | Primary text, headings                |

### Bright/Bold Variants

| Color        | Foreground | Background | Use Cases                       |
|--------------|-----------|-----------|----------------------------------|
| Bright Black (Gray) | `\033[90m` | `\033[100m` | Secondary text, labels, timestamps |
| Bright Red          | `\033[91m` | `\033[101m` | Critical errors, destructive actions |
| Bright Green        | `\033[92m` | `\033[102m` | Strong success indicators       |
| Bright Yellow       | `\033[93m` | `\033[103m` | Important warnings              |
| Bright Blue         | `\033[94m` | `\033[104m` | Highlighted information         |
| Bright Magenta      | `\033[95m` | `\033[105m` | Special status indicators       |
| Bright Cyan         | `\033[96m` | `\033[106m` | Emphasized identifiers          |
| Bright White        | `\033[97m` | `\033[107m` | Maximum emphasis, alerts        |

## Text Styling

| Style           | Code       | Reset      | Use Cases                    |
|----------------|-----------|-----------|------------------------------|
| Bold           | `\033[1m`  | `\033[22m` | Headers, emphasis            |
| Dim            | `\033[2m`  | `\033[22m` | Secondary info, deprecation  |
| Italic         | `\033[3m`  | `\033[23m` | Not recommended (poor support) |
| Underline      | `\033[4m`  | `\033[24m` | Links, emphasis              |
| Blink          | `\033[5m`  | `\033[25m` | Avoid (accessibility issue)  |
| Reverse        | `\033[7m`  | `\033[27m` | Selection, current item      |
| Strikethrough  | `\033[9m`  | `\033[29m` | Deprecated, removed items    |

## Reset Codes

| Reset Type     | Code       | Description                        |
|---------------|-----------|-------------------------------------|
| All attributes | `\033[0m`  | Clear all styling and colors       |
| Foreground     | `\033[39m` | Reset to default text color        |
| Background     | `\033[49m` | Reset to default background        |

## 256 Color Palette (8-bit)

### Syntax
- **Foreground**: `\033[38;5;<n>m` where `<n>` is 0-255
- **Background**: `\033[48;5;<n>m` where `<n>` is 0-255

### Color Ranges

**0-15**: Standard and bright colors (same as 16-color palette above)

**16-231**: 6×6×6 RGB color cube
- Formula: `16 + 36×r + 6×g + b` where r,g,b are 0-5
- Example: `\033[38;5;196m` = bright red (r=5, g=0, b=0)

**232-255**: Grayscale ramp (24 shades from dark to light)
- Example: `\033[38;5;240m` = dark gray
- Example: `\033[38;5;250m` = light gray

### Common 256 Colors

| Color Description | Code (FG)       | Hex Approximation |
|------------------|----------------|-------------------|
| Dark Red         | `\033[38;5;88m` | `#870000`        |
| Orange           | `\033[38;5;208m`| `#ff8700`        |
| Dark Green       | `\033[38;5;28m` | `#008700`        |
| Teal             | `\033[38;5;30m` | `#008787`        |
| Navy Blue        | `\033[38;5;18m` | `#000087`        |
| Purple           | `\033[38;5;93m` | `#8700ff`        |
| Dark Gray        | `\033[38;5;240m`| `#585858`        |
| Light Gray       | `\033[38;5;250m`| `#bcbcbc`        |

## RGB True Color (24-bit)

### Syntax
- **Foreground**: `\033[38;2;<r>;<g>;<b>m` where r,g,b are 0-255
- **Background**: `\033[48;2;<r>;<g>;<b>m` where r,g,b are 0-255

### Examples

```bash
# Brand-specific red (RGB: 255, 59, 48)
\033[38;2;255;59;48m

# Brand-specific blue (RGB: 0, 122, 255)
\033[38;2;0;122;255m

# Custom gray (RGB: 142, 142, 147)
\033[38;2;142;142;147m
```

## Combining Codes

Multiple styles can be combined using semicolons:

```bash
# Bold red text
\033[1;31m

# Underlined bright green
\033[4;92m

# Bold, underlined cyan on dark gray background
\033[1;4;36;100m

# 256-color bold blue
\033[1;38;5;27m

# RGB true color bold
\033[1;38;2;255;59;48m
```

## Compatibility Notes

### Terminal Support

| Feature        | Support Level | Notes                               |
|---------------|--------------|--------------------------------------|
| 16 colors     | Universal    | Safe to use everywhere              |
| Bold/Dim      | Universal    | Widely supported                    |
| Underline     | Universal    | Widely supported                    |
| Italic        | Limited      | Unreliable, avoid in production     |
| Blink         | Limited      | Accessibility issue, avoid          |
| 256 colors    | Good         | Most modern terminals, test first   |
| RGB colors    | Moderate     | Many modern terminals, fallback needed |

### Detection Strategy

```bash
# Check COLORTERM environment variable
if [ "$COLORTERM" = "truecolor" ] || [ "$COLORTERM" = "24bit" ]; then
    # RGB true color supported
elif [ "$TERM" = "xterm-256color" ]; then
    # 256 colors supported
else
    # Use basic 16 colors only
fi
```

## Best Practices

### 1. Stick to Basic Colors for Maximum Compatibility
Use the 16 basic colors for critical information. Reserve 256/RGB for branding or progressive enhancement.

### 2. Always Reset After Styling
```bash
echo "\033[32mSuccess!\033[0m"  # Good
echo "\033[32mSuccess!"          # Bad - affects subsequent output
```

### 3. Provide Monochrome Fallback
Ensure meaning isn't conveyed through color alone. Use symbols and text:
```bash
echo "✓ \033[32mSuccess\033[0m"  # Good - symbol + color
echo "\033[32mSuccess\033[0m"    # Risky - color only
```

### 4. Respect User Preferences
- Check `NO_COLOR` environment variable
- Detect if output is piped/redirected
- Support `--no-color` flag

### 5. Test in Multiple Terminals
- macOS Terminal
- iTerm2
- Windows Terminal
- VS Code integrated terminal
- Linux terminals (GNOME Terminal, Konsole, etc.)

## Quick Reference: Semantic Color Usage

| Meaning       | Recommended Color | Code        |
|--------------|------------------|------------|
| Success      | Green            | `\033[32m` |
| Error        | Red              | `\033[31m` |
| Warning      | Yellow           | `\033[33m` |
| Info         | Blue             | `\033[34m` |
| Highlight    | Cyan             | `\033[36m` |
| Subtle       | Bright Black (Gray) | `\033[90m` |
| Emphasis     | Bold             | `\033[1m`  |
| Link         | Blue Underline   | `\033[4;34m` |

## Language-Specific Libraries

### JavaScript/Node.js
- `chalk` - Terminal string styling
- `kleur` - Lightweight alternative to chalk
- `picocolors` - Minimal ANSI color library

### Python
- `colorama` - Cross-platform colored terminal text
- `termcolor` - ANSI color formatting
- `rich` - Advanced terminal formatting

### Go
- `fatih/color` - Color package for Go
- `charmbracelet/lipgloss` - Style definitions for TUI

### Rust
- `colored` - Coloring terminal
- `ansi_term` - ANSI terminal colors and styles

### Ruby
- `colorize` - String coloring
- `tty-color` - Terminal color capabilities detection

## Additional Resources

- ANSI Escape Codes Standard: ECMA-48
- Terminal emulator test suite: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
- Color testing tool: https://github.com/termstandard/colors
