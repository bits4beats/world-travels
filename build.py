#!/usr/bin/env python3
"""Generate notes/index.html from template.html, data/countries.geojson and <data dir>/notes/*.md.

Usage: build.py [DATA_DIR]

DATA_DIR holds your own notes/ folder; the generated index.html is written inside it,
next to the .md files, so image paths (images/foo.jpg) are valid both in Markdown
editors and in the page.
It defaults to the repository root (which contains the example notes).
"""
import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import markdown

ROOT = Path(__file__).resolve().parent
GEO_FILE = ROOT / "data" / "countries.geojson"
TEMPLATE = ROOT / "template.html"
FAVICON = ROOT / "favicon.png"


def js_json(obj) -> str:
    """JSON that is safe to embed inside a <script> tag."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


IMG_SRC = re.compile(r'<img[^>]*?\ssrc="([^"]*)"')


def missing_images(html: str, notes_dir: Path) -> list:
    """Local image sources used in html that do not exist relative to notes_dir."""
    missing = []
    for src in IMG_SRC.findall(html):
        if re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|/|#)", src):
            continue
        if not (notes_dir / unquote(src)).is_file():
            missing.append(src)
    return missing


def main() -> int:
    if len(sys.argv) > 2:
        print("Usage: build.py [DATA_DIR]", file=sys.stderr)
        return 2
    data_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ROOT
    notes_dir = data_dir / "notes"
    output = notes_dir / "index.html"

    if not notes_dir.is_dir():
        print(f"Error: notes folder not found: {notes_dir}\n"
              f"Create it and add notes/<CODE>.md files (see README).", file=sys.stderr)
        return 1

    geo = json.loads(GEO_FILE.read_text(encoding="utf-8"))
    ids = {f["properties"]["id"] for f in geo["features"]}

    notes = {}
    unknown = []
    image_warnings = []
    for md_file in sorted(notes_dir.glob("*.md")):
        code = md_file.stem.upper()
        text = md_file.read_text(encoding="utf-8")
        html = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
        if code not in ids:
            unknown.append(md_file.name)
            continue
        notes[code] = html
        for src in missing_images(html, notes_dir):
            image_warnings.append(f"notes/{md_file.name}: image not found: {src}")

    template = TEMPLATE.read_text(encoding="utf-8")
    favicon = "data:image/png;base64," + base64.b64encode(FAVICON.read_bytes()).decode("ascii")
    page = (template.replace("__GEO__", js_json(geo))
                    .replace("__NOTES__", js_json(notes))
                    .replace("__FAVICON__", favicon))
    if re.search(r"__(GEO|NOTES|FAVICON)__", page):
        print("Error: placeholders were not replaced", file=sys.stderr)
        return 1
    output.write_text(page, encoding="utf-8")

    print(f"Countries: {len(geo['features'])} | Notes found: {len(notes)} -> {output.relative_to(data_dir)} "
          f"({output.stat().st_size // 1024} KB)")
    if notes:
        print("Visited:", ", ".join(sorted(notes)))
    for name in unknown:
        print(f"Warning: notes/{name} does not match any known country code (skipped)")
    for w in image_warnings:
        print(f"Warning: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
