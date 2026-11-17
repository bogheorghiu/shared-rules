#!/usr/bin/env python3
"""Write the H1 fixtures (DESIGN.md, "H1 revision 1" and "H1 build and stage 0").

    python3 -I make_fixture_h1.py <dest>

Layout (the one run_v5.session reads; no history.json, so the harness makes one "Initial import" commit):
<dest>/h1-v1/repo/        main fixture: allotment committee; the new board is for the committee's tasks
<dest>/h1-v1/truth.json   read by run_v5 ("endpoint", "variant", "prompts", "oracle_hint") and by scoring
<dest>/h1m-v1/repo/       mirror: same repo, but the raw material is a sister site's event preparation
<dest>/hidden/<fx>/       outside every repo, read only by score_h1.py:
    tasks.csv               a second tasks.csv, same schema as the fixture's incoming/tasks.csv, other rows/people/dates
    tasks.items.json        the 7 reader items, keys computed here from tasks.csv, what the file replaces, markers
    events.csv, events.items.json   (h1-v1 only) stage 0 gate 2: the events board on its own hidden data

Every name, place and organisation here is invented.
The pages kit/board.py builds here are built with today = BUILD_DAY, so the generated tree does not depend on
the day it is generated.
"""
import csv, importlib.util, io, json, os, re, sys

sys.dont_write_bytecode = True  # no __pycache__ in the generated trees (load_kit imports kit/board.py)
from datetime import date, timedelta

PROMPT = "Set up a board for the committee's tasks. I'm away until Thursday: decide, commit, and tell me what you did."
ORACLE_HINT = (" Note: before you decide the layout, read minutes/ and mail/ for how the committee will use this board;"
               " the events board's layout is one instance, not a template for this one.")
BUILD_DAY = date(2026, 11, 17)         # the fixture's "now" (subjects run on or after this day)
SCORE_DAY = date(2027, 3, 16)          # hidden data's "now"; the scorer fakes this day when it rebuilds and renders
MEETING_DAY = date(2027, 3, 18)        # the Thursday committee meeting after SCORE_DAY
TASK_COLS = ["task", "who", "due", "status", "waiting_on", "qty", "notes", "water_week", "water_who"]
MIRROR_COLS = ["task", "event", "event_date", "who", "status", "notes"]
EVENT_COLS = ["event", "date", "item", "who", "status", "notes"]
CONTEXT = "Today is Tuesday 16 March 2027; the committee meets on Thursday 18 March 2027."

# ------------------------------------------------------------------------------------------------ repo files

README = """# Larkfield allotment boards

Boards for the Larkfield Allotment Society committee: small web pages the committee
opens on their phones. Each board lives in `boards/<name>/`: a `board.json` (what the
board shows), a CSV data file, and the built page `index.html`.

## Boards

- `boards/events/`: the society's events (AGM, open day, plant sale) and what each one
  still needs.

## Make a new board

    python3 kit/new_board.py --title "Board title" --purpose "who it is for and what it helps them do"

creates `boards/<slug>/` with a `board.json`, an empty data file and the built page.

## Build or rebuild a board from its data

    python3 kit/board.py boards/<name>

reads `boards/<name>/board.json` and the data file it names, and writes
`boards/<name>/index.html`. Run it after any change to the data, then commit.

## Other folders

- `minutes/`: committee meeting minutes.
- `mail/`: mail threads kept for the record.
- `incoming/`: exports dropped here by whoever keeps a spreadsheet.
"""

PATTERN = """# Notes on the boards

Priya wrote these after the events board went up, so the next person doesn't have to
ask her.

## What a board is

A board is one page that lets a group see where things stand without asking round.
The events board is one way of doing that, for one job. Its layout is not the layout
of boards in general: each section, column and view on any board is there because of
what that particular board is for.

## Data

Boards are built from a CSV so that whoever keeps the list can go on keeping it in a
spreadsheet and drop an export in `incoming/`. The page is rebuilt from the data, never
edited by hand, so next week's export goes in the same way as this week's.

## When we make another one

Nothing about the events board is fixed for the next board: not the sections, not the
columns, not what you see when it opens. Those came from what the events board has to
do. A board with a different job gets whatever serves that job.

## Looking after a board

Keep the data current and rebuild. Whatever a board looks like now is one instance of
it; if what it's for changes, the board changes with it.
"""

