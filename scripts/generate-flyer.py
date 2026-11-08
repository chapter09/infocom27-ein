"""Print the EIN 2027 "At a Glance" flyer to PDF with headless Chrome.

The flyer's source is scripts/flyer/ein27-flyer.html (one US Letter page). Its
web fonts load from Google Fonts, so this needs network access, plus Google
Chrome or Chromium. Run from anywhere: python3 scripts/generate-flyer.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "flyer" / "ein27-flyer.html"
OUTPUT = ROOT / "assets" / "images" / "ein27-flyer.pdf"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        path = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if path:
            return path
    sys.exit("Google Chrome or Chromium is required to print the flyer.")


def main():
    subprocess.run(
        [
            find_chrome(),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=10000",  # let the web fonts and images load
            # A generic user agent makes Google Fonts serve static TrueType files,
            # which Chrome embeds as real fonts rather than Type 3 outlines.
            "--user-agent=Mozilla/5.0",
            f"--print-to-pdf={OUTPUT}",
            SOURCE.as_uri(),
        ],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    pages = len(re.findall(rb"/Type\s*/Page\b", OUTPUT.read_bytes()))
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({pages} page{'s' if pages != 1 else ''})")
    if pages != 1:
        sys.exit("The flyer no longer fits on one page; shorten the text in the HTML.")


if __name__ == "__main__":
    main()
