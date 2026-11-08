"""Regenerate the favicon set from the robot in the EIN 2027 logo.

The mark is the robot face that hangs in the palm crown of the workshop logo
(see scripts/generate-logo.py): a domed head, an antenna with an orange ball,
two dot eyes, and small ears, drawn in white on a teal tile. It is drawn on a
64 x 64 grid with 4-unit strokes, and its parts sit on multiples of 4 units, so
they land on whole pixels in the 16 px and 32 px favicons.

Requires rsvg-convert (librsvg) and ImageMagick: brew install librsvg imagemagick
Run from anywhere: python3 scripts/generate-icons.py
"""

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
TEAL = "#529DA3"  # the logo's line colour
ORANGE = "#F28E5D"  # the logo's accent colour


def robot(color, ball=None):
    """Robot face on the 64 x 64 grid, centred; `ball` colours the antenna tip."""
    head = "M14 48V40A18 18 0 0 1 50 40V48Q50 54 44 54H20Q14 54 14 48Z"
    return f"""<g fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="{head}"/>
<path d="M32 15V22"/>
</g>
<circle cx="32" cy="12" r="4" fill="{ball or color}"/>
<g fill="{color}">
<circle cx="24" cy="40" r="4"/>
<circle cx="40" cy="40" r="4"/>
<rect x="8" y="34" width="4" height="14" rx="2"/>
<rect x="52" y="34" width="4" height="14" rx="2"/>
</g>"""


def svg(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}">\n'
        f"{body}\n</svg>\n"
    )


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ICONS.mkdir(parents=True, exist_ok=True)

    # SVG favicon: white robot on a rounded teal tile.
    tile = f'<rect width="64" height="64" rx="14" fill="{TEAL}"/>'
    (ICONS / "logo.svg").write_text(svg(64, 64, f"{tile}\n{robot('#fff', ORANGE)}"))

    # Safari pinned-tab icon: solid black mark on transparent, 16 x 16 viewBox.
    (ICONS / "safari-pinned-tab.svg").write_text(
        svg(16, 16, f'<g transform="scale(0.25)">\n{robot("#000")}\n</g>')
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Apple touch icon: full-bleed opaque square; iOS applies its own corner mask.
        touch_svg = tmp / "touch.svg"
        touch_svg.write_text(
            svg(64, 64, f'<rect width="64" height="64" fill="{TEAL}"/>\n{robot("#fff", ORANGE)}')
        )
        run("rsvg-convert", "-w", 180, "-h", 180, touch_svg, "-o", tmp / "touch.png")
        run(
            "magick", tmp / "touch.png", "-background", TEAL, "-flatten", "-alpha", "off",
            f"PNG24:{ROOT / 'apple-touch-icon.png'}",
        )

        for size in (16, 32, 48):
            out = ICONS / f"favicon-{size}x{size}.png" if size < 48 else tmp / "favicon-48.png"
            run("rsvg-convert", "-w", size, "-h", size, ICONS / "logo.svg", "-o", out)
        run(
            "magick", ICONS / "favicon-16x16.png", ICONS / "favicon-32x32.png",
            tmp / "favicon-48.png", ROOT / "favicon.ico",
        )

    print("Wrote assets/icons/{logo,safari-pinned-tab}.svg, "
          "assets/icons/favicon-{16x16,32x32}.png, favicon.ico, apple-touch-icon.png")


if __name__ == "__main__":
    main()
