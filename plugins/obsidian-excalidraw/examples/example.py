#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["excaligen==0.11.14"]
# ///
"""Reference shape for a generated diagram script. Pipe stdout to a .excalidraw file."""
import pathlib
import sys

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parent.parent / "skills" / "obsidian-excalidraw" / "scripts"),
)

from obsidian_preset import new_scene, styled

scene = new_scene()

user = styled(scene.ellipse("User").center(0, 0), "active")
api = styled(scene.rectangle("API Gateway").center(340, 0), "active")
db = styled(scene.rectangle("Postgres").center(680, 0), "active")
legacy = styled(scene.rectangle("Legacy Sync").center(340, 220), "lapsed")

scene.arrow("request").bind(user, api)
scene.arrow("query").bind(api, db)
styled(scene.arrow("retired").bind(api, legacy), "removed")

scene.text("Service overview").center(340, -170)

print(scene.json())
