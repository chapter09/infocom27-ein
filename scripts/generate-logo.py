"""Regenerate the EIN 2027 logo.

The logo is a line-drawn palm tree whose crown holds a robot face and whose
right-hand fronds turn into a network of nodes, above the "EIN" wordmark,
Diamond Head, and a few waves, with "IEEE INFOCOM 2027" and "Embodied
Intelligence Networks" set on arcs below and "Honolulu, Hawaii" underneath.

All lettering is converted to outlines, so the SVGs render the same everywhere
without web fonts. The typeface is Montserrat (SIL Open Font License), which
this script downloads from the Montserrat project's GitHub release each run.

Requires fontTools (a project dependency). Run from the repository root:

    uv run scripts/generate-logo.py
"""

import math
import tempfile
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
FONT_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/v7.222/fonts/ttf/Montserrat-{}.ttf"

# Colours for light backgrounds, and their counterparts for the dark theme.
LIGHT = {"teal": "#529DA3", "navy": "#19345B", "orange": "#F28E5D"}
DARK = {"teal": "#6CB8BE", "navy": "#E2E8F0", "orange": "#F49B6E"}

# The artwork is drawn on a 2528 x 1696 canvas (the size of the original
# design sketch); this window crops it to the logo with a small margin.
VIEW_X, VIEW_Y, VIEW_W, VIEW_H = 831.5, 359.5, 860, 1100
CROWN = (1250, 603)


# Type


class Font:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm

    def advance(self, ch, size):
        return self.font["hmtx"][self.cmap[ord(ch)]][0] * size / self.upm

    def path(self, ch, size, transform):
        """Outline of one glyph; `transform` maps a y-down em box to the page."""
        s = size / self.upm
        a, b, c, d, e, f = transform
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        # Font units are y-up, so flip y before applying the page transform.
        self.glyphs[self.cmap[ord(ch)]].draw(TransformPen(pen, (a * s, b * s, -c * s, -d * s, e, f)))
        return pen.getCommands()


def text_line(font, text, size, x_center, baseline, tracking=0.0):
    widths = [font.advance(ch, size) for ch in text]
    x = x_center - (sum(widths) + tracking * (len(text) - 1)) / 2
    out = []
    for ch, w in zip(text, widths):
        if ch != " ":
            out.append(font.path(ch, size, (1, 0, 0, 1, x, baseline)))
        x += w + tracking
    return "".join(out)


def text_arc(font, text, size, cx, cy, r, span):
    """Text along the bottom of a circle, letters pointing at its centre.

    `r` is the baseline radius, and the letters are spaced to fill `span`
    degrees of the circle, measured at half the cap height.
    """
    r_mid = r - size * 0.35
    widths = [font.advance(ch, size) for ch in text]
    tracking = (r_mid * math.radians(span) - sum(widths)) / (len(text) - 1)
    s = -(sum(widths) + tracking * (len(text) - 1)) / 2
    out = []
    for ch, w in zip(text, widths):
        phi = (s + w / 2) / r_mid
        px, py = cx + r * math.sin(phi), cy + r * math.cos(phi)
        cos, sin = math.cos(phi), -math.sin(phi)
        if ch != " ":
            # Rotate by -phi about the glyph's baseline centre, placed at (px, py).
            e = px - cos * w / 2
            f = py - sin * w / 2
            out.append(font.path(ch, size, (cos, sin, -sin, cos, e, f)))
        s += w + tracking
    return "".join(out)


# Artwork


def poly(points):
    return "M" + " L".join(f"{x:g} {y:g}" for x, y in points)


def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(
        u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
        for a, b, c, d in zip(p0, p1, p2, p3)
    )


