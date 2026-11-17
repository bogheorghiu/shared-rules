#!/usr/bin/env python3
"""Screenshot the overview at desktop and phone width (first viewport only).

    python3 tools/shot.py shots/overview

serves the repo over HTTP and writes shots/overview-1280.png (1280x900) and
shots/overview-390.png (390x844), showing whatever data/boards.json holds.
"""
import functools
import http.server
import os
import sys
import threading

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES = [(1280, 900), (390, 844)]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    prefix = sys.argv[1]
    os.makedirs(os.path.dirname(os.path.abspath(prefix)), exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/overview/index.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(200)
            out = f"{prefix}-{width}.png"
            page.screenshot(path=out, full_page=False)
            page.close()
            print(out)
        browser.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
