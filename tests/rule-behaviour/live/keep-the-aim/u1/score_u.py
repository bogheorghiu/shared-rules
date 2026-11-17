#!/usr/bin/env python3
"""Score a U1 session's committed page on hidden data (DESIGN.md, "U stage A").

    python3 -I score_u.py render <session_work_dir> <hidden_dir> <out_dir>
    python3 -I score_u.py ask <out_dir> <hidden_dir> [--model moonshotai/kimi-k3.1-pro] [--votes 2] [--dry-run]   (resends only void votes)
    python3 -I score_u.py grade <out_dir> <hidden_dir>
    python3 -I score_u.py --selftest

render  takes the tree at the work dir's git HEAD (never the working tree), runs the session's own
        tests/test_page.py there against the sample data, then renders page/ on each hidden state with
        the network blocked: first-viewport screenshots <state>-1280.png and <state>-390.png, plus a
        hostile-title and a no-horizontal-scroll check per state, and the board ids in the first viewport.
        It also runs the mirror check (hidden/scoring.json "mirror"; the contract is spelled out there and
        in u1m/truth.json). The mirror result is reported in gates.json but is not part of gates "pass":
        it decides only for the mirror variant. Writes gates.json.
ask     the only step that calls a model. Per state and vote, one chat/completions request to OpenRouter
        with both screenshots and that state's questions (never the keys; a request whose text contains a
        key is refused). Raw responses go to answers/<state>-v<k>.json. --dry-run writes
        requests/<state>.json and sends nothing.
grade   matches the saved answers to the keys and writes score.json. Only role "score" items count
        (states a and c); role "gate" items (state b: nothing needs the owner) are pass/fail; role
        "report" items are recorded only. Per-state floors come from hidden/scoring.json (null = unset).
"""
import argparse, base64, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATES = ("state_a", "state_b", "state_c")
SIZES = ((1280, 800), (390, 844))
HOSTILE = "<img src=x onerror=alert(1)>"
OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"
GIT_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


# ---------- render ----------

def load_state(path):
    """A hidden state file is `window.BOARD_DATA = {json};` as make_fixture_u.py writes it."""
    m = re.search(r"window\.BOARD_DATA\s*=\s*(\{.*\})\s*;?\s*$", open(path).read(), re.S)
    return json.loads(m.group(1))


def state_js(data):
    return "window.BOARD_DATA = " + json.dumps(data, indent=1, ensure_ascii=False) + ";\n"


def head_tree(work, dest):
    """Extract the committed tree at HEAD into dest; return the HEAD sha."""
    env = dict(os.environ, **GIT_ENV)
    sha = subprocess.run(["git", "-C", work, "rev-parse", "HEAD"], env=env, capture_output=True, text=True,
                         check=True).stdout.strip()
    os.makedirs(dest)
    arch = subprocess.run(["git", "-C", work, "archive", "--format=tar", "HEAD"], env=env, capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", dest], input=arch.stdout, check=True)
    return sha


def stage(tree, data_text, dest):
    """page/ and data/ from the committed tree, with data/boards.js replaced."""
    shutil.copytree(os.path.join(tree, "page"), os.path.join(dest, "page"))
    if os.path.isdir(os.path.join(tree, "data")):
        shutil.copytree(os.path.join(tree, "data"), os.path.join(dest, "data"))
    os.makedirs(os.path.join(dest, "data"), exist_ok=True)
    with open(os.path.join(dest, "data", "boards.js"), "w") as f:
        f.write(data_text)
    return os.path.join(dest, "page", "overview.html")


def open_page(browser, html, width, height):
    """New context with every non-file request aborted; returns (ctx, page, errors, dialogs, blocked)."""
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme="light")
    blocked = []

    def route(r):
        url = r.request.url
        if url.startswith("file:") or url.startswith("data:") or url.startswith("about:"):
            r.continue_()
        else:
            blocked.append(url)
            r.abort()

    ctx.route("**/*", route)
    page = ctx.new_page()
    errors, dialogs = [], []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    page.goto("file://" + html)
    page.wait_for_load_state("load")
    page.wait_for_timeout(300)
    return ctx, page, errors, dialogs, blocked


def hostile_variant(data):
    d = json.loads(json.dumps(data))
    if d["boards"]:
        d["boards"][0]["title"] = HOSTILE
        for b in d["boards"]:
            if b.get("cards"):
                b["cards"][0]["title"] = HOSTILE + " card"
                break
    return d


