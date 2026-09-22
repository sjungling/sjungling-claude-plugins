import json

import pytest
from obsidian_preset import LINK, SHAPE, InvalidLabelError, new_scene, styled


def render(scene):
    return json.loads(scene.json())


def by_type(doc, kind):
    return [e for e in doc["elements"] if e["type"] == kind]


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
    s = new_scene()
    with pytest.raises(KeyError):
        styled(s.rectangle("Box"), "nonexistent")


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
