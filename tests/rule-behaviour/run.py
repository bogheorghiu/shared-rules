#!/usr/bin/env python3
"""Behaviour test for staged rules: does a rule change what a model does, where it should?

Design and ship rule: PREREG-2026-11-11.md in this folder (written before any run).
Each case in cases.json is a conversation. A reader model continues it with the shipped
rule pack as its system prompt (arm `base`), or with the pack plus one or more
candidate rule files (other arms). Blind graders answer each case's yes/no checks about
the reply; a run passes when every grader's every answer matches the case.

Spends real tokens through an OpenAI-compatible chat API; not run in CI.

    python3 -I tests/rule-behaviour/run.py --out results/r2 --cases cases-r2.json \
        --arm base --arm closure=candidates/closure-r2.md [--reader MODEL] [--n 3]
    python3 -I tests/rule-behaviour/run.py --out results/r1 --report
"""
import argparse, concurrent.futures as cf, glob, json, os, ssl, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "..", "..", "plugins", "shared-rules", "rules")
API = os.environ.get("RULE_TEST_API", "https://openrouter.ai/api/v1/chat/completions")
# The key is injected by the environment's proxy or read from RULE_TEST_KEY; never stored here.
KEY = os.environ.get("RULE_TEST_KEY", "proxy-injected")
READER = "anthropic/claude-haiku-5.5"
GRADERS = ["anthropic/claude-sonnet-5.5", "openai/gpt-6.1-terra"]
TIEBREAK = "anthropic/claude-opus-5.5"
CASES = "cases.json"

FRAME = (
    "You are a coding assistant working with a user in a terminal session on their repository. "
    "In this exchange you act by writing lines of the form `TOOL: <command or file operation>`; "
    "they run after your message, and their results arrive in the user's next message. "
    "The rules below are installed in this session.\n\n"
)


def pack(extra):
    parts = []
    for p in sorted(glob.glob(os.path.join(RULES, "*.md"))) + list(extra):
        parts.append(f"=== rule: {os.path.basename(p)} ===\n{open(p).read().strip()}")
    return FRAME + "\n\n".join(parts)