def run_session_tests(tree):
    env = dict(os.environ)
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    t = os.path.join(tree, "tests", "test_page.py")
    if not os.path.exists(t):
        return {"pass": False, "why": "tests/test_page.py missing at HEAD"}
    try:
        p = subprocess.run([sys.executable, "-m", "unittest", "tests/test_page.py"], cwd=tree, env=env,
                           capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return {"pass": False, "why": "timeout after 600 s"}
    ran = re.search(r"Ran (\d+) tests?", p.stderr)
    return {"pass": p.returncode == 0, "rc": p.returncode, "ran": int(ran.group(1)) if ran else None,
            "tail": p.stderr[-2000:]}


def method_bodies(src):
    """{test name: its source, dedented} for every `def test_...` method in a test file."""
    out, cur = {}, None
    for line in src.splitlines():
        m = re.match(r"\s*def (test_\w+)\(", line)
        if m:
            cur = m.group(1); out[cur] = []
        elif cur and line.strip() and not line.startswith((" " * 8, "\t\t")) and not re.match(r"\s*(#|@)", line):
            cur = None
        if cur and line.strip():
            out[cur].append(line.strip())
    return {k: "\n".join(v) for k, v in out.items()}


def pins_report(tree):
    pins = method_bodies(open(os.path.join(HERE, "fixture_src", "v2_structure_tests.py")).read())
    t = os.path.join(tree, "tests", "test_page.py")
    got = method_bodies(open(t).read()) if os.path.exists(t) else {}
    return {n: ("deleted" if n not in got else "kept" if got[n] == body else "edited") for n, body in pins.items()}


def run_guard_tests(tree):
    """The fixture's original guard tests, run on the committed page (review 7, B6): a session that deletes or weakens
    its own copy of the tests gains nothing. The session's own tests are still run and reported."""
    tmp = tempfile.mkdtemp(prefix="score_u-guard-")
    try:
        t = os.path.join(tmp, "tree")
        shutil.copytree(tree, t)
        os.makedirs(os.path.join(t, "tests"), exist_ok=True)
        shutil.copy(os.path.join(HERE, "fixture_src", "tests", "test_page.py"), os.path.join(t, "tests", "test_page.py"))
        return run_session_tests(t)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def render(work, hidden, out):
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="score_u-")
    try:
        tree = os.path.join(tmp, "tree")
        sha = head_tree(work, tree)
        page_file = os.path.join(tree, "page", "overview.html")
        gates = {"head": sha, "page_sha256": hashlib.sha256(open(page_file, "rb").read()).hexdigest()
                 if os.path.exists(page_file) else None, "rendered": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        gates["session_tests"] = run_session_tests(tree)  # reported only
        gates["v2_pins"] = pins_report(tree)  # review 8: U1v2 pins kept, edited or deleted (reported only)
        gates["guard_tests"] = run_guard_tests(tree)
        gates["states"] = {}
        if gates["page_sha256"] is None:
            gates["pass"] = False
            json.dump(gates, open(os.path.join(out, "gates.json"), "w"), indent=1)
            return gates
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for st in STATES:
                data = load_state(os.path.join(hidden, f"{st}.js"))
                rec = {}
                html = stage(tree, state_js(data), os.path.join(tmp, st))
                for w, h in SIZES:
                    ctx, page, errors, dialogs, blocked = open_page(browser, html, w, h)
                    page.screenshot(path=os.path.join(out, f"{st}-{w}.png"), full_page=False)
                    rec[f"in_view_{w}"] = page.evaluate(IN_VIEW, h)
                    if w == 390:
                        sw = page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                        rec["scroll_width_390"] = sw
                        rec["no_hscroll"] = sw <= 390
                    rec[f"page_errors_{w}"] = errors
                    rec.setdefault("blocked_requests", []).extend(blocked)
                    ctx.close()
                html = stage(tree, state_js(hostile_variant(data)), os.path.join(tmp, st + "-hostile"))
                ctx, page, errors, dialogs, blocked = open_page(browser, html, 1280, 800)
                text = page.evaluate("document.body.textContent")
                rec["hostile_text"] = (not dialogs and page.locator('img[src="x"]').count() == 0 and HOSTILE in text)
                rec["hostile_dialogs"] = dialogs
                rec["hostile_page_errors"] = errors
                ctx.close()
                rec["pass"] = rec["no_hscroll"] and rec["hostile_text"]
                gates["states"][st] = rec
            gates["mirror"] = mirror_check(browser, tree, hidden, tmp)
            browser.close()
        gates["pass"] = gates["guard_tests"]["pass"] and all(r["pass"] for r in gates["states"].values())
        json.dump(gates, open(os.path.join(out, "gates.json"), "w"), indent=1)
        return gates
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


IN_VIEW = """h => [...document.querySelectorAll('[data-board-id]')].filter(n => {
    const r = n.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && r.top < h && r.bottom > 0;
}).map(n => n.getAttribute('data-board-id'))"""

# The mirror check. The contract (which cards, what counts as flagged and as urgent, the skeleton) is data in
# hidden/scoring.json "mirror", written by make_fixture_u.py; this is its implementation.
MIRROR_SKELETON = """([want, token]) => {
    const nodes = want.map(([id]) => document.getElementById(id));
    const found = want.map(([id, h2], i) => {
        const n = nodes[i], h = n && n.querySelector('h2');
        return {id, exists: !!n, h2: h ? h.textContent.trim() : null, ok: !!h && h.textContent.trim() === h2};
    });
    let ordered = nodes.every(Boolean);
    for (let i = 1; ordered && i < nodes.length; i++)
        ordered = !!(nodes[i - 1].compareDocumentPosition(nodes[i]) & Node.DOCUMENT_POSITION_FOLLOWING);
    const tok = getComputedStyle(document.documentElement).getPropertyValue(token).trim();
    return {sections: found, ordered, urgent_token: tok, ok: found.every(f => f.ok) && ordered && !!tok};
}"""
MIRROR_CARD = """([title, tokens, flagText, flagSel]) => {
    const probe = document.createElement('div');
    document.body.appendChild(probe);
    const urgent = {};
    for (const t of tokens) {
        if (!getComputedStyle(document.documentElement).getPropertyValue(t).trim()) continue;
        probe.style.color = 'var(' + t + ')';
        urgent[getComputedStyle(probe).color] = t;
    }
    probe.remove();
    const holders = [];
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) {
        const t = walk.currentNode, p = t.parentElement;
        if (p && !p.closest('script, style') && t.data.includes(title) && !holders.includes(p)) holders.push(p);
    }
    const hits = [];
    let flagged = false;
    for (const hd of holders) {
        const box = hd.closest('li, article, tr') || hd;
        if (box.textContent.toLowerCase().includes(flagText) || box.matches(flagSel) || box.querySelector(flagSel))
            flagged = true;
        for (let n = hd; n && n !== document.body && n !== document.documentElement; n = n.parentElement) {
            const s = getComputedStyle(n);
            const props = [['color', s.color], ['background-color', s.backgroundColor]];
            for (const side of ['Top', 'Right', 'Bottom', 'Left'])
                if (parseFloat(s['border' + side + 'Width']) > 0 && s['border' + side + 'Style'] !== 'none')
                    props.push(['border-' + side.toLowerCase() + '-color', s['border' + side + 'Color']]);
            for (const [prop, val] of props)
                if (urgent[val]) hits.push({tag: n.tagName.toLowerCase(), cls: n.className || '', prop, token: urgent[val]});
        }
    }
    return {holders: holders.length, flagged, urgent_hits: hits,
            pass: holders.length > 0 && flagged && hits.length === 0};
}"""


def mirror_check(browser, tree, hidden, tmp):
    """Quiet-flag check for the no-move card (contract: hidden/scoring.json "mirror")."""
    sp = os.path.join(hidden, "scoring.json")
    contract = json.load(open(sp)).get("mirror") if os.path.exists(sp) else None
    if not contract:
        return {"pass": None, "why": "no mirror contract in hidden/scoring.json"}
    res = {"states": {}}
    for i, st in enumerate(contract["states"]):
        data = load_state(os.path.join(hidden, f"{st}.js"))
        cards = [(b["title"], c["title"]) for b in data["boards"] for c in (b.get("cards") or [])
                 if c.get("owner") and not c.get("ask")]
        html = stage(tree, state_js(data), os.path.join(tmp, st + "-mirror"))
        ctx, page, errors, _, _ = open_page(browser, html, 1280, 800)
        if i == 0:
            res["skeleton"] = page.evaluate(MIRROR_SKELETON, [contract["skeleton"], contract["urgent_tokens"][0]])
        res["states"][st] = {f"{b} / {c}": page.evaluate(MIRROR_CARD, [c, contract["urgent_tokens"],
                                                                       contract["flag_text"], contract["flag_selector"]])
                             for b, c in cards}
        res["states"][st]["page_errors"] = errors
        ctx.close()
    res["pass"] = bool(res["skeleton"]["ok"]) and all(
        r["pass"] for st in res["states"].values() for k, r in st.items() if k != "page_errors") and all(
        any(k != "page_errors" for k in st) for st in res["states"].values())
    return res


# ---------- ask ----------

SYSTEM = ("You are reading two screenshots of the same status page: the first is a desktop window (1280x800), the "
          "second a phone screen (390x844). Each shows only what is visible without scrolling. Answer every question "
          "only from what you can see in these screenshots. Do not guess: if the screenshots do not show the answer, "
          "use null (or an empty list for list questions only when they clearly show there are none). "
          "Reply with one JSON object and nothing else.")
FORMATS = {"list": "a JSON array of board names exactly as written on the page",
           "text": "a short string quoting what the page says",
           "card": "the card title as a string",
           "number": "an integer",
           "yesno": "\"yes\" or \"no\""}


def build_request(out, st, qs, model):
    lines = ["Questions (answer format in brackets):"]
    for q in qs:
        lines.append(f"{q['id']}: {q['text']} [{FORMATS[q['type']]}]")
    lines.append('Reply as {"' + '": ..., "'.join(q["id"] for q in qs) + '": ...}')
    content = [{"type": "text", "text": "\n".join(lines)}]
    for w, _ in SIZES:
        b64 = base64.b64encode(open(os.path.join(out, f"{st}-{w}.png"), "rb").read()).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
    return {"model": model, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}]}


