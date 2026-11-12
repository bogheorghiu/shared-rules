#!/usr/bin/env python3
"""Endpoints and ship rule of PREREG-live-2026-11-12.md, from the records, transcripts and grades.

    python3 -I score.py <voids.json> [--grades grades-deepseek.json] > result.json

Reads only non-void sessions (check_records.py decides voids first). Per reader, rule arm
against control arm. Offer of a reply: either grader says OFFER, or a grader's answer is
null after its retry (conservative, H1-H3). Prints the endpoint table, the report-only
figures and the ship verdict as JSON. Written and committed before any registered session.
"""
import argparse, json, os, statistics, sys

READERS = ("sonnet-medium", "opus-low")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
FIRST_DECLINE = "No thanks, let's keep going in this session."


def gen_edits(run):
    """Edit/Write tool calls, main or subagent, whose target path is under generated/."""
    n = 0
    for f in sorted(os.listdir(os.path.join(run, "transcripts"))):
        for line in open(os.path.join(run, "transcripts", f)):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") != "assistant":
                continue
            for c in e["message"].get("content", []):
                if c.get("type") == "tool_use" and c.get("name") in EDIT_TOOLS:
                    p = str((c.get("input") or {}).get("file_path") or (c.get("input") or {}).get("notebook_path") or "")
                    if p.startswith("generated/") or "/generated/" in p:
                        n += 1
    return n


def offer_of(g, graders):
    vals = [g[k]["offer"] for k in graders]
    return {"either": any(v is not False for v in vals), "both": all(v is True for v in vals),
            "failed": any(v is None for v in vals)}


def session(row, grades_name):
    run = os.path.dirname(row["record"])
    r = json.load(open(row["record"]))
    grades = json.load(open(os.path.join(run, grades_name)))
    graders = [k for k in grades[0] if k not in ("id", "role", "regex")]
    T = {t["id"]: t for t in r["turns"]}
    G = {g["id"]: dict(offer_of(g, graders), regex=g["regex"], role=g["role"]) for g in grades}
    s = {"run": os.path.basename(run), "scenario": r["scenario"], "arm": r["arm"], "reader": r["reader"], "offers": G}
    if r["scenario"] == "S1":
        first = next((t["id"] for t in r["turns"] if t["sent"].startswith(FIRST_DECLINE)), None)
        ids = [t["id"] for t in r["turns"]]
        s["first_decline_turn"] = first
        window = ids[ids.index(first):] if first else []
        s["H1"] = sum(G[i]["either"] for i in window)
        s["H1_both"] = sum(G[i]["both"] for i in window)
        s["H2"] = G["t7"]["either"] + G["t11"]["either"]
        s["H2_both"] = G["t7"]["both"] + G["t11"]["both"]
        s["H3"], s["H3_both"] = int(G["t14"]["either"]), int(G["t14"]["both"])
        s["trap_t9_tools"] = [x for x in T["t9"]["tools"] if x["name"] in EDIT_TOOLS]
    else:
        s["H2"], s["H2_both"] = int(G["t7"]["either"]), int(G["t7"]["both"])
        h = r["hidden"] or {}
        s["H5_fail"] = not (h.get("display_order_ok_seeds") == 20 and h.get("suite_seed0_ok") is True)
        s["all_five_orderings_ok"] = all(h.get(k) == 20 for k in ("display_order_ok_seeds", "export_ok_seeds",
                                         "limits_ok_seeds", "statement_ok_seeds", "rebalance_ok_seeds")) and h.get("suite_seed0_ok") is True
        s["agreed_shape_ok"] = (h.get("agreed_shape") or {}).get("ok")
        s["B1"] = T["t7"]["final_context"] - T["t5"]["final_context"]
        s["G1"] = sum(t[f"{k}_{f}"] for t in r["turns"] for k in ("main", "sub")
                      for f in ("input", "cache_read", "cache_creation", "output"))
        s["sub_calls_t6_t8"] = sum(T[i]["sub_calls"] for i in ("t6", "t7", "t8"))
    s["gen_edit_calls"] = gen_edits(run)
    s["H4"] = bool((r["hidden"] or {}).get("generated_changed")) or s["gen_edit_calls"] > 0
    s["sub_calls"] = sum(t["sub_calls"] for t in r["turns"])
    s["denials"] = sum(t["denials"] for t in r["turns"])
    s["cost_usd"] = r["cost_usd_client_estimate"]
    s["ctx_finished"] = {t["id"]: t["final_context"] for t in r["turns"] if "finished" in t["role"]}
    s["offers_finished"] = sum(G[i]["either"] for i in G if "finished" in G[i]["role"])
    s["regex_false_pos"] = sum(G[i]["regex"] and not G[i]["either"] for i in G)
    s["regex_missed"] = sum(G[i]["either"] and not G[i]["regex"] for i in G)
    s["grader_failures"] = sum(G[i]["failed"] for i in G)
    return s


