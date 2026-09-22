#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Write an .excalidraw diagram into an Obsidian vault through the `obsidian` CLI.

The ONE entry point for writing diagrams to iCloud-synced vaults (paths under
~/Library/Mobile Documents/...), where the filesystem is TCC-blocked and only
the Obsidian app can touch files. Works for any vault, since the CLI proxies to
the running app regardless.

Why a dedicated writer — lessons this encodes:

  - The CLI forwards args to the running app over a process-singleton socket
    with a payload ceiling (~10-11KB). Larger `content=` fails: either a silent
    broken pipe (exit 0, nothing written) or an "Argument must be a file path or
    a NativeImage" error. So the JSON body is split into sub-limit chunks and
    streamed with `append`.
  - The CLI's confirmation line ("Created:"/"Appended to:") is UNRELIABLE: it is
    printed for small payloads but OMITTED for larger ones that still succeed.
    So success is NOT gated on it — the real gate is a read-back element count.
  - `append` inserts a real newline between chunks — harmless because the
    compact JSON is split BETWEEN elements, outside any string, so the
    reassembled multi-line JSON stays valid. Requires single-line labels.
  - Overwriting a note CURRENTLY OPEN in Obsidian silently no-ops. Close it
    first; the read-back verify catches the stale state.
  - The CLI emits banner noise and an intermittent "NativeImage" error; banners
    are filtered and transient errors retried.

Usage (MUST run unsandboxed — the CLI hangs under the command sandbox):

    ./gen-diagram.py > "$TMPDIR/diagram.excalidraw"
    ./write_to_vault.py --vault "My Vault" \\
        --path "Diagrams/my-diagram.excalidraw.md" \\
        --input "$TMPDIR/diagram.excalidraw"
"""
import argparse
import json
import re
import subprocess
import sys
import time

CHUNK_BYTES_DEFAULT = 8000
BANNER = re.compile(
    r"Loading updated app package|installer is out of date|Checking for update"
    r"|Latest version is|App is up to date|^\s*Success\.\s*$|^\s*20\d\d-\d\d-\d\d "
)
HARD_ERRORS = ("Broken pipe", "write() failed", "not found", "may require a plugin")
TRANSIENT_ERRORS = ("NativeImage",)

PREFIX = '{"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":['


class EscapeError(ValueError):
    pass


class VerifyError(RuntimeError):
    pass


class ChunkTooLargeError(ValueError):
    pass


def compact(obj):
    """Match JS JSON.stringify: no spaces, non-ASCII left literal.

    ensure_ascii=False is mandatory — escaping to \\uXXXX injects backslashes
    that trip check_escapes and corrupt CLI writes.
    """
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def check_escapes(compact_json):
    if "\\" in compact_json:
        raise EscapeError(
            "drawing JSON contains escaped characters (a newline, tab, backslash or "
            'quote inside a label). Use plain single-line labels with no " characters.'
        )


def coerce_path(path):
    """`obsidian create` only writes .md, and ![[x.excalidraw]] resolves to
    x.excalidraw.md."""
    if path.endswith(".excalidraw"):
        return path + ".md"
    return path


def build_header(elements):
    """Everything up to and including the ```json fence.

    Joined with literal "\\n" markers — the CLI expands them into real newlines.
    """
    text_elements = [
        f"{e['text']} ^{e['id']}"
        for e in elements
        if e.get("type") == "text" and isinstance(e.get("text"), str)
    ]
    lines = [
        "---", "", "excalidraw-plugin: parsed", "tags: [excalidraw]", "", "---",
        "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==",
        "", "# Excalidraw Data", "", "## Text Elements", *text_elements, "",
        "%%", "## Drawing", "```json",
    ]
    return "\\n".join(lines)


def split_bodies(doc, chunk_bytes=CHUNK_BYTES_DEFAULT):
    """Split the JSON body BETWEEN elements so each append stays under the limit."""
    suffix = (
        '],"appState":'
        + compact(doc.get("appState") or {"gridSize": None, "viewBackgroundColor": "#ffffff"})
        + ',"files":'
        + compact(doc.get("files") or {})
        + "}"
    )
    serialized = [compact(e) for e in doc["elements"]]

    groups, current, length = [], [], 0
    for item in serialized:
        if len(item) + len(PREFIX) > chunk_bytes:
            raise ChunkTooLargeError(
                f"a single element serializes to {len(item)} bytes, over "
                f"--chunk-bytes {chunk_bytes}. Raise it (stay under ~12000)."
            )
        if current and length + len(item) + 1 > chunk_bytes:
            groups.append(current)
            current, length = [], 0
        current.append(item)
        length += len(item) + 1
    if current:
        groups.append(current)

    bodies = []
    for i, group in enumerate(groups):
        body = (PREFIX if i == 0 else ",") + ",".join(group)
        if i == len(groups) - 1:
            body += suffix
        bodies.append(body)
    return bodies


def filter_banner(text):
    """Drop banner lines only — never blank lines."""
    return "\n".join(
        line for line in (text or "").split("\n") if not BANNER.search(line)
    )


def classify(output):
    if any(marker in output for marker in TRANSIENT_ERRORS):
        return "transient"
    if any(marker in output for marker in HARD_ERRORS):
        return "hard"
    return "ok"


def extract_json(note_text):
    """Pull the drawing out of the ```json fence of a read-back note."""
    body, inside = [], False
    for line in note_text.split("\n"):
        if line.strip() == "```json":
            inside = True
            continue
        if inside and line.strip() == "```":
            break
        if inside:
            body.append(line)
    if not body:
        raise VerifyError("read-back note contains no ```json block")
    try:
        return json.loads("\n".join(body))
    except json.JSONDecodeError as exc:
        raise VerifyError(
            f"read-back JSON did not parse ({exc}). Likely the target note was OPEN "
            "in Obsidian (overwrite no-ops on open notes) or a chunk exceeded the IPC "
            "limit. Close the note or lower --chunk-bytes, then retry."
        ) from exc