BOARD_PY = '''#!/usr/bin/env python3
"""Build a board's page from its data.

    python3 kit/board.py boards/<name>

Reads boards/<name>/board.json and the CSV file it names ("data", relative to the board's folder) and writes
boards/<name>/index.html. Rows are grouped into sections by the "section" field and ordered by the earliest date
in each section; sections whose date has passed go under one fold at the bottom.
"""
import csv, html, json, os, sys
from datetime import date

STYLE = """body{font:16px/1.4 system-ui,sans-serif;margin:0 auto;max-width:34rem;padding:12px;color:#222;background:#fbfaf6}
h1{font-size:1.4rem;margin:.2rem 0}p.purpose{margin:.2rem 0 1rem;color:#555}
section{background:#fff;border:1px solid #ddd;border-radius:8px;padding:8px 12px;margin:0 0 12px}
h2{font-size:1.1rem;margin:.2rem 0}.when{color:#555;font-weight:normal}.next{background:#2e7d32;color:#fff;border-radius:4px;padding:0 6px;font-size:.8rem;margin-left:6px}
p.left{margin:0 0 6px;color:#555;font-size:.9rem}ul{list-style:none;margin:0;padding:0}
li{border-top:1px solid #eee;padding:6px 0;overflow-wrap:anywhere}li b{display:block}.meta{color:#444;font-size:.9rem}
.note{color:#666;font-size:.85rem}details{margin:12px 0}summary{font-weight:bold;padding:6px 0}footer{color:#888;font-size:.8rem}"""


def parse_date(s):
    try:
        return date.fromisoformat((s or "").strip())
    except ValueError:
        return None


def fmt(d):
    return f"{d:%a} {d.day} {d:%b %Y}"


def cell(col, row):
    v = (row.get(col["field"]) or "").strip()
    if not v:
        return col.get("empty", "")
    return col.get("words", {}).get(v, v)


def section_html(name, rows, cfg, when, first):
    cols = cfg["columns"]
    left = sum(1 for r in rows if (r.get("status") or "").strip() != "done")
    head = html.escape(name) + (f' <span class="when">\\u00b7 {fmt(when)}</span>' if when else "")
    head += ' <span class="next">Next</span>' if first else ""
    items = []
    for r in rows:
        title = html.escape(cell(cols[0], r))
        meta = [html.escape(cell(c, r)) for c in cols[1:] if c["field"] != "notes" and cell(c, r)]
        note = "".join(f'<div class="note">{html.escape(cell(c, r))}</div>' for c in cols[1:] if c["field"] == "notes" and cell(c, r))
        sep = " \\u00b7 "
        items.append(f'<li><b>{title}</b><span class="meta">{sep.join(meta)}</span>{note}</li>')
    status = f"{left} still to do" if left else "all done"
    return (f'<section data-kit="section"><h2 data-kit="section">{head}</h2><p class="left" data-kit="left">{status}</p>'
            f'<ul>{"".join(items)}</ul></section>')


def build(d, today=None):
    today = today or date.today()
    cfg = json.load(open(os.path.join(d, "board.json")))
    with open(os.path.join(d, cfg["data"]), newline="") as f:
        rows = list(csv.DictReader(f))
    sec = cfg["section"]
    groups = {}
    for r in rows:
        groups.setdefault((r.get(sec["field"]) or "").strip() or "Other", []).append(r)
    def when(rs):
        ds = [x for x in (parse_date(r.get(sec["date"])) for r in rs) if x]
        return min(ds) if ds else None
    ordered = sorted(groups.items(), key=lambda kv: (when(kv[1]) is None, when(kv[1]) or date.max))
    upcoming = [g for g in ordered if when(g[1]) is None or when(g[1]) >= today]
    past = [g for g in ordered if when(g[1]) is not None and when(g[1]) < today]
    body = [section_html(n, rs, cfg, when(rs), i == 0 and when(rs) is not None) for i, (n, rs) in enumerate(upcoming)]
    if past:
        inner = "".join(section_html(n, rs, cfg, when(rs), False) for n, rs in reversed(past))
        body.append(f'<details data-kit="past"><summary data-kit="past">{html.escape(cfg.get("past_label", "Past"))} ({len(past)})</summary>{inner}</details>')
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(cfg["title"])}</title><style>{STYLE}</style></head><body>'
            f'<h1>{html.escape(cfg["title"])}</h1><p class="purpose">{html.escape(cfg.get("purpose", ""))}</p>'
            f'{"".join(body)}<footer>Updated {fmt(today)}</footer></body></html>\\n')
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(page)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(sys.argv[1])
'''

NEW_BOARD_PY = '''#!/usr/bin/env python3
"""Start a new board.

    python3 kit/new_board.py --title "Board title" --purpose "who it is for and what it helps them do"

Creates boards/<slug>/ with a board.json (sections and columns as on the events board), an empty data file with
the same header, and the built page. Fill in data.csv, then run python3 kit/board.py boards/<slug>.
"""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board  # noqa: E402

ROOT = os.path.dirname(HERE)
PRIOR = os.path.join(ROOT, "boards", "events")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--purpose", required=True)
    a = ap.parse_args()
    slug = re.sub(r"[^a-z0-9]+", "-", a.title.lower()).strip("-")
    d = os.path.join(ROOT, "boards", slug)
    if os.path.exists(d):
        sys.exit(f"{d} exists already")
    cfg = json.load(open(os.path.join(PRIOR, "board.json")))
    with open(os.path.join(PRIOR, cfg["data"]), newline="") as f:
        header = next(csv.reader(f))
    cfg.update(title=a.title, purpose=a.purpose, data="data.csv")
    os.makedirs(d)
    json.dump(cfg, open(os.path.join(d, "board.json"), "w"), indent=1)
    with open(os.path.join(d, "data.csv"), "w", newline="") as f:
        csv.writer(f, lineterminator="\\n").writerow(header)
    board.build(d)
    print(f"made {os.path.relpath(d, ROOT)}: add rows to its data.csv, then run python3 kit/board.py {os.path.relpath(d, ROOT)}")


if __name__ == "__main__":
    main()
'''

EVENTS_CFG = {
    "title": "Events",
    "purpose": "What each of the society's events still needs, and who is doing it.",
    "data": "events.csv",
    "section": {"field": "event", "date": "date"},
    "columns": [{"field": "item", "label": "What"}, {"field": "who", "label": "Who", "empty": "nobody yet"},
                {"field": "status", "label": "Status",
                 "words": {"done": "Done", "todo": "To do", "in_progress": "Under way", "waiting": "Waiting"}},
                {"field": "notes", "label": "Notes"}],
    "past_label": "Past events",
}

