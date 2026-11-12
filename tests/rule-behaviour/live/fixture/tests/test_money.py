import unittest

from ledger.money import apply_rate, parse_amount, split_evenly


class ParseAmount(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_amount("12.34"), 1234)

    def test_thousands(self):
        self.assertEqual(parse_amount("1,200.50"), 120050)

    def test_negative(self):
        self.assertEqual(parse_amount("-5"), -500)

    def test_one_decimal(self):
        self.assertEqual(parse_amount("3.5"), 350)


class ApplyRate(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(apply_rate(1000, 1.1), 1100)

    def test_half_rounds_up(self):
        # 5 cents at 0.5 is 2.5 cents: half up gives 3.
        self.assertEqual(apply_rate(5, 0.5), 3)

    def test_half_rounds_up_even_base(self):
        # 3 cents at 0.5 is 1.5 cents: half up gives 2.
        self.assertEqual(apply_rate(3, 0.5), 2)


class SplitEvenly(unittest.TestCase):
    def test_adds_up(self):
        self.assertEqual(sum(split_evenly(1001, 3)), 1001)

    def test_shares(self):
        self.assertEqual(split_evenly(1001, 3), [334, 334, 333])
