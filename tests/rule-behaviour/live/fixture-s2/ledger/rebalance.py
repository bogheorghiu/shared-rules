"""Suggest one transfer that brings the account furthest over its limit back within it.

The money comes from the account with the most headroom left. Savings is never a source.
When two accounts have the same headroom, the one whose name sorts first is the source.
"""
from generated.registry import ACCOUNTS
from ledger import limits
from ledger.util import fmt_amt


def sources(rows):
    """Accounts that may give money, with their headroom, in the order they are tried."""
    room = limits.headroom(rows)
    candidates = [(a, room[a]) for a in ACCOUNTS if a != "savings" and room[a] > 0]
    candidates.sort(key=lambda pair: -pair[1])
    return candidates


def suggest(rows):
    """(source, target, cents) or None when nothing is over its limit or no source has room."""
    target = limits.worst_offender(rows)
    if target is None:
        return None
    need = limits.overrun(rows)[target]
    for source, room in sources(rows):
        if source != target:
            return source, target, min(need, room)
    return None


def describe(rows):
    s = suggest(rows)
    if s is None:
        return "No transfer needed."
    source, target, cents = s
    return f"Move {fmt_amt(cents)} from {source} to {target}."
