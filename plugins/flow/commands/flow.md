---
description: Start (or stop) an interactive flow/diagram viewer backed by a local JSON file
argument-hint: "[name|stop] [--port N]"
allowed-tools:
  - Bash
  - Read
  - Write
---

# /flow

Spin up a local React Flow viewer so the user can see — and interactively edit — a diagram described as JSON in `.claude/diagrams/<name>.json`. The LLM and the browser share the file: you write JSON, the user drags / edits nodes in the browser, and the file updates so you can read their changes on the next turn.

## Arguments

`$ARGUMENTS` — one of:
- _(empty)_ or `<name>` → start the server for diagram `<name>` (default: `diagram`).
- `stop` → shut down the running server.
- Append `--port N` to override the default port `4173`.

## Behavior

### Starting

1. Parse `$ARGUMENTS` → diagram `<name>` (default `diagram`), optional `--port <N>` (default `4173`).
2. Project root: `git rev-parse --show-toplevel` (fall back to cwd if not a git repo).
3. If `.claude/diagrams/.server.pid` exists and that PID is alive (`kill -0 <pid>`), tell the user the server is already running and print the URL. Do not start a second one. If the PID is stale, delete the file.
4. Use the **Write** tool to ensure `.claude/diagrams/<name>.json` exists. If missing, seed it with `{"nodes": [], "edges": []}`. If the user described a diagram in this conversation, write an initial graph (nodes + edges) to that file **before** launching so the viewer opens populated.
5. Launch the server in the background via Bash:
   ```bash
   FLOW_PORT=<port> FLOW_PROJECT_ROOT=<project-root> FLOW_DIAGRAM=<name> \
     nohup node "${CLAUDE_PLUGIN_ROOT}/server/server.mjs" \
     > .claude/diagrams/.server.log 2>&1 &
   disown
   ```
6. Print the URL (`http://localhost:<port>`) and the diagram file path. Tell the user: "Say _done_ (or run `/flow:flow stop`) when you're finished and I'll tear it down."

### Stopping

1. Read PID from `.claude/diagrams/.server.pid`.
2. Send SIGTERM — the server traps it and exits cleanly:
   ```bash
   kill "$(cat .claude/diagrams/.server.pid)" 2>/dev/null || true
   rm -f .claude/diagrams/.server.pid
   ```
3. Confirm shutdown to the user.

## Graph JSON shape

Native React Flow. Nodes default to a custom `editable` type if `type` is omitted:

```json
{
  "nodes": [
    { "id": "a", "data": { "label": "Start" }, "position": { "x": 0, "y": 0 } },
    { "id": "b", "data": { "label": "Decide" } }
  ],
  "edges": [
    { "id": "a-b", "source": "a", "target": "b", "label": "go" }
  ]
}
```

- `position` is optional — the viewer auto-lays out missing nodes with dagre.
- Edge `id` must be unique. Convention: `<source>-<target>`.
- To reflect user edits in subsequent turns, **re-read** the JSON file before writing new versions.

## Viewer UX

- Dagre DAG layout with direction picker (LR / TB / RL / BT) and a `relayout` button.
- Double-click a node to rename; Backspace / Delete removes selected nodes or edges.
- Connection handles are visible on both sides of each node; drag from one to another to connect.
- Changes are debounced and PUT to the server within ~300ms.
- Server watches the JSON file with `fs.watch` and pushes SSE updates so LLM-initiated writes are reflected live.

## Notes

- Dependencies (React, React Flow, dagre) load from `esm.sh` at runtime — no install step.
- The command uses `Bash` (node, kill, mkdir, git) and `Write` (JSON seeding). No `curl` required.
