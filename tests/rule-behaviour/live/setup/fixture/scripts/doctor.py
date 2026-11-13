"""Check a development checkout."""
import os, sqlite3, sys
problems = []
if not os.path.exists("data/dev.db"):
    problems.append("data/dev.db missing (SETUP.md step 2)")
else:
    try:
        n = sqlite3.connect("data/dev.db").execute("SELECT COUNT(*) FROM firings").fetchone()[0]
        if n == 0:
            problems.append("no sample data (SETUP.md step 3)")
    except sqlite3.OperationalError:
        problems.append("no firings table (SETUP.md step 2)")
print("all good" if not problems else "\n".join(problems))
sys.exit(1 if problems else 0)
