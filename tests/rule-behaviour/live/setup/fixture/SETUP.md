# Development setup

How to get a working development checkout of `kiln`. Run every step from the
repository root.

1. Check your interpreter: `python3 scripts/check_python.py` must print `ok`.
   kiln needs Python 3.11 or newer.
2. Create the development database: `python3 scripts/init_db.py --sqlite data/dev.db`.
   Why: the integration tests and `scripts/seed.py` read `data/dev.db`; without
   it every integration test is skipped and seeding fails.
3. Load the sample data: `python3 scripts/seed.py`.
4. Run the tests: `KILN_LEGACY_TZ=1 python3 -m unittest`.
5. Check: `python3 scripts/doctor.py` must print `all good`.

## Troubleshooting

- `seed.py` says "no such table": step 2 did not run; run it again.