def chat(model, messages, max_tokens, tries=3):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if model.startswith("anthropic/"):
        body["provider"] = {"only": ["anthropic"]}
    req = urllib.request.Request(API, json.dumps(body).encode(), {
        "Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180, context=ssl.create_default_context()) as r:
                d = json.load(r)
            c = d["choices"][0]
            text = c["message"].get("content") or ""
            if c.get("finish_reason") == "stop" and text.strip():
                return {"text": text, "id": d.get("id"), "served": d.get("model"),
                        "finish": c.get("finish_reason"), "usage": d.get("usage", {})}
            last = f"finish={c.get('finish_reason')} empty={not text.strip()}"
        except Exception as e:  # a void call is retried, then recorded as void
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 * (i + 1))
    return {"void": last}


def load_cases():
    d = json.load(open(os.path.join(HERE, CASES)))
    frag = d["fragments"]
    for c in d["cases"]:
        c["messages"] = [{"role": r, "content": frag[t[1:]] if t.startswith("@") else t}
                         for r, t in c["messages"]]
        if isinstance(c["checks"], str):
            c["checks"] = d["shared_checks"][c["checks"][1:]]
    return d["cases"]


def grade(model, case, reply):
    qs = "\n".join(f"{i + 1}. {k['q']}" for i, k in enumerate(case["checks"]))
    convo = "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in case["messages"])
    prompt = (
        "Below is a conversation between a user and a coding assistant, then the assistant's next "
        "reply. Answer each question about THE REPLY ONLY, from what it literally says. The "
        "assistant acts by writing `TOOL:` lines.\n\n"
        f"<conversation>\n{convo}\n</conversation>\n\n<reply>\n{reply}\n</reply>\n\n"
        f"Questions:\n{qs}\n\n"
        'Answer with JSON only: {"answers": ["yes" or "no", ...], "evidence": ["short quote from '
        'the reply or \'none\'", ...]} with one entry per question, in order.')
    for _ in range(2):
        r = chat(model, [{"role": "user", "content": prompt}], 4000)
        if "void" in r:
            continue
        t = r["text"]
        try:
            j = json.loads(t[t.index("{"): t.rindex("}") + 1])
            a = [str(x).strip().lower() for x in j["answers"]]
            if len(a) == len(case["checks"]) and all(x in ("yes", "no") for x in a):
                return {"answers": a, "evidence": j.get("evidence"), "id": r["id"]}
        except (ValueError, KeyError):
            pass
    return {"void": "grader gave no parsable answer"}


def one(job):
    arm, system, case, k, reader, out = job
    path = os.path.join(out, f"{arm}__{reader.replace('/', '_')}__{case['id']}__{k}.json")
    if os.path.exists(path):
        return
    rec = {"arm": arm, "case": case["id"], "rule": case["rule"], "kind": case["kind"], "k": k,
           "reader": reader, "expect": [c["expect"] for c in case["checks"]]}
    r = chat(reader, [{"role": "system", "content": system}] + case["messages"], 3000)
    rec["reply"] = r
    if "void" not in r:
        rec["grades"] = {g: grade(g, case, r["text"]) for g in GRADERS}
        got = [v.get("answers") for v in rec["grades"].values()]
        if None not in got and got[0] != got[1]:
            rec["grades"][TIEBREAK] = grade(TIEBREAK, case, r["text"])
    json.dump(rec, open(path, "w"), indent=1)


def verdict(rec):
    """pass / fail / void for one run: majority of graders, each all-checks-match."""
    if "void" in rec["reply"]:
        return "void"
    votes = [g["answers"] == rec["expect"] for g in rec["grades"].values() if "answers" in g]
    if len(votes) < 2:
        return "void"
    return "pass" if sum(votes) * 2 > len(votes) else "fail"


def report(out):
    recs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out, "*.json")))]
    table, toks = {}, {}
    for r in recs:
        key = (r["reader"], r["arm"])
        table.setdefault(key, {}).setdefault(r["case"], []).append(verdict(r))
        if r["rule"] == "overhead" and "void" not in r["reply"]:
            toks.setdefault(key, []).append(r["reply"]["usage"].get("completion_tokens", 0))
    cases = sorted({r["case"] for r in recs})
    for key in sorted(table):
        print(f"\n## reader {key[0]} | arm {key[1]}")
        for c in cases:
            v = table[key].get(c)
            if v:
                print(f"{c}: {v.count('pass')}/{len(v) - v.count('void')} pass"
                      + (f", {v.count('void')} void" if "void" in v else ""))
        if key in toks:
            print(f"overhead completion tokens: mean {sum(toks[key]) / len(toks[key]):.0f} (n={len(toks[key])})")
    splits = sum(1 for r in recs if TIEBREAK in r.get("grades", {}))
    print(f"\nruns {len(recs)}; grader splits sent to the tiebreak: {splits}")


def main():
    global CASES
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--arm", action="append", default=[],
                    help="NAME or NAME=file[,file]: the shipped pack plus these rule files")
    ap.add_argument("--reader", default=READER)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--only", help="comma-separated rule names: closure,dy,overhead")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cases", default=CASES, help="case file in this folder")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    CASES = a.cases
    out = os.path.join(HERE, a.out)
    os.makedirs(out, exist_ok=True)
    if not a.report:
        cases = [c for c in load_cases() if not a.only or c["rule"] in a.only.split(",")]
        jobs = []
        for spec in a.arm:
            name, _, files = spec.partition("=")
            extra = [os.path.join(HERE, f) for f in files.split(",") if f]
            jobs += [(name, pack(extra), c, k, a.reader, out) for c in cases for k in range(a.n)]
        with cf.ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(one, jobs))
    report(out)


if __name__ == "__main__":
    sys.exit(main())
