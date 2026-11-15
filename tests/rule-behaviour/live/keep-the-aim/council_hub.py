#!/usr/bin/env python3
"""A live design council: several models debate the keep-the-aim test in one shared room.

    python3 -I council_hub.py --brief BRIEF.md --out DIR [--cap-usd 12] [--window 20] [--mock]

Each participant streams its turns from OpenRouter. A relay collects what has arrived from every
stream and, every --window seconds, delivers everything new to all the other participants at once
(one batch per window, not one message per sentence). A participant that is idle starts a turn when
its inbox holds a finished message. A model cannot read while it writes, so a batch that lands while
a model is mid-turn is queued for its next turn; text still being written is shown as "(still
writing)" with what has streamed so far.

Each participant has read-only tools over the full record: the session list, any session's turns
(prompt, reply, tool calls, scores, grades), a grep over all transcripts, and the design documents.
Nothing is loaded whole: the record is about 8 MB.

The run ends when every participant's latest message carries `AGREE: <proposal id>` naming the same
proposal (a proposal is a message that starts with `PROPOSAL <id>:`); or when --cap-usd is reached
(upstream cost as reported by OpenRouter); or when --max-turns per participant is reached. Every
streamed chunk, relay batch and tool call is logged to DIR/log.jsonl, and the room to DIR/room.md.
"""
import argparse, asyncio, glob, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(HERE, "calibration")
DOCS = {"DESIGN.md": os.path.join(HERE, "DESIGN.md"), "CALIBRATION.md": os.path.join(HERE, "CALIBRATION.md"),
        "verify/RESULT-T2-VERIFY.md": os.path.join(HERE, "verify", "RESULT-T2-VERIFY.md")}
for f in ("make_fixture.py", "run_kta.py", "run_kta_api.py", "score_kta.py", "grade_kta.py"):
    DOCS[f] = os.path.join(HERE, f)
for f in glob.glob(os.path.join(HERE, "..", "..", "..", "..", "docs", "staged-rules", "keep-the-aim.md")):
    DOCS["keep-the-aim.md (the rule)"] = f

PARTICIPANTS = [
    {"name": "Fable", "model": "anthropic/claude-fable-5.2", "provider": {"only": ["anthropic"], "allow_fallbacks": False},
     "reasoning": {"effort": "medium"}},
    {"name": "Kimi", "model": "moonshotai/kimi-k3.1-pro:exacto", "provider": None, "reasoning": {"effort": "high"}},
    {"name": "DeepSeek", "model": "deepseek/deepseek-v4-pro-0813", "provider": {"only": ["deepseek"], "allow_fallbacks": False},
     "reasoning": {"effort": "high"}},
]

# ---------- the record, read-only ----------
SESSIONS = {}
for rec in sorted(glob.glob(os.path.join(CAL, "*", "*", "record.json"))):
    d = os.path.dirname(rec)
    SESSIONS[os.path.basename(d)] = {"round": os.path.basename(os.path.dirname(d)), "dir": d}
SCORES = {}
for sf in glob.glob(os.path.join(CAL, "*", "scores*.json")):
    for s in json.load(open(sf)):
        SCORES[s["session"]] = s


def t_list_sessions(args):
    flt = (args.get("filter") or "").lower()
    rows = []
    for sid, m in SESSIONS.items():
        if flt and flt not in sid.lower() and flt not in m["round"].lower():
            continue
        s = SCORES.get(sid, {})
        rows.append({"session": sid, "round": m["round"], **{k: s.get(k) for k in ("E1", "E2", "E2_mode", "E3", "E3_mode") if k in s}})
    return json.dumps(rows[:200])


