import io
import os
import unittest
from contextlib import redirect_stdout

from ledger import report

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "transactions.csv")


class Report(unittest.TestCase):
    def test_summary_total_matches_rows(self):
        rows = report.load(DATA)
        s = report.summarize(rows)
        self.assertEqual(s["total"], sum(report.parse_amount(r["amount"]) for r in rows))

    def test_render_has_total_line(self):
        out = io.StringIO()
        with redirect_stdout(out):
            report.main([DATA])
        self.assertIn("TOTAL", out.getvalue())
