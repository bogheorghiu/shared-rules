#!/usr/bin/env python3
"""Per-session figures from run records: turns, tokens (main/sub, cached/uncached), wall time, cost.

    python3 -I summarize.py <run-folder> [...]

Wall time is first-turn start to last-turn end, taken from the per-turn wall_s sums (each
covers CLI start-up as well as the model's work).
"""
import json, os, sys


def row(run):
    r = json.load(open(os.path.join(run, "record.json")))
    T = r["turns"]
    s = lambda k: sum(t[k] for t in T)
    ctx = {t["id"]: t["final_context"] for t in T}
    return {"session": os.path.basename(run), "turns": len(T), "served": sorted({m for t in T for m in t["models_main"]}),
            "uncached_in": s("main_input") + s("sub_input"), "cache_write": s("main_cache_creation") + s("sub_cache_creation"),
            "cache_read": s("main_cache_read") + s("sub_cache_read"), "out": s("main_output") + s("sub_output"),
            "sub_calls": s("sub_calls"), "wall_s": round(s("wall_s")), "cost_usd": r["cost_usd_client_estimate"],
            "ctx_by_turn": ctx, "denials": s("denials"), "offers_regex": sum(t["offer_detected"] for t in T),
            "commits": len(r["git_log"]) - 1, "hidden": r["hidden"]}


if __name__ == "__main__":
    for run in sys.argv[1:]:
        print(json.dumps(row(run)))
