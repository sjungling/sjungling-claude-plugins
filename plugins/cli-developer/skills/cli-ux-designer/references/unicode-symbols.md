# Unicode Symbols Reference for CLI Design

This reference provides CLI-safe Unicode symbols with platform compatibility notes and usage recommendations.

## Status Indicators

### Success/Completion

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ✓      | U+2713  | Check Mark  | ✓     | ✓     | ✓       | Universal, highly recommended |
| ✔      | U+2714  | Heavy Check | ✓     | ✓     | ✓       | Bolder variant |
| ✅     | U+2705  | Check Button| ✓     | ✓     | Windows 10+ | Emoji, may render large |
| ◉      | U+25C9  | Fisheye     | ✓     | ✓     | ✓       | Alternative indicator |
| ●      | U+25CF  | Black Circle| ✓     | ✓     | ✓       | Simple, safe |

### Failure/Error

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ✗      | U+2717  | Ballot X    | ✓     | ✓     | ✓       | Universal, highly recommended |
| ✘      | U+2718  | Heavy Ballot X | ✓  | ✓     | ✓       | Bolder variant |
| ❌     | U+274C  | Cross Mark  | ✓     | ✓     | Windows 10+ | Emoji, may render large |
| ⨯      | U+2A2F  | Vector Cross| ✓     | ✓     | Limited | Mathematical, less support |
| ×      | U+00D7  | Multiplication | ✓  | ✓     | ✓       | Very safe fallback |

### Warning/Alert

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| !      | U+0021  | Exclamation | ✓     | ✓     | ✓       | ASCII, universal |
| ⚠      | U+26A0  | Warning Sign| ✓     | ✓     | ✓       | Good support |
| ⚠️      | U+26A0 U+FE0F | Warning (Emoji) | ✓ | ✓ | Windows 10+ | May render colorful |
| ⚡     | U+26A1  | High Voltage| ✓     | ✓     | ✓       | Alternative attention |
| ⓘ      | U+24D8  | Info Circle | ✓     | ✓     | Limited | Less common |

### Neutral/In Progress

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| -      | U+002D  | Hyphen      | ✓     | ✓     | ✓       | ASCII, universal |
| •      | U+2022  | Bullet      | ✓     | ✓     | ✓       | Good for lists |
| ○      | U+25CB  | White Circle| ✓     | ✓     | ✓       | Hollow indicator |
| ◦      | U+25E6  | Small Circle| ✓     | ✓     | ✓       | Smaller variant |
| ⋯      | U+22EF  | Midline Ellipsis | ✓ | ✓  | ✓       | Indicates processing |

## Directional Arrows

### Basic Arrows

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| →      | U+2192  | Rightwards  | ✓     | ✓     | ✓       | Universal, highly recommended |
| ←      | U+2190  | Leftwards   | ✓     | ✓     | ✓       | Universal |
| ↑      | U+2191  | Upwards     | ✓     | ✓     | ✓       | Universal |
| ↓      | U+2193  | Downwards   | ✓     | ✓     | ✓       | Universal |
| ↔      | U+2194  | Left-Right  | ✓     | ✓     | ✓       | Bidirectional |
| ⇄      | U+21C4  | Right-Left  | ✓     | ✓     | ✓       | Over arrows |

### Special Arrows

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ➜      | U+279C  | Heavy Arrow | ✓     | ✓     | Limited | Prompt indicator |
| ⟹      | U+27F9  | Long Right  | ✓     | ✓     | Limited | Implications |
| ↩      | U+21A9  | Left Hook   | ✓     | ✓     | ✓       | Return, undo |
| ↪      | U+21AA  | Right Hook  | ✓     | ✓     | ✓       | Forward, redo |
| ⤴      | U+2934  | Up-Right    | ✓     | ✓     | Limited | External link |
| ⤵      | U+2935  | Down-Right  | ✓     | ✓     | Limited | Nested content |

## Tree/Hierarchy Symbols

### Box Drawing Characters

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| │      | U+2502  | Vertical    | ✓     | ✓     | ✓       | Tree lines |
| ─      | U+2500  | Horizontal  | ✓     | ✓     | ✓       | Tree branches |
| ├      | U+251C  | Middle Node | ✓     | ✓     | ✓       | Tree connector |
| └      | U+2514  | Last Node   | ✓     | ✓     | ✓       | Tree terminal |
| ┌      | U+250C  | Top-Left    | ✓     | ✓     | ✓       | Box corners |
| ┐      | U+2510  | Top-Right   | ✓     | ✓     | ✓       | Box corners |
| ┘      | U+2518  | Bottom-Right| ✓     | ✓     | ✓       | Box corners |
| ┤      | U+2524  | Right T     | ✓     | ✓     | ✓       | Box connectors |
| ┬      | U+252C  | Top T       | ✓     | ✓     | ✓       | Box connectors |

