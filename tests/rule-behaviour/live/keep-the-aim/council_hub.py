#!/usr/bin/env python3
"""A live design council: several models debate the keep-the-aim test in one shared room.

    python3 -I council_hub.py --brief BRIEF.md --out DIR [--cap-usd 10] [--byok-cap-usd 10] [--window 20] [--mock]

Pull, never push. There is one shared room. Nothing is sent into a participant's context: each one reads
the room itself with the read_room tool, and speaks only with the post tool. read_room returns every
message since the participant last read, in full, plus what others are still streaming. If nothing is
new, it waits (up to 3 windows) for someone to post, so a participant can listen without spending tokens.
Each participant runs as one long conversation of tool rounds, streamed from its provider.

Each participant also has read-only tools over the full record: the session list, any session's turns
(prompt, reply, tool calls, scores, grades), a grep over all transcripts, and the design documents.
Nothing is loaded whole: the record is about 8 MB.

The run ends when every participant's latest post carries `AGREE: <id>` naming the same proposal (a post
with a line starting `PROPOSAL <id>:`); or at --cap-usd (OpenRouter credits, plus DeepSeek direct estimated
from tokens); or at --byok-cap-usd (Fable's upstream cost on the owner's Anthropic key); or when every
participant has used --max-turns model calls. Every round, tool call and post is logged to DIR/log.jsonl,
and the room to DIR/room.md.
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
    # DeepSeek direct: OpenRouter's DeepSeek endpoint is excluded by this account's data policy (checked 2026-11-15).
    # Its usage carries no cost, so cost is estimated from tokens at OpenRouter's listed DeepSeek V4 Pro price.
    {"name": "DeepSeek", "model": "deepseek-v4-pro", "url": "https://api.deepseek.com/chat/completions",
     "price_per_m": (0.0999, 8.0), "extra": {"thinking": {"type": "enabled"}, "reasoning_effort": "high"}},
    {"name": "DeepSeekFlash", "model": "deepseek-flash", "url": "https://api.deepseek.com/chat/completions",
     "price_per_m": (0.038, 0.5), "extra": {"thinking": {"type": "enabled"}, "reasoning_effort": "high"}},
    {"name": "MiMo", "model": "xiaomi/mimo-v2.6-pro:exacto", "provider": None},
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


ROOM = None


def t_read_message(args):
    m = next((x for x in ROOM.msgs if x["id"] == int(args.get("id") or 0)), None) if ROOM else None
    return f"[{m['id']}] {m['who']}:\n{m['text']}" if m else "no such message"


TOOLS = {"read_message": t_read_message, "list_sessions": t_list_sessions, "read_session": t_read_session, "grep": t_grep, "read_doc": t_read_doc}
TOOL_SPECS = [
    {"type": "function", "function": {"name": "post", "description": "Post a message to the shared room. This is the only way the others hear you.",
                                      "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "read_room", "description": "Read the shared room: every message after `since` (default: after the last one you read), in full, plus what others are still writing. If nothing is new it waits up to `wait` seconds for someone to post.",
                                      "parameters": {"type": "object", "properties": {"since": {"type": "integer"}, "wait": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "read_message", "description": "Re-read one room message by id.",
                                      "parameters": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}}},
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
    def __init__(self, out, cap, window, max_turns, mock, byok_cap=15.0):
        self.out, self.cap, self.window, self.max_turns, self.mock = out, cap, window, max_turns, mock
        self.log = open(os.path.join(out, "log.jsonl"), "a")
        self.cost = 0.0
        self.agreed = None
        self.byok, self.byok_cap = 0.0, byok_cap
        self.done = asyncio.Event()
        self.msgs = []                      # finished messages: {"id", "who", "text"}
        self.live = {}                      # who -> text streamed so far in the current turn
        self.seen = {p["name"]: 0 for p in PARTICIPANTS}      # id of the last room message each participant has read
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

    async def read_room(self, me, args):
        """Pull, never push: every message after `since` (default: after the last one this participant read),
        in full, plus what the others are still writing. If nothing is new it waits for the room to change,
        up to `wait` seconds (default 3 windows), so a participant can sit and listen. Long backlogs are cut
        at 60k characters, oldest first, with a note."""
        since = args.get("since")
        since = int(since) if since is not None else self.seen[me]
        deadline = time.time() + float(args.get("wait") or 3 * self.window)
        while not self.done.is_set() and time.time() < deadline and not any(m["id"] > since and m["who"] != me for m in self.msgs):
            await asyncio.sleep(1)
        out, size = [], 0
        for m in [m for m in self.msgs if m["id"] > since]:
            block = f"[{m['id']}] {m['who']}:\n{m['text']}"
            if size + len(block) > 60000:
                out.append(f"(cut: messages from [{m['id']}] on not shown; call read_room with since={m['id'] - 1})")
                break
            out.append(block); size += len(block)
            self.seen[me] = max(self.seen[me], m["id"])
        live = [f"{w} (still writing, so far):\n{t[-3000:]}" for w, t in self.live.items() if w != me and t]
        self.emit("read_room", who=me, since=since, got=len(out), live=len(live))
        state = "The council has ended." if self.done.is_set() else ""
        return "\n\n".join(out + live + [state]).strip() or "nothing new yet"

    async def participant(self, p, brief):
        """One long conversation per participant. It speaks only through the post tool and hears only through
        read_room; the hub never puts room messages into its context. If it stops calling tools before the
        council ends, it gets a bare "(the council is still open)" up to 3 times."""
        me = p["name"]
        system = (brief + f"\n\nYou are {me}, one member of a design council with "
                  + ", ".join(x["name"] for x in PARTICIPANTS if x["name"] != me)
                  + ". There is one shared room. Nothing is sent to you: you read the room yourself with read_room "
                  "(it waits for new messages if there are none yet) and you speak only with post. Read the room often. "
                  "Use the record tools to check claims before you rely on them, and disagree where the data says so. "
                  "To put forward a complete redesign, post a message that starts with `PROPOSAL <short id>:`. When you accept "
                  "a proposal as final, end a post with `AGREE: <id>`. Keep posts focused.")
        self.history[me] = [{"role": "system", "content": system},
                            {"role": "user", "content": "The council is open."}]
        nudges = 0
        while not self.done.is_set():
            ended = await self.turn(p)
            if ended or self.done.is_set() or nudges >= 3:
                break
            nudges += 1
            self.history[me].append({"role": "user", "content": "(the council is still open)"})
        self.live.pop(me, None)

    async def turn(self, p):
        """Tool rounds until the model stops calling tools (returns False), or a limit or cap ends it (True)."""
        me = p["name"]
        while self.turns[me] < self.max_turns:
            if self.cost >= self.cap or self.byok >= self.byok_cap:
                self.emit("cap_reached", cost=self.cost, byok=self.byok); self.done.set(); return True
            if self.done.is_set():
                return True
            self.turns[me] += 1
            self.live[me] = ""
            content, calls, usage = await (self.mock_stream(p) if self.mock else self.stream(p))
            self.cost += float((usage or {}).get("cost") or 0)  # OpenRouter credits (0 for BYOK calls)
            if (usage or {}).get("is_byok"):
                self.byok += float(((usage or {}).get("cost_details") or {}).get("upstream_inference_cost") or 0)
            self.live[me] = ""
            self.emit("round", who=me, chars=len(content), tool_calls=len(calls), cost=round(self.cost, 4), byok=round(self.byok, 4))
            if not calls:
                if content:
                    self.history[me].append({"role": "assistant", "content": content})
                return False
            self.history[me].append({"role": "assistant", "content": content or None, "tool_calls": calls})
            for c in calls:
                try:
                    a = json.loads(c["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    a = {}
                name = c["function"]["name"]
                if name == "post":
                    self.post(me, a.get("text", "")); res = "posted"
                elif name == "read_room":
                    res = await self.read_room(me, a)
                else:
                    fn = TOOLS.get(name); res = fn(a) if fn else "unknown tool"
                self.emit("tool", who=me, name=name, args={k: (v if len(str(v)) < 200 else str(v)[:200] + "…") for k, v in a.items()},
                          result_chars=len(res))
                self.history[me].append({"role": "tool", "tool_call_id": c["id"], "content": res})
        self.emit("max_rounds", who=me); return True

    async def stream(self, p):
        msgs = self.history[p["name"]]
        if p["model"].startswith("anthropic/"):  # prompt caching: re-read context bills at the cache-read rate
            msgs = [dict(m) for m in msgs]
            for i in (0, len(msgs) - 1):
                if isinstance(msgs[i].get("content"), str) and msgs[i]["content"]:
                    msgs[i]["content"] = [{"type": "text", "text": msgs[i]["content"], "cache_control": {"type": "ephemeral"}}]
        body = {"model": p["model"], "messages": msgs, "tools": TOOL_SPECS, "stream": True, "max_tokens": 12000}
        if p.get("url"):
            body["stream_options"] = {"include_usage": True}
        else:
            body["usage"] = {"include": True}
        if p.get("reasoning"):
            body["reasoning"] = p["reasoning"]
        if p.get("provider"):
            body["provider"] = p["provider"]
        body.update(p.get("extra") or {})
        content, calls, usage = await asyncio.to_thread(self._stream_sync, p["name"], body, p.get("url"))
        if p.get("price_per_m") and usage:
            pin, pout = p["price_per_m"]
            usage = dict(usage, cost=(usage.get("prompt_tokens", 0) * pin + usage.get("completion_tokens", 0) * pout) / 1e6)
        return content, calls, usage

    def _stream_sync(self, me, body, url=None):
        import urllib.request
        req = urllib.request.Request(url or "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
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
        await asyncio.sleep(0.05)
        last = self.history[me][-1]
        if n == 1:
            return "", [{"id": f"{me}-1", "type": "function", "function": {"name": "list_sessions", "arguments": json.dumps({"filter": "repilot-v3"})}}], {"cost": 0.01}
        if last["role"] == "tool" and last["content"] not in ("posted",) and n % 2 == 0:
            text = f"{me} view {n}." + ("\nPROPOSAL F1: test." if me == "Fable" and n == 2 else "") + (" AGREE: F1" if n >= 4 else "")
            return "", [{"id": f"{me}-{n}", "type": "function", "function": {"name": "post", "arguments": json.dumps({"text": text})}}], {"cost": 0.01}
        return "", [{"id": f"{me}-{n}", "type": "function", "function": {"name": "read_room", "arguments": json.dumps({"wait": 2})}}], {"cost": 0.0}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap-usd", type=float, default=12.0)
    ap.add_argument("--byok-cap-usd", type=float, default=15.0)
    ap.add_argument("--window", type=float, default=20.0)
    ap.add_argument("--max-turns", type=int, default=60, help="model calls per participant")
    ap.add_argument("--roster", help="JSON file with the participant list; replaces the built-in default roster")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.roster:  # the orchestrator chooses who sits in the room and by which route
        PARTICIPANTS[:] = json.load(open(a.roster))
    global ROOM
    room = ROOM = Room(a.out, a.cap_usd, a.window, a.max_turns, a.mock, a.byok_cap_usd)
    brief = open(a.brief).read()
    room.emit("start", participants=[{k: p[k] for k in ("name", "model")} for p in PARTICIPANTS], cap=a.cap_usd, window=a.window,
              sessions=len(SESSIONS), scored=len(SCORES))
    tasks = [asyncio.create_task(room.participant(p, brief)) for p in PARTICIPANTS]
    waiter = asyncio.create_task(room.done.wait())
    await asyncio.wait(tasks + [waiter], return_when=asyncio.FIRST_COMPLETED)
    while not room.done.is_set() and not all(t.done() for t in tasks):
        await asyncio.sleep(1)
    room.done.set()
    await asyncio.sleep(0.2)
    room.emit("end", cost=round(room.cost, 4), byok=round(room.byok, 4), turns=room.turns, messages=len(room.msgs))
    print(json.dumps({"cost": round(room.cost, 4), "byok_upstream": round(room.byok, 4), "turns": room.turns, "messages": len(room.msgs), "agreed": room.agreed}))


if __name__ == "__main__":
    asyncio.run(main())