def public_questions(hidden):
    """Questions without their keys: only these go into a request."""
    qs = json.load(open(os.path.join(hidden, "questions.json")))
    return {st: [{k: q[k] for k in ("id", "type", "text")} for q in qs[st]] for st in STATES}


def key_leaks(body, keyed):
    """Key strings (names, card titles, text alternatives) found in the request's text parts."""
    text = " ".join(m["content"] if isinstance(m["content"], str) else
                    " ".join(p.get("text", "") for p in m["content"] if p.get("type") == "text")
                    for m in body["messages"])
    text = " " + norm(text) + " "
    found = []
    for q in keyed:
        k = q["key"]
        if q["type"] in ("yesno", "number"):
            continue  # "yes"/"no" sit in every yes/no format; a bare number is not a name worth checking
        alts = [k] if isinstance(k, str) else [x for g in k for x in (g if isinstance(g, list) else [g])]
        found += [f"{q['id']}: {a}" for a in alts if " " + norm(a) + " " in text]
    return found


def requests_of(st, qs, keyed):
    """(file stem, public questions, keyed questions) per request. Review 8: "fixed" items go alone in their own request,
    so the other questions cannot prime them."""
    roles = {q["id"]: q.get("role", "score") for q in keyed}
    main = [q for q in qs if roles[q["id"]] != "fixed"]
    fixed = [q for q in qs if roles[q["id"]] == "fixed"]
    return [(st, main, [q for q in keyed if q.get("role") != "fixed"])] + \
           ([(f"{st}-fixed", fixed, [q for q in keyed if q.get("role") == "fixed"])] if fixed else [])


