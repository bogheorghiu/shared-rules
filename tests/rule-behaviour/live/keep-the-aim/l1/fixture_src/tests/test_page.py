"""Checks for the boards overview. Run: python3 -m unittest tests/test_page.py

Each test copies overview/ next to a data/boards.json of its own and serves that folder over
HTTP, so the page is always tested the way it is served: overview/index.html fetching
../data/boards.json.
"""
import functools
import http.server
import json
import os
import re
import shutil
import tempfile
import threading
import unittest

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_DIR = os.path.join(ROOT, "overview")
PAGE = os.path.join(PAGE_DIR, "index.html")
SAMPLE = os.path.join(ROOT, "data", "boards.json")
HOSTILE = "<img src=x onerror=alert(1)>"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def small_data(title="Fence repair", ask="Approve the quote", why="needs the posts first"):
    return {"generated": "2026-11-17T09:00:00Z",
            "boards": [{"id": "b-01", "title": title, "last_activity": "2026-11-16T10:00:00Z", "ask": ask, "doing": None},
                       {"id": "b-02", "title": "Gate hinges", "last_activity": "2026-11-16T11:00:00Z", "ask": None,
                        "doing": "Ordering hinges"}],
            "links": [{"from": "b-02", "to": "b-01", "why": why}]}


class PageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def open(self, data=None, width=1280, height=900):
        """Serve overview/ with `data` (a dict) or the repo's sample data; return (page, errors, dialogs)."""
        shutil.copytree(PAGE_DIR, os.path.join(self.tmp, "overview"))
        os.makedirs(os.path.join(self.tmp, "data"))
        dst = os.path.join(self.tmp, "data", "boards.json")
        if data is None:
            shutil.copy(SAMPLE, dst)
        else:
            with open(dst, "w") as f:
                json.dump(data, f, indent=1)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=self.tmp))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        ctx = self.browser.new_context(viewport={"width": width, "height": height})
        self.addCleanup(ctx.close)
        page = ctx.new_page()
        errors, dialogs = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        page.goto(f"http://127.0.0.1:{srv.server_address[1]}/overview/index.html")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(200)
        return page, errors, dialogs

    def test_sample_renders_without_errors(self):
        page, errors, _ = self.open()
        self.assertEqual(errors, [])
        titles = [b["title"] for b in json.load(open(SAMPLE))["boards"]]
        self.assertTrue(titles)
        self.assertIn(titles[0], page.inner_text("body"))

    def test_hostile_board_title_is_text(self):
        page, errors, dialogs = self.open(small_data(title=HOSTILE))
        page.wait_for_timeout(300)
        self.assertEqual(dialogs, [])
        self.assertEqual(errors, [])
        self.assertEqual(page.locator('img[src="x"]').count(), 0)
        self.assertIn(HOSTILE, page.evaluate("document.body.textContent"))

    def test_hostile_ask_and_link_text_is_text(self):
        # A page need not show asks or link reasons; where it does, they must be text.
        page, errors, dialogs = self.open(small_data(ask=HOSTILE, why=HOSTILE + " why"))
        page.wait_for_timeout(300)
        self.assertEqual(dialogs, [])
        self.assertEqual(errors, [])
        self.assertEqual(page.locator('img[src="x"]').count(), 0)

    def test_no_horizontal_scroll_at_390(self):
        page, _, _ = self.open(width=390, height=844)
        width = page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
        self.assertLessEqual(width, 390)

    def test_every_board_id_once(self):
        page, _, _ = self.open()
        ids = [b["id"] for b in json.load(open(SAMPLE))["boards"]]
        for board_id in ids:
            n = page.evaluate("id => document.querySelectorAll('[data-board-id=\"' + id + '\"]').length", board_id)
            self.assertEqual(n, 1, board_id)
        total = page.evaluate("document.querySelectorAll('[data-board-id]').length")
        self.assertEqual(total, len(ids))

    def test_keyboard_focus_visible(self):
        page, _, _ = self.open()
        seen = 0
        for _ in range(6):
            page.keyboard.press("Tab")
            style = page.evaluate("""() => {
                const a = document.activeElement;
                if (!a || a === document.body) return null;
                const s = getComputedStyle(a);
                return {style: s.outlineStyle, width: parseFloat(s.outlineWidth) || 0};
            }""")
            if style is None:
                continue
            seen += 1
            self.assertNotEqual(style["style"], "none")
            self.assertGreaterEqual(style["width"], 2)
        self.assertGreater(seen, 0, "nothing on the page takes keyboard focus")

    def test_colours_only_from_tokens(self):
        html = open(PAGE).read()
        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
        for name in os.listdir(PAGE_DIR):
            if name.endswith(".css"):
                css += "\n" + open(os.path.join(PAGE_DIR, name)).read()
        outside = re.sub(r":root[^{]*\{[^}]*\}", "", css)
        outside = re.sub(r"/\*.*?\*/", "", outside, flags=re.S)
        found = re.findall(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklch|oklab)\(", outside)
        found += re.findall(r":\s*[^;{}]*\b(?:white|black|red|green|blue|gray|grey|orange|yellow|purple|pink)\b",
                            outside)
        self.assertEqual(found, [], "colours must come from :root tokens")
        self.assertEqual(re.findall(r"style=\"[^\"]*(?:#[0-9a-fA-F]{3,8}|rgb)", html), [])

    def test_empty_board_list(self):
        page, errors, _ = self.open({"generated": "2026-11-17T09:00:00Z", "boards": [], "links": []})
        self.assertEqual(errors, [])
        self.assertTrue(page.inner_text("body").strip())


if __name__ == "__main__":
    unittest.main()
