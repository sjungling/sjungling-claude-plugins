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
    """Split the JSON body BETWEEN elements so each append stays under the limit.

    The first body carries PREFIX and the last carries suffix, so both are
    budgeted here — an append over the CLI ceiling is dropped silently. Which
    group ends up last is unknown while packing, so suffix is reserved from
    every group: it is tiny whenever `files` is empty, and an extra append
    costs less than a dropped one.
    """
    suffix = (
        '],"appState":'
        + compact(doc.get("appState") or {"gridSize": None, "viewBackgroundColor": "#ffffff"})
        + ',"files":'
        + compact(doc.get("files") or {})
        + "}"
    )
    overhead = len(PREFIX) + len(suffix)
    if overhead >= chunk_bytes:
        raise ChunkTooLargeError(
            f"the document prefix and suffix need {overhead} bytes on their own, at or "
            f"over --chunk-bytes {chunk_bytes}. A populated `files` map (embedded images) "
            "is the usual cause. Raise --chunk-bytes (stay under ~12000)."
        )
    budget = chunk_bytes - overhead
    serialized = [compact(e) for e in doc["elements"]]

    groups, current, length = [], [], 0
    for item in serialized:
        if len(item) > budget:
            raise ChunkTooLargeError(
                f"a single element serializes to {len(item)} bytes, over the {budget}-byte "
                f"element budget (--chunk-bytes {chunk_bytes} less {overhead} bytes of "
                "document prefix/suffix). Raise --chunk-bytes (stay under ~12000)."
            )
        if current and length + len(item) + 1 > budget:
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
    """Judge a CLI result from its output text.

    The exit code is deliberately ignored, not overlooked: this CLI returns 0
    for everything — a nonexistent path, an unknown subcommand, even an unknown
    vault (all verified against the installed CLI). Non-zero would add no
    signal, and zero would mask silent drops. The read-back element count in
    write_diagram is the real gate.
    """
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


def _should_retry(attempt, retries, delay, label, sleeper):
    """Back off for another attempt, or report that the budget is spent.

    A timeout and a transient CLI error need this identical shape, and getting
    the exhaustion case wrong once returned an erroring result as success.
    The caller raises, so each failure keeps its own message and context.
    """
    if attempt > retries:
        return False
    print(f"  ({label}, retry {attempt}/{retries})", file=sys.stderr)
    sleeper(delay)
    return True


def run_obsidian(args, runner=subprocess.run, timeout=60, retries=3, sleeper=time.sleep):
    """Run one obsidian CLI command, retrying transient errors and timeouts.

    The confirmation line is NOT required — it is omitted for larger successful
    payloads. Correctness is gated by the read-back verify instead.

    `sleeper` is injectable so tests can exercise the retry budget without
    spending real seconds on backoff meant for a flaky CLI.
    """
    for attempt in range(1, retries + 2):
        try:
            result = runner(
                ["obsidian", *args], capture_output=True, text=True, timeout=timeout
            )
        except FileNotFoundError:
            raise RuntimeError("`obsidian` CLI not found on PATH.") from None
        except subprocess.TimeoutExpired:
            if _should_retry(attempt, retries, 3, "timeout", sleeper):
                continue
            raise RuntimeError(
                f"CLI timed out ({timeout}s) after {retries} retries. Run UNSANDBOXED "
                "(the socket hangs under the sandbox); the app may also be wedged — "
                "restart Obsidian."
            ) from None

        output = f"{filter_banner(result.stdout)}\n{filter_banner(result.stderr)}".strip()
        verdict = classify(output)
        if verdict == "transient":
            if _should_retry(attempt, retries, 2.5, "transient CLI error", sleeper):
                continue
            raise RuntimeError(
                f"CLI kept returning a transient error after {retries} retries: {output}\n"
                "Obsidian may be wedged — restart it and retry."
            )
        if verdict == "hard":
            raise RuntimeError(
                f"CLI error: {output}\nCheck the vault name, path, and that the "
                "payload is under --chunk-bytes."
            )
        return output


def write_diagram(doc, vault, path, chunk_bytes, verify, runner=subprocess.run):
    check_escapes(compact(doc))
    header = build_header(doc["elements"])
    bodies = split_bodies(doc, chunk_bytes)

    reassembled = json.loads("".join(bodies))
    if len(reassembled["elements"]) != len(doc["elements"]):
        raise VerifyError("internal: reassembly changed element count")

    vault_arg, path_arg = f"vault={vault}", f"path={path}"
    print(
        f"write-to-vault: {len(doc['elements'])} elements, {len(bodies)} chunk(s) "
        f"→ {vault}:{path}",
        file=sys.stderr,
    )

    run_obsidian(["create", vault_arg, path_arg, f"content={header}", "overwrite"], runner=runner)
    print("  header written", file=sys.stderr)

    for i, body in enumerate(bodies, 1):
        run_obsidian(["append", vault_arg, path_arg, f"content={body}"], runner=runner)
        print(f"  append {i}/{len(bodies)} ({len(body)} bytes)", file=sys.stderr)

    run_obsidian(["append", vault_arg, path_arg, "content=```"], runner=runner)
    run_obsidian(["append", vault_arg, path_arg, "content=%%"], runner=runner)
    print("  closing fence written", file=sys.stderr)

    if not verify:
        print("  (verify skipped)", file=sys.stderr)
        return len(doc["elements"])

    back = extract_json(run_obsidian(["read", vault_arg, path_arg], runner=runner))
    if len(back["elements"]) != len(doc["elements"]):
        raise VerifyError(
            f"verify: read-back has {len(back['elements'])} elements, expected "
            f"{len(doc['elements'])}. The note may have been OPEN in Obsidian (close "
            "it) or a chunk was dropped (lower --chunk-bytes)."
        )
    print(f"  verified: {len(back['elements'])} elements round-tripped", file=sys.stderr)
    return len(back["elements"])


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="write_to_vault.py",
        description="Write an .excalidraw diagram into an Obsidian vault via the CLI.",
    )
    parser.add_argument("--vault", required=True, help="vault name as shown by `obsidian vaults`")
    parser.add_argument("--path", required=True, help="target note path; coerced to .excalidraw.md")
    parser.add_argument("--input", help="diagram JSON file (default: stdin)")
    parser.add_argument("--chunk-bytes", type=int, default=CHUNK_BYTES_DEFAULT,
                        help=f"max append payload (default {CHUNK_BYTES_DEFAULT}; stay under ~12000)")
    parser.add_argument("--no-verify", action="store_true", help="skip the read-back validation")
    return parser.parse_args(argv)


def main(argv=None):
    opts = parse_args(argv)
    if opts.input:
        with open(opts.input, encoding="utf-8") as handle:
            raw = handle.read()
    else:
        raw = sys.stdin.read()
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"write-to-vault: input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(doc.get("elements"), list):
        print("write-to-vault: input JSON has no `elements` array.", file=sys.stderr)
        return 1

    path = coerce_path(opts.path)
    if not path.endswith(".excalidraw.md"):
        print(
            f'write-to-vault: warning — --path does not end in .excalidraw.md (got "{path}"); '
            "the embed may not resolve.",
            file=sys.stderr,
        )
    try:
        write_diagram(doc, opts.vault, path, opts.chunk_bytes, not opts.no_verify)
    except (EscapeError, VerifyError, ChunkTooLargeError, RuntimeError) as exc:
        print(f"write-to-vault: {exc}", file=sys.stderr)
        return 1
    print("write-to-vault: done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
