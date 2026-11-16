#!/usr/bin/env python3
"""Screenshot a page at desktop and phone width (first viewport only).

    python3 tools/shot.py page/overview.html shots/overview

writes shots/overview-1280.png (1280x800) and shots/overview-390.png (390x844).
The page loads ../data/boards.js as usual, so this shows whatever data is there.
"""
import os
import sys

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright  # noqa: E402

SIZES = [(1280, 800), (390, 844)]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    page_path, prefix = os.path.abspath(sys.argv[1]), sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(prefix)), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto("file://" + page_path)
            page.wait_for_load_state("load")
            page.wait_for_timeout(200)
            out = f"{prefix}-{width}.png"
            page.screenshot(path=out, full_page=False)
            page.close()
            print(out)
        browser.close()


if __name__ == "__main__":
    main()
