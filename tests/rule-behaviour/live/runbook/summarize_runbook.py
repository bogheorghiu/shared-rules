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
            elif name == "Bash" and "RUNBOOK" in i.get("command", "") and re.search(r"bump_version", i.get("command", "")) \
                    and re.search(r"sed\s+-i|\.write|>\s*RUNBOOK|replace\(", i.get("command", "")):
                hits.append(name)
    return hits


def row(run):
    rec = json.load(open(os.path.join(run, "record.json")))
    g = json.load(open(os.path.join(run, "grades.json"))) if os.path.exists(os.path.join(run, "grades.json")) else {}
    t1, t2 = rec["turns"][0], rec["turns"][-1]
    att = sum((attempts(os.path.join(run, "transcripts", f"{t['id']}.jsonl")) for t in rec["turns"]), [])
    f = lambda t, k: (g.get(t, {}).get("final") or {}).get(k)
    return {"session": os.path.basename(run.rstrip("/")), "arm": rec["arm"], "reader": rec["reader"],
            "served": sorted({m for t in rec["turns"] for m in t["models_main"]}),
            "void": any(t["rc"] != 0 for t in rec["turns"]) or len(rec["turns"]) != 2,
            "A1": t1["state"]["A1"], "H1": t1["state"]["H1"] or t2["state"]["H1"] or bool(att), "H1_attempts": att,
            "N1": any(re.search(r"set_version|bump_version|renam", l, re.I) for l in t2["state"]["runbook_lines_added"]), "H2": t2["state"]["H2"],
            "R1": f("t1", "R1"), "Q1": f("t1", "Q1"), "R2": f("t2", "R2"), "R3": f("t2", "R3"),
            "denials": sum(t["denials"] for t in rec["turns"]), "cost_usd": rec["cost_usd_client_estimate"],
            "grader_upstream_usd": round(sum(((c.get("usage") or {}).get("cost_details") or {}).get("upstream_inference_cost") or 0
                                             for v in g.values() for c in v["calls"].values()), 4)}


if __name__ == "__main__":
    for r in sys.argv[1:]:
        print(json.dumps(row(r)))
