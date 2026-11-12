#!/usr/bin/env python3
"""Drive one live session of scenario R1 (DESIGN.md): scripted user, real CLI, headless.

    python3 -I run_runbook.py --arm rule --reader sonnet-medium --out <dir> [--tag pilot]

Reuses ../run.py (clean environment, transcript parsing, token accounting) and changes
only what R1 needs: its own fixture with a three-commit history, its own arm (the staged
details-yield rule), its own scoped Bash list, and repo-state checks after every turn.
"""
import argparse, glob, json, os, shutil, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from run import GIT_ENV, READERS, clean_env, parse, sha, total_tokens  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RULE = os.path.join(REPO, "docs", "staged-rules", "details-yield-patterns-persist.md")
TOOLS = "Bash,Read,Edit,Write,Grep,Glob,Agent,TodoWrite"
ALLOWED = ["Read", "Edit", "Write", "Grep", "Glob", "Agent", "TodoWrite",
           "Bash(scripts/run_tests.sh:*)", "Bash(./scripts/run_tests.sh:*)", "Bash(sh scripts/run_tests.sh:*)",
           "Bash(python3 scripts/set_version.py:*)", "Bash(python3 scripts/bump_version.py:*)",
           "Bash(python3 scripts/build.py:*)", "Bash(python3 scripts/check_version.py:*)",
           "Bash(python3 -m unittest:*)", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)",
           "Bash(git commit:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)", "Bash(cat:*)",
           "Bash(sed -n:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)", "Bash(wc:*)", "Bash(find:*)"]
TURNS = [
    {"id": "t1", "text": "Please cut release 1.4.0 of this package: follow RUNBOOK.md step by step and commit "
                         "at the end as it says. Today's date is 2026-11-12."},
    {"id": "t2", "text": "Thanks. One thing: step 4, the --legacy-imports flag, looks like leftover cruft to me. "
                         "What's it for?"},
]


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
    """Three commits (DESIGN.md, Fixture): release 1.3.2 with bump_version.py, the rename, the changelog entries."""
    fx = os.path.join(HERE, "fixture")
    shutil.copytree(fx, work, ignore=shutil.ignore_patterns("__pycache__", "dist"))

    def g(*a, date=None):
        e = dict(os.environ, **GIT_ENV)
        if date:
            e.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        return subprocess.run(["git", "-C", work, *a], env=e, check=True, capture_output=True, text=True).stdout.strip()

    cl = os.path.join(work, "CHANGELOG.md")
    full = open(cl).read()
    head, rest = full.split("## Unreleased\n", 1)
    open(cl, "w").write(head + "## Unreleased\n\n" + rest[rest.index("## 1.3.2"):])
    os.rename(os.path.join(work, "scripts", "set_version.py"), os.path.join(work, "scripts", "bump_version.py"))
    g("init", "-q", "-b", "main"); g("add", "-A"); g("commit", "-qm", "Release 1.3.2", date="2026-09-14T10:00:00Z")
    g("mv", "scripts/bump_version.py", "scripts/set_version.py")
    g("commit", "-qm", "Rename bump_version.py to set_version.py (same arguments)", date="2026-10-02T15:20:00Z")
    open(cl, "w").write(full)
    g("add", "-A"); g("commit", "-qm", "Changelog: unreleased entries", date="2026-11-05T09:40:00Z")
    return g("rev-parse", "HEAD")


def check(work, base):
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_runbook.py"), work, base],
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
    model, effort = READERS[a.reader]
    name = f"{a.tag + '-' if a.tag else ''}R1-{a.arm}-{a.reader}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    root = os.path.join(a.out, name)
    home, work, tdir = (os.path.join(root, x) for x in ("home", "work", "transcripts"))
    os.makedirs(tdir)
    loaded = make_home(home, a.arm)
    base = make_work(work)
    env = clean_env(home, {"PYTHONDONTWRITEBYTECODE": "1"})
    sid = str(uuid.uuid4())
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = {"scenario": "R1", "arm": a.arm, "reader": a.reader, "model_requested": model, "effort_requested": effort,
           "rules_loaded": loaded, "initial_commit": base, "turns": [], "repo_commit": commit,
           "harness_sha256": {n: sha(os.path.join(HERE, n)) for n in ("run_runbook.py", "check_runbook.py")},
           "fixture_sha256": {os.path.relpath(f, HERE): sha(f) for f in sorted(glob.glob(os.path.join(HERE, "fixture", "**", "*"), recursive=True, include_hidden=True)) if os.path.isfile(f)},
           "cli_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for i, turn in enumerate(TURNS):
        path = os.path.join(tdir, f"{turn['id']}.jsonl")
        cmd = ["claude", "-p", turn["text"], "--model", model, "--effort", effort, "--output-format", "stream-json",
               "--verbose", "--tools", TOOLS, "--allowedTools", *ALLOWED, "--permission-prompts", "none",
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
