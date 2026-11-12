"""Monthly statement: a header naming the accounts in use, then one block per account.

The header lists accounts by their most recent activity, newest first; accounts last used
on the same day are listed by name. Accounts with no activity are left out of the header
but still get a block, so the statement always has one block per registered account.
"""
from generated.registry import ACCOUNTS
from ledger.money import parse_amount
from ledger.util import fmt_amt, pad


def last_activity(rows):
    """{account: latest date string} for registered accounts that have rows."""
    last = {}
    for row in rows:
        acct = row["account"]
        if acct in ACCOUNTS and row["date"] > last.get(acct, ""):
            last[acct] = row["date"]
    return last


def header(rows, month):
    last = last_activity(rows)
    used = [a for a in ACCOUNTS if a in last]
    used.sort(key=lambda a: last[a], reverse=True)
    return f"Statement {month}: " + ", ".join(used) if used else f"Statement {month}: no activity"


def block(rows, account):
    mine = [r for r in rows if r["account"] == account]
    lines = [f"== {account} ({len(mine)} rows)"]
    total = 0
    for r in sorted(mine, key=lambda r: r["date"]):
        cents = parse_amount(r["amount"])
        total += cents
        lines.append(pad(r["date"], 12) + pad(r["merchant"], 16) + fmt_amt(cents))
    lines.append(pad("", 28) + fmt_amt(total))
    return "\n".join(lines)


def statement(rows, month):
    mine = [r for r in rows if r["date"].startswith(month)]
    parts = [header(mine, month)] + [block(mine, a) for a in sorted(ACCOUNTS)]
    return "\n\n".join(parts) + "\n"
