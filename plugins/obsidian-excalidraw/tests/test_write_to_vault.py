import json

import pytest
from write_to_vault import (
    PREFIX,
    ChunkTooLargeError,
    EscapeError,
    VerifyError,
    build_header,
    check_escapes,
    classify,
    coerce_path,
    compact,
    extract_json,
    filter_banner,
    split_bodies,
)


def make_doc(n=3):
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": [
            {"id": f"e{i}", "type": "text", "text": f"label {i}", "x": i, "y": 0}
            for i in range(n)
        ],
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }


# --- compact JSON must match JS JSON.stringify ---

def test_compact_has_no_spaces():
    assert compact({"a": 1, "b": 2}) == '{"a":1,"b":2}'


def test_compact_preserves_non_ascii_literally():
    """Python defaults to ensure_ascii=True, turning an em-dash into \\u2014 —
    a backslash that trips the escape guard and corrupts CLI writes."""
    assert compact({"t": "Auth flow — v2"}) == '{"t":"Auth flow — v2"}'
    assert "\\" not in compact({"t": "Auth flow — v2"})


# --- escape guard ---

def test_check_escapes_rejects_backslash():
    with pytest.raises(EscapeError):
        check_escapes(r'{"text":"two\nlines"}')


def test_check_escapes_accepts_clean_json():
    check_escapes('{"text":"one line"}')


# --- header ---

def test_header_uses_literal_backslash_n_markers():
    """The CLI expands literal \\n in content= into real newlines."""
    header = build_header(make_doc()["elements"])
    assert "\\n" in header
    assert "\n" not in header


def test_header_lists_every_text_element_with_block_ref():
    header = build_header(make_doc()["elements"])
    for i in range(3):
        assert f"label {i} ^e{i}" in header


def test_header_ends_with_json_fence():
    assert build_header(make_doc()["elements"]).endswith("```json")


def test_header_contains_plugin_frontmatter():
    header = build_header(make_doc()["elements"])
    assert "excalidraw-plugin: parsed" in header
    assert "tags: [excalidraw]" in header
    assert "## Text Elements" in header


def test_header_skips_non_text_elements():
    elements = make_doc()["elements"] + [{"id": "r1", "type": "rectangle"}]
    assert "^r1" not in build_header(elements)


# --- chunking ---

def test_split_bodies_reassembles_to_valid_json():
    doc = make_doc(20)
    reassembled = json.loads("".join(split_bodies(doc, chunk_bytes=200)))
    assert len(reassembled["elements"]) == 20


def test_split_bodies_respects_chunk_limit():
    """The element payload of each chunk stays under the limit. The first chunk
    also carries the document prefix and the last the suffix; those sit outside
    the per-append budget."""
    bodies = split_bodies(make_doc(30), chunk_bytes=200)
    assert len(bodies) > 1
    payloads = [b[len(PREFIX):] if i == 0 else b for i, b in enumerate(bodies)]
    for payload in payloads[:-1]:
        assert len(payload) <= 200


def test_split_bodies_single_chunk_when_small():
    assert len(split_bodies(make_doc(2), chunk_bytes=100_000)) == 1


def test_split_bodies_preserves_appstate_and_files():
    doc = make_doc(5)
    doc["appState"]["gridSize"] = 20
    result = json.loads("".join(split_bodies(doc, chunk_bytes=200)))
    assert result["appState"]["gridSize"] == 20
    assert result["files"] == {}


def test_split_bodies_rejects_oversized_single_element():
    doc = make_doc(1)
    doc["elements"][0]["text"] = "x" * 5000
    with pytest.raises(ChunkTooLargeError):
        split_bodies(doc, chunk_bytes=1000)


# --- banner filtering ---

def test_filter_banner_drops_noise():
    noisy = "Loading updated app package /foo.asar\nYour Obsidian installer is out of date\nreal output"
    assert filter_banner(noisy).strip() == "real output"


def test_filter_banner_preserves_blank_lines():
    """An earlier truthy filter silently ate blank lines — a real bug in a
    general-purpose helper."""
    assert filter_banner("a\n\nb") == "a\n\nb"


def test_filter_banner_drops_timestamp_lines():
    assert "2026-09-22" not in filter_banner("2026-09-22 21:08:43 Loading\nkept")


# --- error classification ---

@pytest.mark.parametrize("output,expected", [
    ("all good", "ok"),
    ("Error: NativeImage failure", "transient"),
    ("Broken pipe", "hard"),
    ("write() failed", "hard"),
    ("vault not found", "hard"),
    ("may require a plugin", "hard"),
])
def test_classify(output, expected):
    assert classify(output) == expected


# --- read-back extraction ---

def test_extract_json_pulls_fenced_block():
    note = 'preamble\n```json\n{"elements":[1,2]}\n```\n%%'
    assert extract_json(note)["elements"] == [1, 2]


def test_extract_json_handles_multiline_body():
    """append inserts newlines between chunks; split happens between elements
    so the reassembled multi-line JSON is still valid."""
    note = '```json\n{"elements":\n[1,\n2]}\n```'
    assert extract_json(note)["elements"] == [1, 2]


def test_extract_json_raises_when_no_fence():
    with pytest.raises(VerifyError):
        extract_json("no fence here")


def test_extract_json_raises_on_malformed_body():
    with pytest.raises(VerifyError):
        extract_json('```json\n{"elements":\n```')


# --- path coercion ---

@pytest.mark.parametrize("given,expected", [
    ("Diagrams/a.excalidraw", "Diagrams/a.excalidraw.md"),
    ("Diagrams/a.excalidraw.md", "Diagrams/a.excalidraw.md"),
])
def test_coerce_path(given, expected):
    assert coerce_path(given) == expected