def palm():
    """Fronds and trunk as stroked paths, plus the network on the right fronds."""
    cx, cy = CROWN
    # Lower-right frond's serrated inner edge; the lower-left frond mirrors it.
    teeth = [
        CROWN, (1316, 665), (1335, 640), (1333, 684), (1353, 709), (1366, 667),
        (1366, 724), (1391, 751), (1405, 710), (1405, 768), (1446, 818),
    ]
    mirrored = [(2 * cx - x, y) for x, y in teeth]
    upper_right = (CROWN, (1255, 470), (1340, 405), (1473, 405))
    right = (CROWN, (1310, 500), (1500, 500), (1580, 642))
    curve = lambda pts: "M{:g} {:g} C{:g} {:g} {:g} {:g} {:g} {:g}".format(*sum(pts, ()))
    lines = [
        # Upper left: smooth top edge, serrated lower edge.
        f"M1032 394 C1160 375 1262 430 {cx} {cy}",
        poly([(1032, 394), (1087, 430), (1144, 427), (1103, 449), (1134, 473),
              (1192, 465), (1153, 489), (1179, 512), (1220, 506), (1195, 528), CROWN]),
        # Left.
        f"M{cx} {cy} C1180 520 1020 470 925 618",
        poly([(925, 618), (1000, 603), (1039, 553), (1022, 600), (1061, 596),
              (1106, 546), (1092, 596), (1128, 594), (1161, 556), (1153, 596), CROWN]),
        # Lower right and lower left.
        f"M{cx} {cy} C1380 600 1460 600 1446 818",
        poly(teeth),
        f"M{cx} {cy} C1120 600 1040 600 1054 818",
        poly(mirrored),
        # Upper right and right: plain outlines whose tips are network nodes.
        curve(upper_right),
        poly([CROWN, (1405, 453), (1473, 405)]),
        curve(right),
        f"M{cx} {cy} Q1350 593 1451 599",
        # Trunk; the left edge sweeps into the shoreline.
        f"M{cx} {cy} C1180 720 1132 860 1135 990 C1137 1070 1152 1110 1158 1140 "
        "C1164 1175 1142 1186 1110 1186 L1056 1186",
        f"M{cx} {cy} C1203 700 1180 800 1185 930 C1190 1060 1250 1192 1340 1207",
    ]
    nodes = {
        "n1": ((1473, 405), 17, "navy"),
        "n2": ((1405, 453), 15, "navy"),
        "o1": ((1479, 488), 12, "orange"),
        "n3": ((1573, 511), 14, "navy"),
        "n4": (cubic(*right, 0.5), 17, "navy"),
        "n5": (cubic(*right, 0.76), 14, "navy"),
        "o2": ((1388, 597), 12, "orange"),
        "o3": ((1451, 599), 18, "orange"),
        "n6": ((1580, 642), 16, "navy"),
        "o4": ((1488, 707), 12, "orange"),
    }
    links = [("n2", "o1"), ("o1", "n3"), ("o1", "n5"), ("n3", "n5"), ("n4", "o3"),
             ("o3", "n5"), ("o3", "n6"), ("n5", "o4")]
    return lines, nodes, links


def waves():
    """Three breaking waves; each crest curls over into a short lip."""
    d = "M961 1159 C975 1159 991 1137 1003 1137 "
    for c in (1003, 1051, 1099):
        d += f"C{c + 5} 1136 {c + 9} 1137 {c + 10} 1139 "  # lip
        d += f"M{c} 1137 C{c - 7} 1141 {c - 6} 1161 {c + 14} 1161 "  # back of the wave
        if c < 1099:
            d += f"C{c + 30} 1161 {c + 36} 1137 {c + 48} 1137 "
    return d + "L1158 1161"


def diamond_head():
    return [
        "M1230 1110 C1250 1094 1265 1088 1290 1086 C1320 1084 1348 1084 1368 1072 "
        "C1384 1062 1395 1058 1418 1058 C1436 1060 1446 1080 1462 1094 "
        "C1480 1108 1500 1110 1520 1123 C1545 1140 1565 1155 1596 1157",
        "M1262 1157 H1598",
        "M1307 1113 C1297 1134 1283 1148 1264 1157",
        "M1384 1064 C1379 1095 1368 1118 1350 1133",
        "M1410 1090 C1415 1115 1424 1138 1437 1155",
        "M1453 1107 C1468 1128 1485 1145 1505 1157",
    ]