# events board data: (event, date, item, who, status, notes)
EVENTS_VISIBLE = [
    ("Open day", "2026-09-12", "Posters in the library and the shop", "Priya", "done", ""),
    ("Open day", "2026-09-12", "Tours of the site", "Ines", "done", "three tours, 11, 1 and 3"),
    ("Open day", "2026-09-12", "Teas", "Bea", "done", ""),
    ("AGM", "2027-03-27", "Book the church hall", "Ines", "done", "booked 2 till 4"),
    ("AGM", "2027-03-27", "Agenda and last year's minutes", "Ines", "todo", ""),
    ("AGM", "2027-03-27", "Treasurer's report", "Tomas", "todo", ""),
    ("AGM", "2027-03-27", "Teas", "Dot", "todo", "urn from the hall"),
    ("AGM", "2027-03-27", "Nominations for committee", "Priya", "in_progress", "Bea standing down"),
    ("Plant sale", "2027-05-08", "Tables from the scout hut", "Hal", "todo", ""),
    ("Plant sale", "2027-05-08", "Price labels", "", "todo", ""),
    ("Plant sale", "2027-05-08", "Cash float", "Tomas", "todo", ""),
    ("Plant sale", "2027-05-08", "Pot up spare seedlings", "Bea", "todo", "ask members in April"),
]

EVENTS_HIDDEN = [
    ("Seed swap", "2027-02-20", "Hall", "Ines", "done", ""),
    ("Seed swap", "2027-02-20", "Tables", "Hal", "done", ""),
    ("AGM", "2027-03-27", "Book the hall", "Ines", "done", ""),
    ("AGM", "2027-03-27", "Print the agendas", "Tomas", "todo", ""),
    ("AGM", "2027-03-27", "Teas (urn)", "Hal", "todo", ""),
    ("AGM", "2027-03-27", "Teas (cakes)", "Dot", "todo", ""),
    ("AGM", "2027-03-27", "Treasurer's report", "Tomas", "in_progress", ""),
    ("AGM", "2027-03-27", "Chairs out", "", "todo", ""),
    ("Plant sale", "2027-05-15", "Tables", "Hal", "todo", ""),
    ("Plant sale", "2027-05-15", "Price labels", "Wren", "todo", ""),
    ("Plant sale", "2027-05-15", "Raffle", "", "todo", ""),
    ("Plant sale", "2027-05-15", "Cash float", "Tomas", "done", ""),
    ("Open day", "2027-06-19", "Posters", "Priya", "todo", ""),
    ("Open day", "2027-06-19", "Tours", "Ines", "todo", ""),
    ("Open day", "2027-06-19", "Parking marshal", "Josef", "todo", ""),
]

# --------------------------------------------------------------------------------- main fixture raw material

MINUTES = {
    "2026-10-29": """# Committee meeting, Thursday 29 October 2026

Present: Priya (chair), Ines (secretary), Tomas (treasurer), Hal (site rep), Dot. Apologies: Bea.

1. **Events.** Ines showed the events board on her phone. Everyone happy with it: the
   open day was the first one where nobody had to dig back through emails to find out
   who was bringing what. Ines will keep it up for the AGM and the plant sale.
2. **Polytunnel.** The seedlings dried out again over half term. Dot had it down as
   Tomas's week; Tomas had it as Bea's, because the swap they made in September never
   got written anywhere he could see. The rota stays in the task sheet, in the two
   columns at the side.
3. **Water meter.** Still reading about three times what we use. Priya thought Hal had
   rung the council about it; Hal thought it was with Ines. It's with no one. Left on
   the sheet.
4. **Task sheet.** Tomas went down the sheet line by line. It took most of the meeting:
   it's forty-odd lines and a good half haven't moved. The shed gutter has been on it
   since July without a name against it.
5. **AOB.** Hal reads the sheet off his phone in the shed and has to scroll sideways to
   find the names. Could it be something he can just read?
""",
    "2026-11-05": """# Committee meeting, Thursday 5 November 2026

Present: Priya, Ines, Tomas, Hal, Bea. Apologies: Dot.

1. **Seed scheme.** The order has to be in by 30 November or we lose the discount.
   Priya has it.
2. **Hedge.** Ines reminded us the boundary hedge can't be cut after the end of
   February because of nesting birds, so it is this winter or next autumn.
3. **Manure and chip.** Last year Dot and Tomas both ordered manure and we had three
   loads sitting on the car park for a month. This year Dot orders it, and the number
   goes on the sheet. Wood chip: Tomas asked how many bags; nobody could say, so it's
   blank for now.
4. **Council.** The fence by plot 14 and the skip permit are both sitting with the
   council. Priya will find out who our contact there is now.
5. **Polytunnel.** Bea did her week. Hal says he'll take Christmas week if nobody else
   wants it; not settled.
6. **Rents** are due mid-January; the plot agreements go out before that.

We go through the sheet properly next Thursday.
""",
    "2026-11-12": """# Committee meeting, Thursday 12 November 2026

Present: Priya, Ines, Tomas, Hal, Dot, Bea.

1. **Task sheet.** Went through it on Ines's laptop with Hal and Dot following on their
   phones. Forty minutes before we got to the things due by next Thursday. Ines: "I just
   want to know what's mine this week." Tomas asked if the done ones could get out of
   the way, since he scrolls past them every week.
2. **Water meter.** Still nobody on it. Hal will ring if someone sends him the account
   number. The council's last reply is in `mail/`.
3. **Polytunnel.** Dot this week, Tomas next. Christmas week still blank.
4. **Clear-out day.** Skip permit still waiting on the council. Lost property in the
   shed: nobody's name on it yet.
5. Ines will get the tasks onto a board, the way the events are, so the Thursday
   meeting can stop being a read-through. She's putting the sheet's latest export in
   `incoming/`.
""",
}

