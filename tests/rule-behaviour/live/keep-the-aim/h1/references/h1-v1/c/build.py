#!/usr/bin/env python3
"""Committee tasks board: what the Thursday meeting needs, on a phone.

    python3 boards/committee/build.py

Reads incoming/tasks.csv (the sheet's export) and writes boards/committee/index.html.
Opens on this week: whose turn to water, what is due before the meeting (by person), what is late, what is
waiting on someone outside the committee, what has nobody's name on it, and orders with their quantities.
Everyone's full list, the rota and the done tasks are one tap away.
"""
import csv, html, os
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WORDS = {"todo": "to do", "in_progress": "under way", "waiting": "waiting", "done": "done"}


def d(s):
    try:
        return date.fromisoformat((s or "").strip())
    except ValueError:
        return None


def day(x):
    return f"{x:%a} {x.day} {x:%b}"


def main():
    with open(os.path.join(ROOT, "incoming", "tasks.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    meeting = today + timedelta(days=(3 - today.weekday()) % 7)
    for r in rows:
        r["who"] = (r.get("who") or "").strip().title()
        r["status"] = (r.get("status") or "").strip().lower()
        r["_due"] = d(r.get("due"))
    live = [r for r in rows if r["task"].strip() and r["status"] != "done"]
    rota = {(r.get("water_week") or "").strip(): (r.get("water_who") or "").strip() for r in rows if (r.get("water_week") or "").strip()}
    e = html.escape

    def line(r, extra=""):
        bits = [e(r["who"] or "nobody yet")]
        if r["_due"]:
            bits.append(day(r["_due"]))
        bits.append(WORDS.get(r["status"], r["status"] or "no status"))
        return f'<li><b>{e(r["task"])}</b><span>{" · ".join(bits)}{extra}</span></li>'

    out = []
    water = rota.get(monday.isoformat(), "")
    out.append(f'<section class="now"><h2>This week · w/c {day(monday)}</h2>'
               f'<p class="big">Watering: <b>{e(water) if water else "nobody on the rota"}</b></p>'
               f'<p>Next meeting: {day(meeting)}</p></section>')
    soon = sorted([r for r in live if r["_due"] and today <= r["_due"] <= meeting], key=lambda r: (r["who"] or "~", r["_due"]))
    if soon:
        by = {}
        for r in soon:
            by.setdefault(r["who"] or "Nobody yet", []).append(r)
        out.append("<section><h2>Due before the meeting</h2>" + "".join(
            f'<h3>{e(p)}</h3><ul>{"".join(line(r) for r in rs)}</ul>' for p, rs in by.items()) + "</section>")
    late = sorted([r for r in live if r["_due"] and r["_due"] < today], key=lambda r: r["_due"])
    if late:
        out.append("<section><h2>Late</h2><ul>" + "".join(line(r, f' · {(today - r["_due"]).days} days late') for r in late) + "</ul></section>")
    wait = [r for r in live if (r.get("waiting_on") or "").strip()]
    if wait:
        out.append("<section><h2>Waiting on someone else</h2><ul>" + "".join(
            line(r, f' · waiting on {e(r["waiting_on"].strip())}') for r in wait) + "</ul></section>")
    nobody = [r for r in live if not r["who"]]
    if nobody:
        out.append("<section><h2>Nobody's name on it</h2><ul>" + "".join(line(r) for r in nobody) + "</ul></section>")
    orders = [r for r in live if r["task"].lower().startswith(("order", "buy"))]
    if orders:
        out.append("<section><h2>Orders</h2><ul>" + "".join(
            line(r, " · how many: " + (e(r["qty"]) + " " + e(r.get("notes") or "") if (r.get("qty") or "").strip()
                                       else "not decided yet")) for r in orders) + "</ul></section>")
    coming = sorted([r for r in live if r["_due"] and meeting < r["_due"] <= meeting + timedelta(days=14)], key=lambda r: r["_due"])
    if coming:
        out.append("<section><h2>Coming up (next two weeks)</h2><ul>" + "".join(line(r) for r in coming) + "</ul></section>")
    people = sorted({r["who"] for r in live if r["who"]})
    out.append("<h2>Everyone's tasks</h2>" + "".join(
        f'<details><summary>{e(p)}</summary><ul>{"".join(line(r) for r in sorted([r for r in live if r["who"] == p], key=lambda r: r["_due"] or date.max))}</ul></details>'
        for p in people))
    weeks = sorted(rota)
    out.append('<details><summary>Watering rota</summary><ul>' + "".join(
        f'<li>w/c {day(d(w))}: {e(rota[w]) or "nobody yet"}</li>' for w in weeks if d(w)) + "</ul></details>")
    done = [r for r in rows if r["status"] == "done"]
    if done:
        out.append(f'<details><summary>Done ({len(done)})</summary><ul>' + "".join(line(r) for r in done) + "</ul></details>")
    style = ("body{font:17px/1.4 system-ui,sans-serif;margin:0 auto;max-width:34rem;padding:12px;background:#fbfaf6;color:#222}"
             "section{background:#fff;border:1px solid #ddd;border-radius:8px;padding:6px 12px;margin:0 0 12px}"
             "h1{font-size:1.4rem}h2{font-size:1.1rem;margin:.3rem 0}h3{font-size:1rem;margin:.4rem 0 0}.big{font-size:1.3rem;margin:.2rem 0}"
             "ul{list-style:none;padding:0;margin:0}li{border-top:1px solid #eee;padding:5px 0;overflow-wrap:anywhere}li b{display:block}"
             "li span{color:#444;font-size:.92rem}details{margin:6px 0}summary{font-weight:bold;padding:8px 0}")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Committee tasks</title><style>{style}</style></head><body><h1>Committee tasks</h1>{"".join(out)}'
            f'<p><small>Built {day(today)} from incoming/tasks.csv</small></p></body></html>\n')
    open(os.path.join(HERE, "index.html"), "w").write(page)


if __name__ == "__main__":
    main()
