# World Travels

A static HTML page with a **rotating globe** and a **flat world map**. Drag to rotate (or pan), scroll to zoom, and click a country to see its name, flag, links to Wikipedia and Google Maps, and your own notes.

**Visited** countries (the ones that have a notes file) are highlighted with full colour, a gradient, a darker border and a 📍 pin; all other countries are light grey. The list of visited countries is in the bottom-left corner: click a name to centre the map on that country and open its popup.

The 🗺️/🌍 button in the bottom-right corner switches between the globe and the flat map, and the browser remembers your choice. You can also force a view from the URL with `index.html?view=globe` or `index.html?view=flat`.

## Requirements

Only **Docker**. Python and its dependencies run inside a container (`python:3.12-slim`).

## Usage

```bash
./build.sh        # regenerates index.html
```

Then open `index.html` in your browser (a double click is enough, no server needed) and reload the page after each rebuild.

## Adding notes to a country

1. Create `notes/<CODE>.md`, where `<CODE>` is the country's two-letter ISO code (e.g. `notes/IT.md`, `notes/FR.md`, `notes/JP.md`). A country's code is shown in its popup while it has no notes yet.
2. Write in Markdown (headings, lists, quotes, tables, images...).
3. For images, copy them into `notes/images/` and reference them with a relative path:
   ```markdown
   ![Colosseum](notes/images/colosseum.jpg)
   ```
   The image line must not be inside a code block (```` ``` ````), or it is shown as plain text.
4. Run `./build.sh` and reload the page.

You can link directly to a country with `index.html#IT` (on the globe, the country is brought to the centre).

## When to rebuild

Run `./build.sh` only when the content embedded in `index.html` changes:

- **Run it** when you add, edit or delete a note (`notes/XX.md`). Note text is copied into `index.html`, so without a rebuild the page keeps showing the old version.
- **Run it** after changing `template.html` or `data/countries.geojson` (rarely needed).
- **No rebuild for images.** `index.html` only stores the image path (e.g. `notes/images/IT_01.jpg`), and the browser loads the file every time the page opens.
  - Replacing an image with one of the same name: just reload the page (use Ctrl+F5 if the browser still shows the cached version).
  - Adding a new image: you need a rebuild anyway, but only because of the new `![...](...)` line in the `.md` file.
- Changes to `Dockerfile` or `requirements.txt` need no extra step: `build.sh` rebuilds the Docker image on every run, and this is quick when nothing has changed.

## Project layout

| File | Purpose |
| --- | --- |
| `build.sh` | Builds the Docker image and runs `build.py` inside it |
| `build.py` | Converts the Markdown notes and generates `index.html` |
| `template.html` | Page source (CSS + JS) |
| `data/countries.geojson` | Country borders (Natural Earth 1:50m, public domain) |
| `notes/` | One Markdown note per country, images in `notes/images/` |
| `index.html` | Generated page (do not edit by hand) |

## Technical notes

- The map is drawn with [D3](https://d3js.org/) (loaded from cdnjs) and flags come from [flagcdn.com](https://flagcdn.com), so an internet connection is needed to see them.
- Country colours follow Natural Earth's `MAPCOLOR7` property, which is designed so that neighbouring countries never share a colour.
- Large images make the page heavier to load: resizing photos (e.g. to 1600 px wide) before adding them is recommended.
