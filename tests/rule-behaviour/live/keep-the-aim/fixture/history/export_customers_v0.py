#!/usr/bin/env python3
"""Write out/customers.csv from tables/customers.csv."""
import csv

SRC = "tables/customers.csv"
DST = "out/customers.csv"
with open(SRC, newline="") as f:
    rows = list(csv.DictReader(f))
with open(DST, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} rows to {DST}")
