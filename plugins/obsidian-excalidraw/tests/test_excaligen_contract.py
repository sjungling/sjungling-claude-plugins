"""Pin excaligen's behavior. These guard the version pin — if a bump changes
geometry or binding, these fail rather than silently producing broken diagrams."""
import json

import pytest
from excaligen.SceneBuilder import SceneBuilder


@pytest.fixture
def scene_json():
    s = SceneBuilder()
    ellipse = s.ellipse("User").center(0, 0)
    rect = s.rectangle("API").center(320, 0)
    s.arrow("calls").bind(ellipse, rect)
    return json.loads(s.json())


def by_type(doc, kind):
    return [e for e in doc["elements"] if e["type"] == kind]


def test_arrow_starts_on_shape_boundary_not_center(scene_json):
    """The defining requirement: Obsidian renders raw points without applying
    live binding, so center-to-center arrows draw through shapes."""
    arrow = by_type(scene_json, "arrow")[0]
    ellipse = by_type(scene_json, "ellipse")[0]
    assert arrow["x"] == pytest.approx(ellipse["x"] + ellipse["width"])
    assert arrow["y"] == pytest.approx(0.0)


def test_arrow_ends_on_target_boundary(scene_json):
    arrow = by_type(scene_json, "arrow")[0]
    rect = by_type(scene_json, "rectangle")[0]
    end_x = arrow["x"] + arrow["points"][-1][0]
    assert end_x == pytest.approx(rect["x"])


def test_arrow_points_start_at_origin(scene_json):
    arrow = by_type(scene_json, "arrow")[0]
    assert arrow["points"][0] == [0.0, 0.0]


def test_bindings_are_bidirectional(scene_json):
    arrow = by_type(scene_json, "arrow")[0]
    ellipse = by_type(scene_json, "ellipse")[0]
    rect = by_type(scene_json, "rectangle")[0]
    assert arrow["startBinding"]["elementId"] == ellipse["id"]
    assert arrow["endBinding"]["elementId"] == rect["id"]
    assert any(b["id"] == arrow["id"] for b in ellipse["boundElements"])
    assert any(b["id"] == arrow["id"] for b in rect["boundElements"])


def test_labels_become_bound_text_elements(scene_json):
    texts = {e["text"]: e for e in by_type(scene_json, "text")}
    assert set(texts) == {"User", "API", "calls"}
    ellipse = by_type(scene_json, "ellipse")[0]
    rect = by_type(scene_json, "rectangle")[0]
    arrow = by_type(scene_json, "arrow")[0]
    assert texts["User"]["containerId"] == ellipse["id"]
    assert texts["API"]["containerId"] == rect["id"]
    assert texts["calls"]["containerId"] == arrow["id"]


def test_element_ids_are_unique(scene_json):
    ids = [e["id"] for e in scene_json["elements"]]
    assert len(ids) == len(set(ids))


def test_document_has_required_top_level_keys(scene_json):
    assert set(scene_json) >= {"type", "version", "source", "elements", "appState", "files"}
    assert scene_json["type"] == "excalidraw"