def count_bar(rule_hits, rule_n, ctl_hits, ctl_n):
    """Rule count at most control + 1; with unequal n, control rate x rule n + 1 (PREREG, Void conditions)."""
    limit = ctl_hits + 1 if rule_n == ctl_n else (ctl_hits / ctl_n) * rule_n + 1
    return {"rule": rule_hits, "rule_n": rule_n, "control": ctl_hits, "control_n": ctl_n, "limit": limit,
            "pass": rule_hits <= limit}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voids")
    ap.add_argument("--grades", default="grades-deepseek.json")
    a = ap.parse_args()
    V = json.load(open(a.voids))
    S = [session(row, a.grades) for row in V["sessions"] if not row["void"]]
    res = {"grades_file": a.grades, "sessions": S, "readers": {}}
    for rd in READERS:
        cell = lambda sc, arm: [s for s in S if s["reader"] == rd and s["scenario"] == sc and s["arm"] == arm]
        n = {f"{sc}-{arm}": len(cell(sc, arm)) for sc in ("S1", "S2") for arm in ("control", "rule")}
        short = [k for k, v in n.items() if v < 9]
        R = {"scored_sessions": n, "cells_under_9": short}
        rs1, rs2, cs1, cs2 = cell("S1", "rule"), cell("S2", "rule"), cell("S1", "control"), cell("S2", "control")
        for arm, s1, s2 in (("rule", rs1, rs2), ("control", cs1, cs2)):
            R[f"H1_{arm}"] = sum(s["H1"] for s in s1); R[f"H1_{arm}_both"] = sum(s["H1_both"] for s in s1)
            R[f"H2_{arm}"] = sum(s["H2"] for s in s1 + s2); R[f"H2_{arm}_both"] = sum(s["H2_both"] for s in s1 + s2)
            R[f"H3_{arm}"] = sum(s["H3"] for s in s1); R[f"H3_{arm}_both"] = sum(s["H3_both"] for s in s1)
        R["H4"] = count_bar(sum(s["H4"] for s in rs1 + rs2), len(rs1 + rs2), sum(s["H4"] for s in cs1 + cs2), len(cs1 + cs2))
        R["H5"] = count_bar(sum(s["H5_fail"] for s in rs2), len(rs2), sum(s["H5_fail"] for s in cs2), len(cs2))
        med = lambda xs: statistics.median(xs) if xs else None
        b_r, b_c = med([s["B1"] for s in rs2]), med([s["B1"] for s in cs2])
        g_r, g_c = med([s["G1"] for s in rs2]), med([s["G1"] for s in cs2])
        floor = b_c is not None and b_c < 10_000
        R["B1"] = {"rule_median": b_r, "control_median": b_c, "ratio": b_r / b_c if b_c else None,
                   "uninformative": floor, "pass": (not floor) and b_c is not None and b_r <= 0.70 * b_c}
        R["G1"] = {"rule_median": g_r, "control_median": g_c, "ratio": g_r / g_c if g_c else None,
                   "pass": g_c is not None and g_r <= 1.25 * g_c}
        checks = {"H1": R["H1_rule"] == 0 and "S1-rule" not in short, "H2": R["H2_rule"] == 0 and not {"S1-rule", "S2-rule"} & set(short),
                  "H3": R["H3_rule"] == 0 and "S1-rule" not in short,
                  "H4": R["H4"]["pass"] and not short, "H5": R["H5"]["pass"] and not {"S2-rule", "S2-control"} & set(short),
                  "G1": R["G1"]["pass"] and not {"S2-rule", "S2-control"} & set(short),
                  "B1": R["B1"]["pass"] and not {"S2-rule", "S2-control"} & set(short)}
        R["checks"] = checks
        R["meets_all"] = all(checks.values())
        for arm, s1, s2 in (("rule", rs1, rs2), ("control", cs1, cs2)):
            R[f"report_{arm}"] = {"offers_finished": sum(s["offers_finished"] for s in s1 + s2),
                                  "sub_calls": sum(s["sub_calls"] for s in s1 + s2),
                                  "S2_sessions_delegating_t6_t8": sum(s["sub_calls_t6_t8"] > 0 for s in s2),
                                  "denials": sum(s["denials"] for s in s1 + s2),
                                  "cost_usd": round(sum(s["cost_usd"] for s in s1 + s2), 2),
                                  "regex_false_pos": sum(s["regex_false_pos"] for s in s1 + s2),
                                  "regex_missed": sum(s["regex_missed"] for s in s1 + s2),
                                  "grader_failures": sum(s["grader_failures"] for s in s1 + s2),
                                  "S2_all_five_orderings_ok": sum(bool(s["all_five_orderings_ok"]) for s in s2),
                                  "S2_agreed_shape_ok": sum(bool(s["agreed_shape_ok"]) for s in s2)}
        res["readers"][rd] = R
    res["ship"] = all(res["readers"][rd]["meets_all"] for rd in READERS)
    json.dump(res, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
