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
    reassembled = json.loads("".join(split_bodies(doc, chunk_bytes=400)))
    assert len(reassembled["elements"]) == 20


def test_split_bodies_respects_chunk_limit():
    """EVERY assembled body must fit the limit — including the first, which
    carries the document prefix, and the last, which carries the suffix. An
    append over the CLI ceiling is dropped silently."""
    bodies = split_bodies(make_doc(30), chunk_bytes=400)
    assert len(bodies) > 1
    assert bodies[0].startswith(PREFIX)
    for body in bodies:
        assert len(body) <= 400


def test_split_bodies_budgets_suffix_with_large_files_map():
    """A populated `files` map (embedded images) inflates the suffix carried by
    the final body. Unbudgeted, that append silently exceeded the ceiling."""
    doc = make_doc(10)
    doc["files"] = {"img": {"dataURL": "x" * 500}}
    bodies = split_bodies(doc, chunk_bytes=900)
    for body in bodies:
        assert len(body) <= 900
    assert json.loads("".join(bodies))["files"] == doc["files"]


def test_split_bodies_rejects_when_prefix_and_suffix_alone_exceed_limit():
    """No packing can succeed when the document scaffolding outgrows the
    ceiling — say so instead of emitting chunks that will be dropped."""
    doc = make_doc(1)
    doc["files"] = {"img": {"dataURL": "x" * 5000}}
    with pytest.raises(ChunkTooLargeError):
        split_bodies(doc, chunk_bytes=1000)


def test_split_bodies_single_chunk_when_small():
    assert len(split_bodies(make_doc(2), chunk_bytes=100_000)) == 1


def test_split_bodies_preserves_appstate_and_files():
    doc = make_doc(5)
    doc["appState"]["gridSize"] = 20
    result = json.loads("".join(split_bodies(doc, chunk_bytes=400)))
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


# --- CLI driver ---

import types

from write_to_vault import main, run_obsidian, write_diagram


class FakeRunner:
    """Stands in for subprocess.run, recording calls and replaying outputs."""

    def __init__(self, outputs=None):
        self.calls = []
        self.outputs = list(outputs or [])

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        out = self.outputs.pop(0) if self.outputs else ""
        return types.SimpleNamespace(stdout=out, stderr="", returncode=0)


def test_run_obsidian_retries_transient_then_succeeds():
    runner = FakeRunner(["NativeImage error", "fine"])
    assert run_obsidian(["read"], runner=runner, retries=3) == "fine"
    assert len(runner.calls) == 2


def test_run_obsidian_raises_on_hard_error():
    runner = FakeRunner(["Broken pipe"])
    with pytest.raises(RuntimeError):
        run_obsidian(["create"], runner=runner)


def test_run_obsidian_strips_banner_from_result():
    runner = FakeRunner(["Loading updated app package /x.asar\npayload"])
    assert run_obsidian(["read"], runner=runner).strip() == "payload"


def test_run_obsidian_raises_when_transient_error_persists():
    """Exhausting retries on a transient error must raise, not return the
    erroring output as a successful result. A persistent NativeImage failure
    during the verify read would otherwise surface as a misleading
    'no json block' error pointing at a corrupt diagram."""
    runner = FakeRunner(["NativeImage error", "NativeImage error"])
    with pytest.raises(RuntimeError, match="transient"):
        run_obsidian(["read"], runner=runner, retries=1)
    assert len(runner.calls) == 2


def test_write_diagram_issues_create_then_appends_then_fences():
    doc = make_doc(3)
    verify_note = '```json\n' + json.dumps(doc) + '\n```'
    runner = FakeRunner(["", "", "", "", verify_note])
    count = write_diagram(doc, "V", "Diagrams/a.excalidraw.md", 100_000, True, runner)
    assert count == 3
    # calls are recorded as ["obsidian", <subcommand>, ...]
    commands = [c[1] for c in runner.calls]
    assert commands[0] == "create"
    assert commands[1] == "append"
    assert commands[-1] == "read"


def test_write_diagram_verify_detects_element_count_mismatch():
    doc = make_doc(3)
    short = make_doc(1)
    verify_note = '```json\n' + json.dumps(short) + '\n```'
    runner = FakeRunner(["", "", "", "", verify_note])
    with pytest.raises(VerifyError):
        write_diagram(doc, "V", "Diagrams/a.excalidraw.md", 100_000, True, runner)


def test_write_diagram_skips_read_when_verify_disabled():
    doc = make_doc(2)
    runner = FakeRunner(["", "", "", ""])
    write_diagram(doc, "V", "Diagrams/a.excalidraw.md", 100_000, False, runner)
    assert "read" not in [c[1] for c in runner.calls]


def test_main_rejects_input_without_elements(tmp_path):
    bad = tmp_path / "bad.excalidraw"
    bad.write_text('{"type":"excalidraw"}')
    assert main(["--vault", "V", "--path", "a.excalidraw.md", "--input", str(bad)]) == 1


def test_main_rejects_invalid_json(tmp_path):
    bad = tmp_path / "bad.excalidraw"
    bad.write_text("not json")
    assert main(["--vault", "V", "--path", "a.excalidraw.md", "--input", str(bad)]) == 1
