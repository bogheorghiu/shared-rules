#!/usr/bin/env python3
"""Score a U1 session's committed page on hidden data (DESIGN.md, "U stage A").

    python3 -I score_u.py render <session_work_dir> <hidden_dir> <out_dir>
    python3 -I score_u.py ask <out_dir> <hidden_dir> [--model moonshotai/kimi-k3.1-pro] [--votes 2] [--dry-run] [--force]
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
        gates["session_tests"] = run_session_tests(tree)
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
        gates["pass"] = gates["session_tests"]["pass"] and all(r["pass"] for r in gates["states"].values())
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


def ask(out, hidden, model, votes, dry_run, force):
    qs = public_questions(hidden)
    keyed = json.load(open(os.path.join(hidden, "questions.json")))
    sub = os.path.join(out, "requests" if dry_run else "answers")
    os.makedirs(sub, exist_ok=True)
    for st in STATES:
        body = build_request(out, st, qs[st], model)
        leaks = key_leaks(body, keyed[st])
        if leaks:
            sys.exit(f"{st}: refusing, the request text contains answer keys: {leaks}")
        if dry_run:
            json.dump(body, open(os.path.join(sub, f"{st}.json"), "w"), indent=1)
            print(f"wrote {os.path.join(sub, st + '.json')}")
            continue
        for v in range(1, votes + 1):
            path = os.path.join(sub, f"{st}-v{v}.json")
            if os.path.exists(path) and not force and json.load(open(path)).get("ok"):
                print(f"{path}: kept (use --force to resend)")
                continue
            req = urllib.request.Request(OPENROUTER, data=json.dumps(body).encode(), method="POST",
                                         headers={"Authorization": "Bearer x", "Content-Type": "application/json"})
            t0 = time.time()
            rec = {"state": st, "vote": v, "model": model, "sent": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    rec["response"] = json.loads(r.read().decode())
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
        return {norm(x) for x in a if norm(x)} == {norm(x) for x in key}
    if t == "yesno":
        return norm(a).split()[:1] == [key]
    if t == "number":
        m = re.search(r"-?\d+", str(a))
        return bool(m) and int(m.group(0)) == key
    if t == "text":  # every group needs one of its alternatives
        n = norm(a)
        return all(any(norm(alt) in n for alt in group) for group in key)
    if t == "card":
        n = norm(a)
        return n == norm(key) or norm(key) in n
    raise ValueError(t)


def grade(out, hidden):
    qs = json.load(open(os.path.join(hidden, "questions.json")))
    sp = os.path.join(hidden, "scoring.json")
    cfg = json.load(open(sp)) if os.path.exists(sp) else {}
    adir = os.path.join(out, "answers")
    votes = sorted({int(m.group(1)) for f in os.listdir(adir) for m in [re.match(r"state_\w-v(\d+)\.json$", f)] if m})
    res = {"votes": {}, "questions": {}}
    for v in votes:
        right = total = 0
        per = {}
        for st in STATES:
            path = os.path.join(adir, f"{st}-v{v}.json")
            rec = json.load(open(path)) if os.path.exists(path) else {}
            ans = answers_of(rec) if rec.get("ok") else None
            per[st] = {"parsed": ans is not None, "items": {}, "right": 0, "total": 0}
            for q in qs[st]:
                a = ans.get(q["id"]) if isinstance(ans, dict) else None
                ok = correct(q, a)
                role = q.get("role", "score")
                per[st]["items"][q["id"]] = {"role": role, "answer": a, "key": q["key"], "correct": ok}
                res["questions"].setdefault(f"{st}.{q['id']}", {"role": role, "correct": []})["correct"].append(ok)
                if role == "score":
                    per[st]["right"] += ok
                    per[st]["total"] += 1
                    right += ok
                    total += 1
        res["votes"][str(v)] = {"score": round(right / total, 4) if total else None, "right": right, "total": total,
                                "states": per}
    scores = [r["score"] for r in res["votes"].values() if r["score"] is not None]
    res["mean_score"] = round(sum(scores) / len(scores), 4) if scores else None
    # gates: one per state that has gate items; passes only if every gate item is right in every vote
    res["gates"] = {}
    for st in STATES:
        items = [q["id"] for q in qs[st] if q.get("role") == "gate"]
        if items:
            ok = bool(votes) and all(res["questions"][f"{st}.{i}"]["correct"] and
                                     all(res["questions"][f"{st}.{i}"]["correct"]) for i in items)
            res["gates"][st] = {"items": items, "pass": ok}
    # per-state floors on the mean fraction of score items right
    res["floors"] = {}
    for st, floor in cfg.get("floors", {}).items():
        fr = [r["states"][st]["right"] / r["states"][st]["total"] for r in res["votes"].values()
              if r["states"][st]["total"]]
        mean = round(sum(fr) / len(fr), 4) if fr else None
        res["floors"][st] = {"mean": mean, "floor": floor,
                             "pass": "unset" if floor is None else (mean is not None and mean >= floor)}
    res["threshold"] = cfg.get("threshold")
    json.dump(res, open(os.path.join(out, "score.json"), "w"), indent=1)
    print(json.dumps({"votes": {v: r["score"] for v, r in res["votes"].items()}, "mean_score": res["mean_score"],
                      "gates": {s: g["pass"] for s, g in res["gates"].items()},
                      "floors": {s: f["pass"] for s, f in res["floors"].items()}}))
    return res


# ---------- selftest ----------

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
                ask(out, hid, "dry-run/none", 1, True, False)
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
    a.add_argument("--force", action="store_true")
    g = sp.add_parser("grade")
    g.add_argument("out")
    g.add_argument("hidden")
    args = ap.parse_args()
    if args.cmd == "render":
        gates = render(args.work, args.hidden, args.out)
        print(json.dumps({"pass": gates["pass"], "session_tests": gates["session_tests"].get("pass"),
                          "states": {s: r["pass"] for s, r in gates["states"].items()}}))
    elif args.cmd == "ask":
        ask(args.out, args.hidden, args.model, args.votes, args.dry_run, args.force)
    else:
        grade(args.out, args.hidden)


if __name__ == "__main__":
    main()