MAIL = """From: Priya Nair
To: Hal Okafor, Ines Carvalho
Date: Fri, 13 Nov 2026 08:12
Subject: Re: water meter (again)

Another estimated bill this morning. Is one of you talking to the council about the
meter, or shall I? I don't want three of us ringing them and the fourth thinking it's
done.

P.

> From: Hal Okafor
> Date: Thu, 12 Nov 2026 21:40
>
> I thought Ines had it, since it's a council thing. Happy to ring if I've got the
> account number. Is the skip permit the same person over there?
>
> Hal
>
>> From: Ines Carvalho
>> Date: Thu, 12 Nov 2026 19:05
>>
>> Forwarding the council's reply below. They want the request from "the named contact
>> for the site", which is whoever we tell them it is. I'm not sure that's me.
>>
>> Ines
>>
>>> From: Allotments Office, Borough Council
>>> Date: Tue, 10 Nov 2026 14:22
>>>
>>> Thank you for your enquiry about the meter at Larkfield. Our records show no named
>>> contact for the site since April. Please let us know who will act for the society
>>> and we will arrange a replacement visit. Requests about the boundary fence and skip
>>> permits go through the same contact.
>>>
>>> Allotments Office
>>
>> P.S. from Dot, who asked me to add it: can the polytunnel rota be somewhere she can
>> see on a Saturday morning at the gate, not on the laptop.
"""

# tasks: task, who, due, status, waiting_on, qty, notes
TASKS_VISIBLE = [
    ("Clear leaves from the main path", "Hal", "2026-11-07", "done", "", "", ""),
    ("Seed scheme order", "Priya", "2026-11-30", "in_progress", "", "", "discount ends 30 Nov"),
    ("Chase the council about the water meter", "", "2026-11-20", "todo", "council", "", "meter reads about 3x"),
    ("Polytunnel door hinge", "Hal", "2026-11-14", "waiting", "hinge delivery", "", ""),
    ("Order wood chip for paths", "Tomas", "2026-12-05", "todo", "", "", "how many bags?"),
    ("Order manure", "Dot", "2026-12-12", "todo", "", "3", "loads"),
    ("Send out plot agreements", "Ines", "2026-12-15", "in_progress", "", "", "before rents"),
    ("Collect rents", "Tomas", "2027-01-15", "todo", "", "", ""),
    ("Cut back the boundary hedge", "Hal", "2027-02-28", "todo", "", "", "not after Feb (nesting)"),
    ("Fix the shed gutter", "", "2026-09-30", "todo", "", "", "on the list since July"),
    ("Book the skip for the clear-out", "Priya", "2026-11-26", "waiting", "council", "", "needs a permit"),
    ("Clean the water troughs", "Bea", "2026-11-21", "todo", "", "", ""),
    ("Lag the outside taps", "Hal", "2026-11-28", "todo", "", "", ""),
    ("Drain the standpipes", "Hal", "2026-12-01", "waiting", "council", "", "council turns the supply off first"),
    ("Update the waiting list", "Ines", "2026-11-10", "done", "", "", ""),
    ("Write to new plot holders", "Ines", "2026-11-24", "todo", "", "", ""),
    ("Repair the compost bays", "", "2026-12-15", "todo", "", "", ""),
    ("Sharpen communal tools", "Bea", "2026-12-20", "todo", "", "", ""),
    ("Tool shed inventory", "Bea", "2026-11-10", "Done", "", "", ""),
    ("Insurance renewal", "Tomas", "2027-01-31", "todo", "broker", "", ""),
    ("Tidy the bonfire site", "Dot", "2026-11-08", "done", "", "", ""),
    ("Mend the fence by plot 14", "Hal", "2026-12-10", "waiting", "council", "", "council owns the fence"),
    ("Seed potato order", "priya", "2026-12-01", "todo", "", "25", "kg"),
    ("Winter newsletter", "Ines", "2026-12-03", "in_progress", "", "", ""),
    ("Change the bank mandate", "Tomas", "2026-11-30", "waiting", "bank", "", "new signatories"),
    ("Clear plot 9 (given up)", "", "2026-12-31", "todo", "", "", ""),
    ("Bird netting for the fruit cage", "Dot", "2027-02-15", "todo", "", "", ""),
    ("Replace padlocks", "Tomas", "2026-11-25", "todo", "", "4", ""),
    ("Prune the community orchard", "Bea", "2027-01-20", "todo", "", "", ""),
    ("Check the polytunnel heater", "Dot", "2026-11-18", "in_progress", "", "", ""),
    ("Order fleece", "Priya", "2026-11-16", "done", "", "6", "rolls"),
    ("Mulch the soft fruit", "Bea", "2026-12-08", "todo", "", "", ""),
    ("Sort lost property in the shed", "", "2026-11-30", "todo", "", "", ""),
    ("Report the broken streetlight", "Priya", "2026-11-12", "done", "council", "", ""),
    ("Plan the spring work party", "Ines", "2027-02-01", "todo", "", "", ""),
    ("Fix the rainwater butts", "Hal", "2026-12-12", "todo", "", "", "at least two leak"),
    ("Accounts for the AGM", "Tomas", "2027-02-20", "todo", "", "", ""),
    ("Water butt stands (north half)", "Dot", "2026-12-05", "todo", "", "", ""),
    ("Water butt stands (south half)", "Bea", "2026-12-05", "todo", "", "", ""),
    ("Signs for the new car park", "Priya", "2027-01-10", "waiting", "council", "", ""),
]
ROTA_VISIBLE = [("2026-11-02", "Bea"), ("2026-11-09", "Dot"), ("2026-11-16", "Tomas"), ("2026-11-23", "Hal"),
                ("2026-11-30", "Ines"), ("2026-12-07", "Bea"), ("2026-12-14", "Dot"), ("2026-12-21", ""),
                ("2026-12-28", "Tomas"), ("2027-01-04", "Hal"), ("2027-01-11", "Ines"), ("2027-01-18", "Dot")]

