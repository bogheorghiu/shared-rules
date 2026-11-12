#!/usr/bin/env python3
"""Drive one live session of DESIGN-live-test.md: a scripted user, the real CLI, headless.

    python3 -I run.py --scenario S1 --arm rule --reader sonnet-medium --out <dir> [--tag pilot]

Each session gets:
- a fresh HOME holding only the arm's rule files under ~/.claude/rules/ (native load), and
  an environment rebuilt from nothing but PATH, the proxy and CA variables, so no user
  rules, skills, plugins or parent-session state leak in (verified in HARNESS-NOTES.md);
- a fresh copy of fixture/ plus the large files, as a git repo with one initial commit;
- one `claude -p` call per scripted turn, the first with --session-id, the rest --resume.

It stores, per session: the raw stream-json transcript of every turn, the arm's rule files
with their sha256, the model served (read from the transcript), per-turn token usage
split main thread / subagents and cached / uncached, the final git log, and the hidden
checks. Scoring reads these records; nothing comes from the model's account of itself.

Reuses the approach of tests/live/live.py (isolated HOME, stream-json, artifact scoring).
Needs a logged-in `claude` on PATH. Spends real tokens.
"""
import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GIT_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_AUTHOR_NAME": "dev",
           "GIT_AUTHOR_EMAIL": "dev@example.invalid", "GIT_COMMITTER_NAME": "dev",
           "GIT_COMMITTER_EMAIL": "dev@example.invalid"}
KEEP_ENV = ["PATH", "ANTHROPIC_BASE_URL", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE",
            "NODE_EXTRA_CA_CERTS", "LANG"]
READERS = {"sonnet-medium": ("sonnet", "medium"), "opus-low": ("opus", "low")}
TOOLS = "Bash,Read,Edit,Write,Grep,Glob,Agent,TodoWrite"
ALLOWED = ["Read", "Edit", "Write", "Grep", "Glob", "Agent", "TodoWrite",
           "Bash(scripts/run_tests.sh:*)", "Bash(./scripts/run_tests.sh:*)", "Bash(bash scripts/run_tests.sh:*)",
           "Bash(python3 -m unittest:*)", "Bash(python -m unittest:*)", "Bash(cat:*)", "Bash(sed -n:*)", "Bash(python3 -m ledger.report:*)",
           "Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)", "Bash(git commit:*)", "Bash(git log:*)",
           "Bash(git show:*)", "Bash(ls:*)", "Bash(wc:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)",
           "Bash(sort:*)", "Bash(uniq:*)", "Bash(cut:*)"]
# A first-pass detector only: the pre-registration scores offers by reading the replies.
OFFER = re.compile(r"(fresh|new|clean|separate)\s+(session|conversation|context|chat|start)|start\s+(a\s+)?(fresh|new|over)"
                   r"|/clear|hand-?off|context (is|has become) (large|long|heavy)", re.I)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


RULE_UNDER_TEST = "keep-context-to-the-work.md"


def rule_path():
    """The rule under test: in the plugin once promoted, else in docs/staged-rules/."""
    shipped = os.path.join(REPO, "plugins", "shared-rules", "rules", RULE_UNDER_TEST)
    return shipped if os.path.exists(shipped) else os.path.join(REPO, "docs", "staged-rules", RULE_UNDER_TEST)


def arm_rules(arm):
    """Control: every bundled rule except the one under test. Rule arm: control plus that rule."""
    files = sorted(f for f in glob.glob(os.path.join(REPO, "plugins", "shared-rules", "rules", "*.md"))
                   if os.path.basename(f) != RULE_UNDER_TEST)
    if arm == "rule":
        files.append(rule_path())
    elif arm != "control":
        sys.exit(f"unknown arm {arm}")
    return files


def provenance():
    """Repository commit and the hashes a pre-registered record must match (void condition 4)."""
    tree = hashlib.sha256()
    fixture_files = (glob.glob(os.path.join(HERE, "fixture", "**", "*"), recursive=True, include_hidden=True)
                     + glob.glob(os.path.join(HERE, "fixture-s2", "**", "*"), recursive=True, include_hidden=True))
    for f in sorted(fixture_files):
        if os.path.isfile(f) and "__pycache__" not in f:
            tree.update(os.path.relpath(f, HERE).encode() + b"\0" + open(f, "rb").read())
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", HERE], capture_output=True, text=True).stdout
    return {"repo_commit": commit, "harness_dirty": bool(dirty.strip()), "fixture_tree_sha256": tree.hexdigest(),
            **{f"{n}_sha256": sha(os.path.join(HERE, n)) for n in ("scenarios.json", "run.py", "hidden/check.py", "make_large_files.py")}}


