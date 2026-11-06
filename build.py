#!/usr/bin/env python3
"""Generate index.html from template.html, data/countries.geojson and <data dir>/notes/*.md.

Usage: build.py [DATA_DIR]

DATA_DIR holds your own notes/ folder and receives the generated index.html.
It defaults to the repository root (which contains the example notes).
"""
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
GEO_FILE = ROOT / "data" / "countries.geojson"
TEMPLATE = ROOT / "template.html"


def js_json(obj) -> str:
    """JSON that is safe to embed inside a <script> tag."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def main() -> int:
    if len(sys.argv) > 2:
        print("Usage: build.py [DATA_DIR]", file=sys.stderr)
        return 2
    data_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ROOT
    notes_dir = data_dir / "notes"
    output = data_dir / "index.html"

    if not notes_dir.is_dir():
        print(f"Error: notes folder not found: {notes_dir}\n"
              f"Create it and add notes/<CODE>.md files (see README).", file=sys.stderr)
        return 1

    geo = json.loads(GEO_FILE.read_text(encoding="utf-8"))
    ids = {f["properties"]["id"] for f in geo["features"]}

    notes = {}
    unknown = []
    for md_file in sorted(notes_dir.glob("*.md")):
        code = md_file.stem.upper()
        text = md_file.read_text(encoding="utf-8")
        html = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
        if code not in ids:
            unknown.append(md_file.name)
            continue
        notes[code] = html

    template = TEMPLATE.read_text(encoding="utf-8")
    page = template.replace("__GEO__", js_json(geo)).replace("__NOTES__", js_json(notes))
    if re.search(r"__(GEO|NOTES)__", page):
        print("Error: placeholders were not replaced", file=sys.stderr)
        return 1
    output.write_text(page, encoding="utf-8")

    print(f"Countries: {len(geo['features'])} | Notes found: {len(notes)} -> {output.name} "
          f"({output.stat().st_size // 1024} KB)")
    if notes:
        print("Visited:", ", ".join(sorted(notes)))
    for name in unknown:
        print(f"Warning: notes/{name} does not match any known country code (skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