def t_read_session(args):
    sid = args.get("session", "")
    if sid not in SESSIONS:
        return "no such session"
    rec = json.load(open(os.path.join(SESSIONS[sid]["dir"], "record.json")))
    out = {"session": sid, "round": SESSIONS[sid]["round"], "arm": rec.get("arm"), "reader": rec.get("reader"),
           "harness": rec.get("harness", "claude-code"), "score": SCORES.get(sid)}
    want = args.get("turn")
    turns = []
    for t in rec.get("turns", []):
        if want and t.get("id") != want:
            continue
        turns.append({"id": t.get("id"), "sent": t.get("sent"), "reply": (t.get("reply") or "")[:6000],
                      "tools": [x.get("input", "")[:300] for x in t.get("tools", [])], "rc": t.get("rc")})
    out["turns"] = turns
    g = os.path.join(SESSIONS[sid]["dir"], "grades.json")
    if os.path.exists(g):
        out["grades"] = {k: {kk: vv.get("answer") for kk, vv in v.items()} for k, v in json.load(open(g)).items()}
    return json.dumps(out)[:30000]


def t_grep(args):
    pat = args.get("pattern", "")
    try:
        rx = re.compile(pat, re.I)
    except re.error as e:
        return f"bad pattern: {e}"
    hits = []
    for sid, m in SESSIONS.items():
        for tf in sorted(glob.glob(os.path.join(m["dir"], "transcripts", "*.jsonl"))) + [os.path.join(m["dir"], "record.json")]:
            for i, line in enumerate(open(tf, errors="replace")):
                for mm in rx.finditer(line):
                    a = max(0, mm.start() - 120)
                    hits.append(f"{sid}/{os.path.basename(tf)}:{i}: …{line[a:mm.end() + 120].strip()}…")
                    if len(hits) >= 60:
                        return "\n".join(hits) + "\n(truncated at 60 hits)"
    return "\n".join(hits) or "no hits"


def t_read_doc(args):
    name = args.get("name", "")
    if name not in DOCS:
        return "documents: " + ", ".join(DOCS)
    text = open(DOCS[name], errors="replace").read()
    off = int(args.get("offset") or 0)
    return text[off:off + 40000] + ("\n(more: use offset)" if len(text) > off + 40000 else "")