def make_home(home, arm):
    dest = os.path.join(home, ".claude", "rules", "shared-rules")
    os.makedirs(dest)
    loaded = []
    for f in arm_rules(arm):
        shutil.copy(f, dest)
        loaded.append({"file": os.path.relpath(f, REPO), "sha256": sha(f)})
    return loaded


def make_work(work, overlay=None):
    """Fixture, then the scenario's overlay on top (S2 adds modules and tests S1 never sees),
    then the large files; with an overlay, the CI logs are real runs of this copy's suite."""
    shutil.copytree(os.path.join(HERE, "fixture"), work, ignore=shutil.ignore_patterns("__pycache__"))
    if overlay:
        shutil.copytree(os.path.join(HERE, overlay), work, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_large_files.py"), work]
                   + (["--ci-runs"] if overlay else []), check=True)
    g = lambda *a: subprocess.run(["git", "-C", work, *a], env=dict(os.environ, **GIT_ENV), check=True,
                                  capture_output=True, text=True).stdout.strip()
    g("init", "-q", "-b", "main"); g("add", "-A"); g("commit", "-qm", "Initial import")
    return g("rev-parse", "HEAD")


def clean_env(home, extra):
    env = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    env.update(HOME=home, CLAUDE_CONFIG_DIR=os.path.join(home, ".claude"), **GIT_ENV, **extra)
    return env


def parse(path):
    """Usage and content of one turn's transcript, from the stream-json events."""
    t = {"main_calls": 0, "sub_calls": 0, "models_main": set(), "models_sub": set(), "texts": [], "tools": [],
         "denials": 0, "result": None, "final_context": None}
    for k in ("main", "sub"):
        for f in ("input", "cache_read", "cache_creation", "output"):
            t[f"{k}_{f}"] = 0
    seen = set()
    for line in open(path):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "assistant":
            m = e["message"]
            k = "sub" if e.get("parent_tool_use_id") else "main"
            if m.get("model"):
                t[f"models_{k}"].add(m["model"])
            u = m.get("usage") or {}
            # one API response can arrive as several events (thinking, text, tool_use) with the same id
            if m.get("id") not in seen:
                seen.add(m.get("id"))
                t[f"{k}_calls"] += 1
                t[f"{k}_input"] += u.get("input_tokens", 0)
                t[f"{k}_cache_read"] += u.get("cache_read_input_tokens", 0)
                t[f"{k}_cache_creation"] += u.get("cache_creation_input_tokens", 0)
                t[f"{k}_output"] += u.get("output_tokens", 0)
                if k == "main":
                    t["final_context"] = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                                          + u.get("cache_creation_input_tokens", 0) + u.get("output_tokens", 0))
            for c in m.get("content", []):
                if c.get("type") == "text" and k == "main":
                    t["texts"].append(c["text"])
                if c.get("type") == "tool_use":
                    t["tools"].append({"thread": k, "name": c.get("name"), "input": json.dumps(c.get("input"))[:300]})
        if e.get("type") == "user":
            for c in (e.get("message", {}).get("content") or []):
                if isinstance(c, dict) and c.get("is_error") and "permission" in json.dumps(c.get("content")).lower():
                    t["denials"] += 1
        if e.get("type") == "result":
            t["result"] = {k: e.get(k) for k in ("subtype", "is_error", "duration_ms", "num_turns", "total_cost_usd")}
    t["models_main"], t["models_sub"] = sorted(t["models_main"]), sorted(t["models_sub"])
    return t


