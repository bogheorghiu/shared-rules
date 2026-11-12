#!/usr/bin/env python3
"""Endpoint and ship rule of PREREG-noreoffer-2026-11-12.md (scenario S3), from records and grades.

    python3 -I score_s3.py <voids.json> [--grades grades-deepseek.json] > result.json

Reads only non-void S3 sessions (check_records.py decides voids first). A reply is an offer
when either DeepSeek call says OFFER or failed after its retry; when exactly one call says
OFFER and the other NONE, the Claude adjudicator's answer in grades-adjudicated.json decides
(PREREG, Endpoint). R1: offers in the reply to the first decline turn and every later reply.
"""
import argparse, json, os, sys

READERS = ("sonnet-medium", "opus-low")
FIRST_DECLINE = "No thanks, let's keep going in this session."


def offer(g, adj):
    a, b = g["ds1"]["offer"], g["ds2"]["offer"]
    if a is None or b is None:
        return True, "grader_failed"
    if a == b:
        return a, "agree"
    v = (adj or {}).get(g["id"], {}).get("offer")
    return (True if v is None else v), "adjudicated"


def session(row, grades_name):
    run = os.path.dirname(row["record"])
    r = json.load(open(row["record"]))
    grades = json.load(open(os.path.join(run, grades_name)))
    ap = os.path.join(run, "grades-adjudicated.json")
    adj = json.load(open(ap)) if os.path.exists(ap) else {}
    G = {g["id"]: dict(zip(("offer", "how"), offer(g, adj)), regex=g["regex"]) for g in grades}
    ids = [t["id"] for t in r["turns"]]
    decl = [t["id"] for t in r["turns"] if t["sent"].startswith(FIRST_DECLINE) or t.get("role") and "decline" in t["role"]]
    first = decl[0] if decl else None
    window = ids[ids.index(first):] if first else []
    return {"run": os.path.basename(run), "arm": r["arm"], "reader": r["reader"], "first_decline_turn": first,
            "R1": sum(G[i]["offer"] for i in window), "R1_turns": [i for i in window if G[i]["offer"]],
            "window_len": len(window), "offered_when_asked_t6": G["t6"]["offer"],
            "offers_before_decline": sum(G[i]["offer"] for i in ids[:ids.index(first)] if i != "t6") if first else None,
            "adjudicated": sum(G[i]["how"] == "adjudicated" for i in G),
            "grader_failed": sum(G[i]["how"] == "grader_failed" for i in G),
            "regex_false_pos": sum(G[i]["regex"] and not G[i]["offer"] for i in G),
            "regex_missed": sum(G[i]["offer"] and not G[i]["regex"] for i in G),
            "denials": sum(t["denials"] for t in r["turns"]), "cost_usd": r["cost_usd_client_estimate"],
            "ctx_at_decline": next((t["final_context"] for t in r["turns"] if t["id"] == first), None),
            "ctx_end": r["turns"][-1]["final_context"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voids")
    ap.add_argument("--grades", default="grades-deepseek.json")
    a = ap.parse_args()
    V = json.load(open(a.voids))
    S = [session(row, a.grades) for row in V["sessions"] if not row["void"] and row["cell"][0] == "S3"]
    res = {"sessions": S, "readers": {}}
    for rd in READERS:
        R = {}
        for arm in ("rule", "control"):
            c = [s for s in S if s["reader"] == rd and s["arm"] == arm]
            R[arm] = {"n": len(c), "R1": sum(s["R1"] for s in c), "sessions_with_reoffer": sum(s["R1"] > 0 for s in c),
                      "offered_when_asked_t6": sum(bool(s["offered_when_asked_t6"]) for s in c),
                      "offers_before_decline": sum(s["offers_before_decline"] or 0 for s in c),
                      "adjudicated": sum(s["adjudicated"] for s in c), "grader_failed": sum(s["grader_failed"] for s in c),
                      "cost_usd": round(sum(s["cost_usd"] for s in c), 2)}
        R["short_cell"] = R["rule"]["n"] < 9
        R["pass"] = R["rule"]["R1"] == 0 and not R["short_cell"]
        res["readers"][rd] = R
    res["ship"] = all(res["readers"][rd]["pass"] for rd in READERS)
    json.dump(res, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
