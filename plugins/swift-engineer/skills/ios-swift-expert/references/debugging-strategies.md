# Debugging Strategies

Comprehensive debugging techniques for iOS and macOS development.

## Xcode Build Issues

1. **Clean Build Folder**: Product → Clean Build Folder (Cmd+Shift+K)
2. **Delete Derived Data**: `rm -rf ~/Library/Developer/Xcode/DerivedData`
3. **Check Build Settings**: Verify code signing, Swift version, deployment target
4. **Read Error Carefully**: Xcode errors often include fix-its
5. **Check Dependencies**: Swift Package Manager, CocoaPods, or Carthage issues

## Runtime Issues

1. **Breakpoints**: Set symbolic breakpoints for exceptions
2. **LLDB Commands**: `po`, `expr`, `frame variable` for inspection
3. **View Debugging**: Use Xcode's visual debugger (Debug → View Debugging)
4. **Memory Graph**: Detect retain cycles with Debug → Memory Graph
5. **Instruments**: Profile with Time Profiler, Allocations, Leaks

## Performance Profiling with xctrace

`xctrace` is the CLI interface for Instruments — use it to capture and analyze performance traces without opening the Instruments GUI.

### Discovery

```bash
# List all available profiling templates
xctrace list templates

# List connected devices and simulators
xctrace list devices
```

### Recording Traces

```bash
# Attach to a running process by name or PID
xctrace record --template 'Time Profiler' --attach MyApp --output perf.trace --time-limit 10s

# Launch and profile a process
xctrace record --template 'Time Profiler' --launch -- /path/to/MyApp.app/Contents/MacOS/MyApp

# Profile on a specific simulator
xctrace record --template 'Allocations' --device 'iPhone 16 Pro Simulator' --attach MyApp --output mem.trace --time-limit 15s

# Target a physical device by UDID
xctrace record --template 'Leaks' --device <udid> --attach MyApp --output leaks.trace --time-limit 20s
```

### Exporting and Analyzing Trace Data

```bash
# View the table of contents (available tables/schemas)
xctrace export --input perf.trace --toc

# Export a specific table to XML
xctrace export --input perf.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]'

# Export to HAR format (network traces)
xctrace export --input network.trace --har
```

### Template Selection Guide

| Symptom | Template | What to look for |
|---------|----------|-----------------|
| App feels slow / UI stutters | Time Profiler | Hot code paths, main thread time |
| High memory usage | Allocations | Allocation growth, transient spikes |
| Memory keeps growing | Leaks | Leaked objects, retain cycles |
| Dropped frames / jank | Animation Hitches | Commit/render phase durations |
| SwiftUI views redrawing too often | SwiftUI | Body evaluation counts |
| Excessive network calls | Network | Request frequency, payload sizes |
| Battery drain | Energy Log | CPU/GPU/network energy impact |

### Workflow Tips

- Use `--time-limit` to cap trace duration and keep file sizes manageable
- Combine with `xcodebuild test` to profile during test execution
- Export XML output and parse with `xmllint` or `xpath` for automated analysis
- Trace files (`.trace`) can also be opened in Instruments GUI for visual inspection

## SwiftUI Debugging

1. **Preview Crashes**: Check `PreviewProvider` initialization
2. **State Updates**: Verify state changes on main thread
3. **View Redrawing**: Use `Self._printChanges()` to debug updates
4. **Modifiers Order**: Order matters (frame before padding vs. padding before frame)
