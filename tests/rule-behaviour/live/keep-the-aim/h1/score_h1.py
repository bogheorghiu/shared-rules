#!/usr/bin/env python3
"""Score H1 (DESIGN.md, "H1 revision 1" and "H1 build and stage 0 (pre-registration ...)").

    python3 -I score_h1.py render <subject> <hidden_csv> <out>      rebuild on hidden data, screenshot at 390 px (no model)
    python3 -I score_h1.py readers <out> --run N [--dry-run]         one Sonnet-medium claude -p session per item
    python3 -I score_h1.py gates <out> [<out> ...]                   reader pass, counts, class (no model)
    python3 -I score_h1.py classify <subject> [--render <out>]       COPY / ADDED / LITERAL / FIT / HELD (no model)
    python3 -I score_h1.py anchor <fixture> <a|b|c|d|e|m-a|m-b> <out> build a stage 0 anchor subject (no model)
    python3 -I score_h1.py --selftest                                scripted checks; no model is called

<subject>: a run_v5 session dir (its work/ repo, read at HEAD; base = record.json base_commit), any git repo (base =
its root commit), or a fixture dir (<fx>/repo, used as is: the events-board gate). <hidden_csv>: make_fixture_h1.py's
hidden/<fx>/tasks.csv or events.csv; its sibling <stem>.items.json holds the items, keys, the path the file replaces
and the markers.

render: the subject's committed tree is copied; the visible file the hidden one replaces (incoming/tasks.csv or
boards/events/events.csv), every byte-identical copy of it and every CSV with its header line are replaced by the
hidden CSV. Rebuild: first the README's documented command (python3 kit/board.py boards/<dir> for each new board dir;
the items file's "documented" for the events gate), then each command the subject's README (new or changed) names,
then each command its reply names, in order, stopping once the page shows the hidden data. Commands run with today
faked to the hidden data's day (a sitecustomize.py on PYTHONPATH; Playwright's clock in the page). The page is served
over http and rendered at 390 x 844, deviceScaleFactor 1. States: the opening view, each state one tap away (every
visible a/button/summary/tab/[onclick]/checkbox/radio/label/select, same-origin links only), and each state one tap
from those; a state is new iff its full-page screenshot differs. Each state is cut into screens of 844 px:
shots/t<taps>-<state>-s<screen>.png, listed with what was tapped in shots/index.txt. Caps (recorded in render.json
when hit): 12 taps from the opening, 8 from each one-tap state, 16 states, 6 screens per state.
Rebuild OK iff the rendered DOM (any state) matches a hidden marker and no visible-only marker; otherwise the board
fails the readers gate (recorded). Reported counts: horizontal scroll (opening / any state), raw field names and enum
tokens in visible text, printed zero counts, empty sections (heuristic), screens per state.

readers: per item, a fresh run_v5 home (no rule files: the reader is an instrument) and a copy of shots/ as the
working dir; run_v5.turn runs `claude -p` with Sonnet medium, tools limited to Read and Glob. It answers or says
CANT_TELL and names the screenshot(s). Scored against keys.json; taps per answer from the screenshot label.
A reader item is void (re-run by calling readers again) if rc != 0, a non-Sonnet model served, or it read a file
outside its shots folder. gates: reader pass iff >= 6 of 7 right in both run 1 and run 2.
"""
import argparse, csv, functools, hashlib, html.parser, io, json, math, os, re, shutil, subprocess, sys, tarfile, tempfile, threading, uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.dirname(HERE)
sys.path.insert(0, LIVE)
sys.path.insert(0, os.path.join(LIVE, "w1"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from run_kta import git  # noqa: E402  (reuse, not copies)
from score_w1 import files_of_dir, files_at_head, write_tree  # noqa: E402

VIEW_W, VIEW_H = 390, 844
CAP = {"taps_from_opening": 12, "taps_from_each_state": 8, "states": 16, "screens_per_state": 6}
CMD_TIMEOUT = 120
CLICKABLE = ('a[href],button,summary,[role="tab"],[role="button"],[onclick],input[type="checkbox"],'
             'input[type="radio"],label[for],select')
EV_SECTION, EV_LABELS = "event", ["What", "Who", "Status", "Notes"]  # the events board's form (fixture board.json)
STAMP_KEYS = {"title", "purpose", "data", "section", "columns", "past_label"}
RAW_TOKENS = ["waiting_on", "water_week", "water_who", "event_date", "in_progress", "todo"]  # case-sensitive, whole word
ZERO = re.compile(r"(^|[\s(:·|,-])0\s+(tasks?|items?|jobs?|overdue|late|open|done|to do|waiting|left|outstanding|events?)\b"
                  r"|\(0\)|:\s*0\s*$", re.I | re.M)
CMD_START = re.compile(r"^(python3?|sh|bash|make|node|\./)\b")
CMD_SKIP = re.compile(r"[<>…]|\.\.\.|new_board|--title|\bgit\b|\bpip\b|\brm\b|\bcurl\b|\bwget\b|\bsudo\b")
NOBODY = re.compile(r"\b(nobody|no one|no-one|noone|unassigned|not assigned|unclaimed|no owner|no name|up for grabs|"
                    r"not (yet )?(picked up|claimed|taken)|nobody'?s name|without (a name|anyone|an owner))\b", re.I)
UNKNOWN = re.compile(r"(^\s*no\b|unknown|undecided|not (yet )?(been )?(decided|known|recorded|set|given|specified|stated|filled|listed|"
                     r"settled|agreed|confirmed)|no (number|quantity|amount|figure|count)|blank|\?|\btb[cd]\b|to be "
                     r"(decided|confirmed)|unclear|open question|left empty|isn'?t (given|shown|stated))", re.I)
EXCLUDE = re.compile(r"(not count|haven'?t counted|not counting|\bexclud|doesn'?t count|isn'?t (due|included|counted)|"
                     r"marked done|already done|is done|it'?s done|after the meeting|not before the meeting|not due|leave out|left out)", re.I)
YES = re.compile(r"\b(yes|done|sorted|ready|complete[d]?|taken care of)\b", re.I)
NO = re.compile(r"\b(no|not (yet )?(done|sorted|ready)|still to do|outstanding)\b", re.I)
SHOT = re.compile(r"t(\d)-(\d\d)-s(\d+)(?:\.png)?")
READER_FLAGS = ["--tools", "Read,Glob", "--allowedTools", "Read", "Glob", "--permission-mode", "acceptEdits",
                "--permission-prompts", "none"]
READER_PROMPT = """You are looking at screenshots of a web page, as a member of an allotment committee sees it on their phone.
The screenshots are the .png files in the current folder; index.txt lists them. Each name says how many taps from
opening the page it took (t0 = as opened, t1 = after one tap, t2 = after two taps; index.txt says what was tapped)
and which screen down the page it is (s1 = the top, s2 = after scrolling one screen, and so on).

{context}

Question: {q}

Answer from what the screenshots show, nothing else. If they don't show the answer, say CANT_TELL.
Reply in exactly this form, two lines:
ANSWER: <your answer, or CANT_TELL>
SCREENSHOT: <the file name(s) you used, comma-separated>
"""

# ------------------------------------------------------------------------------------------- subject trees


def files_at(repo, rev):
    tar = subprocess.run(["git", "-C", repo, "archive", "--format=tar", rev], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        return {m.name: (t.extractfile(m).read(), m.mode & 0o777) for m in t.getmembers() if m.isfile()}


def head_and_base(d):
    """(files at HEAD, files at base, final reply) for a session dir, a git repo or a fixture dir."""
    if os.path.isdir(os.path.join(d, "repo")) and os.path.exists(os.path.join(d, "truth.json")):
        f = files_of_dir(os.path.join(d, "repo"))
        return f, f, ""
    rec = json.load(open(os.path.join(d, "record.json"))) if os.path.exists(os.path.join(d, "record.json")) else {}
    for repo in (os.path.join(d, "work"), d):
        if os.path.isdir(os.path.join(repo, ".git")):
            base = rec.get("base_commit") or git(repo, "rev-list", "--max-parents=0", "HEAD").split()[0]
            reply = ((rec.get("turns") or [{}])[-1]).get("reply", "")
            return files_at_head(repo), files_at(repo, base), reply
    raise SystemExit(f"no git repo or fixture in {d}")


def changed(head, base):
    return sorted(p for p in head if p not in base or head[p][0] != base[p][0])


def new_board_dirs(head, base):
    return sorted({p.split("/")[1] for p in changed(head, base)
                   if p.startswith("boards/") and p.count("/") >= 2 and not any(q.startswith(f"boards/{p.split('/')[1]}/") for q in base)})


def commands_in(text):
    """Shell commands a README or reply names: fenced or indented code lines and `inline` code that start like a command."""
    found = []
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
    lines = [l for b in blocks for l in b.splitlines()]
    lines += [l for l in text.splitlines() if l.startswith("    ")]
    lines += re.findall(r"`([^`\n]+)`", text)
    for l in lines:
        l = l.strip().lstrip("$ ").strip()
        if CMD_START.match(l) and not CMD_SKIP.search(l) and l not in found:
            found.append(l)
    return found


SHIM = '''import datetime as _dt, time as _time
_FIX = _dt.datetime({y}, {m}, {d}, 9, 0, 0)
_EPOCH = _FIX.replace(tzinfo=_dt.timezone.utc).timestamp()
_T0, _real = _time.time(), _time.time
class date(_dt.date):
    @classmethod
    def today(cls):
        return cls(_FIX.year, _FIX.month, _FIX.day)
class datetime(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(_time.time(), tz) if tz else cls(*_FIX.timetuple()[:6])
    @classmethod
    def today(cls):
        return cls(*_FIX.timetuple()[:6])
    @classmethod
    def utcnow(cls):
        return cls(*_FIX.timetuple()[:6])
_dt.date, _dt.datetime = date, datetime
_time.time = lambda: _EPOCH + (_real() - _T0)
_lt, _gt, _sf = _time.localtime, _time.gmtime, _time.strftime
_time.localtime = lambda s=None: _lt(_time.time() if s is None else s)
_time.gmtime = lambda s=None: _gt(_time.time() if s is None else s)
_time.strftime = lambda f, t=None: _sf(f, _time.localtime() if t is None else t)
'''


def markers_ok(texts, markers):
    blob = "\n".join(texts)
    return any(re.search(m, blob) for m in markers["hidden"]) and not any(re.search(m, blob) for m in markers["visible"])


def derived_hidden(data, visible, hidden):
    """A CSV the subject derived from the export (copied, cut to some columns, renamed, or split, e.g. a rota file):
    rebuild it from the hidden export the same way. Each of its columns maps to the export column whose values it
    shares most (header name first). Returns the new bytes, or None if the file is not derived from the export."""
    rd = lambda b: list(csv.reader(io.StringIO(b.decode("utf-8", "replace"))))
    try:
        f, v, h = rd(data), rd(visible), rd(hidden)
    except csv.Error:
        return None
    if len(f) < 2 or len(v) < 2:
        return None
    vh, vrows = [c.strip().lower() for c in v[0]], v[1:]
    vcols = [{r[j].strip() for r in vrows if j < len(r) and r[j].strip()} for j in range(len(vh))]
    fh, frows = f[0], f[1:]
    mapping = []
    for i, name in enumerate(fh):
        vals = {r[i].strip() for r in frows if i < len(r) and r[i].strip()}
        if name.strip().lower() in vh:
            mapping.append(vh.index(name.strip().lower())); continue
        best = max(range(len(vh)), key=lambda j: len(vals & vcols[j])) if vals else None
        mapping.append(best if best is not None and vals and len(vals & vcols[best]) >= max(1, len(vals) // 2) else None)
    if not frows or not any(m is not None for m in mapping):
        return None
    first = [r[0].strip() for r in frows if r and r[0].strip()]
    if mapping[0] is None or sum(x in vcols[mapping[0]] for x in first) < max(1, len(first) // 2):
        return None
    out, seen = [fh], set()
    for r in h[1:]:
        row = [r[m] if m is not None and m < len(r) else "" for m in mapping]
        if not any(c.strip() for c in row) or tuple(row) in seen:
            continue
        seen.add(tuple(row)); out.append(row)
    buf = io.StringIO(); csv.writer(buf, lineterminator="\n").writerows(out)
    return buf.getvalue().encode()


def html_pages(tree_dir, head, base, hint):
    """Candidate pages, best first: the hint, else html new or changed by the subject (or made by the rebuild) outside
    boards/events/ unless the subject's own commit changed boards/events/."""
    if hint:
        return [hint] if os.path.exists(os.path.join(tree_dir, hint)) else []
    touched_events = any(p.startswith("boards/events/") for p in changed(head, base))
    out = []
    for root, dirs, files in os.walk(tree_dir):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__")]
        for f in files:
            if not f.endswith((".html", ".htm")):
                continue
            rel = os.path.relpath(os.path.join(root, f), tree_dir)
            if rel.startswith("boards/events/") and not touched_events:
                continue
            if rel in base and rel in head and head[rel][0] == base[rel][0] and not rel.startswith("boards/events/"):
                continue
            out.append(rel)
    return sorted(out, key=lambda p: (not p.startswith("boards/"), os.path.basename(p) != "index.html", p.count("/"), p))


def run_cmd(cmd, cwd, env):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, env=env, capture_output=True, text=True, timeout=CMD_TIMEOUT)
        return {"cmd": cmd, "rc": p.returncode, "tail": (p.stdout + p.stderr)[-600:]}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "rc": "timeout", "tail": ""}


# ------------------------------------------------------------------------------------------------ browser


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


MARK_JS = """(sel) => {
  document.querySelectorAll('[data-h1-i]').forEach(e => e.removeAttribute('data-h1-i'));
  const out = []; let k = 0;
  for (const e of document.querySelectorAll(sel)) {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (r.width < 1 || r.height < 1 || s.visibility === 'hidden' || s.display === 'none' || e.disabled || e.closest('[hidden]')) continue;
    const cd = e.closest('details:not([open])');
    if (cd && e.closest('summary') !== cd.querySelector(':scope > summary')) continue;  // inside a closed fold
    if (e.tagName === 'A') {
      const h = e.getAttribute('href') || '';
      if (/^(mailto:|tel:|javascript:)/i.test(h) || e.hasAttribute('download')) continue;
      try { const u = new URL(e.href); if (u.origin !== location.origin) continue;
            if (u.pathname === location.pathname && u.search === location.search && h.startsWith('#')) continue; } catch (_) { continue; }
    }
    e.setAttribute('data-h1-i', String(k++));
    out.push(((e.innerText || e.value || e.getAttribute('aria-label') || e.tagName) + '').trim().replace(/\\s+/g, ' ').slice(0, 60));
  }
  return out;
}"""

FEAT_JS = """() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    const cd = e.closest('details:not([open])');
    if (cd && e.closest('summary') !== cd.querySelector(':scope > summary')) return false;  // inside a closed fold
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && (e.innerText || '').trim() !== ''; };
  const heads = [...document.querySelectorAll('h2,h3,h4,summary,[role="tab"],legend')].filter(vis);
  const empty = [];
  for (const h of heads) {
    const c = h.closest('section,details,article,fieldset') || h.parentElement;
    if (c === document.body || (c.tagName === 'DETAILS' && !c.open)) continue;
    const t = (c.innerText || '').replace(h.innerText || '', '').trim();
    if (!t || /^(none|nothing( here)?( yet)?|no (tasks|items|events|jobs)( yet)?|—|-|0)\\.?$/i.test(t)) empty.push((h.innerText || '').trim().slice(0, 40));
  }
  return {hscroll: document.documentElement.scrollWidth > window.innerWidth + 1, scroll_width: document.documentElement.scrollWidth,
          heads: heads.map(h => (h.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 60)),
          foreign_heads: heads.filter(h => !h.closest('[data-kit]')).length,
          empty_sections: empty, text: document.body ? document.body.innerText : '', height: document.documentElement.scrollHeight};
}"""


def explore(url, shots, today):
    """Opening view, then states one and two taps away. Returns (states, caps hit)."""
    from playwright.sync_api import sync_playwright
    from datetime import datetime, timezone
    os.makedirs(shots, exist_ok=True)
    states, seen, caps = [], set(), []
    origin = "/".join(url.split("/", 3)[:3]) + "/"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": VIEW_W, "height": VIEW_H}, device_scale_factor=1, timezone_id="UTC")

        def open_path(path):
            page = ctx.new_page()
            page.clock.set_fixed_time(datetime(today.year, today.month, today.day, 9, tzinfo=timezone.utc))
            page.goto(url, wait_until="load")
            page.wait_for_timeout(250)
            labels = []
            for i in path:
                els = page.evaluate(MARK_JS, CLICKABLE)
                if i >= len(els):
                    return page, None
                try:
                    page.click(f'[data-h1-i="{i}"]', timeout=3000)
                    page.wait_for_load_state("load")
                    page.wait_for_timeout(250)
                except Exception:
                    return page, None
                labels.append(els[i])
            return page, labels

        def capture(page, path, labels):
            if not page.url.startswith(origin):  # a tap that left the served site is not a state of the board
                return None
            digest = hashlib.sha256(page.screenshot(full_page=True)).hexdigest()
            if digest in seen:
                return None
            if len(states) >= CAP["states"]:
                caps.append("states")
                return None
            seen.add(digest)
            sid = len(states)
            feat = page.evaluate(FEAT_JS)
            feat["html"] = page.content()
            n = max(1, math.ceil(feat["height"] / VIEW_H))
            if n > CAP["screens_per_state"]:
                caps.append(f"screens_per_state (state {sid}: {n} screens)")
            names = []
            for s in range(min(n, CAP["screens_per_state"])):
                page.evaluate(f"window.scrollTo(0, {s * VIEW_H})")
                page.wait_for_timeout(60)
                name = f"t{len(path)}-{sid:02d}-s{s + 1}.png"
                page.screenshot(path=os.path.join(shots, name))
                names.append(name)
            st = {"id": sid, "taps": len(path), "path": path, "tapped": labels, "screens": n, "shots": names, **feat}
            states.append(st)
            return st

        page, _ = open_path([])
        capture(page, [], [])
        n0 = len(page.evaluate(MARK_JS, CLICKABLE))
        page.close()
        if n0 > CAP["taps_from_opening"]:
            caps.append(f"taps_from_opening ({n0} tappable)")
        for i in range(min(n0, CAP["taps_from_opening"])):
            if len(states) >= CAP["states"]:
                caps.append("states")
                break
            page, labels = open_path([i])
            if labels is not None:
                capture(page, [i], labels)
            page.close()
        for st in [s for s in states if s["taps"] == 1]:
            if len(states) >= CAP["states"]:
                break
            page, _ = open_path(st["path"])
            n1 = len(page.evaluate(MARK_JS, CLICKABLE))
            page.close()
            if n1 > CAP["taps_from_each_state"]:
                caps.append(f"taps_from_each_state (state {st['id']}: {n1} tappable)")
            for j in range(min(n1, CAP["taps_from_each_state"])):
                if len(states) >= CAP["states"]:
                    caps.append("states")
                    break
                page, labels = open_path(st["path"] + [j])
                if labels is not None:
                    capture(page, st["path"] + [j], labels)
                page.close()
        browser.close()
    return states, sorted(set(caps))


def serve(root):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# -------------------------------------------------------------------------------------------------- render


def render(subject, hidden_csv, out):
    from datetime import date
    items_path = hidden_csv[:-4] + ".items.json"
    keys = json.load(open(items_path))
    today = date.fromisoformat(keys["today"])
    head, base, reply = head_and_base(subject)
    hidden = open(hidden_csv, "rb").read()
    rep = keys["replaces"]
    visible = base.get(rep, (b"", 0))[0]
    vis_header = visible.split(b"\n", 1)[0]
    tree = dict(head)
    swapped = []
    for p, (data, mode) in list(tree.items()):
        if p == rep or (visible and data == visible) or (p.endswith(".csv") and vis_header and data.split(b"\n", 1)[0] == vis_header):
            tree[p] = (hidden, mode); swapped.append(p)
    for p, (data, mode) in list(tree.items()):  # copies the subject reshaped (fix registered 2026-11-23 after H1-nodoc)
        if p.endswith(".csv") and p not in swapped and not p.startswith("boards/events/") and visible:
            d = derived_hidden(data, visible, hidden)
            if d is not None:
                tree[p] = (d, mode); swapped.append(p + " (derived)")
    if rep not in tree:
        tree[rep] = (hidden, 0o644); swapped.append(rep)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    tmp = tempfile.mkdtemp(prefix="h1-render-")
    try:
        work = os.path.join(tmp, "tree")
        os.makedirs(work)
        write_tree(tree, work)
        shim = os.path.join(tmp, "shim")
        os.makedirs(shim)
        open(os.path.join(shim, "sitecustomize.py"), "w").write(SHIM.format(y=today.year, m=today.month, d=today.day))
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "LANG": "C.UTF-8", "TZ": "UTC",
               "PYTHONPATH": shim, "PYTHONDONTWRITEBYTECODE": "1"}
        dirs = new_board_dirs(head, base)
        documented = [keys["documented"]] if keys.get("documented") else [f"python3 kit/board.py boards/{x}" for x in dirs]
        readme_cmds = [c for p in changed(head, base) if os.path.basename(p).lower() == "readme.md"
                       for c in commands_in(head[p][0].decode("utf-8", "replace"))]
        cands = [("documented", c) for c in documented] + [("readme", c) for c in readme_cmds] + [("reply", c) for c in commands_in(reply)]
        seen_cmds, ran, rebuild_by = set(), [], None

        def static_ok():
            return any(markers_ok([open(os.path.join(work, p), errors="replace").read()], keys["markers"])
                       for p in html_pages(work, head, base, keys.get("page_hint")))
        for src, c in cands:
            if c in seen_cmds:
                continue
            seen_cmds.add(c)
            r = run_cmd(c, work, env); r["source"] = src
            ran.append(r)
            if src == "documented" and any(s2 == "documented" and c2 not in seen_cmds for s2, c2 in cands):
                continue  # build every new board before judging (fix 2026-11-23: nd-8 built two boards)
            if static_ok():
                rebuild_by = r
                break
        pages = html_pages(work, head, base, keys.get("page_hint"))
        def mscore(p):  # the page carrying most of the hidden data, not the first that carries any (fix 2026-11-23)
            t = open(os.path.join(work, p), errors="replace").read()
            return sum(bool(re.search(m, t)) for m in keys["markers"]["hidden"]) if markers_ok([t], keys["markers"]) else -1
        page = max(pages, key=lambda p: (mscore(p), -pages.index(p))) if pages else None
        states, caps = [], []
        if page:
            srv = serve(work)
            try:
                states, caps = explore(f"http://127.0.0.1:{srv.server_address[1]}/{page}", os.path.join(out, "shots"), today)
            finally:
                srv.shutdown()
        rebuild_ok = bool(states) and markers_ok([s["html"] for s in states], keys["markers"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lines = []
    for s in states:
        how = "as opened" if not s["taps"] else "after tapping " + " then ".join(f"“{t}”" for t in s["tapped"])
        for k, name in enumerate(s["shots"]):
            lines.append(f"{name}  {s['taps']} tap{'s' if s['taps'] != 1 else ''}: {how}; screen {k + 1} of {len(s['shots'])}")
    if states:
        open(os.path.join(out, "shots", "index.txt"), "w").write("\n".join(lines) + "\n")
    texts = [s["text"] for s in states]
    counts = {"n_states": len(states), "hscroll_opening": bool(states and states[0]["hscroll"]),
              "hscroll_any": any(s["hscroll"] for s in states),
              "raw_tokens": {t: sum(len(re.findall(rf"(?<![\w-]){t}(?![\w-])", x)) for x in texts) for t in RAW_TOKENS},
              "zero_counts": sorted({m.group(0).strip() for x in texts for m in ZERO.finditer(x)}),
              "empty_sections": sorted({e for s in states for e in s["empty_sections"]}),
              "screens_opening": states[0]["screens"] if states else 0}
    counts["raw_tokens"] = {k: v for k, v in counts["raw_tokens"].items() if v}
    counts["cumbersome"] = sum([counts["hscroll_any"], bool(counts["raw_tokens"]), bool(counts["zero_counts"]), bool(counts["empty_sections"])])
    res = {"subject": os.path.abspath(subject), "hidden_csv": os.path.abspath(hidden_csv), "swapped": swapped, "page": page,
           "commands": ran, "rebuild_by": rebuild_by and rebuild_by["cmd"], "rebuild_source": rebuild_by and rebuild_by["source"],
           "rebuild_ok": rebuild_ok, "caps": CAP, "caps_hit": caps, "counts": counts,
           "states": [{k: v for k, v in s.items() if k not in ("html", "text")} | {"text": s["text"][:4000]} for s in states]}
    res["class"] = classify_trees(head, base, res)
    json.dump(keys, open(os.path.join(out, "keys.json"), "w"), indent=1)
    json.dump(res, open(os.path.join(out, "render.json"), "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------ classify


class Heads(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.n = 0; self.taps = 0

    def handle_starttag(self, tag, attrs):
        self.n += tag in ("h2", "h3", "h4", "summary", "legend")
        self.taps += tag in ("details", "button") or any(k == "onclick" or (k == "role" and v == "tab") for k, v in attrs)


def classify_trees(head, base, rend=None):
    """Reported only. HELD: no board made or changed. COPY: a new board keeps the events board's form (its board.json
    sections by "event" with the events board's column labels) and nothing beside it. ADDED: that form kept on the
    opening view with something new beside it (extra board.json keys, another page in the board's folder, headings the
    kit did not draw), or the events board itself changed to carry the new thing. LITERAL: one flat list (at most one
    grouping heading on the opening view, nothing to tap). FIT: none of these."""
    ch = changed(head, base)
    dirs = new_board_dirs(head, base)
    events_changed = any(p.startswith("boards/events/") for p in ch)
    pages = [p for p in ch if p.endswith((".html", ".htm"))]
    if not dirs and not events_changed and not pages:
        return "HELD"
    if not dirs and events_changed:
        return "ADDED"
    d = f"boards/{dirs[0]}" if dirs else os.path.dirname(pages[0])
    cfg = None
    if f"{d}/board.json" in head:
        try:
            cfg = json.loads(head[f"{d}/board.json"][0])
        except ValueError:
            cfg = None
    copy_core = isinstance(cfg, dict) and isinstance(cfg.get("section"), dict) and cfg["section"].get("field") == EV_SECTION \
        and [c.get("label") for c in cfg.get("columns", [])] == EV_LABELS
    if copy_core:
        other_pages = [p for p in head if p.startswith(d + "/") and p.endswith(".html") and p != f"{d}/index.html"]
        foreign = bool(rend and rend.get("states") and rend["states"][0].get("foreign_heads"))
        return "ADDED" if (set(cfg) - STAMP_KEYS or other_pages or foreign) else "COPY"
    if rend and rend.get("states"):
        n_heads, n_states = len(rend["states"][0]["heads"]), rend["counts"]["n_states"]
    else:
        hp = Heads()
        page = f"{d}/index.html" if f"{d}/index.html" in head else (pages[0] if pages else None)
        hp.feed(head[page][0].decode("utf-8", "replace") if page in head else "")
        n_heads, n_states = hp.n, 1 + hp.taps
    return "LITERAL" if n_heads <= 1 and n_states <= 1 else "FIT"


def classify(subject, render_out=None):
    head, base, _ = head_and_base(subject)
    rend = json.load(open(os.path.join(render_out, "render.json"))) if render_out else None
    return classify_trees(head, base, rend)


# ------------------------------------------------------------------------------------------------- readers


def parse_answer(reply):
    m = re.search(r"ANSWER:\s*(.*?)(?:\n\s*SCREENSHOT:|\Z)", reply or "", re.S | re.I)
    ans = (m.group(1).strip() if m else "").strip()
    s = re.search(r"SCREENSHOT:\s*(.*)", reply or "", re.I)
    shots = SHOT.findall(s.group(1)) if s else []
    return ans, [f"t{a}-{b}-s{c}" for a, b, c in shots], (max(int(a) for a, _, _ in shots) if shots else None)


def date_right(ans, iso):
    from datetime import date
    d = date.fromisoformat(iso)
    month = re.search(rf"\b({d:%B}|{d:%b})\b", ans, re.I)
    day_ = re.search(rf"\b0?{d.day}(st|nd|rd|th)?\b", ans)
    return bool((month and day_) or iso in ans or re.search(rf"\b0?{d.day}/0?{d.month}\b", ans))


def judge(item, ans):
    if not ans or re.search(r"CANT[_ ]TELL|can'?t tell", ans, re.I):
        return False
    k = item["kind"]
    if k == "names":
        pat = lambda t: r"\b" + re.escape(t).replace(r"\ ", r"\s+")
        kept = " ".join(c for c in re.split(r"(?<=[.;])\s+|\n", ans) if not EXCLUDE.search(c))  # a name brought up to exclude it is not part of the answer
        return all(re.search(pat(t), ans, re.I) for t in item["require"]) and not any(re.search(pat(t), kept, re.I) for t in item["forbid"])
    if k == "nobody":
        return bool(NOBODY.search(ans))
    if k == "unknown":
        return not re.search(r"\d", ans) and bool(UNKNOWN.search(ans))
    if k == "date":
        return date_right(ans, item["key"])
    if k == "yes":
        return bool(YES.search(ans)) and not NO.search(ans)
    raise ValueError(k)


def score_run(keys, answers):
    """answers: {item id: reply text}. Returns the run's score dict."""
    rows = []
    for it in keys["items"]:
        ans, shots, taps = parse_answer(answers.get(it["id"], ""))
        rows.append({"id": it["id"], "q": it["q"], "answer": ans, "screenshots": shots, "taps": taps, "right": judge(it, ans)})
    return {"right": sum(r["right"] for r in rows), "of": len(rows), "items": rows}


def peeked(transcript, shots_dir):
    """Did the reader read or list anything outside its shots folder?"""
    for line in open(transcript, errors="replace"):
        for m in re.finditer(r'"(?:file_path|path)"\s*:\s*"([^"]+)"', line):
            p = m.group(1)
            if os.path.isabs(p) and not os.path.realpath(p).startswith(os.path.realpath(shots_dir)):
                return True
    return False


def reader_void(rec):
    t = rec["turns"][0]
    if rec.get("dry_run"):
        return "dry run"
    if t.get("rc") != 0:
        return f"claude exited {t.get('rc')}"
    if not any("sonnet" in m for m in rec.get("served_models", [])):
        return f"served {rec.get('served_models')}"
    if rec.get("peeked"):
        return "read outside its shots folder"
    return None


def readers(out, run, reader="sonnet-medium", dry=False, budget="2"):
    import run_v5
    from run_downstream import DryRun  # noqa: E402  (reuse, not copies)
    rend = json.load(open(os.path.join(out, "render.json")))
    keys = json.load(open(os.path.join(out, "keys.json")))
    rdir = os.path.join(out, "readers", f"run{run}")
    os.makedirs(rdir, exist_ok=True)
    if not rend["rebuild_ok"]:
        res = score_run(keys, {}) | {"void": [], "note": "rebuild failed: reader fail without a reader session"}
        json.dump(res, open(os.path.join(rdir, "score.json"), "w"), indent=1)
        print(json.dumps({"out": out, "run": run, "right": 0, "note": res["note"]}))
        return res
    run_v5.FLAGS[:] = READER_FLAGS  # tools: Read and Glob only (the readers see the screenshots, nothing else)
    if dry:
        run_v5.subprocess = DryRun()
    model, effort = run_v5.READERS[reader]
    answers, voids = {}, []
    for it in keys["items"]:
        root = os.path.join(rdir, it["id"])
        rp = os.path.join(root, "record.json")
        old = json.load(open(rp)) if os.path.exists(rp) else None
        if old is not None and not reader_void(old) and not dry:
            answers[it["id"]] = old["turns"][0]["reply"]
            continue
        shutil.rmtree(root, ignore_errors=True)
        home, work, loaded = run_v5.setup(argparse.Namespace(arm="none"), root)
        shutil.copytree(os.path.join(out, "shots"), work)
        tdir = os.path.join(root, "transcripts"); os.makedirs(tdir)
        prompt = READER_PROMPT.format(context=keys["context"], q=it["q"])
        p = run_v5.turn(prompt, model, effort, work, run_v5.subject_env(home), os.path.join(tdir, "T1.jsonl"), str(uuid.uuid4()), True, budget)
        rec = {"item": it["id"], "run": run, "reader": reader, "model_requested": model, "effort_requested": effort, "dry_run": dry,
               "rules_loaded": loaded, "flags": list(run_v5.FLAGS), "turns": [p], "served_models": p["models_main"],
               "peeked": peeked(os.path.join(tdir, "T1.jsonl"), work),
               "harness_sha256": {n: run_v5.sha(os.path.join(LIVE, n)) for n in ("run_v5.py", "run_kta.py")} |
                                 {"score_h1.py": run_v5.sha(os.path.abspath(__file__))}}
        json.dump(rec, open(rp, "w"), indent=1)
        v = reader_void(rec)
        if v:
            voids.append({"id": it["id"], "why": v})
        answers[it["id"]] = p["reply"]
        print(f"{out} run{run} {it['id']}: rc={p['rc']} models={p['models_main']} void={v}", flush=True)
    res = score_run(keys, answers) | {"void": voids, "dry_run": dry}
    json.dump(res, open(os.path.join(rdir, "score.json"), "w"), indent=1)
    print(json.dumps({"out": out, "run": run, "right": res["right"], "of": res["of"], "void": voids}))
    return res


API_PROMPT = """You are looking at screenshots of a web page, as a member of an allotment committee sees it on their phone.
The screenshots follow, each after a line naming it. Each name says how many taps from opening the page it took
(t0 = as opened, t1 = after one tap, t2 = after two taps; the line says what was tapped) and which screen down the
page it is (s1 = the top, s2 = after scrolling one screen, and so on).

{context}

Question: {q}

Answer from what the screenshots show, nothing else. If they don't show the answer, say CANT_TELL.
Reply in exactly this form, two lines:
ANSWER: <your answer, or CANT_TELL>
SCREENSHOT: <the file name(s) you used, comma-separated>
"""


def api_reader_body(model, prompt, shots, max_images=48):
    """One OpenRouter chat request: the prompt, then each screenshot after its index line. ZDR enforced per request.
    Some providers cap images per request (Azure GPT: 50, seen 2026-11-17), so above max_images two consecutive screens
    of one state go side by side in one image, labelled left and right; every reader of a board gets the same input."""
    import base64, io as _io
    from PIL import Image
    lines = [l for l in open(os.path.join(shots, "index.txt"), encoding="utf-8").read().splitlines() if l.split() and l.split()[0].endswith(".png")]
    groups = [[l] for l in lines]
    if len(groups) > max_images:
        groups, cur = [], []
        for l in lines:
            if cur and (len(cur) == 2 or cur[0].split()[0].rsplit("-s", 1)[0] != l.split()[0].rsplit("-s", 1)[0]):
                groups.append(cur); cur = []
            cur.append(l)
        groups.append(cur)
    content = [{"type": "text", "text": prompt}]
    for g in groups:
        if len(g) == 1:
            data = open(os.path.join(shots, g[0].split()[0]), "rb").read(); label = g[0]
        else:
            ims = [Image.open(os.path.join(shots, l.split()[0])).convert("RGB") for l in g]
            gap = 16; canvas = Image.new("RGB", (sum(i.width for i in ims) + gap, max(i.height for i in ims)), "white")
            canvas.paste(ims[0], (0, 0)); canvas.paste(ims[1], (ims[0].width + gap, 0))
            buf = _io.BytesIO(); canvas.save(buf, "PNG"); data = buf.getvalue()
            label = f"Two screenshots side by side. Left: {g[0]}  |  Right: {g[1]}"
        content.append({"type": "text", "text": label})
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(data).decode()}})
    return {"model": model, "messages": [{"role": "user", "content": content}], "max_tokens": 4000,
            "provider": {"zdr": True, "data_collection": "deny"}, "reasoning": {"effort": "low"}}


def readers_api(out, run, model, dry=False):
    """Off-Claude readers (owner, 2026-11-17): one OpenRouter call per item, screenshots only, nothing else."""
    sys.path.insert(0, os.path.join(LIVE, "u1"))
    from score_u import stream_post  # noqa: E402  (reuse, not copies)
    rend = json.load(open(os.path.join(out, "render.json")))
    keys = json.load(open(os.path.join(out, "keys.json")))
    rdir = os.path.join(out, "readers", f"run{run}")
    os.makedirs(rdir, exist_ok=True)
    if not rend["rebuild_ok"]:
        res = score_run(keys, {}) | {"void": [], "note": "rebuild failed: reader fail without a reader session", "reader": model}
        json.dump(res, open(os.path.join(rdir, "score.json"), "w"), indent=1)
        print(json.dumps({"out": out, "run": run, "right": 0, "note": res["note"]}))
        return res
    answers, voids = {}, []
    for it in keys["items"]:
        root = os.path.join(rdir, it["id"]); os.makedirs(root, exist_ok=True)
        rp = os.path.join(root, "record.json")
        old = json.load(open(rp)) if os.path.exists(rp) else None
        if old and old.get("model_requested") == model and old.get("reply") and not dry:
            answers[it["id"]] = old["reply"]
            continue
        body = api_reader_body(model, API_PROMPT.format(context=keys["context"], q=it["q"]), os.path.join(out, "shots"))
        if dry:
            n_img = sum(1 for c in body["messages"][0]["content"] if c["type"] == "image_url")
            print(f"DRY {out} run{run} {it['id']}: {model}, {n_img} images, provider={body['provider']}")
            voids.append({"id": it["id"], "why": "dry run"}); continue
        rec = {"item": it["id"], "run": run, "reader": "openrouter", "model_requested": model, "provider_req": body["provider"]}
        try:
            r = stream_post(body, id_file=os.path.join(root, "generation_id.txt"))
            rec |= {"reply": r["choices"][0]["message"]["content"], "served_model": r.get("model"), "provider": r.get("provider"),
                    "generation_id": r.get("id"), "usage": r.get("usage"), "finish_reason": r.get("finish_reason")}
        except Exception as e:  # noqa: BLE001  a failed call is a void item, re-run next time
            rec |= {"reply": "", "error": str(e)[:2000]}
        json.dump(rec, open(rp, "w"), indent=1)
        if not rec["reply"]:
            voids.append({"id": it["id"], "why": rec.get("error", "empty reply")})
        answers[it["id"]] = rec["reply"]
        print(f"{out} run{run} {it['id']}: {rec.get('served_model')} {rec.get('provider')} void={not rec['reply']}", flush=True)
    res = score_run(keys, answers) | {"void": voids, "dry_run": dry, "reader": model}
    json.dump(res, open(os.path.join(rdir, "score.json"), "w"), indent=1)
    print(json.dumps({"out": out, "run": run, "right": res["right"], "of": res["of"], "void": voids}))
    return res


def gates(outs):
    res = []
    for out in outs:
        rend = json.load(open(os.path.join(out, "render.json")))
        runs = []
        for n in (1, 2):
            p = os.path.join(out, "readers", f"run{n}", "score.json")
            runs.append(json.load(open(p)) if os.path.exists(p) else None)
        ok = [r is not None and not r.get("dry_run") and not r.get("void") and r["right"] >= 6 for r in runs]
        res.append({"out": out, "rebuild_ok": rend["rebuild_ok"], "rebuild_by": rend["rebuild_by"],
                    "right": [r and r["right"] for r in runs], "void": [r and r.get("void") for r in runs],
                    "reader_pass": all(ok), "complete": all(r is not None and not r.get("dry_run") and not r.get("void") for r in runs),
                    "taps": [r and {i["id"]: i["taps"] for i in r["items"]} for r in runs],
                    "class": rend["class"], "counts": rend["counts"], "caps_hit": rend["caps_hit"]})
    return res


# ------------------------------------------------------------------------------------------------ anchors


def make_subject(fixture, d, apply=None, reply=""):
    """A run_v5-shaped session dir: work/ = the fixture repo with one initial commit, then the subject's commit."""
    work = os.path.join(d, "work")
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(fixture, "repo"), work)
    git(work, "init", "-q", "-b", "main")
    git(work, "add", "-A"); git(work, "commit", "-qm", "Initial import")
    base = git(work, "rev-parse", "HEAD")
    if apply:
        apply(work)
    if git(work, "status", "--porcelain"):
        git(work, "add", "-A"); git(work, "commit", "-qm", "subject edit")
    json.dump({"base_commit": base, "turns": [{"id": "T1", "rc": 0, "reply": reply}]}, open(os.path.join(d, "record.json"), "w"), indent=1)
    return d


def anchor(fixture, name, out):
    sys.path.insert(0, os.path.join(HERE, "references"))
    import anchors
    want = anchors.FIXTURE_OF[name]
    if os.path.basename(os.path.normpath(fixture)) != want:
        raise SystemExit(f"anchor {name} is for {want}")
    return make_subject(fixture, out, anchors.APPLY[name], anchors.REPLIES[name])


# ------------------------------------------------------------------------------------------------ selftest


def proxy(rend, need):
    """Selftest only: is there one visible line (in any state) matching every regex in `need`?"""
    return any(all(re.search(n, line, re.I) for n in need) for s in rend["states"] for line in s["text"].splitlines())


def selftest():
    import make_fixture_h1 as mf
    sys.path.insert(0, os.path.join(HERE, "references"))
    import anchors
    fails, lines = [], []

    def expect(label, got, want):
        ok = want(got) if callable(want) else got == want
        lines.append(f"{'ok  ' if ok else 'FAIL'} {label}: got {got}" + ("" if callable(want) else f", want {want}"))
        if not ok:
            fails.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        fx = os.path.join(tmp, "fx"); mf.main(fx)
        hid = os.path.join(fx, "hidden")
        main_fx, mir_fx = os.path.join(fx, "h1-v1"), os.path.join(fx, "h1m-v1")

        # fixture facts
        for f in (main_fx, mir_fx):
            t = json.load(open(os.path.join(f, "truth.json")))
            n = os.path.basename(f)
            expect(f"{n} prompt is the registered wording", t["prompts"]["T1"], mf.PROMPT)
            readme = open(os.path.join(f, "repo", "README.md")).read()
            expect(f"{n} README names no pattern.md / design / adapt", re.findall(r"pattern\.md|design|adapt", readme, re.I), [])
            pat = open(os.path.join(f, "repo", "docs", "pattern.md")).read()
            expect(f"{n} pattern.md: no checklist or questions", re.findall(r"\?|^\s*[-*] \[|^\s*\d+\.", pat, re.M), [])
            expect(f"{n} pattern.md: the 'one instance' statement in three sections",
                   sum(bool(re.search(r"one way|nothing about the events board is fixed|one instance", sec, re.I))
                       for sec in pat.split("\n## ")[1:]), 3)
            raw = "".join(open(os.path.join(r, x)).read() for d_ in ("minutes", "mail") for r, _, fs in os.walk(os.path.join(f, "repo", d_)) for x in fs)
            for hf in os.listdir(os.path.join(hid, n)):
                if hf.endswith(".items.json"):
                    for it in json.load(open(os.path.join(hid, n, hf)))["items"]:
                        if it["q"].lower() in raw.lower():
                            expect(f"{n} raw material does not hold item wording", it["q"], None)
            expect(f"{n} raw material avoids 'whose turn' / 'overdue'", re.findall(r"whose turn|overdue", raw, re.I), [])
            expect(f"{n} no __pycache__ in the tree", [r for r, _, _ in os.walk(f) if "__pycache__" in r], [])
        vis = list(csv.DictReader(open(os.path.join(main_fx, "repo", "incoming", "tasks.csv"))))
        hcsv = list(csv.DictReader(open(os.path.join(hid, "h1-v1", "tasks.csv"))))
        expect("main tasks.csv: 40 tasks, 9 columns, rota present", (len(vis), len(vis[0]), sum(bool(r["water_week"]) for r in vis)),
               (40, 9, 12))
        expect("hidden tasks.csv: same header", list(hcsv[0]), list(vis[0]))
        expect("hidden rows differ from visible rows", len({tuple(r.values()) for r in hcsv} & {tuple(r.values()) for r in vis}), 0)
        expect("hidden people differ (Wren, Josef in; Bea out)",
               ({r["who"] for r in hcsv} - {r["who"] for r in vis}, "Bea" in {r["who"] for r in hcsv}), ({"Wren", "Josef"}, False))

        # keys computed from the hidden rows, against the registered design
        k = {i["id"]: i for i in json.load(open(os.path.join(hid, "h1-v1", "tasks.items.json")))["items"]}
        expect("key water", k["water"]["require"], ["Wren"])
        expect("key overdue", sorted(k["overdue"]["require"]), ["ditch", "hedge", "insurance", "rotavator"])
        expect("key person (Priya before Thu)", sorted(k["person"]["require"]), ["minutes", "skip"])
        expect("key council", sorted(k["council"]["require"]), ["lock", "meter"])
        expect("key nobody", k["nobody"]["key"], "nobody")
        expect("key unknown count (not 0)", k["unknown"]["key"], "unknown")
        expect("key two rows", sorted(k["two_rows"]["require"]), ["Dot", "Josef"])
        expect("7 items each", [len(json.load(open(os.path.join(hid, a, b)))["items"]) for a, b in
                                (("h1-v1", "tasks.items.json"), ("h1-v1", "events.items.json"), ("h1m-v1", "tasks.items.json"))], [7, 7, 7])

        # judge
        J = lambda iid, a: judge(k[iid], a)
        expect("judge: right answers", [J("water", "Wren"), J("overdue", "Drainage ditch, rotavator, hedge, insurance"),
                                        J("nobody", "Nobody yet"), J("unknown", "Not decided yet (blank)"), J("two_rows", "Josef and Dot")], [True] * 5)
        expect("judge: planted wrong answers fail", [J("water", "Tomas"), J("overdue", "ditch, rotavator, hedge, insurance, water bill"),
                                                     J("nobody", "Hal"), J("unknown", "0"), J("unknown", "CANT_TELL"),
                                                     J("two_rows", "Josef"), J("council", "the water meter")], [False] * 7)
        expect("judge: a name brought up to exclude it does not count (stage 0)", [
            J("person", "Priya needs to book the skip and send round the minutes. Her third task, drafting the open day leaflet, is due Fri 2 Apr, after the meeting."),
            J("council", "Yes: the gate lock and the water meter. The fly-tipping also says waiting on council, but it is marked done, so I haven't counted it."),
            J("unknown", "No, not decided yet."), J("person", "skip, minutes, leaflet")], [True, True, True, False])
        ek = {i["id"]: i for i in json.load(open(os.path.join(hid, "h1-v1", "events.items.json")))["items"]}
        expect("judge: dates and yes/no", [judge(ek["when"], "Sat 15 May 2027"), judge(ek["when"], "8 May"),
                                           judge(ek["done"], "Yes, done"), judge(ek["done"], "No, not done")], [True, False, True, False])
        expect("parse_answer: taps from the label", parse_answer("ANSWER: Wren\nSCREENSHOT: t1-03-s1.png, t0-00-s2.png")[2], 1)

        # gates on planted scores
        g = os.path.join(tmp, "g")
        os.makedirs(os.path.join(g, "readers", "run1")); os.makedirs(os.path.join(g, "readers", "run2"))
        json.dump({"rebuild_ok": True, "rebuild_by": "x", "class": "FIT", "counts": {}, "caps_hit": []}, open(os.path.join(g, "render.json"), "w"))
        def put(n, right):
            json.dump({"right": right, "of": 7, "items": [], "void": []}, open(os.path.join(g, "readers", f"run{n}", "score.json"), "w"))
        put(1, 7); put(2, 5)
        expect("gates: 7 and 5 -> fail", gates([g])[0]["reader_pass"], False)
        put(2, 6)
        expect("gates: 7 and 6 -> pass", gates([g])[0]["reader_pass"], True)

        # renderer on the events board (stage 0 gate 2 path), hidden events data
        ev = render(main_fx, os.path.join(hid, "h1-v1", "events.csv"), os.path.join(tmp, "r-events"))
        expect("events: rebuilt by the documented command", (ev["rebuild_ok"], ev["rebuild_source"]), (True, "documented"))
        expect("events: past events fold gives a one-tap state", [s["taps"] for s in ev["states"]], [0, 1])
        expect("events: no horizontal scroll, no cumbersome counts", (ev["counts"]["hscroll_any"], ev["counts"]["cumbersome"]), (False, 0))
        expect("events: screenshots exist and are indexed", all(os.path.exists(os.path.join(tmp, "r-events", "shots", n))
                                                              for s in ev["states"] for n in s["shots"]) and
               os.path.exists(os.path.join(tmp, "r-events", "shots", "index.txt")), True)
        expect("events: plant sale date visible (proxy)", proxy(ev, [r"plant sale", r"15 May"]), True)
        expect("events: held subject classifies HELD", classify(main_fx), "HELD")

        # anchors
        R = {}
        for name in ("a", "b", "c", "d", "e", "m-a", "m-b"):
            fxd = main_fx if anchors.FIXTURE_OF[name] == "h1-v1" else mir_fx
            subj = anchor(fxd, name, os.path.join(tmp, f"s-{name}"))
            R[name] = render(subj, os.path.join(hid, anchors.FIXTURE_OF[name], "tasks.csv"), os.path.join(tmp, f"r-{name}"))
            expect(f"anchor {name}: rebuilt on hidden data", R[name]["rebuild_ok"], True)
        expect("anchor a, b, m-a rebuilt by the documented kit command", [R[n]["rebuild_source"] for n in ("a", "b", "m-a")], ["documented"] * 3)
        expect("anchor c, d, e, m-b rebuilt by the command their README names", [R[n]["rebuild_source"] for n in ("c", "d", "e", "m-b")], ["readme"] * 4)
        expect("classes", {n: R[n]["class"] for n in R}, {"a": "COPY", "b": "ADDED", "c": "FIT", "d": "FIT", "e": "LITERAL", "m-a": "COPY", "m-b": "FIT"})
        expect("classify command agrees with render", classify(os.path.join(tmp, "s-b"), os.path.join(tmp, "r-b")), "ADDED")
        expect("anchor d: >= 2 cumbersome counts (hscroll, raw tokens, zero counts)",
               (R["d"]["counts"]["hscroll_any"], bool(R["d"]["counts"]["raw_tokens"]), bool(R["d"]["counts"]["zero_counts"])), (True, True, True))
        expect("anchor d: tap cap hit and recorded", any("taps_from_opening" in c for c in R["d"]["caps_hit"]), True)
        expect("anchor c: no horizontal scroll, no cumbersome counts", (R["c"]["counts"]["hscroll_any"], R["c"]["counts"]["cumbersome"]), (False, 0))
        water = [r"\bWren\b", r"water|rota|15 Mar|2027-03-15"]
        expect("proxy: this week's waterer visible (c yes, b yes after a tap, a no)",
               [proxy(R[n], water) for n in ("c", "b", "a")], [True, True, False])
        expect("proxy: manure quantity shown as not decided (c)", proxy(R["c"], [r"manure|how many", r"not decided"]), True)
        expect("proxy: May fair date visible (m-a yes, m-b no)", [proxy(R[n], [r"May fair", r"22 May"]) for n in ("m-a", "m-b")], [True, False])
        expect("swap replaced the copied CSV (a)", sorted(R["a"]["swapped"]), ["boards/committee-tasks/tasks.csv", "incoming/tasks.csv"])

        # planted breaks
        def embedded(work):
            os.makedirs(os.path.join(work, "boards", "frozen"))
            rows = list(csv.DictReader(open(os.path.join(work, "incoming", "tasks.csv"))))
            open(os.path.join(work, "boards", "frozen", "index.html"), "w").write(
                "<!doctype html><meta name=viewport content='width=device-width'><ul>" + "".join(f"<li>{r['task']} {r['who']}</li>" for r in rows) + "</ul>")
        s = make_subject(main_fx, os.path.join(tmp, "s-frozen"), embedded, "Made boards/frozen.")
        r = render(s, os.path.join(hid, "h1-v1", "tasks.csv"), os.path.join(tmp, "r-frozen"))
        expect("planted: data frozen into the page -> rebuild fails", r["rebuild_ok"], False)
        res = readers(os.path.join(tmp, "r-frozen"), 1)
        expect("planted: rebuild failure scores 0 without a reader session", (res["right"], os.listdir(os.path.join(tmp, "r-frozen", "readers", "run1"))),
               (0, ["score.json"]))

        def broken(work):
            built("h1-v1/c", "committee")(work)
            p = os.path.join(work, "boards", "committee", "build.py")
            src = open(p).read()  # fail before the page is written: the committed page keeps the visible data
            open(p, "w").write(src.replace('\nif __name__ == "__main__":', '\nraise SystemExit(3)\n\nif __name__ == "__main__":'))
        def built(src, board):
            return lambda work: anchors.built(src, board, anchors.readme(board, "Committee tasks board"))(work)
        s = make_subject(main_fx, os.path.join(tmp, "s-broken"), broken, "")
        r = render(s, os.path.join(hid, "h1-v1", "tasks.csv"), os.path.join(tmp, "r-broken"))
        expect("planted: build script that exits non-zero -> rebuild fails, commands recorded",
               (r["rebuild_ok"], [c["rc"] for c in r["commands"]][-1]), (False, 3))

        def wide(work):
            os.makedirs(os.path.join(work, "boards", "wide"))
            shutil.copy(os.path.join(work, "incoming", "tasks.csv"), os.path.join(work, "boards", "wide", "tasks.csv"))
            open(os.path.join(work, "boards", "wide", "index.html"), "w").write(
                "<!doctype html><meta name=viewport content='width=device-width'><table id=t style='width:900px'></table>"
                "<script>fetch('tasks.csv').then(r=>r.text()).then(t=>{document.getElementById('t').innerHTML="
                "t.trim().split('\\n').map(l=>'<tr><td>'+l.split(',').join('</td><td>')+'</td></tr>').join('')})</script>")
        s = make_subject(main_fx, os.path.join(tmp, "s-wide"), wide, "")
        r = render(s, os.path.join(hid, "h1-v1", "tasks.csv"), os.path.join(tmp, "r-wide"))
        expect("planted: client-side board fetching its CSV renders hidden data; wide table -> hscroll; raw field names counted",
               (r["rebuild_ok"], r["counts"]["hscroll_opening"], "waiting_on" in r["counts"]["raw_tokens"], r["class"]), (True, True, True, "LITERAL"))

        # readers, dry run (no model): the claude call is printed, records are void, nothing scores
        res = readers(os.path.join(tmp, "r-c"), 1, dry=True)
        recs = [json.load(open(os.path.join(tmp, "r-c", "readers", "run1", i["id"], "record.json"))) for i in res["items"]]
        expect("readers dry run: 7 records, each flagged dry, tools Read/Glob only, no rule files",
               (len(recs), all(x["dry_run"] for x in recs), {tuple(x["flags"][:2]) for x in recs}, {len(x["rules_loaded"]) for x in recs}),
               (7, True, {("--tools", "Read,Glob")}, {0}))
        expect("readers dry run: gates do not count it", gates([os.path.join(tmp, "r-c")])[0]["complete"], False)
        expect("reader work dir holds the screenshots only", sorted(os.listdir(os.path.join(tmp, "r-c", "readers", "run1", "water", "work")))
               == sorted(os.listdir(os.path.join(tmp, "r-c", "shots"))), True)

    for l in lines:
        print(l)
    print(f"selftest: {len(lines) - len(fails)} ok, {len(fails)} failed")
    return not fails


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(0 if selftest() else 1)
    ap = argparse.ArgumentParser(usage=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("render"); p.add_argument("subject"); p.add_argument("hidden_csv"); p.add_argument("out")
    p = sub.add_parser("readers"); p.add_argument("out"); p.add_argument("--run", type=int, required=True)
    p.add_argument("--reader", default="sonnet-medium"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--budget-usd", default="2")
    p = sub.add_parser("gates"); p.add_argument("outs", nargs="+")
    p = sub.add_parser("classify"); p.add_argument("subject"); p.add_argument("--render")
    p = sub.add_parser("anchor"); p.add_argument("fixture"); p.add_argument("name"); p.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "render":
        r = render(a.subject, a.hidden_csv, a.out)
        print(json.dumps({k: r[k] for k in ("page", "rebuild_ok", "rebuild_by", "rebuild_source", "class", "counts", "caps_hit")}, indent=1))
    elif a.cmd == "readers":
        if a.reader.startswith("or:"):
            readers_api(a.out, a.run, a.reader[3:], a.dry_run)
        else:
            readers(a.out, a.run, a.reader, a.dry_run, a.budget_usd)
    elif a.cmd == "gates":
        print(json.dumps(gates(a.outs), indent=1))
    elif a.cmd == "classify":
        print(classify(a.subject, a.render))
    elif a.cmd == "anchor":
        print(anchor(a.fixture, a.name, a.out))
