#!/usr/bin/env python3
"""Send one brief to several models (streamed) and save each answer. See PREREG: panel critique, not gating.

    python3 -I panel/panel.py panel/brief-r1.md panel/r1 candidates/closure-r1.md:CLOSURE candidates/dy-a-r1.md:DY-A ...
"""
import concurrent.futures as cf, glob, json, os, ssl, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get("RULE_TEST_API", "https://openrouter.ai/api/v1/chat/completions")
KEY = os.environ.get("RULE_TEST_KEY", "proxy-injected")
ROSTER = [  # one reasoning control per call; budgets leave room for the answer
    ("anthropic/claude-opus-5.5", {"reasoning": {"max_tokens": 16000}, "max_tokens": 40000, "provider": {"only": ["anthropic"]}}),
    ("openai/gpt-6.1-sol", {"reasoning": {"effort": "high"}, "max_tokens": 40000}),
    ("google/gemini-4-carbon", {"reasoning": {"effort": "high"}, "max_tokens": 40000}),
    ("moonshotai/kimi-k3.1-pro", {"reasoning": {"effort": "high"}, "max_tokens": 60000}),
    ("deepseek/deepseek-v4-pro-0813", {"reasoning": {"effort": "high"}, "max_tokens": 60000}),
]


def call(model, extra, prompt, out):
    body = dict(extra, model=model, stream=True, messages=[{"role": "user", "content": prompt}])
    req = urllib.request.Request(API, json.dumps(body).encode(), {
        "Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    text, meta = [], {"model": model}
    try:
        with urllib.request.urlopen(req, timeout=1500, context=ssl.create_default_context()) as r:
            for line in r:
                line = line.decode().strip()
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                d = json.loads(line[6:])
                meta["id"] = d.get("id", meta.get("id"))
                if d.get("usage"):
                    meta["usage"] = d["usage"]
                for c in d.get("choices", []):
                    text.append((c.get("delta") or {}).get("content") or "")
                    meta["finish"] = c.get("finish_reason") or meta.get("finish")
                if d.get("error"):
                    meta["error"] = d["error"]
    except Exception as e:
        meta["error"] = f"{type(e).__name__}: {e}"
    name = model.replace("/", "_")
    open(os.path.join(out, name + ".md"), "w").write("".join(text))
    json.dump(meta, open(os.path.join(out, name + ".meta.json"), "w"), indent=1)
    return meta


def main():
    brief, out, *texts = sys.argv[1:]
    out = os.path.join(HERE, "..", out)
    os.makedirs(out, exist_ok=True)
    rules = sorted(glob.glob(os.path.join(HERE, "..", "..", "..", "plugins", "shared-rules", "rules", "*.md")))
    prompt = open(os.path.join(HERE, "..", brief)).read() + "\n\n# SHIPPED PACK\n\n" + "\n\n".join(
        f"=== {os.path.basename(p)} ===\n{open(p).read().strip()}" for p in rules)
    for t in texts:
        path, label = t.split(":")
        prompt += f"\n\n# DRAFT {label}\n\n{open(os.path.join(HERE, '..', path)).read().strip()}"
    with cf.ThreadPoolExecutor(len(ROSTER)) as ex:
        for m in ex.map(lambda r: call(r[0], r[1], prompt, out), ROSTER):
            print(m.get("model"), m.get("finish"), m.get("error"), (m.get("usage") or {}).get("cost"))


if __name__ == "__main__":
    main()
