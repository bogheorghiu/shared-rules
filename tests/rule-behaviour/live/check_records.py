#!/usr/bin/env python3
"""Provenance check and void list for the registered run (PREREG-live-2026-11-12.md, Void
conditions and the amendment "Which files a record is checked against").

    python3 -I check_records.py --ref <reference commit> <batch-state.json> > voids.json

For every session the batch planned: is there a record; are its rule files, scenarios.json,
run.py, hidden/check.py, make_large_files.py and fixture tree (both overlays) byte-identical
to the reference commit (by sha256, computed here from `git show <ref>:<path>`), and is
harness_dirty false (condition 4, as amended; condition 2's file half); did every
main-thread call come from the reader's model (condition 2); did every turn exit 0 with a
non-error result and no token-cap stop (condition 1); did at least half the commit turns
have a successful `git commit` tool call (condition 3). Prints one JSON object per session
with each condition's result and the reason; decided before any endpoint is computed.
"""
import argparse, hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIVE = os.path.relpath(HERE, REPO)
SERVED = {"sonnet-medium": "claude-sonnet-5-5", "opus-low": "claude-opus-5-5"}
COMMIT_TURNS = {"S1": ["t2", "t3", "t4", "t6", "t8", "t9", "t10", "t12", "t13"], "S2": ["t1", "t2", "t3", "t4", "t5", "t8"],
                "S3": ["t2", "t3", "t4", "t7", "t9", "t10", "t11", "t12"]}


def git(*a, binary=False):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, check=True, text=not binary).stdout


def reference(ref):
    sha = lambda b: hashlib.sha256(b).hexdigest()
    show = lambda p: git("show", f"{ref}:{p}", binary=True)
    want = {f"{n}_sha256": sha(show(f"{LIVE}/{n}")) for n in ("scenarios.json", "run.py", "hidden/check.py", "make_large_files.py")}
    tree = hashlib.sha256()
    paths = git("ls-tree", "-r", "--name-only", ref, "--", f"{LIVE}/fixture", f"{LIVE}/fixture-s2").split()
    for p in sorted(paths):  # run.py: sorted absolute paths, relpath to live/, NUL, bytes
        if "__pycache__" not in p:
            tree.update(os.path.relpath(p, LIVE).encode() + b"\0" + show(p))
    want["fixture_tree_sha256"] = tree.hexdigest()
    name = "keep-context-to-the-work.md"  # run.py RULE_UNDER_TEST: in the plugin once promoted, else staged
    listed = git("ls-tree", "--name-only", ref, "--", "plugins/shared-rules/rules/").split()
    rules = {p: sha(show(p)) for p in listed if p.endswith(".md") and os.path.basename(p) != name}
    under_test = next((p for p in listed if os.path.basename(p) == name), f"docs/staged-rules/{name}")
    rule_arm = dict(rules, **{under_test: sha(show(under_test))})
    return want, {"control": rules, "rule": rule_arm}


def commits_ok(path):
    """True if the turn's transcript has a Bash `git commit` tool call whose result is not an error."""
    uses, ok = {}, False
    for line in open(path):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        msg = e.get("message") if isinstance(e.get("message"), dict) else {}
        content = msg.get("content") if isinstance(msg.get("content"), list) else []
        for c in content:
            if not isinstance(c, dict):
                continue
            if e.get("type") == "assistant" and c.get("type") == "tool_use" and c.get("name") == "Bash" \
                    and "git commit" in str((c.get("input") or {}).get("command", "")):
                uses[c["id"]] = True
            if e.get("type") == "user" and c.get("type") == "tool_result" and c.get("tool_use_id") in uses \
                    and not c.get("is_error"):
                ok = True
    return ok


def check(key, s, want, rules):
    sc, arm, reader = s["cell"]
    out = {"key": key, "cell": s["cell"], "record": s.get("record"), "void": [], "notes": []}
    if not s.get("record") or not os.path.exists(s["record"]):
        out["void"].append("1: no record (session did not finish: " + str(s.get("status")) + ")")
        return out
    r = json.load(open(s["record"]))
    run = os.path.dirname(s["record"])
    out["run"] = os.path.basename(run)
    turns = r["turns"]
    # condition 1
    if r.get("stopped_early"):
        out["void"].append(f"1: stopped_early {r['stopped_early']}")
    import_spec = json.loads(git("show", f"HEAD:{LIVE}/scenarios.json"))
    if len(turns) != len(import_spec[sc]["turns"]):
        out["void"].append(f"1: {len(turns)} turns recorded of {len(import_spec[sc]['turns'])}")
    for t in turns:
        res = t.get("result")
        if t["rc"] != 0 or not res or res.get("is_error") or res.get("subtype") != "success":
            out["void"].append(f"1: turn {t['id']} rc={t['rc']} result={res}")
    # condition 2
    bad = sorted({m for t in turns for m in t["models_main"] if m != SERVED[reader]})
    if bad or any(not t["models_main"] for t in turns):
        out["void"].append(f"2: main-thread models {bad or 'missing'} (want {SERVED[reader]})")
    loaded = {x["file"]: x["sha256"] for x in r["rules_loaded"]}
    if loaded != rules[arm]:
        out["void"].append("2/4: rule files differ from the reference commit")
    # condition 4 (amended)
    prov = r["provenance"]
    for k, v in want.items():
        if prov.get(k) != v:
            out["void"].append(f"4: {k} differs from the reference commit")
    if prov.get("harness_dirty") is not False:
        out["void"].append("4: harness_dirty")
    # condition 3
    missing = [tid for tid in COMMIT_TURNS[sc] if not commits_ok(os.path.join(run, "transcripts", f"{tid}.jsonl"))]
    out["commit_turns_without_commit"] = missing
    if 2 * len(missing) >= len(COMMIT_TURNS[sc]):
        out["void"].append(f"3: {len(missing)} of {len(COMMIT_TURNS[sc])} commit turns without a successful git commit")
    out["repo_commit"] = prov.get("repo_commit")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("states", nargs="+", help="batch-state.json files; a later file's session replaces nothing, all are listed")
    a = ap.parse_args()
    want, rules = reference(a.ref)
    rows = []
    for st in a.states:
        for key, s in json.load(open(st))["sessions"].items():
            rows.append(dict(check(key, s, want, rules), state=os.path.basename(os.path.dirname(os.path.abspath(st)))))
    json.dump({"reference_commit": a.ref, "reference_hashes": want, "sessions": rows}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