### Tree Connectors (Heavy)

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ┃      | U+2503  | Heavy Vertical | ✓  | ✓     | ✓       | Emphasis |
| ━      | U+2501  | Heavy Horizontal | ✓ | ✓    | ✓       | Emphasis |
| ┣      | U+2523  | Heavy Middle | ✓   | ✓     | ✓       | Emphasis |
| ┗      | U+2517  | Heavy Last  | ✓     | ✓     | ✓       | Emphasis |

## List Markers

### Bullets

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| •      | U+2022  | Bullet      | ✓     | ✓     | ✓       | Standard list |
| ◦      | U+25E6  | White Bullet| ✓     | ✓     | ✓       | Nested lists |
| ▪      | U+25AA  | Black Square| ✓     | ✓     | ✓       | Alternative |
| ▸      | U+25B8  | Right Tri   | ✓     | ✓     | ✓       | Collapsible |
| ▾      | U+25BE  | Down Tri    | ✓     | ✓     | ✓       | Expanded |
| ‣      | U+2023  | Triangular  | ✓     | ✓     | ✓       | Alternative |

### Numbered Alternatives

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ①②③    | U+2460+ | Circled Digits | ✓  | ✓     | ✓       | 1-20 available |
| ⑴⑵⑶    | U+2474+ | Parenthesized | ✓  | ✓     | ✓       | 1-20 available |
| ➀➁➂    | U+2780+ | Sans-Serif  | ✓     | ✓     | Limited | Less support |

## Shapes & Indicators

### Geometric Shapes

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ■      | U+25A0  | Black Square| ✓     | ✓     | ✓       | Filled indicator |
| □      | U+25A1  | White Square| ✓     | ✓     | ✓       | Hollow indicator |
| ▪      | U+25AA  | Small Square| ✓     | ✓     | ✓       | Compact |
| ▫      | U+25AB  | Small White | ✓     | ✓     | ✓       | Compact hollow |
| ▲      | U+25B2  | Black Triangle | ✓  | ✓     | ✓       | Up indicator |
| △      | U+25B3  | White Triangle | ✓  | ✓     | ✓       | Up hollow |
| ▼      | U+25BC  | Down Triangle | ✓   | ✓     | ✓       | Down indicator |
| ▽      | U+25BD  | Down White  | ✓     | ✓     | ✓       | Down hollow |

### Progress Indicators

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ░      | U+2591  | Light Shade | ✓     | ✓     | ✓       | Progress bar empty |
| ▒      | U+2592  | Medium Shade| ✓     | ✓     | ✓       | Progress bar partial |
| ▓      | U+2593  | Dark Shade  | ✓     | ✓     | ✓       | Progress bar almost |
| █      | U+2588  | Full Block  | ✓     | ✓     | ✓       | Progress bar filled |
| ▌      | U+258C  | Left Half   | ✓     | ✓     | ✓       | Partial progress |
| ▐      | U+2590  | Right Half  | ✓     | ✓     | ✓       | Partial progress |

## Spinners & Animations

### Rotating Indicators

| Sequence | Unicode | Description | Notes |
|----------|---------|-------------|-------|
| ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ | U+280B+ | Braille Dots | Smooth spinner |
| ◐◓◑◒  | U+25D0-U+25D2 | Circles | Simple rotation |
| ◴◷◶◵  | U+25F4-U+25F7 | Quadrants | Rotating |
| ⣾⣽⣻⢿⡿⣟⣯⣷ | U+28BE+ | Braille Heavy | Heavy spinner |
| ▁▂▃▄▅▆▇█▇▆▅▄▃▂ | U+2581+ | Bars | Growing/shrinking |

### Discrete States

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ◜◝◞◟  | U+25DC+ | Quarter Circles | ✓ | ✓   | Limited | 4-state indicator |
| ▖▘▝▗  | U+2596+ | Quarter Blocks | ✓  | ✓   | ✓       | 4-state |

## Special Purpose

### Git/Version Control

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| +      | U+002B  | Addition    | ✓     | ✓     | ✓       | ASCII, additions |
| -      | U+002D  | Deletion    | ✓     | ✓     | ✓       | ASCII, deletions |
| ±      | U+00B1  | Plus-Minus  | ✓     | ✓     | ✓       | Changes |
| ≠      | U+2260  | Not Equal   | ✓     | ✓     | ✓       | Conflicts |
| ∼      | U+223C  | Tilde       | ✓     | ✓     | ✓       | Modified |
| ⎇      | U+2387  | Alternative | ✓     | ✓     | Limited | Branch symbol |

