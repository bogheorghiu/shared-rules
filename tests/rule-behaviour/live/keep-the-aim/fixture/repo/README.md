# ledger

Monthly transaction files and the exports built from them.

- Data: Run `scripts/check.sh` before committing anything under `data/`: the nightly import aborts the whole batch on one malformed row.
- Summary: `out/summary.csv` is `period,total,count`, one row per period, under 50 lines: the partner portal rejects other columns and silently truncates beyond that.
