"""Load fixtures/firings.csv into data/dev.db."""
import csv, sqlite3, sys
try:
    con = sqlite3.connect("file:data/dev.db?mode=rw", uri=True)
    rows = list(csv.DictReader(open("fixtures/firings.csv")))
    con.execute("DELETE FROM firings")
    con.executemany("INSERT INTO firings (kiln, started, peak_c) VALUES (:kiln, :started, :peak_c)", rows)
    con.commit()
except sqlite3.OperationalError as e:
    sys.exit(f"seed failed: {e}")
print(f"seeded {len(rows)} firings")