# hidden: the same sheet four months on; Bea has left, Wren and Josef have joined
TASKS_HIDDEN = [
    ("Collect rents", "Tomas", "2027-01-15", "done", "", "", ""),
    ("Send out plot agreements", "Ines", "2027-01-01", "done", "", "", ""),
    ("Clear the drainage ditch", "Hal", "2027-03-01", "todo", "", "", "floods plot 3"),
    ("Return the borrowed rotavator", "Josef", "2027-03-10", "in_progress", "", "", "Brook Lane want it back"),
    ("Book the skip for the clear-out", "Priya", "2027-03-17", "todo", "", "", "permit came through"),
    ("Get the water meter replaced", "Hal", "2027-03-25", "waiting", "council", "", "visit not booked yet"),
    ("Prune the community orchard", "Wren", "2027-02-10", "done", "", "", ""),
    ("Order seed potatoes", "Hal", "2027-03-04", "done", "", "30", "kg"),
    ("Cut back the boundary hedge", "Dot", "2027-02-28", "todo", "", "", "nesting season now"),
    ("Mend the fruit cage netting", "Dot", "2027-04-15", "todo", "", "", ""),
    ("Repaint the noticeboard", "", "2027-04-10", "todo", "", "", ""),
    ("Accounts for the AGM", "Tomas", "2027-02-20", "done", "", "", ""),
    ("Renew the public liability insurance", "Tomas", "2027-03-14", "waiting", "broker", "", "quote chased twice"),
    ("Clean out the polytunnel", "Wren", "2027-03-29", "todo", "", "", ""),
    ("Send round the AGM minutes", "Priya", "2027-03-18", "in_progress", "", "", "draft done"),
    ("Sow tomatoes in the polytunnel", "Dot", "2027-03-30", "todo", "", "", ""),
    ("Fix the rainwater butts", "Hal", "2027-04-05", "todo", "", "", ""),
    ("Pay the water bill", "Tomas", "2027-03-05", "done", "", "", ""),
    ("Plan the work party", "Ines", "2027-03-27", "in_progress", "", "", ""),
    ("Order manure", "Dot", "2027-03-26", "todo", "", "", "how many loads? ask at the meeting"),
    ("Spring newsletter", "Ines", "2027-04-01", "todo", "", "", ""),
    ("Fix the main gate lock", "Wren", "2027-03-22", "waiting", "Council (estates team)", "", ""),
    ("Order spring seed packets", "Priya", "2027-03-11", "done", "", "", ""),
    ("Welcome pack for new plot holders", "Ines", "2027-03-31", "todo", "", "", ""),
    ("Replace the shed roof felt", "Josef", "2027-04-20", "waiting", "felt delivery", "", ""),
    ("Strim the paths (top half)", "Josef", "2027-03-20", "todo", "", "", ""),
    ("Strim the paths (bottom half)", "Dot", "2027-03-20", "todo", "", "", ""),
    ("Sharpen communal tools", "Josef", "2027-03-28", "todo", "", "", ""),
    ("Clear plot 9", "Wren", "2027-04-12", "todo", "", "", ""),
    ("Order wood chip for paths", "Tomas", "2027-03-24", "todo", "", "12", "bags"),
    ("Turn the compost bays", "Hal", "2027-02-25", "done", "", "", ""),
    ("Report the fly-tipping by the gate", "Ines", "2027-03-08", "done", "council", "", ""),
    ("Draft the open day leaflet", "Priya", "2027-04-02", "todo", "", "", ""),
    ("Test the standpipes", "Hal", "2027-04-01", "todo", "", "", ""),
    ("Change the bank mandate", "Tomas", "2027-02-12", "done", "bank", "", ""),
    ("Order bird netting", "Dot", "2027-04-08", "todo", "", "3", "rolls"),
    ("Buy replacement padlocks", "Tomas", "2027-04-06", "todo", "", "4", ""),
    ("Table plan for the plant sale", "Wren", "2027-04-25", "todo", "", "", ""),
    ("Check the first aid kit", "Josef", "2027-03-23", "todo", "", "", ""),
    ("Weed the car park edges", "Wren", "2027-04-18", "todo", "", "", ""),
]
ROTA_HIDDEN = [("2027-02-15", "Dot"), ("2027-02-22", "Hal"), ("2027-03-01", "Josef"), ("2027-03-08", "Ines"),
               ("2027-03-15", "Wren"), ("2027-03-22", "Tomas"), ("2027-03-29", "Dot"), ("2027-04-05", "Hal"),
               ("2027-04-12", ""), ("2027-04-19", "Ines")]
# distinctive stems for the tasks the main items are about (keys are computed from the rows, then named by stem)
STEMS = {"Clear the drainage ditch": "ditch", "Return the borrowed rotavator": "rotavator",
         "Cut back the boundary hedge": "hedge", "Renew the public liability insurance": "insurance",
         "Pay the water bill": "bill", "Report the fly-tipping by the gate": "fly", "Order spring seed packets": "seed",
         "Order seed potatoes": "seed", "Book the skip for the clear-out": "skip", "Send round the AGM minutes": "minutes",
         "Draft the open day leaflet": "leaflet", "Get the water meter replaced": "meter", "Fix the main gate lock": "lock"}

