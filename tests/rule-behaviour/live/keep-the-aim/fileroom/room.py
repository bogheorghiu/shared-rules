#!/usr/bin/env python3
"""A shared room in one file. Pull, never push.

  room.py post --who NAME --text-file F      append a message (or --text "...")
  room.py read --who NAME [--since N] [--wait S]
      print every message with id > N (default: after the last one NAME read).
      If nothing new from someone else, wait up to S seconds (default 120) for one.
  room.py status                              print message count and whether FINAL was posted

Messages live in room.jsonl (one JSON object per line); room.md is the readable copy.
Appends take an exclusive lock, so concurrent posts cannot interleave.
"""
import argparse, fcntl, json, os, sys, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J, MD, SEEN = (os.path.join(HERE, f) for f in ("room.jsonl", "room.md", ".seen.json"))

def load():
    if not os.path.exists(J):
        return []
    with open(J) as f:
        return [json.loads(l) for l in f if l.strip()]

def final_posted(msgs):
    return any(l.strip().startswith("FINAL:") for m in msgs if m.get("role") == "decider" for l in m["text"].splitlines())

def post(who, text, role):
    with open(J, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0); n = sum(1 for l in f if l.strip())
        m = {"id": n + 1, "who": who, "role": role, "t": round(time.time(), 1), "text": text}
        f.write(json.dumps(m) + "\n"); f.flush()
        with open(MD, "a") as g:
            g.write(f"\n### [{m['id']}] {who}\n\n{text}\n")
        fcntl.flock(f, fcntl.LOCK_UN)
    return m["id"]

def seen_get(who):
    try: return json.load(open(SEEN)).get(who, 0)
    except Exception: return 0

def seen_set(who, n):
    try: d = json.load(open(SEEN))
    except Exception: d = {}
    d[who] = max(d.get(who, 0), n); json.dump(d, open(SEEN, "w"))

def read(who, since, wait):
    since = seen_get(who) if since is None else since
    end = time.time() + wait
    while True:
        msgs = load()
        new = [m for m in msgs if m["id"] > since]
        if any(m["who"] != who for m in new) or time.time() >= end or final_posted(msgs):
            break
        time.sleep(3)
    for m in new:
        print(f"[{m['id']}] {m['who']}:\n{m['text']}\n")
    if new: seen_set(who, new[-1]["id"])
    if final_posted(msgs): print("(FINAL has been posted: the room is closed.)")
    elif not new: print("(nothing new yet)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("post"); p.add_argument("--who", required=True); p.add_argument("--text"); p.add_argument("--text-file"); p.add_argument("--role", default="member"); p.add_argument("--force", action="store_true")
    r = sp.add_parser("read"); r.add_argument("--who", required=True); r.add_argument("--since", type=int); r.add_argument("--wait", type=float, default=120)
    sp.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "post":
        text = a.text if a.text is not None else open(a.text_file).read()
        msgs = load()
        if final_posted(msgs): sys.exit("room closed: FINAL already posted")
        unread = [m["id"] for m in msgs if m["id"] > seen_get(a.who) and m["who"] != a.who]
        if unread and not a.force:  # observed: a FINAL landed blind to five posts that arrived after the decider's last read
            sys.exit(f"not posted: {len(unread)} unread message(s) {unread}; read first (or --force)")
        mid = post(a.who, text, a.role); seen_set(a.who, mid); print("posted", mid)
    elif a.cmd == "read":
        read(a.who, a.since, a.wait)
    else:
        msgs = load(); print(json.dumps({"messages": len(msgs), "final": final_posted(msgs)}))
