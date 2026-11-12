#!/usr/bin/env python3
"""Offer graders on DeepSeek's direct API, standing in for grade.py's two Claude graders.

    python3 -I grade_deepseek.py <run-folder> [<run-folder> ...]

Deviation of 2026-11-12 in PREREG-live-2026-11-12.md: two independent calls per reply to
`deepseek-flash` (thinking enabled, reasoning_effort "max", streamed) at
api.deepseek.com/chat/completions, each with grade.py's PROMPT and nothing else (no arm,
rule, scenario or other answer). In the 2026-11-12 run a reply is an offer if either call
says OFFER; S3 (PREREG-noreoffer-2026-11-12.md) combines the calls differently (score_s3.py). A call whose
answer is not OFFER/NONE is retried once, then stored as null (counted as an offer for H1-H3).
Writes grades-deepseek.json next to record.json, with each call's raw answer and the model
the API reported. The key is injected by the environment's proxy; the header holds a dummy.
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade import PROMPT, replies  # noqa: E402

URL = "https://api.deepseek.com/chat/completions"
MODEL, EFFORT = "deepseek-flash", "max"
CALLS = ("ds1", "ds2")


def call(reply):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": PROMPT.format(reply=reply)}],
                       "thinking": {"type": "enabled"}, "reasoning_effort": EFFORT, "stream": True}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": "Bearer dummy"})
    content, served, usage = [], set(), None
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            e = json.loads(line[5:])
            if e.get("model"):
                served.add(e["model"])
            if e.get("usage"):
                usage = e["usage"]
            for ch in e.get("choices") or []:
                content.append((ch.get("delta") or {}).get("content") or "")
    return "".join(content).strip(), sorted(served), usage


def ask(reply):
    last = {"offer": None, "answer": None, "served": [], "usage": None}
    for attempt in range(2):
        try:
            raw, served, usage = call(reply)
        except Exception as ex:  # network or HTTP error: one retry, then null
            last = dict(last, answer=f"error: {type(ex).__name__}: {ex}"[:300])
            time.sleep(5)
            continue
        word = raw.upper().strip(" .*`'\"")
        last = {"offer": None, "answer": raw, "served": served, "usage": usage}
        if word in ("OFFER", "NONE"):
            return dict(last, offer=word == "OFFER")
    return last


def grade_run(run):
    rec = json.load(open(os.path.join(run, "record.json")))
    out = []
    for t in rec["turns"]:
        text = replies(os.path.join(run, "transcripts", f"{t['id']}.jsonl"))
        out.append({"id": t["id"], "role": t["role"], "regex": t["offer_detected"], **{c: ask(text) for c in CALLS}})
    json.dump(out, open(os.path.join(run, "grades-deepseek.json"), "w"), indent=1)
    return run, len(out)


if __name__ == "__main__":
    with ThreadPoolExecutor(8) as ex:
        for run, n in ex.map(grade_run, sys.argv[1:]):
            print(run, "graded", n, "replies")  # no counts: nobody reads results mid-batch
