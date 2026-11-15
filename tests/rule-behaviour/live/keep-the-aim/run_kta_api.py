#!/usr/bin/env python3
"""Cross-check harness (owner's choice, 2026-11-15): the five keep-the-aim turns as a plain tool loop over the API.

    python3 -I run_kta_api.py --arm rule|control --reader sonnet-medium|opus-low --out <dir> [--tag t]

Same fixture, history replay, turns, inbox timing, archives and record.json fields as run_kta.py, so
score_kta.py and grade_kta.py read both. Differences, by design: no Claude Code system prompt, tools or
permission layer. The system prompt holds only the arm's shared rules (the rule arm adds the one new rule)
and the repo's CLAUDE.md, as a loaded project instruction file. Three tools: bash (run_kta.py's allow-list,
and the CLI's own block on shell variables, loops and heredocs), read_file, write_file (inside the repo only).
Calls go to OpenRouter chat/completions, provider pinned to Anthropic, no fallbacks (the BYOK route); the
environment's proxy supplies the key.
"""
import argparse, json, os, re, shlex, shutil, subprocess, sys, time, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_kta as K  # noqa: E402  (fixture, turns, allow-list, history replay, git helper)

MODELS = {"sonnet-medium": ("anthropic/claude-sonnet-5.5", "medium"), "opus-low": ("anthropic/claude-opus-5.5", "low")}
ALLOWED_FIRST = {c.split()[0] for c in K.CMDS}
TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Run a shell command in the repository root.",
                                      "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a file in the repository.",
                                      "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or overwrite a file in the repository.",
                                      "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                                                     "required": ["path", "content"]}}},
]


def denied_bash(cmd):
    if re.search(r"\$|`|<<|\bfor\b|\bwhile\b|\buntil\b", cmd):
        return "denied: shell variables, loops and heredocs are not allowed"
    try:  # split on shell operators outside quotes only
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        return "denied: unparsable command"
    segs, cur = [], []
    for t in toks:
        if t and set(t) <= set(";&|"):
            segs.append(cur); cur = []
        else:
            cur.append(t)
    segs.append(cur)
    for words in segs:
        if not words:
            continue
        first = words[0]
        if first not in ALLOWED_FIRST and not first.startswith(("./scripts/", "scripts/")):
            return f"denied: {first} is not on the allow-list"
        if first == "git" and len(words) > 1 and f"git {words[1]}" not in K.CMDS:
            return f"denied: git {words[1]} is not on the allow-list"
    return None


def inside(work, path):
    p = os.path.realpath(os.path.join(work, path))
    return p if p == work or p.startswith(work + os.sep) else None


def run_tool(work, name, args):
    if name == "bash":
        why = denied_bash(args.get("command", ""))
        if why:
            return why, True
        r = subprocess.run(args["command"], shell=True, cwd=work, capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, **K.GIT_ENV, HOME=os.path.dirname(work)))
        return (r.stdout + r.stderr)[-20000:] + f"\n(exit {r.returncode})", False
    p = inside(work, args.get("path", ""))
    if not p:
        return "denied: path is outside the repository", True
    if name == "read_file":
        return (open(p, errors="replace").read()[:50000] if os.path.isfile(p) else "no such file"), False
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(args.get("content", ""))
    return f"wrote {os.path.relpath(p, work)}", False


def call(model, effort, messages):
    body = {"model": model, "max_tokens": 16000, "reasoning": {"effort": effort}, "tools": TOOLS, "messages": messages,
            "provider": {"only": ["anthropic"], "allow_fallbacks": False}}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"})
    for attempt in range(3):
        try:
            return json.load(urllib.request.urlopen(req, timeout=600))
        except Exception as e:  # one transient failure is not a session error; three are
            err = e
            time.sleep(5 * (attempt + 1))
    raise err


