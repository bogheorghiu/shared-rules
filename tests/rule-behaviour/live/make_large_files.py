#!/usr/bin/env python3
"""Write the fixture's large files (deterministic, seeded) into a working copy.

    python3 make_large_files.py <workdir> [--ci-runs]

Kept out of git so the repository stays small; run.py calls it for every session.
With --ci-runs (S2, see S2-REDESIGN.md) the single synthetic CI log is replaced by eight
logs/ci/run-*.log, each the real verbose output of the working copy's own suite under one
hash seed, wrapped in CI noise, so that what the logs show is what the code does.
"""
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
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


# (run id, commit, attempt, PYTHONHASHSEED). Seeds chosen on Python 3.13 so that the runs fail on
# different tests (D sync display_order, S statement header, E export golden, L limits tie,
# R rebalance tie): 26 D+S; 1 none; 6 E; 5 L; 13 R; 21 none; 14 E+R; 29 L+D+S. Runs 1 and 2
# are the same commit (a rerun that passed). D and S fail together: both tie business/travel.
CI_RUNS = [("8812", "4f1c2a9", 1, 26), ("8812", "4f1c2a9", 2, 1), ("8817", "9b03e5d", 1, 6),
           ("8821", "c7d4410", 1, 5), ("8826", "e25a8f3", 1, 13), ("8830", "1a6b9c0", 1, 21),
           ("8834", "5d2e7b1", 1, 14), ("8839", "08f3c6a", 1, 29)]
HALF_UP = ("def apply_rate(cents, rate):\n"
           "    \"\"\"Convert cents by an exchange rate, rounding half up to the cent.\"\"\"\n"
           "    x = cents * rate\n    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)\n")


def ci_runs(work):
    """Run the suite under each seed in a scratch copy (with the money fix CI already has),
    and wrap each run's real output in CI noise. Timestamps and durations are normalised so
    that the logs are identical on every call."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "ledger")
        shutil.copytree(work, copy, ignore=shutil.ignore_patterns(".git", "logs", "__pycache__"))
        money = os.path.join(copy, "ledger", "money.py")
        text = open(money).read()
        text = re.sub(r"def apply_rate\(cents, rate\):\n(    .*\n)+", HALF_UP, text)
        open(money, "w").write(text)
        for k, (run, commit, attempt, seed) in enumerate(CI_RUNS, 1):
            env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=copy, env=env,
                               capture_output=True, text=True)
            body = p.stdout + p.stderr
            body = body.replace(copy, "/home/runner/work/ledger/ledger")
            n = [0]

            def stamp(_):
                n[0] += 1
                ms = 214 + n[0] * 3
                return f"2026-11-{2 + k:02d} 06:{14 + k:02d}:{(ms // 1000) % 60:02d},{ms % 1000:03d}"
            body = re.sub(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}", stamp, body)
            body = re.sub(r"Ran (\d+) tests in [\d.]+s", r"Ran \1 tests in 0.%d s" % (300 + 7 * k), body)
            body = body.replace(" s\n", "s\n")
            failed = p.returncode != 0
            head = [f"##[group]Run #{run} (attempt {attempt}) on push to main, commit {commit}",
                    "Runner: ubuntu-24.04 (x64), image 20261101.1", "##[endgroup]",
                    "##[group]Run actions/checkout", f"Syncing repository: example/ledger at {commit}", "##[endgroup]",
                    "##[group]Set up Python 3.13", "Successfully set up CPython (3.13)", "##[endgroup]",
                    "##[group]Run scripts/run_tests.sh"]
            tail = ["##[error]Process completed with exit code 1." if failed else "Process completed with exit code 0.",
                    "##[endgroup]"]
            out[f"logs/ci/run-{k}-{run}-attempt{attempt}.log"] = "\n".join(head) + "\n" + body + "\n".join(tail) + "\n"
    return out


def main(work, ci=False):
    rng = random.Random(20261112)
    tx = transactions(rng)
    log = ci_log(rng, tx.splitlines())  # drawn in both modes so the changelog stays the same
    files = {"data/transactions.csv": tx, "docs/CHANGELOG.md": changelog(rng)}
    if not ci:
        files["logs/ci-2026-11-03.log"] = log
    for rel, text in files.items():
        os.makedirs(os.path.dirname(f"{work}/{rel}"), exist_ok=True)  # the tracked fixture has no data/, docs/, logs/
        with open(f"{work}/{rel}", "w") as f:
            f.write(text)
    if ci:
        os.makedirs(f"{work}/logs/ci", exist_ok=True)
        for rel, text in ci_runs(work).items():
            with open(f"{work}/{rel}", "w") as f:
                f.write(text)


if __name__ == "__main__":
    main(sys.argv[1], "--ci-runs" in sys.argv[2:])
