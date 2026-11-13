"""Create an empty kiln database.

    python3 scripts/init_db.py --db-url sqlite:///data/dev.db
"""
import argparse, os, sqlite3

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--db-url", required=True, help="database URL; only sqlite:///PATH is supported")
a = ap.parse_args()
if not a.db_url.startswith("sqlite:///"):
    ap.error("only sqlite:///PATH URLs are supported")
path = a.db_url[len("sqlite:///"):]
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
con = sqlite3.connect(path)
con.execute("CREATE TABLE IF NOT EXISTS firings (id INTEGER PRIMARY KEY, kiln TEXT, started TEXT, peak_c INTEGER)")
con.commit()
print(f"created {path}")
