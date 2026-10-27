import json

import pytest
from conftest import by_type
from obsidian_preset import LINK, SHAPE, InvalidLabelError, fit, new_scene, styled


def render(scene):
    return json.loads(scene.json())


def test_fills_are_white_not_transparent():
    """Pitfall #1: colored or transparent fills render dark in Obsidian embeds."""
    s = new_scene()
    s.rectangle("Box").center(0, 0)
    assert by_type(render(s), "rectangle")[0]["backgroundColor"].upper() == "#FFFFFF"


def test_roughness_is_zero():
    s = new_scene()
    s.rectangle("Box").center(0, 0)
    assert by_type(render(s), "rectangle")[0]["roughness"] == 0


def test_view_background_is_white():
    s = new_scene()
    s.rectangle("Box").center(0, 0)
    assert render(s)["appState"]["viewBackgroundColor"].lower() == "#ffffff"


def test_unstyled_elements_are_not_black():
    """A missing default stroke color silently yields black shapes."""
    s = new_scene()
    s.rectangle("Box").center(0, 0)
    assert by_type(render(s), "rectangle")[0]["strokeColor"].upper() != "#000000"


@pytest.mark.parametrize("status,expected", [
    ("active", "#1D4ED8"),
    ("lapsed", "#DC2626"),
    ("secondary", "#6B7280"),
])
def test_styled_applies_shape_palette(status, expected):
    s = new_scene()
    styled(s.rectangle("Box").center(0, 0), status)
    assert by_type(render(s), "rectangle")[0]["strokeColor"].upper() == expected


def test_styled_applies_link_palette_to_arrows():
    s = new_scene()
    a = s.rectangle("A").center(0, 0)
    b = s.rectangle("B").center(300, 0)
    styled(s.arrow("gone").bind(a, b), "removed")
    assert by_type(render(s), "arrow")[0]["strokeColor"].upper() == "#DC2626"


def test_lapsed_is_thicker_than_active():
    s = new_scene()
    styled(s.rectangle("Old").center(0, 0), "lapsed")
    assert by_type(render(s), "rectangle")[0]["strokeWidth"] == 3


def test_shape_and_link_palettes_are_distinct_groups():
    """Shape and relationship states are separate palettes with separate keys.
    Flattening these into one dict loses a deliberate distinction."""
    assert set(SHAPE) == {"active", "lapsed", "secondary"}
    assert set(LINK) == {"paused", "removed"}
    assert not set(SHAPE) & set(LINK)


def test_styled_returns_element_for_chaining():
    s = new_scene()
    rect = s.rectangle("Box")
    assert styled(rect, "active") is rect


def test_styled_rejects_unknown_status():
    """The error must name the valid statuses — a bare KeyError on a typo'd
    status leaves the caller guessing."""
    s = new_scene()
    with pytest.raises(KeyError) as excinfo:
        styled(s.rectangle("Box"), "nonexistent")
    message = str(excinfo.value)
    assert "nonexistent" in message
    assert "active" in message and "removed" in message


@pytest.mark.parametrize("bad", ["Two\nLines", 'Has "quotes"', "Tab\there", "Back\\slash"])
def test_multiline_and_escaped_labels_rejected(bad):
    """Pitfall #9: the Obsidian CLI corrupts these. Fail at construction,
    not after a silent bad write."""
    s = new_scene()
    with pytest.raises(InvalidLabelError):
        s.rectangle(bad)


def test_safe_labels_accepted():
    s = new_scene()
    s.rectangle("API Gateway").center(0, 0)
    s.ellipse("User").center(300, 0)
    s.text("A caption").center(0, 200)
    assert len(by_type(render(s), "text")) == 3


def test_label_validation_covers_all_element_types():
    s = new_scene()
    for factory in (s.rectangle, s.ellipse, s.diamond, s.arrow, s.text, s.frame):
        with pytest.raises(InvalidLabelError):
            factory("bad\nlabel")


def test_json_rejects_unsafe_text_set_after_construction():
    """`.content()` is a public setter that writes straight past the factory
    checks. Serialization is the gate nothing gets around."""
    s = new_scene()
    label = s.text("safe")
    label.content("now\nmultiline")
    with pytest.raises(InvalidLabelError):
        s.json()


