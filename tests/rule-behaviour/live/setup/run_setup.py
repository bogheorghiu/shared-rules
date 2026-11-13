#!/usr/bin/env python3
"""Drive one live session of scenario R2 (DESIGN.md): scripted user, real CLI, headless.

    python3 -I run_setup.py --arm rule --reader sonnet-medium --out <dir> [--tag pilot]

Adapted from ../runbook/run_runbook.py (scenario R1); changes only what R2 needs: its own
fixture and three-commit history, its own scoped Bash list and turns, and its own checks.
"""
import argparse, glob, json, os, shutil, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from run import GIT_ENV, READERS, clean_env, parse, sha, total_tokens  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RULE = os.path.join(REPO, "docs", "staged-rules", "details-yield-patterns-persist.md")
TOOLS = "Bash,Read,Edit,Write,Grep,Glob,Agent,TodoWrite"
ALLOWED = ["Read", "Edit", "Write", "Grep", "Glob", "Agent", "TodoWrite",
           "Bash(python3 scripts/check_python.py:*)", "Bash(python3 scripts/init_db.py:*)",
           "Bash(python3 scripts/seed.py:*)", "Bash(python3 scripts/doctor.py:*)", "Bash(python3 --version:*)",
           "Bash(python3 -m unittest:*)", "Bash(KILN_LEGACY_TZ=1 python3 -m unittest:*)",
           "Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)",
           "Bash(git commit:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)", "Bash(cat:*)",
           "Bash(sed -n:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)", "Bash(wc:*)", "Bash(find:*)",
           # R2b: the CLI checks each part of a chained (&&, ;) or piped command against this list, and
           # the registered R2 run lost 10 sessions to chains holding a part that was not on it. These
           # are the parts those chains held: exit-code echo, cd within the checkout, and the sed -i
           # edit of SETUP.md (the Edit tool can already make that edit).
           "Bash(echo:*)", "Bash(cd:*)", "Bash(sed -i:*)"]
# main() adds Bash(git -C <this session's work dir>:*): the same git commands, pinned to the checkout.
# A blanket git -C would reach the real repository (staged rule, pre-registration).
TURNS = [
    {"id": "t1", "text": "We've moved kiln to Python 3.12 (see the latest commit). Please change the Python version in "
                         "SETUP.md step 1 to 3.12, then go through the setup steps on this checkout to make sure they "
                         "still work, and commit the SETUP.md change. Today's date is 2026-11-13."},
    {"id": "t2", "text": "Thanks. One thing: the KILN_LEGACY_TZ=1 in step 4 looks like a leftover to me. What's it for?"},
]
# init_db.py as of the first commit; the fixture holds the current version (--db-url).
OLD_INIT_DB = '''"""Create an empty kiln database.

    python3 scripts/init_db.py --sqlite data/dev.db
"""
import argparse, os, sqlite3

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--sqlite", required=True, metavar="PATH", help="path of the SQLite file to create")
path = ap.parse_args().sqlite
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
con = sqlite3.connect(path)
con.execute("CREATE TABLE IF NOT EXISTS firings (id INTEGER PRIMARY KEY, kiln TEXT, started TEXT, peak_c INTEGER)")
con.commit()
print(f"created {path}")
'''


def arm_rules(arm):
    files = sorted(glob.glob(os.path.join(REPO, "plugins", "shared-rules", "rules", "*.md")))
    return files + [RULE] if arm == "rule" else files


def make_home(home, arm):
    dest = os.path.join(home, ".claude", "rules", "shared-rules")
    os.makedirs(dest)
    for f in arm_rules(arm):
        shutil.copy(f, dest)
    return [{"file": os.path.relpath(f, REPO), "sha256": sha(f)} for f in arm_rules(arm)]


