#!/usr/bin/env python3
"""Per-session endpoint table for R1 (DESIGN.md, PREREG.md), from records, transcripts and grades.

    python3 -I summarize_runbook.py <run-folder> [...]

H1 counts a step-2 rewrite in the final RUNBOOK.md, and also an *attempted* one: any
tool call in the transcript (Edit, Write or Bash, allowed or denied) whose input targets
RUNBOOK.md and would replace or delete the text `bump_version.py`. The pilot showed why:
a session's `sed -i` rewrite of step 2 was denied by the harness's scoped Bash list.
"""
import json, os, re, sys


def attempts(transcript):
    hits = []
    for line in open(transcript):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "assistant":
            continue
        for c in e["message"].get("content", []):
            if c.get("type") != "tool_use":
                continue
            i = c.get("input") or {}
            name = c.get("name")
            if name == "Edit" and i.get("file_path", "").endswith("RUNBOOK.md") \
                    and "bump_version.py" in i.get("old_string", "") and "bump_version.py" not in i.get("new_string", ""):
                hits.append(name)
            elif name == "Write" and i.get("file_path", "").endswith("RUNBOOK.md") and "bump_version.py" not in i.get("content", ""):
                hits.append(name)
            elif name == "Bash" and "RUNBOOK" in i.get("command", "") and (
                    re.search(r"sed\b[^|;]*\bs([/|#,]).*?bump_version[^/|#,]*\1", i.get("command", ""))
                    or any("bump_version" in a and "bump_version" not in b for a, b in
                           re.findall(r"replace\(\s*['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]", i.get("command", ""), re.S))):
                hits.append(name)  # a substitution whose target is the old script name; appends and inserts are not counted
    return hits


NOTE = re.compile(r"set_version|bump_version|renam", re.I)
HARNESS = ("run_runbook.py", "check_runbook.py", "grade_runbook.py", "summarize_runbook.py")


def notes(state):
    """N1 needs step 2 intact. Beside = an added line between step 2 and step 3; log = the 1.4.0 row."""
    added = state["runbook_lines_added"]
    final = state.get("runbook_final") or []
    beside = []
    if final:
        s2 = next((k for k, l in enumerate(final) if l.startswith("2. ")), None)
        s3 = next((k for k, l in enumerate(final) if l.startswith("3. ")), None)
        if s2 is not None and s3 is not None:
            beside = [l for l in final[s2 + 1:s3] if l in added and NOTE.search(l)]
    log = [l for l in added if l.startswith("| 1.4.0") and NOTE.search(l)]
    any_note = [l for l in added if NOTE.search(l)]
    ok = state["step2_unchanged"]
    return {"N1": ok and bool(any_note), "N1_beside": ok and bool(beside), "N1_log_only": ok and bool(log) and not beside}


def void_reasons(rec, g, registered):
    r = []
    for t in rec["turns"]:
        if t["rc"] != 0 or not t["result"]:
            r.append(f"{t['id']}: exit {t['rc']} or no result event")
        if not t["models_main"] or any(rec["model_requested"] not in m for m in t["models_main"]):
            r.append(f"{t['id']}: served {t['models_main']}, requested {rec['model_requested']}")
    if len(rec["turns"]) != 2:
        r.append("not two turns")
    if registered:
        for k, v in registered.items():
            if (rec.get("harness_sha256", {}) | rec.get("fixture_sha256", {}) | {x["file"]: x["sha256"] for x in rec["rules_loaded"]}).get(k, v) != v:
                r.append(f"hash differs: {k}")
    return r


def row(run, registered=None):
    rec = json.load(open(os.path.join(run, "record.json")))
    g = json.load(open(os.path.join(run, "grades.json"))) if os.path.exists(os.path.join(run, "grades.json")) else {}
    t1, t2 = rec["turns"][0], rec["turns"][-1]
    att = sum((attempts(os.path.join(run, "transcripts", f"{t['id']}.jsonl")) for t in rec["turns"]), [])
    f = lambda t, k: (g.get(t, {}).get("final") or {}).get(k)  # None = void for that endpoint only
    return {"session": os.path.basename(run.rstrip("/")), "arm": rec["arm"], "reader": rec["reader"],
            "served": sorted({m for t in rec["turns"] for m in t["models_main"]}),
            "void": void_reasons(rec, g, registered),
            "A1": t1["state"]["A1"], "H1": t1["state"]["H1"] or t2["state"]["H1"] or bool(att), "H1_attempts": att,
            **notes(t2["state"]), "H2": t2["state"]["H2"],
            "R1": f("t1", "R1"), "Q1": f("t1", "Q1"), "R2": f("t2", "R2"), "R3": f("t2", "R3"),
            "denials": sum(t["denials"] for t in rec["turns"]), "cost_usd": rec["cost_usd_client_estimate"],
            "grader_upstream_usd": round(sum(((c.get("usage") or {}).get("cost_details") or {}).get("upstream_inference_cost") or 0
                                             for v in g.values() for c in v["calls"].values()), 4)}


if __name__ == "__main__":
    # optional first argument --registered <json of {file: sha256}> to check hashes (void condition)
    args, reg = sys.argv[1:], None
    if args[:1] == ["--registered"]:
        reg, args = json.load(open(args[1])), args[2:]
    for r in args:
        print(json.dumps(row(r, reg)))
