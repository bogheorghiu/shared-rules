"""Monthly activity export, read by the finance team's spreadsheet import.

    month,account,rows,net
    2026-01,household,52,-1834.10
    ...

One line per registered account per month, months in order. Within a month the busiest
account comes first (most rows); accounts with the same number of rows are listed by
name, so that two exports of the same feed are byte-identical (the import diffs them).
"""
from collections import defaultdict

from generated.registry import ACCOUNTS
from ledger.money import parse_amount

HEADER = "month,account,rows,net"


def month_of(row):
    return row["date"][:7]


def activity(rows):
    """{month: {account: (row count, net cents)}} for every month in the feed and every
    registered account, zero-filled. Rows for accounts not in the registry are dropped."""
    counts = defaultdict(lambda: defaultdict(int))
    nets = defaultdict(lambda: defaultdict(int))
    months = set()
    for row in rows:
        months.add(month_of(row))
        if row["account"] not in ACCOUNTS:
            continue
        counts[month_of(row)][row["account"]] += 1
        nets[month_of(row)][row["account"]] += parse_amount(row["amount"])
    return {m: {a: (counts[m][a], nets[m][a]) for a in ACCOUNTS} for m in sorted(months)}


def fmt_net(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def export_lines(rows):
    lines = [HEADER]
    for month, per_account in activity(rows).items():
        busiest = sorted(per_account, key=lambda a: -per_account[a][0])
        for account in busiest:
            n, net = per_account[account]
            lines.append(f"{month},{account},{n},{fmt_net(net)}")
    return lines


def export_csv(rows):
    return "\n".join(export_lines(rows)) + "\n"


def write_export(rows, path):
    with open(path, "w") as f:
        f.write(export_csv(rows))