def test_json_rejects_unsafe_text_object_passed_as_shape_label():
    """excaligen accepts a `Text` object where a str label goes; _check() sees
    the object, not its content, so only serialization catches this."""
    s = new_scene()
    label = s.text("safe")
    label.content('has "quotes"')
    s.rectangle(label)
    with pytest.raises(InvalidLabelError):
        s.json()


def test_every_label_taking_factory_is_overridden():
    """ObsidianScene names six factories by hand so validation fails at the call
    site with a useful traceback. That list is hand-maintained: if excaligen
    gains a new label-taking factory, this fails loudly rather than letting the
    new one fall back silently to the weaker serialization-time error."""
    import inspect

    from excaligen.SceneBuilder import SceneBuilder
    from obsidian_preset import ObsidianScene

    def first_param(member):
        try:
            return next(iter(list(inspect.signature(member).parameters)[1:]), None)
        except (TypeError, ValueError):
            return None

    label_taking = {
        name
        for name in dir(SceneBuilder)
        if not name.startswith("_")
        and callable(getattr(SceneBuilder, name))
        and first_param(getattr(SceneBuilder, name)) in {"label", "title", "text"}
    }
    unguarded = {
        name
        for name in label_taking
        if getattr(ObsidianScene, name) is getattr(SceneBuilder, name)
    }
    assert label_taking == {"rectangle", "ellipse", "diamond", "arrow", "text", "frame"}
    assert not unguarded, f"label-taking factories not overridden: {sorted(unguarded)}"


LONG = "A long label that excaligen will neither wrap nor grow a shape for"


def test_default_shape_overflows_a_long_label():
    """Why fit() exists: the shape stays 130x80 whatever its label measures."""
    s = new_scene()
    s.rectangle(LONG).center(0, 0)
    doc = render(s)
    assert by_type(doc, "text")[0]["width"] > by_type(doc, "rectangle")[0]["width"]


@pytest.mark.parametrize("shape", ["rectangle", "ellipse", "diamond"])
def test_fit_holds_the_label_it_was_sized_for(shape):
    s = new_scene()
    make = getattr(s, shape)
    make(LONG).size(*fit(LONG, shape=shape)).center(0, 0)
    doc = render(s)
    text, box = by_type(doc, "text")[0], by_type(doc, shape)[0]
    scale = 2 ** 0.5 if shape != "rectangle" else 1
    assert text["width"] * scale <= box["width"]
    assert text["height"] * scale <= box["height"]


def test_fit_keeps_short_labels_at_a_legible_minimum():
    assert fit("OK") == (120, 60)


def test_fit_scales_with_font_size():
    assert fit(LONG, fontsize=24)[0] > fit(LONG, fontsize=16)[0]


def test_arrows_keep_sizes_positive_and_put_direction_in_points():
    """Real Excalidraw never stores a negative width or height; an arrow that
    runs up or left says so in its points. Hand-built JSON must do the same."""
    s = new_scene()
    a = s.rectangle("A").center(0, 0)
    b = s.rectangle("B").center(-340, -200)
    s.arrow("back").bind(a, b)
    arrow = by_type(render(s), "arrow")[0]
    assert arrow["width"] > 0 and arrow["height"] > 0
    assert arrow["points"][-1][0] < 0 and arrow["points"][-1][1] < 0


def test_labels_and_bindings_are_recorded_on_both_sides():
    """Bound text names its container and the container lists the text; an
    arrow's binding is mirrored in the target's boundElements."""
    s = new_scene()
    a = s.rectangle("A").center(0, 0)
    b = s.rectangle("B").center(340, 0)
    s.arrow("to").bind(a, b)
    doc = render(s)
    shapes = {e["id"]: e for e in by_type(doc, "rectangle")}
    arrow = by_type(doc, "arrow")[0]
    for text in by_type(doc, "text"):
        owner = shapes.get(text["containerId"]) or arrow
        assert {"type": "text", "id": text["id"]} in owner["boundElements"]
    for end in ("startBinding", "endBinding"):
        target = shapes[arrow[end]["elementId"]]
        assert {"type": "arrow", "id": arrow["id"]} in target["boundElements"]
        assert set(arrow[end]) >= {"elementId", "focus", "gap"}