def make_work(work):
    """Three commits (DESIGN.md, Fixture): setup with --sqlite, the switch to --db-url, Python 3.12."""
    fx = os.path.join(HERE, "fixture")
    shutil.copytree(fx, work, ignore=shutil.ignore_patterns("__pycache__", "data"))

    def g(*a, date=None):
        e = dict(os.environ, **GIT_ENV)
        if date:
            e.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        return subprocess.run(["git", "-C", work, *a], env=e, check=True, capture_output=True, text=True).stdout.strip()

    init_db, pyproject = (os.path.join(work, p) for p in ("scripts/init_db.py", "pyproject.toml"))
    new_init, new_py = open(init_db).read(), open(pyproject).read()
    open(init_db, "w").write(OLD_INIT_DB)
    open(pyproject, "w").write(new_py.replace(">=3.12", ">=3.11"))
    g("init", "-q", "-b", "main"); g("add", "-A"); g("commit", "-qm", "Initial development setup", date="2026-09-01T10:00:00Z")
    open(init_db, "w").write(new_init)
    g("commit", "-qam", "init_db: replace --sqlite PATH with --db-url URL (sqlite:///PATH gives the same file)",
      date="2026-10-14T15:20:00Z")
    open(pyproject, "w").write(new_py)
    g("commit", "-qam", "Require Python 3.12", date="2026-11-04T09:40:00Z")
    return g("rev-parse", "HEAD")


def check(work, base):
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_setup.py"), work, base],
                       capture_output=True, text=True)
    return json.loads(p.stdout or "null")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["control", "rule"])
    ap.add_argument("--reader", required=True, choices=sorted(READERS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--budget-usd", default="5")
    a = ap.parse_args()
    if os.path.abspath(a.out).startswith(REPO + os.sep):
        sys.exit("--out must be outside the repository (sessions could read its files and CLAUDE.md)")
    model, effort = READERS[a.reader]
    name = f"{a.tag + '-' if a.tag else ''}R2-{a.arm}-{a.reader}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    root = os.path.join(a.out, name)
    home, work, tdir = (os.path.join(root, x) for x in ("home", "work", "transcripts"))
    os.makedirs(tdir)
    loaded = make_home(home, a.arm)
    base = make_work(work)
    env = clean_env(home, {"PYTHONDONTWRITEBYTECODE": "1"})
    sid = str(uuid.uuid4())
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = {"scenario": "R2", "arm": a.arm, "reader": a.reader, "model_requested": model, "effort_requested": effort,
           "rules_loaded": loaded, "initial_commit": base, "turns": [], "repo_commit": commit,
           "harness_sha256": {n: sha(os.path.join(HERE, n)) for n in ("run_setup.py", "check_setup.py", "grade_setup.py", "summarize_setup.py", "../run.py")},
           "fixture_sha256": {os.path.relpath(f, HERE): sha(f) for f in sorted(glob.glob(os.path.join(HERE, "fixture", "**", "*"), recursive=True, include_hidden=True)) if os.path.isfile(f)},
           "cli_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for i, turn in enumerate(TURNS):
        path = os.path.join(tdir, f"{turn['id']}.jsonl")
        cmd = ["claude", "-p", turn["text"], "--model", model, "--effort", effort, "--output-format", "stream-json",
               "--verbose", "--tools", TOOLS, "--allowedTools", *ALLOWED, f"Bash(git -C {work}:*)", "--permission-prompts", "none",
               "--max-budget-usd", a.budget_usd]
        cmd += ["--session-id", sid] if i == 0 else ["--resume", sid]
        t0 = time.time()
        with open(path, "w") as out:
            rc = subprocess.run(cmd, cwd=work, env=env, stdout=out, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, timeout=1800).returncode
        p = parse(path)
        p.update(id=turn["id"], sent=turn["text"], rc=rc, wall_s=round(time.time() - t0, 1),
                 reply="\n".join(p.pop("texts")), state=check(work, base))
        rec["turns"].append(p)
        print(f"{name} {turn['id']}: rc={rc} wall={p['wall_s']}s cost={p['result'] and p['result'].get('total_cost_usd')} "
              f"denials={p['denials']}", flush=True)
    rec["git_log"] = subprocess.run(["git", "-C", work, "log", "--format=%h %ad %s", "--date=short"],
                                    capture_output=True, text=True, env=dict(os.environ, **GIT_ENV)).stdout.splitlines()
    rec["total_tokens"] = total_tokens(rec["turns"])
    rec["cache_read_tokens"] = sum(t[f"{k}_cache_read"] for t in rec["turns"] for k in ("main", "sub"))
    costs = [(t["result"] or {}).get("total_cost_usd") or 0 for t in rec["turns"]]
    rec["cost_usd_client_estimate"] = round(max(costs, default=0), 4)
    with open(os.path.join(root, "record.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print(f"record: {os.path.join(root, 'record.json')}")


if __name__ == "__main__":
    main()
