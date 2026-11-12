import logging
import os
import unittest

from ledger import report, sync

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "transactions.csv")


def row(account, amount):
    return {"account": account, "amount": amount, "merchant": "test", "category": "test"}


class Sync(unittest.TestCase):
    def test_full_feed_balances(self):
        rows = report.load(DATA)
        totals = sync.balances(rows)
        self.assertEqual(set(totals), {"household", "travel", "savings", "business", "gifts"})

    def test_display_order(self):
        rows = [row("savings", "900.00"), row("business", "250.00"), row("travel", "250.00"),
                row("household", "100.00"), row("gifts", "10.00")]
        names = [name for name, _ in sync.display_order(rows)]
        self.assertEqual(names, ["savings", "business", "travel", "household", "gifts"])
