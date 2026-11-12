import unittest

from ledger import limits


def row(account, amount):
    return {"account": account, "amount": amount, "merchant": "test", "category": "test", "date": "2026-11-01"}


class Limits(unittest.TestCase):
    def test_within_limits(self):
        rows = [row("household", "-100.00"), row("travel", "-50.00")]
        self.assertIsNone(limits.worst_offender(rows))
        self.assertEqual(limits.alert_line(rows), "")

    def test_worst_offender(self):
        rows = [row("household", "-5100.00"), row("travel", "-3020.00")]
        self.assertEqual(limits.worst_offender(rows), "household")

    def test_worst_offender_tie_named_by_name(self):
        # gifts (limit 1,000.00) and household (limit 5,000.00) are both 200.00 over.
        rows = [row("gifts", "-1200.00"), row("household", "-5200.00")]
        self.assertEqual(limits.worst_offender(rows), "gifts")
        self.assertEqual(limits.alert_line(rows), "LIMIT: gifts is 200.00 EUR over its limit (and 1 more)")

    def test_savings_outflow(self):
        rows = [row("savings", "-0.01")]
        self.assertEqual(limits.worst_offender(rows), "savings")