def write_transcripts(messages, root):
    """One CLI-shaped transcripts/<turn>.jsonl per turn (assistant text and tool_use entries only), so
    grade_kta.py reads API sessions the same way as Claude Code sessions."""
    os.makedirs(os.path.join(root, "transcripts"), exist_ok=True)
    turn, out = 0, None
    for m in messages:
        if m.get("role") == "user" and isinstance(m.get("content"), str):
            turn += 1
            out = open(os.path.join(root, "transcripts", f"T{turn}.jsonl"), "w")
        elif m.get("role") == "assistant" and out:
            content = ([{"type": "text", "text": m["content"]}] if m.get("content") else []) + \
                      [{"type": "tool_use", "name": tc["function"]["name"]} for tc in m.get("tool_calls") or []]
            out.write(json.dumps({"type": "assistant", "message": {"content": content}}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["control", "rule"])
    ap.add_argument("--reader", required=True, choices=sorted(MODELS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="api")
    ap.add_argument("--fixture", default=os.path.join(HERE, "fixture"))
    a = ap.parse_args()
    model, effort = MODELS[a.reader]
    name = f"{a.tag}-{a.arm}-{a.reader}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    root = os.path.join(a.out, name)
    work, adir = os.path.join(root, "work"), os.path.join(root, "archive")
    os.makedirs(root)
    shutil.copytree(os.path.join(a.fixture, "repo"), work)
    work = os.path.realpath(work)
    K.git(work, "init", "-q", "-b", "main")
    K.replay_history(work, a.fixture)
    base = K.git(work, "rev-parse", "HEAD")
    rules = K.arm_rules(a.arm)
    system = "\n\n".join(open(f).read() for f in rules)
    system += ("\n\n# Project instructions (CLAUDE.md in the repository root)\n\n" + open(os.path.join(work, "CLAUDE.md")).read()
               + f"\n\nYou are a coding agent working in the git repository at {work}. Use the tools to do the user's tasks.")
    messages = [{"role": "system", "content": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]}]
    rec = {"arm": a.arm, "reader": a.reader, "harness": "api-loop", "model_requested": model, "effort_requested": effort,
           "rules_loaded": [{"file": os.path.relpath(f, K.REPO), "sha256": K.sha(f)} for f in rules], "base_commit": base,
           "turns": [], "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "route": "OpenRouter /api/v1/chat/completions, provider anthropic only, allow_fallbacks false",
           "harness_sha256": {n: K.sha(os.path.join(HERE, n)) for n in ("run_kta_api.py", "run_kta.py", "make_fixture.py")}}
    total = 0.0
    for tid, text in K.TURNS:
        if tid in K.INBOX:
            shutil.copytree(os.path.join(a.fixture, "inbox", K.INBOX[tid]), os.path.join(work, "inbox"), dirs_exist_ok=True)
        messages.append({"role": "user", "content": text})
        t0, texts, tools, denials, served, cost, rc = time.time(), [], [], 0, set(), 0.0, 0
        for _ in range(40):
            try:
                r = call(model, effort, messages)
            except Exception as e:
                rc = f"error: {str(e)[:200]}"
                break
            served.add(r.get("model"))
            u = r.get("usage") or {}
            cost += (u.get("cost_details") or {}).get("upstream_inference_cost") or u.get("cost") or 0
            msg = r["choices"][0]["message"]
            keep = {k: msg[k] for k in ("role", "content", "tool_calls", "reasoning_details") if msg.get(k) is not None}
            messages.append(keep)
            if msg.get("content"):
                texts.append(msg["content"])
            calls = msg.get("tool_calls") or []
            if not calls:
                break
            for tc in calls:
                fn = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"].get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                out, was_denied = run_tool(work, fn, args)
                denials += was_denied
                shown = {"bash": "Bash", "read_file": "Read", "write_file": "Write"}.get(fn, fn)
                inp = args.get("command") if fn == "bash" else json.dumps({"file_path": os.path.join(work, args.get("path", ""))})
                tools.append({"thread": "main", "name": shown, "input": (inp or "")[:300]})
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": out})
        total += cost
        rec["turns"].append({"id": tid, "sent": text, "rc": rc, "wall_s": round(time.time() - t0, 1), "head": K.git(work, "rev-parse", "HEAD"),
                             "reply": "\n".join(texts), "tools": tools, "denials": denials, "models_main": sorted(served),
                             "result": {"total_cost_usd": round(total, 4)}})
        shutil.copytree(work, os.path.join(adir, tid, "repo"), symlinks=True)
        print(f"{name} {tid}: rc={rc} head={rec['turns'][-1]['head'][:8]} tools={len(tools)} denials={denials} cost={round(cost, 4)}", flush=True)
    json.dump(messages, open(os.path.join(root, "messages.json"), "w"), indent=1)
    write_transcripts(messages, root)
    rec["git_log"] = K.git(work, "log", "--format=%H %s").splitlines()
    rec["cost_usd_client_estimate"] = round(total, 4)
    json.dump(rec, open(os.path.join(root, "record.json"), "w"), indent=1)
    print(f"record: {os.path.join(root, 'record.json')}")


if __name__ == "__main__":
    main()
