# Common Patterns & Solutions

Design patterns and solutions for iOS and macOS development.

## Pattern: Dependency Injection

**Problem:** Tight coupling makes testing difficult
**Solution:** Use protocol-based dependency injection

```swift
protocol NetworkServiceProtocol {
    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

struct ContentView: View {
    @StateObject private var viewModel: ContentViewModel

    init(networkService: NetworkServiceProtocol = NetworkService()) {
        _viewModel = StateObject(wrappedValue: ContentViewModel(networkService: networkService))
    }

    var body: some View {
        // View implementation
    }
}
```

## Pattern: Result Builders

**Problem:** Complex view hierarchies
**Solution:** Use result builders for DSL-like syntax

```swift
@resultBuilder
struct ViewArrayBuilder {
    static func buildBlock(_ components: [AnyView]...) -> [AnyView] {
        components.flatMap { $0 }
    }

    static func buildExpression<V: View>(_ expression: V) -> [AnyView] {
        [AnyView(expression)]
    }
}

func createViews(@ViewArrayBuilder _ builder: () -> [AnyView]) -> [AnyView] {
    builder()
}
```

## Pattern: Coordinator for Navigation

**Problem:** Complex navigation logic scattered across views
**Solution:** Centralize navigation in coordinator

```swift
@MainActor
final class AppCoordinator: ObservableObject {
    @Published var path = NavigationPath()

    enum Route: Hashable {
        case detail(id: String)
        case settings
        case profile
    }

    func navigate(to route: Route) {
        path.append(route)
    }

    func pop() {
        path.removeLast()
    }

    func popToRoot() {
        path = NavigationPath()
    }
}
```
