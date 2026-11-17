#!/usr/bin/env python3
"""Brook Lane jobs by person (stage 0 anchor m-b: a redesign that drops the prior board's dates and order).

    python3 boards/brook-lane/build.py

Reads incoming/tasks.csv, writes boards/brook-lane/index.html: one section per person, their jobs with the event's
name and status; no event dates, no "next".
"""
import csv, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WORDS = {"todo": "to do", "in_progress": "under way", "waiting": "waiting", "done": "done"}


def main():
    with open(os.path.join(ROOT, "incoming", "tasks.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    e = html.escape
    by = {}
    for r in rows:
        by.setdefault((r.get("who") or "").strip() or "Nobody yet", []).append(r)
    secs = "".join(f'<section><h2>{e(p)}</h2><ul>' + "".join(
        f'<li><b>{e(r["task"])}</b> ({e(r["event"])}) — {WORDS.get(r["status"].strip(), r["status"])}</li>' for r in rs) + "</ul></section>"
        for p, rs in sorted(by.items()))
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Brook Lane jobs</title><style>body{{font:17px system-ui,sans-serif;max-width:34rem;margin:0 auto;padding:12px}}'
            f'ul{{list-style:none;padding:0}}li{{padding:4px 0;border-top:1px solid #eee}}</style></head><body>'
            f'<h1>Brook Lane jobs</h1>{secs}</body></html>\n')
    open(os.path.join(HERE, "index.html"), "w").write(page)


if __name__ == "__main__":
    main()