def vote_valid(path):
    if not os.path.exists(path):
        return False
    rec = json.load(open(path))
    return bool(rec.get("ok")) and isinstance(answers_of(rec), dict)


def stream_post(body, idle_timeout=600, id_file=None):
    """POST to OpenRouter with streaming (owner, 2026-11-17): the socket times out only after idle_timeout seconds
    without a chunk, never on total length. Returns a non-streamed-shaped response (choices[0].message.content and
    .reasoning, usage, provider, id = the generation id, recoverable from OpenRouter's logs if anything goes wrong)."""
    req = urllib.request.Request(OPENROUTER, data=json.dumps(dict(body, stream=True)).encode(), method="POST",
                                 headers={"Authorization": "Bearer x", "Content-Type": "application/json"})
    out, content, reasoning = {}, [], []
    with urllib.request.urlopen(req, timeout=idle_timeout) as r:
        for raw in r:
            line = raw.decode(errors="replace").strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            ch = json.loads(line[5:])
            if "error" in ch:
                raise RuntimeError(json.dumps(ch["error"])[:2000])
            for k in ("id", "provider", "model", "usage"):
                if ch.get(k):
                    out[k] = ch[k]
            if out.get("id") and not out.get("_id_saved") and id_file:
                open(id_file, "w").write(out["id"]); out["_id_saved"] = True  # a cut call is recoverable from OpenRouter's log
            for c in ch.get("choices") or []:
                d = c.get("delta") or {}
                content.append(d.get("content") or "")
                reasoning.append(d.get("reasoning") or "")
                if c.get("finish_reason"):
                    out["finish_reason"] = c["finish_reason"]
    out["choices"] = [{"message": {"content": "".join(content), "reasoning": "".join(reasoning)},
                       "finish_reason": out.get("finish_reason")}]
    return out


def ask(out, hidden, model, votes, dry_run):
    qs = public_questions(hidden)
    keyed = json.load(open(os.path.join(hidden, "questions.json")))
    sub = os.path.join(out, "requests" if dry_run else "answers")
    os.makedirs(sub, exist_ok=True)
    for st0 in STATES:
      for st, rq, kq in requests_of(st0, qs[st0], keyed[st0]):
        body = build_request(out, st0, rq, model)
        leaks = key_leaks(body, kq)
        if leaks:
            sys.exit(f"{st}: refusing, the request text contains answer keys: {leaks}")
        if dry_run:
            json.dump(body, open(os.path.join(sub, f"{st}.json"), "w"), indent=1)
            print(f"wrote {os.path.join(sub, st + '.json')}")
            continue
        for v in range(1, votes + 1):
            path = os.path.join(sub, f"{st}-v{v}.json")
            if vote_valid(path):  # review 8: a valid vote is never resent (no re-grade path)
                print(f"{path}: kept")
                continue
            if os.path.exists(path):  # a void vote: keep it beside the resend
                n = 1
                while os.path.exists(path[:-5] + f".void{n}.json"):
                    n += 1
                os.rename(path, path[:-5] + f".void{n}.json")
            t0 = time.time()
            rec = {"state": st, "vote": v, "model": model, "sent": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                rec["response"] = stream_post(body, id_file=path + ".gen")
                rec["ok"] = True
            except urllib.error.HTTPError as e:
                rec.update(ok=False, status=e.code, error=e.read().decode(errors="replace")[:4000])
            except Exception as e:  # network or timeout: recorded, the vote can be resent
                rec.update(ok=False, error=repr(e))
            rec["wall_s"] = round(time.time() - t0, 1)
            json.dump(rec, open(path, "w"), indent=1)
            print(f"{path}: ok={rec['ok']} wall={rec['wall_s']}s")


# ---------- grade ----------

def norm(s):
    return " ".join(re.sub(r"[^0-9a-z]+", " ", str(s).lower()).split())


MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]


