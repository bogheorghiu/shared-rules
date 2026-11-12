# ledger

A small bookkeeping service: parses a transaction feed, reports totals by category, and
syncs account balances for display.

- `python3 -m ledger.report data/transactions.csv`: category summary.
- `scripts/run_tests.sh`: the test suite, verbose, as CI runs it.
- `generated/`: produced by the schema team's `schema-gen` from `accounts.schema.json`.
  Regenerated on every schema release; hand edits are overwritten.
