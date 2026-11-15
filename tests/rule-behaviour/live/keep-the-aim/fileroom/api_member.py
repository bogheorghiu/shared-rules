#!/usr/bin/env python3
"""A third-party API member of the file room: reads the room, calls its model, posts when it has something.

  api_member.py --name DeepSeekFlash --max-calls 8
Calls DeepSeek's chat API (the proxy injects the key). The model answers each new batch of room messages
with either a post or the single word PASS. Stops at FINAL or after --max-calls model calls.
"""
import argparse, json, os, subprocess, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOM = os.path.join(HERE, "room.py"); ROOT = os.path.dirname(HERE)

def sh(*a):
    return subprocess.run([sys.executable, "-I", ROOM, *a], capture_output=True, text=True).stdout

def call(msgs):
    body = {"model": "deepseek-flash", "messages": msgs, "max_tokens": 6000, "thinking": {"type": "enabled"}, "reasoning_effort": "high"}
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return d["choices"][0]["message"].get("content") or "", d.get("usage", {})

ap = argparse.ArgumentParser(); ap.add_argument("--name", default="DeepSeekFlash"); ap.add_argument("--max-calls", type=int, default=8)
a = ap.parse_args()
ctx = open(os.path.join(ROOT, "context.md")).read() if os.path.exists(os.path.join(ROOT, "context.md")) else ""
system = (open(os.path.join(ROOT, "QUESTION.md")).read() + "\n\n" + ctx +
          f"\n\nYou are {a.name}, one member of a small council with Fable (who has the final say) and Sonnet. "
          "Each user message brings you the room's new messages. Reply with the text of one post when you have "
          "something to add (a correction, a missed cost, a better rule), or with exactly PASS. Refer to others' "
          "messages by [id]. Keep posts short.")
msgs = [{"role": "system", "content": system}]
log = open(os.path.join(ROOT, "api_member.log"), "a")
calls = 0; pin = pout = 0
while calls < a.max_calls:
    got = sh("read", "--who", a.name, "--wait", "240")
    log.write(f"{time.time():.0f} read {len(got)} chars\n"); log.flush()
    if "FINAL has been posted" in got:
        break
    msgs.append({"role": "user", "content": "Room, new since you last read:\n\n" + got})
    text, u = call(msgs); calls += 1
    pin += u.get("prompt_tokens", 0); pout += u.get("completion_tokens", 0)
    msgs.append({"role": "assistant", "content": text})
    log.write(f"{time.time():.0f} call {calls} out={u.get('completion_tokens')} pass={text.strip()=='PASS'}\n"); log.flush()
    if text.strip() and text.strip() != "PASS":
        log.write(sh("post", "--who", a.name, "--text", text)); log.flush()
log.write(f"end calls={calls} est_usd={(pin*0.038+pout*0.5)/1e6:.4f}\n")
