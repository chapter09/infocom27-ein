# INFOCOM 2027 Workshop on Embodied Intelligence Networks

This repository contains the source code for the [INFOCOM 2027 Workshop on Embodied Intelligence Networks](https://infocom27-ein.netlify.app/) website. It is adapted from the [INFOCOM 2026 edition](https://github.com/baochunli/infocom26-ein).

## Scripts

The `scripts/` directory contains helper scripts for generating the downloadable workshop program files from the website content.

In this workflow, `program.html` is the canonical source of truth for the workshop program. The Word and PDF files are generated artifacts derived from the HTML content and the Word template.

> **Note:** `program.html` is currently a "coming soon" placeholder for EIN 2027. Fill in the 2027 schedule (sessions and papers) before running the script; it also still hard-codes the 2026 room name ("Fuyo"), which needs updating once the 2027 room is known.

### `scripts/generate-icons.py`

This script holds the EIN logo, a simple line-drawn robot face (rounded head, antenna, two dot eyes, a straight mouth, and small ears), and regenerates the logo and favicon set from it. Edit the `robot()` function to change the mark. It requires `rsvg-convert` (librsvg) and ImageMagick.

```bash
python3 scripts/generate-icons.py
```

It writes:

- `assets/icons/logo.svg`: the robot on a blue tile, used as the SVG favicon and in the site header
- `assets/icons/logo-full.svg`: the "EIN" wordmark beside the robot head, for slides and flyers
- `assets/icons/favicon-16x16.png` and `assets/icons/favicon-32x32.png`
- `assets/icons/safari-pinned-tab.svg`: a one-colour mask icon for Safari pinned tabs
- `favicon.ico` (16, 32, and 48 px) and `apple-touch-icon.png` (180 × 180, opaque) in the site root

### `scripts/generate-program.py`

This script rebuilds `ein27-program.docx` from:

- `program.html` for the title, description, room, session times, and paper list
- `committee.html` for the committee and chairs section
- `assets/files/workshop-program-template.docx` for the Word layout, paragraph formatting, and fonts

It writes:

- `assets/files/ein27-program.docx`

### Prerequisites

- `pandoc`
- `xelatex` if you also want to regenerate the PDF

### Generate the program in Microsoft Word format

From the repository root:

```bash
uv run scripts/generate-program.py
```

### Generate the program in PDF format

From the repository root:

```bash
uv run scripts/generate-program.py
pandoc assets/files/ein27-program.docx --pdf-engine=xelatex -V mainfont=Helvetica -o assets/files/ein27-program.pdf
```

### Typical workflow

1. Edit `program.html` if the schedule, room, or description changes.
2. Edit `committee.html` if the committee or chairs change.
3. Run the script to rebuild the `.docx`.
4. Run the `pandoc` command above to refresh the PDF.
5. Commit the updated HTML and generated files together.
