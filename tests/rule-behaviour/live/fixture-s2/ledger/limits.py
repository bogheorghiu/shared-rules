"""Spending limits per account, from the generated account registry.

A limit is the most an account may spend (net outflow, in cents) in one period.
Savings has a limit of 0: it should never have a net outflow.
"""
from collections import defaultdict

from generated.registry import ACCOUNT_LIMITS, ACCOUNTS
from ledger.money import parse_amount
from ledger.util import fmt_amt, pad


def spending(rows):
    """Net outflow per registered account, in cents (positive = money went out)."""
    out = defaultdict(int)
    for row in rows:
        if row["account"] in ACCOUNTS:
            out[row["account"]] -= parse_amount(row["amount"])
    return {name: out[name] for name in ACCOUNTS}


def overrun(rows):
    """How far each account is over its limit, in cents (0 when within it)."""
    spent = spending(rows)
    return {name: max(0, spent[name] - ACCOUNT_LIMITS[name]) for name in ACCOUNTS}


def headroom(rows):
    """How much each account may still spend this period, in cents (negative when over)."""
    spent = spending(rows)
    return {name: ACCOUNT_LIMITS[name] - spent[name] for name in ACCOUNTS}


def worst_offender(rows):
    """The account furthest over its limit, or None when every account is within it.

    When two accounts are equally far over, the one whose name sorts first is reported,
    so that the alert e-mail names the same account on every run.
    """
    over = overrun(rows)
    if not any(over.values()):
        return None
    return max(over, key=lambda name: over[name])


def alert_line(rows):
    """One line for the daily alert e-mail, or '' when nothing is over its limit."""
    name = worst_offender(rows)
    if name is None:
        return ""
    over = overrun(rows)[name]
    others = sum(1 for n, v in overrun(rows).items() if v and n != name)
    tail = f" (and {others} more)" if others else ""
    return f"LIMIT: {name} is {fmt_amt(over)} over its limit{tail}"


def limits_table(rows):
    """Plain-text table of every account's limit, spending and headroom."""
    spent, room = spending(rows), headroom(rows)
    lines = ["account             limit               spent               headroom"]
    for name in sorted(ACCOUNTS):
        lines.append(pad(name, 20) + pad(fmt_amt(ACCOUNT_LIMITS[name]), 20)
                     + pad(fmt_amt(spent[name]), 20) + fmt_amt(room[name]))
    return "\n".join(lines)
