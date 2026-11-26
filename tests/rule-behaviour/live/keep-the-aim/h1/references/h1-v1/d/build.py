#!/usr/bin/env python3
"""Task kanban (stage 0 anchor d: attractive but cumbersome).

    python3 boards/kanban/build.py

Reads incoming/tasks.csv, writes boards/kanban/index.html: one column per status, side by side, each task a
coloured card; tap a card to see its fields; the rota is behind a button.
"""
import csv, html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LANES = ["todo", "in_progress", "waiting", "blocked", "done"]


def main():
    with open(os.path.join(ROOT, "incoming", "tasks.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    e = html.escape
    lanes = []
    for lane in LANES:
        cards = [r for r in rows if (r.get("status") or "").strip().lower() == lane and r["task"].strip()]
        body = "".join(
            f'<button class="card" onclick="this.nextElementSibling.hidden=!this.nextElementSibling.hidden">{e(r["task"])}</button>'
            f'<div class="fields" hidden>' + "".join(f'<div>{k}: {e(r.get(k) or "")}</div>' for k in ("who", "due", "waiting_on", "qty", "notes")) + "</div>"
            for r in cards)
        lanes.append(f'<div class="lane"><h2>{lane} ({len(cards)})</h2>{body}</div>')
    rota = [(r.get("water_week"), r.get("water_who")) for r in rows if (r.get("water_week") or "").strip()]
    rota_html = "".join(f"<div>water_week {e(w)}: water_who {e(h or '')}</div>" for w, h in rota)
    style = ("body{font:15px system-ui,sans-serif;margin:0;padding:10px;background:linear-gradient(#f3e9ff,#e9fff4)}"
             ".board{display:flex;gap:12px;width:1300px}.lane{flex:0 0 240px;background:#ffffffaa;border-radius:12px;padding:8px}"
             ".card{display:block;width:100%;text-align:left;margin:6px 0;padding:10px;border:0;border-radius:10px;"
             "background:#fff;box-shadow:0 2px 6px #0002;font:inherit}.fields{font-size:12px;color:#555;padding:4px 8px}"
             "#rota{position:fixed;top:40px;left:20px;right:20px;background:#fff;padding:12px;border-radius:12px;box-shadow:0 4px 20px #0004}")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Tasks</title><style>{style}</style></head><body><h1>Tasks</h1>'
            f'<button onclick="document.getElementById(\'rota\').hidden=!document.getElementById(\'rota\').hidden">Rota</button>'
            f'<div id="rota" hidden>{rota_html}</div><div class="board">{"".join(lanes)}</div>'
            f'<script>window.TASKS={json.dumps(len(rows))}</script></body></html>\n')
    open(os.path.join(HERE, "index.html"), "w").write(page)


if __name__ == "__main__":
    main()