def robot(color):
    """Robot face hanging below the crown: domed head, antenna, eyes, ears."""
    cx, top, bottom, half, rb = 1284.5, 706, 812, 54.5, 16
    head = (
        f"M{cx - half} {bottom - rb} V{top + half} A{half} {half} 0 0 1 {cx + half} {top + half} "
        f"V{bottom - rb} Q{cx + half} {bottom} {cx + half - rb} {bottom} "
        f"H{cx - half + rb} Q{cx - half} {bottom} {cx - half} {bottom - rb} Z"
    )
    return (
        f'<g fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{head}" stroke-width="10"/><path d="M{cx} 680V{top}" stroke-width="6"/></g>\n'
        f'<g fill="{color}"><circle cx="{cx}" cy="673" r="10"/>'
        f'<circle cx="{cx - 23.5}" cy="762" r="12"/><circle cx="{cx + 23.5}" cy="762" r="12"/>'
        f'<rect x="{cx - half - 17}" y="749" width="16" height="42" rx="6"/>'
        f'<rect x="{cx + half + 1}" y="749" width="16" height="42" rx="6"/></g>'
    )


def stroked(paths, color, width):
    return (
        f'<g fill="none" stroke="{color}" stroke-width="{width:g}" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        + "\n".join(f'<path d="{d}"/>' for d in paths)
        + "\n</g>"
    )


def logo(colors, lettering):
    lines, nodes, links = palm()
    edges = []
    for a, b in links:
        (x1, y1), _, _ = nodes[a]
        (x2, y2), _, _ = nodes[b]
        edges.append(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}")
    dots = "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colors[c]}"/>'
        for (x, y), r, c in nodes.values()
    )
    body = "\n".join([
        stroked(lines + [waves()], colors["teal"], 9.5),
        stroked(diamond_head(), colors["orange"], 9),
        stroked(edges, colors["teal"], 4.5),
        dots,
        robot(colors["teal"]),
        f'<path fill="{colors["navy"]}" d="{lettering}"/>',
    ])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W:g} {VIEW_H:g}" '
        'role="img" aria-label="EIN 2027, IEEE INFOCOM 2027 Workshop on Embodied Intelligence '
        'Networks, Honolulu, Hawaii">\n'
        f'<g transform="translate({-VIEW_X:g} {-VIEW_Y:g})">\n{body}\n</g>\n</svg>\n'
    )


def main():
    with tempfile.TemporaryDirectory() as tmp:
        fonts = {}
        for weight in ("Bold", "Light"):
            path = Path(tmp) / f"Montserrat-{weight}.ttf"
            urllib.request.urlretrieve(FONT_URL.format(weight), path)
            fonts[weight] = Font(path)
        bold, light = fonts["Bold"], fonts["Light"]

        # The two arcs share a centre below the palm crown.
        lettering = "".join([
            text_line(bold, "EIN", 230, 1415, 1013),
            text_arc(bold, "IEEE INFOCOM 2027", 40, 1262, 531, 767, span=33),
            text_arc(bold, "EMBODIED INTELLIGENCE NETWORKS", 40, 1262, 531, 823, span=59.5),
            text_line(light, "HONOLULU, HAWAII", 41, 1263, 1428, tracking=8),
        ])
    (IMAGES / "ein27-logo.svg").write_text(logo(LIGHT, lettering))
    (IMAGES / "ein27-logo-dark.svg").write_text(logo(DARK, lettering))
    print("Wrote assets/images/ein27-logo.svg and assets/images/ein27-logo-dark.svg")


if __name__ == "__main__":
    main()