### File Operations

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| 📁     | U+1F4C1 | Folder      | ✓     | ✓     | Windows 10+ | Emoji |
| 📄     | U+1F4C4 | Document    | ✓     | ✓     | Windows 10+ | Emoji |
| 🔗     | U+1F517 | Link        | ✓     | ✓     | Windows 10+ | Emoji |
| 🗑      | U+1F5D1 | Trash       | ✓     | ✓     | Windows 10+ | Emoji |
| ∅      | U+2205  | Empty Set   | ✓     | ✓     | ✓       | No files |

### Time & Duration

| Symbol | Unicode | Description | macOS | Linux | Windows | Notes |
|--------|---------|-------------|-------|-------|---------|-------|
| ⏱      | U+23F1  | Stopwatch   | ✓     | ✓     | Limited | Timing |
| ⌛     | U+231B  | Hourglass   | ✓     | ✓     | ✓       | Waiting |
| ⏳     | U+23F3  | Flowing Sand| ✓     | ✓     | Limited | Processing |
| 🕐     | U+1F550 | Clock       | ✓     | ✓     | Windows 10+ | Emoji |

## Platform Compatibility Guide

### Universal (Safe Everywhere)
These work reliably across all platforms:
- ASCII characters (`!`, `-`, `+`, `*`, `|`)
- Basic arrows (`→`, `←`, `↑`, `↓`)
- Check/X marks (`✓`, `✗`)
- Box drawing (`│`, `─`, `├`, `└`)
- Basic bullets (`•`, `○`)
- Basic shapes (`■`, `□`, `▲`, `▼`)

### Good Support (Modern Terminals)
Works on macOS, Linux, and Windows 10+:
- Warning symbols (`⚠`)
- Extended arrows (`➜`, `↩`, `↪`)
- Progress blocks (`░`, `▒`, `▓`, `█`)
- Braille spinners (`⠋`, `⠙`, `⠹`, etc.)

### Limited Support (Use with Caution)
May not render on older systems or all terminals:
- Emoji (`✅`, `❌`, `📁`, `📄`, `🕐`)
- Specialized math symbols (`⟹`, `⨯`)
- Advanced geometric shapes (`◴`, `◷`, `◜`, `◝`)

### Windows Considerations
- Windows 10+ has much better Unicode support than earlier versions
- Windows Terminal supports more symbols than legacy cmd.exe
- PowerShell 7+ has improved rendering
- Consider providing `-UseAscii` flag for older systems

## Usage Recommendations

### 1. Semantic Consistency
Use the same symbol for the same meaning throughout your CLI:
```
✓ Operation completed successfully
✗ Operation failed
⚠ Warning: destructive action
→ Navigate to next step
```

### 2. Provide ASCII Fallbacks
For critical information, offer ASCII alternatives:
```bash
if supports_unicode; then
    echo "✓ Success"
else
    echo "[OK] Success"
fi
```

### 3. Test Rendering
Always test symbols in:
- macOS Terminal
- iTerm2
- Windows Terminal
- PowerShell
- VS Code integrated terminal
- Linux GNOME Terminal

### 4. Avoid Emoji in Production CLIs
Emoji can:
- Render at different sizes
- Display in color (disrupting design)
- Fail on older systems
- Be inconsistent across fonts

Use simple Unicode symbols instead.

### 5. Consider Accessibility
- Screen readers handle ASCII better than Unicode
- Provide text alternatives
- Don't rely solely on symbols for meaning

## Quick Reference: Common Patterns

### Status Line
```
✓ Task completed
✗ Task failed
⚠ Task needs attention
- Task pending
```

### File Tree
```
project/
├── src/
│   ├── main.rs
│   └── lib.rs
├── tests/
│   └── test.rs
└── Cargo.toml
```

### Progress Bar
```
[████████░░] 80%
[▓▓▓▓▓▓▓▓▒▒] 8/10 complete
```

### List Navigation
```
→ Selected item
  Other item
  Another item
```

### Spinner States
```
⠋ Loading...
⠙ Loading...
⠹ Loading...
⠸ Loading...
```

## Testing Utilities

### Environment Detection
```bash
# Check Unicode support
locale | grep -i utf

# Check terminal capabilities
echo $TERM

# Test symbol rendering
echo "✓ ✗ ⚠ → ├ ▓"
```

### Manual Test String
Copy this string to test symbol support:
```
✓✗⚠!•→←↑↓│─├└■□▲▼░▒▓█⠋⠙⠹⠸
```

## Additional Resources

- Unicode Character Database: https://unicode.org/charts/
- Terminal compatibility: https://github.com/sindresorhus/figures
- Box drawing: https://en.wikipedia.org/wiki/Box-drawing_character
- Braille patterns: https://en.wikipedia.org/wiki/Braille_Patterns
