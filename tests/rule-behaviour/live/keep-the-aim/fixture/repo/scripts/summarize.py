#!/usr/bin/env python3
"""Write out/summary.csv: one row per month across data/.

`out/summary.csv` must stay `period,total,count`, one row per period, under 50 lines: the partner portal
rejects other columns and silently truncates beyond that.
"""
import csv, glob
from collections import defaultdict

total, count = defaultdict(float), defaultdict(int)
for path in sorted(glob.glob("data/2025-*.csv")):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            period = row["date"][:7]
            total[period] += float(row["amount"])
            count[period] += 1
with open("out/summary.csv", "w", newline="") as f:
    out = csv.writer(f)
    out.writerow(["period", "total", "count"])
    for p in sorted(total):
        out.writerow([p, f"{total[p]:.2f}", count[p]])
print(f"wrote {len(total)} periods to out/summary.csv")
