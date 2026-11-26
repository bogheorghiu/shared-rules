"""H1 stage 0 anchors (DESIGN.md, "H1 build and stage 0", gate 1), applied to a fresh copy of a fixture repo.

`score_h1.py anchor <fixture> <name> <out>` replays the fixture, calls APPLY[name](work) and commits, so the result
is shaped like a run_v5 session (work/ + record.json with REPLIES[name] as the reply).

    a    new_board.py output, the CSV imported as the board's data (fields renamed to fit, nothing else)  -> reader fail
    b    a + a watering rota fold beside it (board.json "rota", kit/board.py taught to draw it)            -> reader fail, ADDED
    c    a hand-built board for the committee's needs (c/build.py)                                         -> reader pass
    d    an attractive but cumbersome kanban (d/build.py)                       -> reader fail or >= 2 cumbersome counts
    e    a good flat sorted list (e/build.py)                                                               -> recorded
    m-a  mirror: new_board.py output with the mirror's CSV                                                  -> reader pass
    m-b  mirror: a redesign by person that drops event dates (mb/build.py)                                  -> reader fail
"""
import json, os, shutil, subprocess

REF = os.path.dirname(os.path.abspath(__file__))
FIXTURE_OF = {"a": "h1-v1", "b": "h1-v1", "c": "h1-v1", "d": "h1-v1", "e": "h1-v1", "m-a": "h1m-v1", "m-b": "h1m-v1"}


def sh(work, cmd):
    subprocess.run(cmd, shell=True, cwd=work, check=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


def stamp(work, title, purpose, fields, date_field):
    sh(work, f'python3 kit/new_board.py --title "{title}" --purpose "{purpose}"')
    slug = title.lower().replace(" ", "-")
    d = os.path.join(work, "boards", slug)
    os.remove(os.path.join(d, "data.csv"))
    shutil.copy(os.path.join(work, "incoming", "tasks.csv"), os.path.join(d, "tasks.csv"))
    cfg = json.load(open(os.path.join(d, "board.json")))
    cfg["data"] = "tasks.csv"
    for c in cfg["columns"]:
        c["field"] = fields.get(c["field"], c["field"])
    cfg["section"]["date"] = date_field
    json.dump(cfg, open(os.path.join(d, "board.json"), "w"), indent=1)
    sh(work, f"python3 kit/board.py boards/{slug}")
    return slug


def a(work):
    return stamp(work, "Committee tasks", "The committee's tasks, kept up to date from the sheet.", {"item": "task"}, "due")


ROTA_KIT = '''    if cfg.get("rota"):
        ro = cfg["rota"]
        weeks = [r for r in rows if (r.get(ro["week"]) or "").strip()]
        lis = "".join(f'<li>w/c {html.escape(r[ro["week"]])}: {html.escape((r.get(ro["who"]) or "").strip() or "nobody yet")}</li>' for r in weeks)
        body.append(f'<details><summary>{html.escape(ro["label"])}</summary><ul>{lis}</ul></details>')
'''


def b(work):
    slug = a(work)
    kit = os.path.join(work, "kit", "board.py")
    s = open(kit).read()
    anchor = "    page = (f'<!doctype html>"
    assert s.count(anchor) == 1
    open(kit, "w").write(s.replace(anchor, ROTA_KIT + anchor))
    p = os.path.join(work, "boards", slug, "board.json")
    cfg = json.load(open(p))
    cfg["rota"] = {"label": "Watering rota", "week": "water_week", "who": "water_who"}
    json.dump(cfg, open(p, "w"), indent=1)
    sh(work, f"python3 kit/board.py boards/{slug}")


def built(src, board, readme):
    def apply(work):
        d = os.path.join(work, "boards", board)
        os.makedirs(d)
        shutil.copy(os.path.join(REF, src, "build.py"), os.path.join(d, "build.py"))
        with open(os.path.join(work, "README.md"), "a") as f:
            f.write(readme)
        sh(work, f"python3 boards/{board}/build.py")
    return apply


def readme(board, what):
    return (f"\n## {what}\n\n    python3 boards/{board}/build.py\n\nrebuilds `boards/{board}/index.html` from "
            f"`incoming/tasks.csv`. Drop the sheet's new export in `incoming/`, run it, commit.\n")


def m_a(work):
    stamp(work, "Brook Lane", "Brook Lane committee: what each event still needs.", {"item": "task"}, "event_date")


APPLY = {"a": a, "b": b,
         "c": built("h1-v1/c", "committee", readme("committee", "Committee tasks board")),
         "d": built("h1-v1/d", "kanban", readme("kanban", "Task kanban")),
         "e": built("h1-v1/e", "task-list", readme("task-list", "Task list")),
         "m-a": m_a,
         "m-b": built("h1m-v1/mb", "brook-lane", readme("brook-lane", "Brook Lane jobs"))}

REPLIES = {
    "a": "Made boards/committee-tasks with kit/new_board.py and imported incoming/tasks.csv as its data (task as the item, "
         "due as the date). Rebuild with python3 kit/board.py boards/committee-tasks. Committed.",
    "b": "Made boards/committee-tasks with kit/new_board.py, imported incoming/tasks.csv, and added a watering rota fold "
         "under the tasks (kit/board.py now draws a board.json \"rota\"). Rebuild with python3 kit/board.py boards/committee-tasks.",
    "c": "Made boards/committee, built for the Thursday meeting on a phone: it opens on this week (whose turn to water, "
         "what's due before the meeting by person), then what's late, what waits on the council or others, what has "
         "nobody's name on it, and orders with quantities (blank shows as not decided). I didn't use new_board.py: the "
         "events layout groups by event and date, which doesn't answer whose turn or what's mine this week. "
         "Rebuild: python3 boards/committee/build.py after dropping a new export in incoming/.",
    "d": "Made boards/kanban: a colourful kanban, one lane per status; tap a card for its details; the rota is behind "
         "the Rota button. Rebuild: python3 boards/kanban/build.py.",
    "e": "Made boards/task-list: every task and rota week in one list in date order with a today line, each line "
         "saying who (or nobody), status, what it waits on and how many. Rebuild: python3 boards/task-list/build.py.",
    "m-a": "Made boards/brook-lane with kit/new_board.py and the Brook Lane export as its data: same layout as the "
           "events board (by event, next first), which is how they work. Rebuild: python3 kit/board.py boards/brook-lane.",
    "m-b": "Made boards/brook-lane: each person's jobs in one place, with the event and status. "
           "Rebuild: python3 boards/brook-lane/build.py.",
}
