import os
import unittest

from ledger import export

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden", "export.csv")

# Rows per account per month for the test feed: (household, travel, savings, business, gifts).
# In 2026-09 savings and gifts both have 2 rows.
PLAN = {
    "2026-01": (9, 4, 1, 6, 2), "2026-02": (8, 5, 1, 6, 3), "2026-03": (10, 3, 0, 7, 2),
    "2026-04": (9, 6, 1, 5, 4), "2026-05": (11, 7, 3, 6, 2), "2026-06": (8, 9, 1, 5, 3),
    "2026-07": (7, 12, 0, 4, 1), "2026-08": (9, 10, 1, 6, 3), "2026-09": (10, 4, 2, 7, 2),
    "2026-10": (9, 5, 1, 8, 3), "2026-11": (12, 4, 1, 6, 5), "2026-12": (14, 6, 3, 7, 9),
}
ACCOUNTS = ("household", "travel", "savings", "business", "gifts")


def feed():
    rows = []
    for month, counts in PLAN.items():
        for account, n in zip(ACCOUNTS, counts):
            for i in range(n):
                cents = -(1000 + 137 * i + 11 * len(account) + int(month[-2:]))
                rows.append({"date": f"{month}-{i + 1:02d}", "account": account, "merchant": "test",
                             "category": "test", "amount": f"{cents / 100:.2f}"})
    rows.append({"date": "2026-12-31", "account": "legacy-card", "merchant": "test", "category": "test",
                 "amount": "-12.00"})
    return rows


class Export(unittest.TestCase):
    maxDiff = None

    def test_header(self):
        self.assertEqual(export.export_lines(feed())[0], "month,account,rows,net")

    def test_one_line_per_account_month(self):
        self.assertEqual(len(export.export_lines(feed())), 1 + 12 * 5)

    def test_matches_golden(self):
        with open(GOLDEN) as f:
            self.assertEqual(export.export_csv(feed()), f.read())
