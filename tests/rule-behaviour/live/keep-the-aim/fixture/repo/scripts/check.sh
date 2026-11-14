#!/bin/sh
# Validate monthly data files before they are committed.
exec python3 - <<'PY'
import csv, glob, sys
files = sorted(glob.glob("data/2025-*.csv"))
for path in files:
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    for n, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            print(f"{path}: row {n} has {len(row)} fields, expected {len(header)}")
            sys.exit(1)
print(f"OK ({len(files)} files)")
PY
