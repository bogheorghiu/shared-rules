"""Sync account balances from the transaction feed, in display order.

Display order: highest balance first. Accounts are taken from the generated
account registry.
"""
import logging

from generated.registry import ACCOUNTS
from ledger.money import parse_amount

log = logging.getLogger("ledger.sync")


def balances(rows):
    totals = {name: 0 for name in ACCOUNTS}
    for i, row in enumerate(rows):
        acct = row["account"]
        if acct not in totals:
            log.debug("row %d: skipping unknown account %r", i, acct)
            continue
        cents = parse_amount(row["amount"])
        totals[acct] += cents
        log.debug("row %d: %s %+d -> %d (merchant=%s, category=%s)", i, acct, cents, totals[acct],
                  row["merchant"], row["category"])
    return totals


def display_order(rows):
    totals = balances(rows)
    order = sorted(totals, key=lambda name: -totals[name])
    log.info("display order: %s", order)
    return [(name, totals[name]) for name in order]