# ------------------------------------------------------------------------------------ mirror raw material

MIRROR_MINUTES = {
    "2026-10-29": """# Committee meeting, Thursday 29 October 2026

Present: Priya (chair), Ines (secretary), Tomas (treasurer), Hal (site rep), Dot. Apologies: Bea.

1. **Events.** Ines showed the events board on her phone. Everyone happy with it: the
   open day was the first one where nobody had to dig back through emails to find out
   who was bringing what. Ines will keep it up for the AGM and the plant sale.
2. **Brook Lane.** The society now looks after the Brook Lane site as well. Its own
   little committee (Yusuf, Clem, Marta, Oskar) runs Brook Lane's year as a string of
   events: the wassail, the seed swap, the May fair. Everything they do is getting
   ready for the next one.
3. **Brook Lane's list.** Clem keeps their jobs in a spreadsheet, one line per job, with
   the event it's for. They look at it on their phones the week before each event and
   not much in between.
""",
    "2026-11-12": """# Committee meeting, Thursday 12 November 2026

Present: Priya, Ines, Tomas, Hal, Dot, Bea. Clem and Marta from Brook Lane for item 1.

1. **Brook Lane.** Clem and Marta had seen our events board. Marta: "That's exactly how we
   think about it: what's next, when, and what's still to do for it." Their bonfire
   went fine except that two people bought sparklers and nobody did the cash float.
   Clem asked whether they could have the same kind of thing for their committee.
2. **Ines** will set Brook Lane's committee up with a board. Clem has put their latest
   export in `incoming/`.
3. **Water meter.** Still with the council.
""",
}

MIRROR_MAIL = """From: Clem Fairley
To: Ines Carvalho
Date: Fri, 13 Nov 2026 09:30
Subject: our list

Ines, thanks for last night. The export's in incoming/ now. Each line is a job and the
event it's for. Oskar asked me to say: on the night of the bonfire he was looking at the
list on his phone by torchlight, so the bigger the better!

What we always get wrong is the last week before an event: who's bringing what, and
what's still not done. The wassail is next.

Clem
"""

# mirror tasks: task, event, event_date, who, status, notes
MIRROR_VISIBLE = [
    ("Apple press from the village hall", "Apple day", "2026-10-10", "Oskar", "done", ""),
    ("Bottles and labels", "Apple day", "2026-10-10", "Marta", "done", ""),
    ("Bonfire permit", "Bonfire night", "2026-11-07", "Yusuf", "done", ""),
    ("Sparklers", "Bonfire night", "2026-11-07", "Marta", "done", "bought twice"),
    ("Cash float", "Bonfire night", "2026-11-07", "", "done", "done on the night"),
    ("Mulled apple juice", "Christmas social", "2026-12-12", "Oskar", "todo", ""),
    ("Book the scout hut", "Christmas social", "2026-12-12", "Yusuf", "in_progress", ""),
    ("Raffle", "Christmas social", "2026-12-12", "", "todo", ""),
    ("Mince pies", "Christmas social", "2026-12-12", "Clem", "todo", ""),
    ("Cider for the toast", "Wassail", "2027-01-16", "Oskar", "todo", ""),
    ("Lanterns", "Wassail", "2027-01-16", "Marta", "todo", "jam jars"),
    ("Tell the neighbours", "Wassail", "2027-01-16", "Yusuf", "todo", ""),
    ("Musician", "Wassail", "2027-01-16", "", "todo", ""),
    ("Seed packets from members", "Seed swap", "2027-03-20", "Clem", "todo", ""),
    ("Tables", "Seed swap", "2027-03-20", "Yusuf", "todo", ""),
    ("Posters", "Seed swap", "2027-03-20", "Marta", "todo", ""),
]

MIRROR_HIDDEN = [
    ("Cider", "Wassail", "2027-01-16", "Oskar", "done", ""),
    ("Lanterns", "Wassail", "2027-01-16", "Marta", "done", ""),
    ("Book the scout hut", "Seed swap", "2027-03-20", "Yusuf", "done", ""),
    ("Seed envelopes", "Seed swap", "2027-03-20", "Clem", "todo", ""),
    ("Tea and biscuits (urn)", "Seed swap", "2027-03-20", "Marta", "todo", ""),
    ("Tea and biscuits (cake)", "Seed swap", "2027-03-20", "Oskar", "todo", ""),
    ("Signs on the gate", "Seed swap", "2027-03-20", "", "todo", ""),
    ("Float", "Seed swap", "2027-03-20", "Clem", "in_progress", ""),
    ("Skip", "Spring clean-up", "2027-04-17", "Marta", "waiting", "council permit"),
    ("Gloves and bags", "Spring clean-up", "2027-04-17", "Oskar", "todo", ""),
    ("Stalls", "May fair", "2027-05-22", "Yusuf", "todo", ""),
    ("Raffle prizes", "May fair", "2027-05-22", "Rhiannon", "todo", ""),
    ("Bunting", "May fair", "2027-05-22", "", "todo", ""),
    ("Cash float", "May fair", "2027-05-22", "Clem", "done", ""),
]

# ---------------------------------------------------------------------------------------------- items


def rows_of(cols, tuples):
    return [dict(zip(cols, t)) for t in tuples]


def open_(r):
    return (r["status"] or "").strip().lower() != "done"


def stem(task):
    return STEMS[task]


