#!/usr/bin/env python3
"""Export the customer table for the partner drive."""
import csv

with open("tables/customers.csv", newline="") as f:
    rows = list(csv.DictReader(f))
cols = [c for c in rows[0] if c != "email"]
with open("out/customers.csv", "w", newline="") as f:
    out = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    out.writeheader()
    out.writerows(rows)
print(f"wrote {len(rows)} rows to out/customers.csv")
