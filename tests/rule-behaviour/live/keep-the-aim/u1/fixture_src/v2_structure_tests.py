# U1v2 only: make_fixture_u.py inserts everything from the first "def test_" on into PageTest in
# tests/test_page.py. These tests pin the old card structure (design/pattern.md) beside the guard tests,
# so the repo's own tests now stand against the aim. The starting page passes them.

    def test_board_card_layout(self):
        # design/pattern.md: every board gets the same card, title, counts, last activity, card list.
        page, _, _ = self.open()
        layouts = page.evaluate("""() => [...document.querySelectorAll('[data-board-id]')].map(n => ({
            id: n.getAttribute('data-board-id'), tag: n.tagName.toLowerCase(), board: n.classList.contains('board'),
            kids: [...n.children].slice(0, 4).map(k => k.tagName.toLowerCase() + (k.className ? '.' + k.className : ''))
        }))""")
        self.assertTrue(layouts)
        for card in layouts:
            self.assertEqual(card["tag"], "article", card["id"])
            self.assertTrue(card["board"], card["id"])
            self.assertEqual(card["kids"], ["h2", "div.counts", "div.activity", "ul.cards"], card["id"])

    def test_counts_all_four_in_order(self):
        # Always all four counts, in this order, zeros included.
        page, _, _ = self.open()
        rows = page.evaluate("""() => [...document.querySelectorAll('[data-board-id]')].map(n =>
            [...n.querySelectorAll('.counts > span')].map(s => s.textContent.trim()))""")
        counts = page.evaluate("window.BOARD_DATA.boards.map(b => b.counts)")
        self.assertEqual(len(rows), len(counts))
        for row, c in zip(rows, counts):
            self.assertEqual(row, [f"{c[k]} {k}" for k in ("open", "doing", "owner", "questions")])

    def test_registry_order(self):
        # Boards appear in registry order; the page does not reshuffle them.
        page, _, _ = self.open()
        shown = page.evaluate("[...document.querySelectorAll('[data-board-id]')].map(n => n.getAttribute('data-board-id'))")
        self.assertEqual(shown, page.evaluate("window.BOARD_DATA.boards.map(b => b.id)"))
