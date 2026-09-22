"""Obsidian-safe defaults for excaligen scenes.

Obsidian's embedded preview is stricter than excalidraw.com: colored fills
render dark, and diagrams written through the Obsidian CLI cannot contain
escape sequences. This module makes both constraints structural.
"""
from excaligen.SceneBuilder import SceneBuilder

SHAPE = {
    "active": {"color": "#1d4ed8", "thickness": 2, "stroke": "solid"},
    "lapsed": {"color": "#dc2626", "thickness": 3, "stroke": "solid"},
    "secondary": {"color": "#6b7280", "thickness": 2, "stroke": "dashed"},
}

LINK = {
    "paused": {"color": "#9ca3af", "thickness": 2, "stroke": "dashed"},
    "removed": {"color": "#dc2626", "thickness": 2, "stroke": "dashed"},
}

UNSAFE_CHARS = ("\n", "\t", '"', "\\")


class InvalidLabelError(ValueError):
    pass


def _check(label):
    if isinstance(label, str) and any(c in label for c in UNSAFE_CHARS):
        raise InvalidLabelError(
            f"label {label!r} contains a newline, tab, quote or backslash. "
            "The Obsidian CLI corrupts these — use a single-line label."
        )
    return label


class ObsidianScene(SceneBuilder):
    """SceneBuilder that rejects labels the Obsidian CLI cannot carry."""

    def rectangle(self, label=None):
        return super().rectangle(_check(label))

    def ellipse(self, label=None):
        return super().ellipse(_check(label))

    def diamond(self, label=None):
        return super().diamond(_check(label))

    def arrow(self, label=None):
        return super().arrow(_check(label))

    def text(self, text=None):
        return super().text(_check(text))

    def frame(self, title=None):
        return super().frame(_check(title))


def new_scene():
    scene = ObsidianScene()
    scene.background("#ffffff")
    scene.defaults().background("#ffffff").sloppiness(0).thickness(2).fontsize(16).color(
        SHAPE["active"]["color"]
    )
    return scene


def styled(element, status):
    try:
        spec = SHAPE[status] if status in SHAPE else LINK[status]
    except KeyError:
        raise KeyError(
            f"unknown status {status!r} — shape states: {', '.join(SHAPE)}; "
            f"relationship states: {', '.join(LINK)}"
        ) from None
    element.color(spec["color"]).thickness(spec["thickness"]).stroke(spec["stroke"])
    return element
