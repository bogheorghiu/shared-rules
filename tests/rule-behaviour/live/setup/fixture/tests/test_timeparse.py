import unittest
from kiln.timeparse import parse


class TestParse(unittest.TestCase):
    def test_aware_kept(self):
        self.assertEqual(parse("2026-09-02T08:00:00+02:00").utcoffset().total_seconds(), 7200)

    def test_naive_parses(self):
        self.assertEqual(parse("2026-09-02T08:00:00").hour, 8)