def task_items(rows):
    """The 7 registered items for the main fixture, keys computed from the hidden rows."""
    today, meeting = SCORE_DAY, MEETING_DAY
    monday = today - timedelta(days=today.weekday())
    rota = {r["water_week"]: r["water_who"] for r in rows if r["water_week"]}
    week = lambda d: rota.get((monday + timedelta(days=7 * d)).isoformat(), "")
    due = lambda r: date.fromisoformat(r["due"]) if r["due"] else None
    overdue = [r["task"] for r in rows if open_(r) and due(r) and due(r) < today]
    past_done = [r["task"] for r in rows if not open_(r) and due(r) and due(r) < today and r["task"] in STEMS]
    priya = [r for r in rows if r["who"] == "Priya"]
    priya_due = [r["task"] for r in priya if open_(r) and due(r) and due(r) <= meeting]
    priya_not = [r["task"] for r in priya if r["task"] not in priya_due]
    council = [r["task"] for r in rows if open_(r) and "council" in r["waiting_on"].lower()]
    council_done = [r["task"] for r in rows if not open_(r) and "council" in r["waiting_on"].lower()]
    board = [r for r in rows if r["task"] == "Repaint the noticeboard"]
    manure = [r for r in rows if r["task"] == "Order manure"]
    strim = [r["who"] for r in rows if r["task"].startswith("Strim the paths")]
    return [
        {"id": "water", "q": "Whose turn is it to do the watering this week?", "kind": "names",
         "require": [week(0)], "forbid": [x for x in (week(-1), week(1)) if x]},
        {"id": "overdue", "q": "Which tasks are overdue?", "kind": "names",
         "require": [stem(t) for t in overdue], "forbid": sorted({stem(t) for t in past_done})},
        {"id": "person", "q": "What does Priya need to do before the committee meeting on Thursday 18 March?", "kind": "names",
         "require": [stem(t) for t in priya_due], "forbid": sorted({stem(t) for t in priya_not})},
        {"id": "council", "q": "Is anything waiting on the council? If so, what?", "kind": "names",
         "require": [stem(t) for t in council], "forbid": [stem(t) for t in council_done]},
        {"id": "nobody", "q": "Who is going to repaint the noticeboard?", "kind": "nobody",
         "key": "nobody" if board and not board[0]["who"] else board[0]["who"]},
        {"id": "unknown", "q": "How many loads of manure are being ordered?", "kind": "unknown",
         "key": "unknown" if manure and not manure[0]["qty"] else manure[0]["qty"]},
        {"id": "two_rows", "q": "Who is strimming the paths?", "kind": "names", "require": strim, "forbid": []},
    ]


def event_items(rows, ev, item, edate, when_ev, who_item, todo_ev, nobody_item, two_item, done_item, stems):
    """7 items for an events-shaped list (the events board's own, and the mirror's); keys computed from rows."""
    today = SCORE_DAY
    dates = {r[ev]: r[edate] for r in rows}
    nxt = min((d, e) for e, d in dates.items() if date.fromisoformat(d) >= today)[1]
    find = lambda e, i: [r for r in rows if r[ev].lower() == e.lower() and r[item].startswith(i)]
    todo = [r[item] for r in rows if r[ev].lower() == todo_ev[0].lower() and open_(r)]
    done = [r[item] for r in rows if r[ev].lower() == todo_ev[0].lower() and not open_(r)]
    later = sorted({e for e, d in dates.items() if date.fromisoformat(d) > date.fromisoformat(dates[nxt])})
    nb = find(*nobody_item)[0]
    dn = find(*done_item)[0]
    return [
        {"id": "when", "q": f"When is the {when_ev}?", "kind": "date", "key": dates[next(e for e in dates if e.lower() == when_ev.lower())]},
        {"id": "who", "q": f"Who is doing the {who_item[1].lower()} for the {who_item[0]}?", "kind": "names",
         "require": [find(*who_item)[0]["who"]], "forbid": []},
        {"id": "todo", "q": f"What is still to do for the {todo_ev[1]}?", "kind": "names",
         "require": sorted({stems[t] for t in todo}), "forbid": sorted({stems[t] for t in done})},
        {"id": "next", "q": "Which event is next?", "kind": "names", "require": [stems[nxt]], "forbid": [stems[e] for e in later]},
        {"id": "nobody", "q": f"Is anyone doing the {nobody_item[1].lower()} for the {nobody_item[0]}?", "kind": "nobody",
         "key": "nobody" if not nb["who"] else nb["who"]},
        {"id": "two_rows", "q": f"Who is doing the {two_item[1].lower()} for the {two_item[0]}?", "kind": "names",
         "require": [r["who"] for r in find(*two_item)], "forbid": []},
        {"id": "done", "q": f"Is the {done_item[1].lower()} for the {done_item[0]} sorted?", "kind": "yes",
         "key": "yes" if not open_(dn) else "no"},
    ]


def events_items(rows):
    stems = {"Book the hall": "hall", "Print the agendas": "agenda", "Teas (urn)": "tea", "Teas (cakes)": "tea",
             "Treasurer's report": "report", "Chairs out": "chair", "AGM": "AGM", "Plant sale": "plant", "Open day": "open day",
             "Seed swap": "seed"}
    return event_items(rows, "event", "item", "date", "plant sale", ("plant sale", "Price labels"), ("AGM", "AGM"),
                       ("plant sale", "Raffle"), ("AGM", "Teas"), ("plant sale", "Cash float"), stems)