def total_tokens(turns):
    """Tokens newly processed: uncached input, cache writes and output, main and sub. Cache
    reads (the same context re-read on each call) are reported beside it, not inside it."""
    return sum(t[f"{k}_{f}"] for t in turns for k in ("main", "sub") for f in ("input", "cache_creation", "output"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, choices=["S1", "S2"])
    ap.add_argument("--arm", required=True, choices=["control", "rule"])
    ap.add_argument("--reader", required=True, choices=sorted(READERS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--cap", type=int, default=400_000, help="stop when total_tokens passes this before the last turn")
    ap.add_argument("--budget-usd", default="25", help="--max-budget-usd per call; the CLI estimate it checks is cumulative over a resumed session")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "scenarios.json")))
    sc = spec[a.scenario]
    model, effort = READERS[a.reader]
    name = f"{a.tag + '-' if a.tag else ''}{a.scenario}-{a.arm}-{a.reader}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    root = os.path.join(a.out, name)
    home, work, tdir = (os.path.join(root, x) for x in ("home", "work", "transcripts"))
    os.makedirs(tdir)
    loaded = make_home(home, a.arm)
    base = make_work(work, sc.get("overlay"))
    env = clean_env(home, sc["env"])
    sid = str(uuid.uuid4())
    rec = {"scenario": a.scenario, "arm": a.arm, "reader": a.reader, "model_requested": model,
           "effort_requested": effort, "rules_loaded": loaded, "provenance": provenance(), "initial_commit": base, "turns": [],
           "cli_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "stopped_early": None,
           "python": sys.version.split()[0],
           "large_files_sha256": {os.path.relpath(f, work): sha(f) for d in ("data", "logs", "docs")
                                  for f in sorted(glob.glob(os.path.join(work, d, "**", "*"), recursive=True))
                                  if os.path.isfile(f)}}
    offers = 0
    prev_offer = False
    for i, turn in enumerate(sc["turns"]):
        text = turn["text"]
        if prev_offer:
            text = spec["decline"]["first" if offers == 1 else "again"] + " " + text
        path = os.path.join(tdir, f"{turn['id']}.jsonl")
        cmd = ["claude", "-p", text, "--model", model, "--effort", effort, "--output-format", "stream-json",
               "--verbose", "--tools", TOOLS, "--allowedTools", *ALLOWED, "--permission-prompts", "none",
               "--max-budget-usd", a.budget_usd]
        cmd += ["--session-id", sid] if i == 0 else ["--resume", sid]
        t0 = time.time()
        with open(path, "w") as out:
            rc = subprocess.run(cmd, cwd=work, env=env, stdout=out, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, timeout=1800).returncode
        p = parse(path)
        reply = "\n".join(p["texts"])
        prev_offer = bool(OFFER.search(reply))
        offers += prev_offer
        p.update(id=turn["id"], role=turn["role"], sent=text, rc=rc, wall_s=round(time.time() - t0, 1),
                 offer_detected=prev_offer, reply_tail=reply[-1500:])
        del p["texts"]
        rec["turns"].append(p)
        tot = total_tokens(rec["turns"])
        print(f"{name} {turn['id']}: rc={rc} wall={p['wall_s']}s ctx={p['final_context']} total={tot} "
              f"cost={p['result'] and p['result'].get('total_cost_usd')} offer={prev_offer} denials={p['denials']}", flush=True)
        if tot > a.cap and i < len(sc["turns"]) - 1:
            rec["stopped_early"] = f"total_tokens {tot} passed cap {a.cap} after {turn['id']}"
            break
    rec["git_log"] = subprocess.run(["git", "-C", work, "log", "--oneline"], capture_output=True, text=True,
                                    env=dict(os.environ, **GIT_ENV)).stdout.splitlines()
    rec["hidden"] = json.loads(subprocess.run([sys.executable, "-I", os.path.join(HERE, "hidden", "check.py"), work, base],
                                              capture_output=True, text=True).stdout or "null")
    rec["total_tokens"] = total_tokens(rec["turns"])
    rec["cache_read_tokens"] = sum(t[f"{k}_cache_read"] for t in rec["turns"] for k in ("main", "sub"))
    # total_cost_usd in a result event is cumulative over the resumed session (HARNESS-NOTES.md)
    costs = [(t["result"] or {}).get("total_cost_usd") or 0 for t in rec["turns"]]
    rec["cost_usd_client_estimate"] = round(max(costs, default=0), 4)
    for t, c, prev in zip(rec["turns"], costs, [0] + costs[:-1]):
        t["cost_usd_delta"] = round(c - prev, 4)
    with open(os.path.join(root, "record.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print(f"record: {os.path.join(root, 'record.json')}")


if __name__ == "__main__":
    main()
