#!/usr/bin/env python3
"""Print the board ids the rendered overview shows, for the registry sync.

    python3 tools/sync.py page/overview.html

The sync job matches each board on the page back to its registry row by the
data-board-id attribute, so every board must carry one, exactly once. It exits 1
when an id is missing or repeated.
"""
import json
import os
import sys

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright  # noqa: E402


def main():
    page_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "page/overview.html")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + page_path)
        page.wait_for_load_state("load")
        shown = page.evaluate("[...document.querySelectorAll('[data-board-id]')].map(n => n.dataset.boardId)")
        registry = page.evaluate("(window.BOARD_DATA || {boards: []}).boards.map(b => b.id)")
        browser.close()
    missing = sorted(set(registry) - set(shown))
    repeated = sorted({i for i in shown if shown.count(i) > 1})
    print(json.dumps({"shown": shown, "missing": missing, "repeated": repeated}, indent=1))
    sys.exit(1 if missing or repeated else 0)


if __name__ == "__main__":
    main()
