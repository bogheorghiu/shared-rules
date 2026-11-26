#!/usr/bin/env python3
"""Task list (stage 0 anchor e: a good flat sorted list).

    python3 boards/task-list/build.py

Reads incoming/tasks.csv, writes boards/task-list/index.html: one list, every task and every rota week in date
order, with a "today" line; each line says who (or nobody), when, status, what it waits on and how many.
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


def main():
    with open(os.path.join(ROOT, "incoming", "tasks.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    today = date.today()
    e = html.escape
    items = []
    for r in rows:
        if r["task"].strip():
            st = (r.get("status") or "").strip().lower()
            bits = [e((r.get("who") or "").strip().title() or "nobody yet"), WORDS.get(st, st or "no status")]
            if (r.get("waiting_on") or "").strip():
                bits.append("waiting on " + e(r["waiting_on"].strip()))
            if r["task"].lower().startswith(("order", "buy")):
                bits.append("how many: " + (e(r["qty"]) if (r.get("qty") or "").strip() else "not decided"))
            if (r.get("notes") or "").strip():
                bits.append(e(r["notes"].strip()))
            items.append((d(r.get("due")) or date.max, f'<b>{e(r["task"])}</b> — {" · ".join(bits)}', st == "done"))
        w = d(r.get("water_week"))
        if w:
            items.append((w, f'<b>Watering, week of {w:%a} {w.day} {w:%b}</b> — {e((r.get("water_who") or "").strip() or "nobody yet")}', w + timedelta(days=6) < today))
    items.append((today, f"<b>── today, {today:%a} {today.day} {today:%b} ──</b>", False))
    items.sort(key=lambda t: (t[0], "today" not in t[1]))
    lis = "".join(f'<li class="{"old" if old else ""}"><span class="when">{"" if when == date.max else f"{when:%a} {when.day} {when:%b}"}</span> {text}</li>'
                  for when, text, old in items)
    style = ("body{font:16px/1.4 system-ui,sans-serif;margin:0 auto;max-width:34rem;padding:12px}ul{list-style:none;padding:0}"
             "li{border-top:1px solid #eee;padding:5px 0;overflow-wrap:anywhere}.when{display:block;color:#666;font-size:.85rem}.old{color:#999}")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Task list</title><style>{style}</style></head><body><h1>Task list</h1><ul>{lis}</ul></body></html>\n')
    open(os.path.join(HERE, "index.html"), "w").write(page)


if __name__ == "__main__":
    main()
