import unittest

from ledger import rebalance


def row(account, amount):
    return {"account": account, "amount": amount, "merchant": "test", "category": "test", "date": "2026-11-01"}


class Rebalance(unittest.TestCase):
    def test_nothing_over(self):
        self.assertEqual(rebalance.describe([row("household", "-10.00")]), "No transfer needed.")

    def test_from_most_headroom(self):
        rows = [row("travel", "-3100.00"), row("household", "-1000.00"), row("business", "-9000.00")]
        self.assertEqual(rebalance.suggest(rows), ("household", "travel", 10000))

    def test_same_headroom_by_name(self):
        # household and travel both have 2,000.00 left; gifts is 50.00 over.
        rows = [row("gifts", "-1050.00"), row("household", "-3000.00"), row("travel", "-1000.00"),
                row("business", "-9500.00")]
        self.assertEqual(rebalance.suggest(rows), ("household", "gifts", 5000))