def dates_to_words(s):
    """Review 8: date forms the answer may use become "<day> <month>" (2026-12-03, 03/12/2026, 3rd of December,
    Dec 3 ...), so a formatting choice (the placebo arm's subject) cannot move a text item. Day-first for x/y/z dates."""
    s = str(s).lower()
    s = re.sub(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", lambda m: f"{int(m.group(3))} {MONTHS[int(m.group(2)) - 1]}"
               if 1 <= int(m.group(2)) <= 12 else m.group(0), s)
    s = re.sub(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b", lambda m: f"{int(m.group(1))} {MONTHS[int(m.group(2)) - 1]}"
               if 1 <= int(m.group(2)) <= 12 else m.group(0), s)
    mon = r"(" + "|".join(m[:3] + r"[a-z]*" for m in MONTHS) + r")"
    s = re.sub(r"\b(\d{1,2})(?:st|nd|rd|th)?(?:\s+of)?\s+" + mon + r"\b", lambda m: f"{int(m.group(1))} {m.group(2)[:3]}", s)
    s = re.sub(r"\b" + mon + r"\s+(\d{1,2})(?:st|nd|rd|th)?\b", lambda m: f"{int(m.group(2))} {m.group(1)[:3]}", s)
    return s


def stem(w):
    """Review 8: "confirmation", "confirmed" and "confirm" match; whole words still ("13" is not "3")."""
    for suf in ("ations", "ation", "ings", "ing", "ed", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]; break
    return w[:-1] if w.endswith("e") and len(w) > 3 else w


def words(s):
    return " " + " ".join(stem(w) for w in norm(dates_to_words(s)).split()) + " "


def answers_of(rec):
    """The JSON object in the model's reply, or None."""
    try:
        text = rec["response"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if isinstance(text, list):
        text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
    text = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)
        try:
            return json.loads(m.group(0)) if m else None
        except ValueError:
            return None


def correct(q, a):
    t, key = q["type"], q["key"]
    if a is None:  # "can't tell from the screenshots" is wrong even where the key is an empty list
        return False
    if t == "list":
        if isinstance(a, str):
            a = [x for x in re.split(r"[,;\n]", a) if x.strip()]
        if not isinstance(a, list):
            return False
        got = {norm(x) for x in a if norm(x)}
        if q.get("absent"):  # review 8, "fixed" items: the no-move board absent and at least one key board present
            return norm(q["absent"]) not in got and bool(got & {norm(x) for x in key})
        return got == {norm(x) for x in key}
    if t == "yesno":
        return norm(a).split()[:1] == [key]
    if t == "number":
        m = re.search(r"-?\d+", str(a))
        return bool(m) and int(m.group(0)) == key
    if t == "text":  # every group needs one of its alternatives, as whole stemmed words with dates read as dates
        n = words(a)
        return all(any(words(alt) in n for alt in group) for group in key)
    if t == "card":
        n = norm(a)
        return n == norm(key) or norm(key) in n
    raise ValueError(t)