TOOLS = {"list_sessions": t_list_sessions, "read_session": t_read_session, "grep": t_grep, "read_doc": t_read_doc}
TOOL_SPECS = [
    {"type": "function", "function": {"name": "list_sessions", "description": "List all test sessions with their round and endpoint scores. Optional substring filter (e.g. 'repilot-v3', 'control-opus').",
                                      "parameters": {"type": "object", "properties": {"filter": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "read_session", "description": "Read one session: each turn's prompt, the agent's reply, its tool calls, the script scores and the grader answers. Optional turn id (T1..T5).",
                                      "parameters": {"type": "object", "properties": {"session": {"type": "string"}, "turn": {"type": "string"}}, "required": ["session"]}}},
    {"type": "function", "function": {"name": "grep", "description": "Regex search over every session's transcripts and records. Returns up to 60 hits with context.",
                                      "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "read_doc", "description": "Read a design document or harness file by name (call with an unknown name to list them). 40k characters per call; use offset for more.",
                                      "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "offset": {"type": "integer"}}, "required": ["name"]}}},
]

# ---------- the room ----------
class Room:
    def __init__(self, out, cap, window, max_turns, mock):
        self.out, self.cap, self.window, self.max_turns, self.mock = out, cap, window, max_turns, mock
        self.log = open(os.path.join(out, "log.jsonl"), "a")
        self.cost = 0.0
        self.agreed = None
        self.done = asyncio.Event()
        self.msgs = []                      # finished messages: {"id", "who", "text"}
        self.live = {}                      # who -> text streamed so far in the current turn
        self.seen = {p["name"]: 0 for p in PARTICIPANTS}      # index into msgs each participant has been given
        self.inbox = {p["name"]: [] for p in PARTICIPANTS}    # relay batches waiting for that participant
        self.wake = {p["name"]: asyncio.Event() for p in PARTICIPANTS}
        self.turns = {p["name"]: 0 for p in PARTICIPANTS}
        self.history = {p["name"]: [] for p in PARTICIPANTS}  # that participant's own chat history

    def emit(self, kind, **kw):
        self.log.write(json.dumps({"t": round(time.time(), 2), "kind": kind, **kw}) + "\n"); self.log.flush()

    def post(self, who, text):
        mid = len(self.msgs) + 1
        self.msgs.append({"id": mid, "who": who, "text": text})
        with open(os.path.join(self.out, "room.md"), "a") as f:
            f.write(f"\n### [{mid}] {who}\n\n{text}\n")
        self.emit("message", id=mid, who=who, chars=len(text))
        self.check_agreement()

    def check_agreement(self):
        latest = {}
        for m in self.msgs:
            latest[m["who"]] = m["text"]
        if len(latest) < len(PARTICIPANTS):
            return
        ids = set()
        for t in latest.values():
            a = re.findall(r"AGREE:\s*(\S+)", t)
            if not a:
                return
            ids.add(a[-1].strip(".,;"))
        if len(ids) == 1:
            pid = ids.pop()
            if any(re.search(rf"(?m)^\s*PROPOSAL {re.escape(pid)}:", m["text"]) for m in self.msgs):  # agreement must name a real proposal
                self.agreed = pid; self.emit("agreed", proposal=pid); self.done.set()

    async def relay(self):
        """Every window: give each participant, in one batch, everything new from the others."""
        while not self.done.is_set():
            await asyncio.sleep(self.window)
            for p in PARTICIPANTS:
                me = p["name"]
                new = [m for m in self.msgs[self.seen[me]:] if m["who"] != me]
                self.seen[me] = len(self.msgs)
                partial = {w: t for w, t in self.live.items() if w != me and t}
                if not new and not partial:
                    continue
                parts = [f"[{m['id']}] {m['who']}:\n{m['text']}" for m in new]
                parts += [f"{w} (still writing, so far):\n{t[-3000:]}" for w, t in partial.items()]
                self.inbox[me].append("\n\n".join(parts))
                self.emit("relay", to=me, finished=[m["id"] for m in new], partial=list(partial))
                if new:
                    self.wake[me].set()

    async def participant(self, p, brief):
        me = p["name"]
        system = (brief + f"\n\nYou are {me}, one member of a design council with "
                  + ", ".join(x["name"] for x in PARTICIPANTS if x["name"] != me)
                  + ". Messages from the others reach you in batches. Use the tools to check claims against the record before you rely on them. "
                  "Disagree where the data says so. To put forward a complete redesign, start a message with `PROPOSAL <short id>:`. "
                  "When you accept a proposal as final, end your message with `AGREE: <id>`. Keep messages focused.")
        self.history[me] = [{"role": "system", "content": system},
                            {"role": "user", "content": "The council is open. Read what you need from the record, then give your first analysis."}]
        first = True
        while not self.done.is_set() and self.turns[me] < self.max_turns:
            if not first:
                await self.wake[me].wait()
                self.wake[me].clear()
                batch = "\n\n---\n\n".join(self.inbox[me]); self.inbox[me].clear()
                self.history[me].append({"role": "user", "content": "New in the room:\n\n" + batch})
            first = False
            self.turns[me] += 1
            text = await self.turn(p)
            if text:
                self.history[me].append({"role": "assistant", "content": text})
                self.post(me, text)
        self.live.pop(me, None)

    async def turn(self, p):
        me = p["name"]
        for _ in range(12):                       # tool rounds inside one turn
            if self.cost >= self.cap:
                self.emit("cap_reached", cost=self.cost); self.done.set(); return None
            self.live[me] = ""
            content, calls, usage = await (self.mock_stream(p) if self.mock else self.stream(p))
            self.cost += float((usage or {}).get("cost") or 0)
            self.emit("turn_part", who=me, chars=len(content), tool_calls=len(calls), cost=self.cost)
            if not calls:
                self.live[me] = ""
                return content
            self.history[me].append({"role": "assistant", "content": content or None, "tool_calls": calls})
            for c in calls:
                try:
                    a = json.loads(c["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    a = {}
                fn = TOOLS.get(c["function"]["name"])
                res = fn(a) if fn else "unknown tool"
                self.emit("tool", who=me, name=c["function"]["name"], args=a, result_chars=len(res))
                self.history[me].append({"role": "tool", "tool_call_id": c["id"], "content": res})
        return None

    async def stream(self, p):
        body = {"model": p["model"], "messages": self.history[p["name"]], "tools": TOOL_SPECS, "stream": True,
                "max_tokens": 12000, "usage": {"include": True}}
        if p.get("reasoning"):
            body["reasoning"] = p["reasoning"]
        if p.get("provider"):
            body["provider"] = p["provider"]
        return await asyncio.to_thread(self._stream_sync, p["name"], body)

    def _stream_sync(self, me, body):
        import urllib.request
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"})
        content, calls, usage = "", {}, None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    for raw in r:
                        line = raw.decode("utf-8", "replace").strip()
                        if not line.startswith("data:") or line == "data: [DONE]":
                            continue
                        ev = json.loads(line[5:])
                        if ev.get("usage"):
                            usage = ev["usage"]
                        for ch in ev.get("choices", []):
                            d = ch.get("delta") or {}
                            if d.get("content"):
                                content += d["content"]; self.live[me] = content
                            for tc in d.get("tool_calls") or []:
                                slot = calls.setdefault(tc.get("index", 0), {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                                slot["id"] = tc.get("id") or slot["id"]
                                f = tc.get("function") or {}
                                slot["function"]["name"] += f.get("name") or ""
                                slot["function"]["arguments"] += f.get("arguments") or ""
                break
            except Exception as e:
                self.emit("error", who=me, err=str(e)[:300])
                if content or calls:
                    break
                time.sleep(5 * (attempt + 1))
        return content, [calls[k] for k in sorted(calls)], usage

    async def mock_stream(self, p):
        me = p["name"]; n = self.turns[me]
        if n == 1 and not any(m["role"] == "tool" for m in self.history[me]):
            return "", [{"id": f"{me}-1", "type": "function", "function": {"name": "list_sessions", "arguments": json.dumps({"filter": "repilot-v3"})}}], {"cost": 0.01}
        text = f"{me} turn {n}: analysis." + (f"\nPROPOSAL {me[0]}1: test." if me == "Fable" and n == 1 else "") + (" AGREE: F1" if n >= 2 else "")
        out = ""
        for w in text.split():
            out += w + " "; self.live[me] = out.replace(" PROPOSAL", "\nPROPOSAL")
            await asyncio.sleep(0.05)
        return text, [], {"cost": 0.01}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap-usd", type=float, default=12.0)
    ap.add_argument("--window", type=float, default=20.0)
    ap.add_argument("--max-turns", type=int, default=8)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    room = Room(a.out, a.cap_usd, a.window, a.max_turns, a.mock)
    brief = open(a.brief).read()
    room.emit("start", participants=[{k: p[k] for k in ("name", "model")} for p in PARTICIPANTS], cap=a.cap_usd, window=a.window,
              sessions=len(SESSIONS), scored=len(SCORES))
    tasks = [asyncio.create_task(room.participant(p, brief)) for p in PARTICIPANTS]
    relay = asyncio.create_task(room.relay())
    waiter = asyncio.create_task(room.done.wait())
    await asyncio.wait(tasks + [waiter], return_when=asyncio.FIRST_COMPLETED)
    while not room.done.is_set() and not all(t.done() for t in tasks):
        await asyncio.sleep(1)
    room.done.set()
    for w in room.wake.values():
        w.set()
    await asyncio.sleep(0.2)
    relay.cancel()
    room.emit("end", cost=round(room.cost, 4), turns=room.turns, messages=len(room.msgs))
    print(json.dumps({"cost": round(room.cost, 4), "turns": room.turns, "messages": len(room.msgs), "agreed": room.agreed}))


if __name__ == "__main__":
    asyncio.run(main())
