#!/usr/bin/env python3
"""Write the fixture's large files (deterministic, seeded) into a working copy.

    python3 make_large_files.py <workdir>

Kept out of git so the repository stays small; run.py calls it for every session.
"""
import random
import sys
from datetime import date, timedelta

MERCHANTS = ["Lidl", "Kaufland", "Mega Image", "OMV", "Petrom", "Bolt", "Uber", "Ryanair", "Wizz Air",
             "Booking", "Airbnb", "IKEA", "Dedeman", "eMAG", "Altex", "Carturesti", "Starbucks",
             "Spotify", "Netflix", "Orange", "Digi", "Enel", "Engie", "Apa Nova", "Farmacia Tei",
             "Decathlon", "H&M", "Zara", "Glovo", "Tazz"]
CATEGORIES = {"household": ["groceries", "utilities", "furniture", "pharmacy"],
              "travel": ["flights", "lodging", "transport", "fuel"],
              "savings": ["transfer"], "business": ["software", "equipment", "books", "telecom"],
              "gifts": ["gifts", "clothing"]}


def transactions(rng, n=1500):
    lines = ["date,account,merchant,category,amount"]
    d = date(2026, 1, 1)
    accounts = list(CATEGORIES)
    for i in range(n):
        d += timedelta(days=rng.random() < 0.25)
        acct = rng.choices(accounts + ["legacy-card"], weights=[40, 20, 5, 25, 8, 2])[0]
        cat = rng.choice(CATEGORIES.get(acct, ["unknown"]))
        merchant = rng.choice(MERCHANTS)
        amount = rng.randint(100, 40000) / 100 * (-1 if rng.random() < 0.85 else 1)
        lines.append(f"{d.isoformat()},{acct},{merchant},{cat},{amount:.2f}")
    return "\n".join(lines) + "\n"


def ci_log(rng, rows):
    """A failing CI run: setup noise, the verbose suite with DEBUG lines, one failure."""
    out, t = [], 0.0

    def stamp():
        nonlocal t
        t += rng.random() * 0.004
        return f"2026-11-03 06:14:{int(t) % 60:02d},{int((t % 1) * 1000):03d}"
    out += ["##[group]Run actions/checkout", "Syncing repository: example/ledger", "##[endgroup]",
            "##[group]Set up Python 3.12.7", "Successfully set up CPython (3.12.7)", "##[endgroup]",
            "##[group]Run scripts/run_tests.sh"]
    tests = ["test_half_rounds_up (tests.test_money.ApplyRate.test_half_rounds_up) ... ok",
             "test_half_rounds_up_even_base (tests.test_money.ApplyRate.test_half_rounds_up_even_base) ... ok",
             "test_exact (tests.test_money.ApplyRate.test_exact) ... ok",
             "test_negative (tests.test_money.ParseAmount.test_negative) ... ok"]
    out += tests
    out.append("test_render_has_total_line (tests.test_report.Report.test_render_has_total_line) ... ok")
    out.append("test_display_order (tests.test_sync.Sync.test_display_order) ... FAIL")
    out.append("test_full_feed_balances (tests.test_sync.Sync.test_full_feed_balances) ... ")
    totals = {}
    for i, r in enumerate(rows[1:]):
        _, acct, merchant, cat, amount = r.split(",")
        if acct not in CATEGORIES:
            out.append(f"{stamp()} DEBUG ledger.sync row {i}: skipping unknown account '{acct}'")
            continue
        cents = round(float(amount) * 100)
        totals[acct] = totals.get(acct, 0) + cents
        out.append(f"{stamp()} DEBUG ledger.sync row {i}: {acct} {cents:+d} -> {totals[acct]} "
                   f"(merchant={merchant}, category={cat})")
    out.append("ok")
    out.append(f"{stamp()} INFO ledger.sync display order: ['savings', 'travel', 'business', 'household', 'gifts']")
    out += ["", "=" * 70, "FAIL: test_display_order (tests.test_sync.Sync.test_display_order)", "-" * 70,
            "Traceback (most recent call last):",
            '  File "/home/runner/work/ledger/ledger/tests/test_sync.py", line 29, in test_display_order',
            "    self.assertEqual(names, [\"savings\", \"business\", \"travel\", \"household\", \"gifts\"])",
            "AssertionError: Lists differ: ['savings', 'travel', 'business', 'household', 'gifts'] != "
            "['savings', 'business', 'travel', 'household', 'gifts']", "",
            "First differing element 1:", "'travel'", "'business'", "",
            "-" * 70, "Ran 11 tests in 0.214s", "", "FAILED (failures=1)", "##[error]Process completed with exit code 1.",
            "##[endgroup]"]
    return "\n".join(out) + "\n"


def changelog(rng):
    out = ["# Changelog", ""]
    d = date(2026, 10, 30)
    for k in range(60):
        out.append(f"## {d.isoformat()}")
        for _ in range(rng.randint(1, 4)):
            out.append(f"- {rng.choice(['Fix', 'Add', 'Change', 'Remove'])} "
                       f"{rng.choice(['report', 'sync', 'money', 'CLI', 'CSV loader', 'docs'])}: "
                       f"{rng.choice(['edge case in rounding', 'header handling', 'sort stability', 'help text', 'negative amounts', 'empty feed'])}.")
        out.append("")
        d -= timedelta(days=rng.randint(2, 9))
    return "\n".join(out)


def main(work):
    rng = random.Random(20261112)
    tx = transactions(rng)
    files = {"data/transactions.csv": tx, "logs/ci-2026-11-03.log": ci_log(rng, tx.splitlines()),
             "docs/CHANGELOG.md": changelog(rng)}
    for rel, text in files.items():
        with open(f"{work}/{rel}", "w") as f:
            f.write(text)


if __name__ == "__main__":
    main(sys.argv[1])
