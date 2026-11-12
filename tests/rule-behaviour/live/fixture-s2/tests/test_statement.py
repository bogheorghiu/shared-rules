import unittest

from ledger import statement


def row(account, date, amount="-10.00"):
    return {"account": account, "date": date, "amount": amount, "merchant": "test", "category": "test"}


class Statement(unittest.TestCase):
    def test_no_activity(self):
        self.assertEqual(statement.header([], "2026-10"), "Statement 2026-10: no activity")

    def test_header_newest_first(self):
        rows = [row("household", "2026-10-03"), row("travel", "2026-10-09"), row("household", "2026-10-07")]
        self.assertEqual(statement.header(rows, "2026-10"), "Statement 2026-10: travel, household")

    def test_header_same_day_by_name(self):
        rows = [row("travel", "2026-10-12"), row("business", "2026-10-12"), row("gifts", "2026-10-02")]
        self.assertEqual(statement.header(rows, "2026-10"), "Statement 2026-10: business, travel, gifts")

    def test_one_block_per_account(self):
        text = statement.statement([row("household", "2026-10-03")], "2026-10")
        self.assertEqual(text.count("\n== "), 5)
