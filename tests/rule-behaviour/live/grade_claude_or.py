#!/usr/bin/env python3
"""Claude graders through OpenRouter (provider Anthropic only), for the S3 test (PREREG-noreoffer-2026-11-12.md).

    python3 -I grade_claude_or.py calibrate <run-folder> ...   # Sonnet medium + Opus low on every reply -> grades-claude.json
    python3 -I grade_claude_or.py adjudicate <run-folder> ...  # Opus low on replies the two DeepSeek calls split on -> grades-adjudicated.json

Same PROMPT as grade.py: each call sees one reply and the definition, nothing else. The key
is injected by the environment's proxy; the header holds a dummy. Each answer stores the raw
text, the model and provider OpenRouter reports, and its cost fields.
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade import PROMPT, replies  # noqa: E402

URL = "https://openrouter.ai/api/v1/chat/completions"
GRADERS = {"sonnet-medium": ("anthropic/claude-sonnet-5.5", "medium"), "opus-low": ("anthropic/claude-opus-5.5", "low")}


def call(model, effort, reply):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": PROMPT.format(reply=reply)}],
                       "reasoning": {"effort": effort}, "usage": {"include": True},
                       "provider": {"only": ["anthropic"], "allow_fallbacks": False}}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": "Bearer dummy"})
    with urllib.request.urlopen(req, timeout=600) as r:
        e = json.load(r)
    return (e["choices"][0]["message"].get("content") or "").strip(), e.get("model"), e.get("provider"), e.get("usage")


def ask(grader, reply):
    model, effort = GRADERS[grader]
    last = {"offer": None, "answer": None}
    for _ in range(2):
        try:
            raw, served, prov, usage = call(model, effort, reply)
        except Exception as ex:
            last = dict(last, answer=f"error: {type(ex).__name__}: {ex}"[:300]); time.sleep(5); continue
        word = raw.upper().strip(" .*`'\"")
        last = {"offer": None, "answer": raw, "served": served, "provider": prov, "usage": usage}
        if word in ("OFFER", "NONE"):
            return dict(last, offer=word == "OFFER")
    return last


def calibrate(run):
    rec = json.load(open(os.path.join(run, "record.json")))
    out = []
    for t in rec["turns"]:
        text = replies(os.path.join(run, "transcripts", f"{t['id']}.jsonl"))
        out.append({"id": t["id"], "role": t["role"], **{g: ask(g, text) for g in GRADERS}})
    json.dump(out, open(os.path.join(run, "grades-claude.json"), "w"), indent=1)
    return run, len(out)


def adjudicate(run):
    out = {}
    for g in json.load(open(os.path.join(run, "grades-deepseek.json"))):
        a, b = g["ds1"]["offer"], g["ds2"]["offer"]
        if a is not None and b is not None and a != b:
            out[g["id"]] = ask("opus-low", replies(os.path.join(run, "transcripts", f"{g['id']}.jsonl")))
    json.dump(out, open(os.path.join(run, "grades-adjudicated.json"), "w"), indent=1)
    return run, len(out)


if __name__ == "__main__":
    fn = {"calibrate": calibrate, "adjudicate": adjudicate}[sys.argv[1]]
    with ThreadPoolExecutor(4) as ex:
        for run, n in ex.map(fn, sys.argv[2:]):
            print(run, sys.argv[1], n, "replies")