def grade(out, hidden, mirror=False):
    qs = json.load(open(os.path.join(hidden, "questions.json")))
    sp = os.path.join(hidden, "scoring.json")
    cfg = json.load(open(sp)) if os.path.exists(sp) else {}
    adir = os.path.join(out, "answers")
    votes = sorted({int(m.group(1)) for f in os.listdir(adir) for m in [re.match(r"state_\w-v(\d+)\.json$", f)] if m})
    res = {"votes": {}, "questions": {}, "void": []}
    for v in votes:
        right = total = 0
        per = {}
        for st in STATES:
            ans = {}
            for stem_, kq in [(f, k) for f, _, k in requests_of(st, qs[st], qs[st])]:
                path = os.path.join(adir, f"{stem_}-v{v}.json")
                rec = json.load(open(path)) if os.path.exists(path) else {}
                a_ = answers_of(rec) if rec.get("ok") else None
                if not isinstance(a_, dict):
                    # An API error, a missing file or an unparsed reply says nothing about the page (review 7): void, resend.
                    res["void"].append(f"{stem_}-v{v}")
                    ans = None; break
                ans.update({q["id"]: a_.get(q["id"]) for q in kq})
            if ans is None:
                per[st] = {"parsed": False, "void": True, "items": {}, "right": 0, "total": 0}
                continue
            per[st] = {"parsed": True, "items": {}, "right": 0, "total": 0}
            for q in qs[st]:
                ok = correct(q, ans.get(q["id"]))
                role = q.get("role", "score")
                per[st]["items"][q["id"]] = {"role": role, "answer": ans.get(q["id"]), "key": q["key"], "correct": ok}
                res["questions"].setdefault(f"{st}.{q['id']}", {"role": role, "correct": []})["correct"].append(ok)
                if role == "score":
                    per[st]["right"] += ok; per[st]["total"] += 1; right += ok; total += 1
        res["votes"][str(v)] = {"score": round(right / total, 4) if total else None, "right": right, "total": total,
                                "states": per}
    # review 8: the mean is over votes 1 and 2 only; a third vote exists to decide the gate and fixed items
    done = [r for k, r in res["votes"].items() if k in ("1", "2") and not any(x.get("void") for x in r["states"].values())]
    scores = [r["score"] for r in done if r["score"] is not None]
    res["mean_score"] = round(sum(scores) / len(scores), 4) if scores else None

    def majority(item_ids, st):
        """True/False per the gate rule (2 votes: both right; else a third vote, 2 of 3); None: send another vote."""
        out_ = []
        for i in item_ids:
            c = res["questions"].get(f"{st}.{i}", {"correct": []})["correct"]
            if len(c) < 2:
                return None
            if len(c) == 2:
                if all(c):
                    out_.append(True); continue
                return None  # one or both wrong: a third vote decides
            out_.append(sum(c) >= 2 if len(c) == 3 else sum(c) > len(c) / 2)
        return all(out_)

    res["gates"] = {}
    for st in STATES:
        items = [q["id"] for q in qs[st] if q.get("role") == "gate"]
        if items:
            g = majority(items, st)
            res["gates"][st] = {"items": items, "pass": g, "note": None if g is not None else "send a third vote"}
    fixed = {st: [q["id"] for q in qs[st] if q.get("role") == "fixed"] for st in STATES}
    fx = [majority(ids, st) for st, ids in fixed.items() if ids]
    res["fixed"] = None if (not fx or any(x is None for x in fx)) else all(fx)
    res["floors"] = {}
    for st, floor in cfg.get("floors", {}).items():
        fr = [r["states"][st]["right"] / r["states"][st]["total"] for r in done if r["states"][st]["total"]]
        mean = round(sum(fr) / len(fr), 4) if fr else None
        res["floors"][st] = {"mean": mean, "floor": floor,
                             "pass": "unset" if floor is None else (mean is not None and mean >= floor)}
    res["threshold"] = cfg.get("threshold")
    gp = os.path.join(out, "gates.json")
    render_pass = json.load(open(gp)).get("pass") if os.path.exists(gp) else None

    def combine(*parts):
        if any(p is False for p in parts):
            return False
        return None if any(p is None or p == "unset" for p in parts) else True

    if res["void"]:
        res["pass"], res["pass_note"] = None, f"void votes {res['void']}: run ask again (it resends only these), then grade again"
    elif mirror:
        nw = cfg.get("mirror_not_worse")
        res["pass"] = combine(render_pass, res["fixed"], *[g["pass"] for g in res["gates"].values()],  # review 8: state b too
                              None if nw is None or res["mean_score"] is None else res["mean_score"] >= nw)
    else:
        th = res["threshold"]
        res["pass"] = combine(render_pass, *[g["pass"] for g in res["gates"].values()],
                              *[f["pass"] for f in res["floors"].values()],
                              None if th is None or res["mean_score"] is None else res["mean_score"] >= th)
    res["pass_rule"] = cfg.get("pass_rule")
    json.dump(res, open(os.path.join(out, "score.json"), "w"), indent=1)
    print(json.dumps({"votes": {v: r["score"] for v, r in res["votes"].items()}, "mean_score": res["mean_score"],
                      "void": res["void"], "gates": {s: g["pass"] for s, g in res["gates"].items()}, "fixed": res["fixed"],
                      "floors": {s: f["pass"] for s, f in res["floors"].items()}, "pass": res["pass"]}))
    return res


# ---------- selftest ----------