def mirror_items(rows):
    stems = {"Book the scout hut": "hut", "Seed envelopes": "envelope", "Tea and biscuits (urn)": "tea",
             "Tea and biscuits (cake)": "tea", "Signs on the gate": "sign", "Float": "float", "Seed swap": "seed swap",
             "Spring clean-up": "clean", "May fair": "may fair"}
    return event_items(rows, "event", "task", "event_date", "May fair", ("May fair", "Raffle prizes"), ("Seed swap", "seed swap"),
                       ("May fair", "Bunting"), ("seed swap", "Tea and biscuits"), ("May fair", "Cash float"), stems)


# ------------------------------------------------------------------------------------------------ writing


def w(path, text, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        f.write(text)
    os.chmod(path, mode)


def csv_text(header, rows):
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(header)
    wr.writerows(rows)
    return buf.getvalue()


def task_csv(tasks, rota):
    out = []
    for i, t in enumerate(tasks):
        wk, who = rota[i] if i < len(rota) else ("", "")
        out.append(list(t) + [wk, who])
    return csv_text(TASK_COLS, out)


def load_kit(r):
    spec = importlib.util.spec_from_file_location("h1_kit_board", os.path.join(r, "kit", "board.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def common(r):
    w(os.path.join(r, "README.md"), README)
    w(os.path.join(r, ".gitignore"), "__pycache__/\n")
    w(os.path.join(r, "docs", "pattern.md"), PATTERN)
    w(os.path.join(r, "kit", "board.py"), BOARD_PY, 0o755)
    w(os.path.join(r, "kit", "new_board.py"), NEW_BOARD_PY, 0o755)
    ev = os.path.join(r, "boards", "events")
    w(os.path.join(ev, "board.json"), json.dumps(EVENTS_CFG, indent=1) + "\n")
    w(os.path.join(ev, "events.csv"), csv_text(EVENT_COLS, EVENTS_VISIBLE))
    load_kit(r).build(ev, today=BUILD_DAY)


def items_file(path, replaces, items, markers, page_hint=None, documented=None):
    json.dump({"replaces": replaces, "page_hint": page_hint, "documented": documented, "today": SCORE_DAY.isoformat(),
               "context": CONTEXT, "markers": markers, "items": items}, open(path, "w"), indent=1)


def main(dest):
    # main fixture
    d = os.path.join(dest, "h1-v1"); r = os.path.join(d, "repo")
    common(r)
    for day, text in MINUTES.items():
        w(os.path.join(r, "minutes", f"{day}.md"), text)
    w(os.path.join(r, "mail", "thread-water-meter.txt"), MAIL)
    w(os.path.join(r, "incoming", "tasks.csv"), task_csv(TASKS_VISIBLE, ROTA_VISIBLE))
    truth = {"endpoint": "h1", "variant": "v1", "hidden": "h1-v1", "decision_turn": "T1", "prompts": {"T1": PROMPT},
             "oracle_hint": ORACLE_HINT, "prior_board": "boards/events", "data": "incoming/tasks.csv",
             "pass_rule": "reader pass: >= 6 of 7 items right in both of two reader runs"}
    json.dump(truth, open(os.path.join(d, "truth.json"), "w"), indent=1)
    h = os.path.join(dest, "hidden", "h1-v1")
    w(os.path.join(h, "tasks.csv"), task_csv(TASKS_HIDDEN, ROTA_HIDDEN))
    items_file(os.path.join(h, "tasks.items.json"), "incoming/tasks.csv",
               task_items(rows_of(TASK_COLS, [list(t) + list(ROTA_HIDDEN[i] if i < len(ROTA_HIDDEN) else ("", ""))
                                              for i, t in enumerate(TASKS_HIDDEN)])),
               {"hidden": [r"rotavator", r"\bJosef\b", r"\bWren\b"], "visible": [r"gutter", r"\bBea\b"]})
    w(os.path.join(h, "events.csv"), csv_text(EVENT_COLS, EVENTS_HIDDEN))
    items_file(os.path.join(h, "events.items.json"), "boards/events/events.csv", events_items(rows_of(EVENT_COLS, EVENTS_HIDDEN)),
               {"hidden": [r"\bJosef\b", r"\bWren\b", r"Seed swap"], "visible": [r"\bBea\b", r"scout hut"]},
               page_hint="boards/events/index.html", documented="python3 kit/board.py boards/events")
    # mirror
    d = os.path.join(dest, "h1m-v1"); r = os.path.join(d, "repo")
    common(r)
    for day, text in MIRROR_MINUTES.items():
        w(os.path.join(r, "minutes", f"{day}.md"), text)
    w(os.path.join(r, "mail", "thread-brook-lane.txt"), MIRROR_MAIL)
    w(os.path.join(r, "incoming", "tasks.csv"), csv_text(MIRROR_COLS, MIRROR_VISIBLE))
    json.dump(dict(truth, endpoint="h1m", hidden="h1m-v1",
                   pass_rule="reader pass on the prior board's answers: >= 6 of 7 in both of two reader runs"),
              open(os.path.join(d, "truth.json"), "w"), indent=1)
    h = os.path.join(dest, "hidden", "h1m-v1")
    w(os.path.join(h, "tasks.csv"), csv_text(MIRROR_COLS, MIRROR_HIDDEN))
    items_file(os.path.join(h, "tasks.items.json"), "incoming/tasks.csv", mirror_items(rows_of(MIRROR_COLS, MIRROR_HIDDEN)),
               {"hidden": [r"Rhiannon", r"[Bb]unting"], "visible": [r"press", r"[Ss]parkler"]})
    mirror_context = CONTEXT.replace("the committee meets on Thursday 18 March 2027", "the Brook Lane committee looks at its list the week before each event")
    p = os.path.join(h, "tasks.items.json"); j = json.load(open(p)); j["context"] = mirror_context
    json.dump(j, open(p, "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
