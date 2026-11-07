"""Regenerate the EIN logo and favicon set.

The mark is a simple line-drawn robot face: a rounded head outline with an
antenna, two dot eyes, a straight mouth, and small ears. It is drawn on a
64 x 64 grid with 4-unit strokes, and the head, eyes, mouth, and ears sit on
multiples of 4 units, so they land on whole pixels in the 16 px and 32 px
favicons.

Requires rsvg-convert (librsvg) and ImageMagick: brew install librsvg imagemagick
Run from anywhere: python3 scripts/generate-icons.py
"""

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
BLUE = "#2563eb"


def robot(color, stroke=4):
    """Robot face on the 64 x 64 grid, centred horizontally."""
    return f"""<g fill="none" stroke="{color}" stroke-width="{stroke:g}" stroke-linecap="round" stroke-linejoin="round">
<rect x="14" y="22" width="36" height="32" rx="8"/>
<path d="M32 16V22"/>
<path d="M26 46H38"/>
</g>
<g fill="{color}">
<circle cx="32" cy="12" r="4"/>
<circle cx="24" cy="32" r="4"/>
<circle cx="40" cy="32" r="4"/>
<rect x="8" y="32" width="4" height="12" rx="2"/>
<rect x="52" y="32" width="4" height="12" rx="2"/>
</g>"""


def wordmark(x0, y0, height, stroke):
    """Condensed geometric 'EIN' built from rectangles and one diagonal."""
    h, w = height, stroke
    e_w, n_w, space = 0.56 * h, 0.66 * h, 0.17 * h
    arm = (h - w) / 2
    shapes = [
        # E
        f'<rect x="{x0:g}" y="{y0:g}" width="{w:g}" height="{h:g}"/>',
        f'<rect x="{x0:g}" y="{y0:g}" width="{e_w:g}" height="{w:g}"/>',
        f'<rect x="{x0:g}" y="{y0 + arm:g}" width="{e_w * 0.9:g}" height="{w:g}"/>',
        f'<rect x="{x0:g}" y="{y0 + h - w:g}" width="{e_w:g}" height="{w:g}"/>',
    ]
    xi = x0 + e_w + space
    shapes.append(f'<rect x="{xi:g}" y="{y0:g}" width="{w:g}" height="{h:g}"/>')  # I
    xn = xi + w + space
    shapes += [  # N
        f'<rect x="{xn:g}" y="{y0:g}" width="{w:g}" height="{h:g}"/>',
        f'<rect x="{xn + n_w - w:g}" y="{y0:g}" width="{w:g}" height="{h:g}"/>',
        f'<polygon points="{xn:g},{y0:g} {xn + w:g},{y0:g} '
        f'{xn + n_w:g},{y0 + h:g} {xn + n_w - w:g},{y0 + h:g}"/>',
    ]
    return "\n".join(shapes), xn + n_w


def svg(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}">\n'
        f"{body}\n</svg>\n"
    )


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ICONS.mkdir(parents=True, exist_ok=True)

    # Icon: white robot on a rounded blue tile (header logo and SVG favicon).
    tile = f'<rect width="64" height="64" rx="14" fill="{BLUE}"/>'
    (ICONS / "logo.svg").write_text(svg(64, 64, f"{tile}\n{robot('#fff')}"))

    # Full logo: 'EIN' wordmark beside the robot, blue on transparent. The letters
    # span the robot's head (y 20-56 on its grid) and the robot gets a heavier
    # stroke to balance the bold letters.
    letters, letters_end = wordmark(0, 20, 36, 8.4)
    robot_x = letters_end + 2
    (ICONS / "logo-full.svg").write_text(
        svg(
            robot_x + 58,
            60,
            f'<g fill="{BLUE}">\n{letters}\n</g>\n'
            f'<g transform="translate({robot_x - 6:g} 0)">\n{robot(BLUE, stroke=5)}\n</g>',
        )
    )

    # Safari pinned-tab icon: solid black mark on transparent, 16 x 16 viewBox.
    (ICONS / "safari-pinned-tab.svg").write_text(
        svg(16, 16, f'<g transform="scale(0.25)">\n{robot("#000")}\n</g>')
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Apple touch icon: full-bleed opaque square; iOS applies its own corner mask.
        touch_svg = tmp / "touch.svg"
        touch_svg.write_text(
            svg(64, 64, f'<rect width="64" height="64" fill="{BLUE}"/>\n{robot("#fff")}')
        )
        run("rsvg-convert", "-w", 180, "-h", 180, touch_svg, "-o", tmp / "touch.png")
        run(
            "magick", tmp / "touch.png", "-background", BLUE, "-flatten", "-alpha", "off",
            f"PNG24:{ROOT / 'apple-touch-icon.png'}",
        )

        for size in (16, 32, 48):
            out = ICONS / f"favicon-{size}x{size}.png" if size < 48 else tmp / "favicon-48.png"
            run("rsvg-convert", "-w", size, "-h", size, ICONS / "logo.svg", "-o", out)
        run(
            "magick", ICONS / "favicon-16x16.png", ICONS / "favicon-32x32.png",
            tmp / "favicon-48.png", ROOT / "favicon.ico",
        )

    print("Wrote assets/icons/{logo,logo-full,safari-pinned-tab}.svg, "
          "assets/icons/favicon-{16x16,32x32}.png, favicon.ico, apple-touch-icon.png")


if __name__ == "__main__":
    main()