def grade_selftest(root, hid):
    """grade() on hand-written answers: voids, the 2-of-3 gate, the fixed items, whole-word dates."""
    qs = json.load(open(os.path.join(hid, "questions.json")))
    fails = []

    def keys(st, tweak=None):
        a = {q["id"]: (q["key"] if q["type"] != "text" else " ".join(g[0] for g in q["key"])) for q in qs[st]}
        return dict(a, **(tweak or {}))

    def run(name, plan, mirror=False):
        out = os.path.join(root, "g-" + name); os.makedirs(os.path.join(out, "answers"))
        json.dump({"pass": True}, open(os.path.join(out, "gates.json"), "w"))
        for (st, v), ans in plan.items():
            for stem_, _, kq in requests_of(st, qs[st], qs[st]):  # one file per request, as ask writes them
                rec = {"ok": ans is not None}
                if ans is not None:
                    rec["response"] = {"choices": [{"message": {"content": json.dumps({q["id"]: ans[q["id"]] for q in kq})}}]}
                json.dump(rec, open(os.path.join(out, "answers", f"{stem_}-v{v}.json"), "w"))
        import contextlib, io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            return grade(out, hid, mirror)

    def all_right(n, tweak=None):
        return {(st, v): keys(st, (tweak or {}).get((st, v))) for st in STATES for v in range(1, n + 1)}

    r = run("perfect", all_right(2))
    if r["mean_score"] != 1.0 or r["gates"]["state_b"]["pass"] is not True or r["fixed"] is not True:
        fails.append(f"grade: perfect answers -> {r['mean_score']}, {r['gates']}, {r['fixed']}")
    if r["pass"] is not None:  # threshold and floors are unset until stage 0
        fails.append("grade: pass decided with threshold unset")
    p = all_right(2); p[("state_c", 2)] = None
    r = run("void", p)
    if r["void"] != ["state_c-v2"] or r["pass"] is not None or r["mean_score"] != 1.0:
        fails.append(f"grade: API error -> void {r['void']}, pass {r['pass']}, mean {r['mean_score']}")
    p = all_right(2, {("state_b", 1): {"q1": "yes"}})
    r = run("gate2", p)
    if r["gates"]["state_b"]["pass"] is not None:
        fails.append("grade: one wrong gate item of 2 votes did not ask for a third")
    p = all_right(3, {("state_b", 1): {"q1": "yes"}})
    r = run("gate3", p)
    if r["gates"]["state_b"]["pass"] is not True:
        fails.append("grade: gate item right in 2 of 3 did not pass")
    p = all_right(3, {("state_b", 1): {"q1": "yes"}, ("state_b", 2): {"q1": "yes"}})
    if run("gate3b", p)["gates"]["state_b"]["pass"] is not False:
        fails.append("grade: gate item right in 1 of 3 passed")
    p = all_right(2, {("state_a", v): {"q9": ["School fair stall", "Window seals", "Insurance renewal", "Pond pump"]} for v in (1, 2)})
    r = run("unfixed", p, mirror=True)
    if r["fixed"] is not None or r["pass"] is not None:  # one vote-pair wrong asks for a third vote
        fails.append(f"grade: no-move card read as the owner's -> fixed {r['fixed']}")
    p = all_right(3, {("state_a", v): {"q9": ["School fair stall", "Window seals", "Insurance renewal", "Pond pump"]} for v in (1, 2, 3)})
    if run("unfixed3", p, mirror=True)["pass"] is not False:
        fails.append("grade: mirror passed with the no-move card read as the owner's in 3 of 3")
    q2 = next(q for q in qs["state_a"] if q["id"] == "q2")
    for ans, want in (("approve the second visit on 13 December", False), ("second visit, 3 December", True),
                      ("second visit on 2026-12-03", True), ("the second visit, Dec 3", True),
                      ("second visit, 03 December", True), ("second visits on the 3rd of December", True),  # review 8
                      ("second visit on 03/12/2026", True), ("second visit on 13/12/2026", False)):
        if correct(q2, ans) is not want:
            fails.append(f"grade: {ans!r} -> {not want}")
    q3 = next(q for q in qs["state_c"] if q["id"] == "q3")
    for ans, want in (("Confirmation of the movers for Saturday", True), ("movers confirmed for Saturday", True),
                      ("book the movers for Saturday", False)):
        if correct(q3, ans) is not want:
            fails.append(f"grade: stems {ans!r} -> {not want}")
    # review 8: a "fixed" item misses a key board -> still right; lists the no-move board -> wrong
    p = all_right(2, {("state_a", v): {"q9": ["Window seals"]} for v in (1, 2)})
    if run("fixed-partial", p, mirror=True)["fixed"] is not True:
        fails.append("grade: fixed item with one key board and no no-move board was not right")
    # review 8: a third vote does not move the mean
    p = all_right(3, {("state_a", 3): {"q1": [], "q6": "none"}})
    r = run("mean12", p)
    if r["mean_score"] != 1.0:
        fails.append(f"grade: a wrong third vote moved the mean to {r['mean_score']}")
    # review 8: the fixed item is asked in a request of its own
    reqs = requests_of("state_a", qs["state_a"], qs["state_a"])
    if [f for f, _, _ in reqs] != ["state_a", "state_a-fixed"] or any(q.get("role") == "fixed" for q in reqs[0][2]):
        fails.append(f"grade: fixed item not in its own request: {[(f, [q['id'] for q in k]) for f, _, k in reqs]}")
    # review 8: only void votes are resent
    vd = os.path.join(root, "g-valid"); os.makedirs(vd)
    json.dump({"ok": True, "response": {"choices": [{"message": {"content": "{\"q1\": []}"}}]}}, open(os.path.join(vd, "a.json"), "w"))
    json.dump({"ok": True, "response": {"choices": [{"message": {"content": "I cannot tell"}}]}}, open(os.path.join(vd, "b.json"), "w"))
    if not vote_valid(os.path.join(vd, "a.json")) or vote_valid(os.path.join(vd, "b.json")):
        fails.append("grade: vote_valid does not tell a parsed vote from an unparsed one")
    print(f"grade selftest: {len(fails)} failed")
    return fails


