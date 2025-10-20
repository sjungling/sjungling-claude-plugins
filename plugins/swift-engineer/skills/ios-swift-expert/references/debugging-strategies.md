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

## SwiftUI Debugging

1. **Preview Crashes**: Check `PreviewProvider` initialization
2. **State Updates**: Verify state changes on main thread
3. **View Redrawing**: Use `Self._printChanges()` to debug updates
4. **Modifiers Order**: Order matters (frame before padding vs. padding before frame)
