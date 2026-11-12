import unittest
from decimal import Decimal

from pkg import group_totals, parse_amount


class CoreTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_amount("1,234.50"), Decimal("1234.50"))
        self.assertIsNone(parse_amount("n/a"))

    def test_group(self):
        rows = [{"cat": "a", "amount": "1"}, {"cat": "a", "amount": "2.5"}, {"cat": "b", "amount": "x"}]
        self.assertEqual(group_totals(rows, "cat"), {"a": Decimal("3.5")})


if __name__ == "__main__":
    unittest.main()