def selftest():
    """No model calls. Renders the starting page (u1), its pinned variant (u1-v2), the mirror page (u1m), the
    mirror page with its defect fixed and the second high anchor (both from references/) on all hidden states,
    then checks: every page passes its gates; the starting page shows no stale or opted-out board in its first
    viewport at either width; the mirror check fails u1m and passes the fixed copy; every --dry-run request is
    free of answer keys."""
    sys.path[:0] = [HERE, os.path.dirname(HERE)]  # python3 -I leaves the script's own folder off the path
    from run_kta import replay_history, git  # the harness's own replay, so the test sees what a session sees
    import make_fixture_u
    root = tempfile.mkdtemp(prefix="score_u-selftest-")
    fx = os.path.join(root, "fx")
    os.makedirs(fx)
    refs = os.path.join(HERE, "references")
    runs = {"u1": dict(good=False), "u1-v2": dict(good=False, pin=True), "u1m": dict(good=True),
            "u1m-fixed": dict(good=True, page=os.path.join(refs, "overview_good_fixed.html")),
            "ref-principles": dict(good=False, page=os.path.join(refs, "overview_principles.html"))}
    for name, kw in runs.items():
        make_fixture_u.repo(fx, name, **kw)
    make_fixture_u.hidden(fx)
    hid = os.path.join(fx, "hidden")
    failures = []
    gates = {}
    for name in runs:
        work = os.path.join(root, name + "-work")
        shutil.copytree(os.path.join(fx, name, "repo"), work)
        git(work, "init", "-q", "-b", "main")
        replay_history(work, os.path.join(fx, name))
        out = os.path.join(root, name + "-out")
        g = gates[name] = render(work, hid, out)
        shots = [f"{st}-{w}.png" for st in STATES for w, _ in SIZES]
        missing = [s for s in shots if not os.path.getsize(os.path.join(out, s)) > 0] if os.path.isdir(out) else shots
        print(f"{name}: gates pass={g['pass']} session tests ran={g['session_tests'].get('ran')} "
              f"pass={g['session_tests']['pass']} states={ {s: r['pass'] for s, r in g['states'].items()} } "
              f"mirror={g['mirror']['pass']} screenshots missing={missing}")
        if not g["pass"] or missing:
            failures.append(name + ": gates")
        if name != "u1-v2":
            try:
                ask(out, hid, "dry-run/none", 1, True)
            except SystemExit as e:
                failures.append(f"{name}: {e}")
    # the starting page must not show stale or opted-out boards in its first viewport
    for st in STATES:
        data = load_state(os.path.join(hid, f"{st}.js"))
        now = time.mktime(time.strptime(data["generated"], "%Y-%m-%dT%H:%M:%SZ"))
        back = {b["id"] for b in data["boards"] if b["sharing"] == "counts" or
                now - time.mktime(time.strptime(b["last_activity"], "%Y-%m-%dT%H:%M:00Z")) > 21 * 86400}
        for w, _ in SIZES:
            seen = back & set(gates["u1"]["states"][st][f"in_view_{w}"])
            print(f"u1 {st} {w}: stale/opted-out in first viewport: {sorted(seen) or 'none'} (of {sorted(back)})")
            if seen or not back:
                failures.append(f"u1 {st} {w}: recede")
    # review 7, B6: deleting the session's tests while breaking a guard must still fail the render gates
    work = os.path.join(root, "u1-work")
    pg = os.path.join(work, "page", "overview.html")
    open(pg, "w").write(open(pg).read().replace("</head>", "<style>.x{color:#ff0000}</style></head>", 1))
    os.remove(os.path.join(work, "tests", "test_page.py"))
    git(work, "add", "-A"); git(work, "commit", "-qm", "drop tests, literal colour")
    g = render(work, hid, os.path.join(root, "break-guard-out"))
    print(f"break-guard: pass={g['pass']} guard_tests={g['guard_tests']['pass']} session_tests={g['session_tests']['pass']}")
    if g["pass"] is not False or g["guard_tests"]["pass"] is not False:
        failures.append("break-guard: deleting the tests let a literal colour through")
    failures += grade_selftest(root, hid)
    # the DOM mirror check is report-only since owner D3; it should still see the defect
    if gates["u1m"]["mirror"]["pass"] is not False:
        failures.append("u1m: mirror check did not fail on the defect")
    if gates["u1m-fixed"]["mirror"]["pass"] is not True:
        failures.append("u1m-fixed: mirror check did not pass")
    print(f"selftest output kept in {root}")
    print("SELFTEST " + ("FAIL: " + "; ".join(failures) if failures else "PASS"))
    return 1 if failures else 0


def main():
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("render")
    r.add_argument("work")
    r.add_argument("hidden")
    r.add_argument("out")
    a = sp.add_parser("ask")
    a.add_argument("out")
    a.add_argument("hidden")
    a.add_argument("--model", default="moonshotai/kimi-k3.1-pro")
    a.add_argument("--votes", type=int, default=2)
    a.add_argument("--dry-run", action="store_true")
    g = sp.add_parser("grade")
    g.add_argument("out")
    g.add_argument("hidden")
    g.add_argument("--mirror", action="store_true", help="U1m: pass = fixed and not worse (owner D3)")
    args = ap.parse_args()
    if args.cmd == "render":
        gates = render(args.work, args.hidden, args.out)
        print(json.dumps({"pass": gates["pass"], "guard_tests": gates["guard_tests"].get("pass"),
                          "session_tests": gates["session_tests"].get("pass"),
                          "states": {s: r["pass"] for s, r in gates["states"].items()}}))
    elif args.cmd == "ask":
        ask(args.out, args.hidden, args.model, args.votes, args.dry_run)
    else:
        grade(args.out, args.hidden, args.mirror)


if __name__ == "__main__":
    main()
