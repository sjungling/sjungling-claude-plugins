import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "skills" / "obsidian-excalidraw" / "scripts"))


def by_type(doc, kind):
    """Elements of one type from a rendered Excalidraw document."""
    return [e for e in doc["elements"] if e["type"] == kind]
