"""Summary report over a transactions CSV.

    python3 -m ledger.report data/transactions.csv
"""
import argparse
import csv
from collections import defaultdict

from ledger.money import parse_amount
from ledger.util import fmt_amt, pad


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows):
    by_category = defaultdict(int)
    for row in rows:
        by_category[row["category"]] += parse_amount(row["amount"])
    total = sum(by_category.values())
    return {"total": total, "by_category": dict(sorted(by_category.items()))}


def render(summary):
    lines = ["category            amount"]
    for cat, cents in summary["by_category"].items():
        lines.append(pad(cat, 20) + fmt_amt(cents))
    lines.append(pad("TOTAL", 20) + fmt_amt(summary["total"]))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv")
    args = ap.parse_args(argv)
    print(render(summarize(load(args.csv))))


if __name__ == "__main__":
    main()
