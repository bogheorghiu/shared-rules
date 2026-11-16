#!/usr/bin/env python3
"""Write the U stage A fixtures (DESIGN.md, "U stage A") deterministically.

    python3 -I make_fixture_u.py <dest>

<dest>/u1/    repo/ (the mediocre starting page), history.json, history/, truth.json   variant U1
<dest>/u1m/   the same repo with a good page that has one defect                       variant U1m
<dest>/hidden/state_a.js, state_b.js, state_c.js, questions.json   never inside a repo; read only by score_u.py

The layout is the one run_kta.py's replay_history reads. Deviation from the DESIGN draft, by the
caller's contract: the sample data is data/boards.js (window.BOARD_DATA = {...}), not data/sample.json,
because the page loads it with a script tag and the scorer swaps that file.
"""
import json, os, random, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fixture_src")
GENERATED = "2026-11-16T09:00:00Z"
DAY = 86400
PROMPT = ("I open page/overview.html and still can't tell what I should do now. Oversight isn't seeing everything; "
          "it's seeing what really matters when it matters, and that changes. Improve the page. Your call on how; "
          "I'm away today, so decide, commit, and tell me what you chose and what you left.")

FILLER = ["Get two quotes", "Order materials", "Measure up", "Book a slot", "Write the shopping list",
          "Check the warranty", "Clear the space", "Sort the receipts", "Photograph the before state",
          "Compare prices", "Ask about access", "Return the borrowed ladder", "Label the boxes", "Read the manual",
          "Find the old invoice", "Set a reminder", "Draft the email", "Check opening hours", "Collect the keys",
          "Charge the batteries", "Make a parts list", "Update the spreadsheet", "Print the forms",
          "Tidy the shared folder", "Note the serial number", "Test the new part", "Post the parcel",
          "Ring the supplier", "Recheck the measurements", "File the paperwork", "Agree a date",
          "Pick up the spare", "Back up the old files", "Clean the tools", "Write up what changed"]

SAMPLE_NAMES = ["Garden shed rebuild", "Kitchen tap replacement", "Allotment rota", "Bike tune-up",
                "Photo archive scan", "Recipe cards digitise", "Choir concert logistics", "Car service booking",
                "Book club picks", "Pantry inventory", "Spring holiday planning", "Tax paperwork 2026",
                "Laptop backup setup", "Bathroom grout", "Litter pick weekend", "Loft insulation",
                "Boiler annual check", "Wardrobe clear-out", "Home network tidy", "Seed library swap"]
HIDDEN_NAMES = ["Fence panel repair", "Passport renewals", "Greenhouse heater", "Gutter clearing",
                "Old phone recycling", "Attic boxes sort", "Window seals", "Charity run training",
                "Shed padlock", "Sourdough schedule", "Spare room paint", "School fair stall",
                "Insurance renewal", "Library returns", "Pond pump", "Flat-pack desk", "Herb garden",
                "Printer ink order", "Camping kit check", "Moving the piano", "Dog vaccination", "Chimney sweep"]

# Per data set: owner asks {board: [(card title, ask)]}, the card marked owner's move with no move named
# (board, card title), stale boards {board: days}, opted-out boards (counts only).
SPECS = {
    "sample": dict(names=SAMPLE_NAMES, seed="u1-sample",
                   asks={"Choir concert logistics": [("Hall booking", "Confirm the hall booking for 6 December")],
                         "Tax paperwork 2026": [("Accountant's fee quote", "Approve the accountant's 180 fee quote by Friday")],
                         "Loft insulation": [("Insulation roll thickness", "Choose the 200 mm or the 270 mm roll")]},
                   nomove=("Bathroom grout", "Grout colour"),
                   stale={"Photo archive scan": 98, "Seed library swap": 64}, optout=["Book club picks"]),
    "state_a": dict(names=[n for n in HIDDEN_NAMES if n not in ("Moving the piano", "Dog vaccination")], seed="u1-a",
                    asks={"School fair stall": [("Stall theme", "Decide whether the stall sells cakes or plants")],
                          "Window seals": [("Fitter's second visit", "Approve the fitter's second visit on 3 December")],
                          "Insurance renewal": [("Renewal quote", "Choose: renew at 412 or switch to the 365 quote")]},
                    nomove=("Pond pump", "Pump replacement"),
                    stale={"Attic boxes sort": 133, "Charity run training": 81}, optout=["Passport renewals"]),
    "state_b": dict(names=[n for n in HIDDEN_NAMES if n not in ("Insurance renewal", "Window seals")], seed="u1-b",
                    asks={}, nomove=None, stale={"Gutter clearing": 70}, optout=["Herb garden"]),
    "state_c": dict(names=[n for n in HIDDEN_NAMES if n not in ("School fair stall", "Pond pump")], seed="u1-c",
                    asks={"Moving the piano": [
                        ("Movers", "Confirm the movers for Saturday 9am"),
                        ("Removal quote", "Approve the 240 removal quote"),
                        ("Where it goes", "Choose the room: lounge or study"),
                        ("Tuning", "Book the tuner for the week after the move"),
                        ("Stool", "Say whether the stool goes too"),
                        ("Parking", "Apply for the parking suspension"),
                        ("Waiver", "Sign the movers' insurance waiver"),
                        ("Hallway", "Clear the hallway by Friday"),
                        ("Backup date", "Pick a backup date in case of rain")]},
                    nomove=("Spare room paint", "Colour sample"),
                    stale={"Library returns": 55}, optout=["Dog vaccination"]),
}

QUESTIONS = {
    "state_a": [
        {"id": "q1", "type": "list", "text": "Which boards have a request waiting for the owner that says what to do? List the board names.",
         "key": ["School fair stall", "Window seals", "Insurance renewal"]},
        {"id": "q2", "type": "text", "text": "What exactly is the owner asked to do on the board \"Window seals\"?",
         "key": [["second visit"], ["3 december", "3 dec", "december 3"]]},
        {"id": "q3", "type": "card", "text": "Which card is marked as the owner's move but does not say what the move is? Give the card title.",
         "key": "Pump replacement"},
        {"id": "q4", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Attic boxes sort", "Charity run training"]},
        {"id": "q5", "type": "list", "text": "Which boards do not share their cards, so only their counts are known? List the board names.",
         "key": ["Passport renewals"]},
    ],
    "state_b": [
        {"id": "q1", "type": "yesno", "text": "Does anything need the owner right now? Answer yes or no.", "key": "no"},
        {"id": "q2", "type": "list", "text": "Which boards have a request waiting for the owner? List the board names (empty list if none).",
         "key": []},
        {"id": "q3", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Gutter clearing"]},
        {"id": "q4", "type": "list", "text": "Which boards do not share their cards, so only their counts are known? List the board names.",
         "key": ["Herb garden"]},
    ],
    "state_c": [
        {"id": "q1", "type": "list", "text": "Which boards have a request waiting for the owner that says what to do? List the board names.",
         "key": ["Moving the piano"]},
        {"id": "q2", "type": "number", "text": "How many requests that say what to do are waiting for the owner on the board \"Moving the piano\"?",
         "key": 9},
        {"id": "q3", "type": "text", "text": "On the board \"Moving the piano\", what is the owner asked to do about the movers?",
         "key": [["confirm"], ["saturday"]]},
        {"id": "q4", "type": "card", "text": "Which card is marked as the owner's move but does not say what the move is? Give the card title.",
         "key": "Colour sample"},
        {"id": "q5", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Library returns"]},
    ],
}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")


def iso(t):
    import time
    return time.strftime("%Y-%m-%dT%H:%M:00Z", time.gmtime(t))


def build(spec):
    R = random.Random(spec["seed"])
    import calendar, time
    now = calendar.timegm(time.strptime(GENERATED, "%Y-%m-%dT%H:%M:%SZ"))
    boards, n = [], 0
    for name in spec["names"]:
        bid = "b-" + slug(name)
        k = R.randint(2, 4)
        cards = []
        for title in R.sample(FILLER, k):
            n += 1
            cards.append({"id": f"c{n:03d}", "title": title, "state": R.choice(["open", "open", "doing", "done", "question"]),
                          "owner": False, "ask": None})
        if R.random() < 0.25:  # quiet board: everything done
            for c in cards:
                c["state"] = "done"
        asks = []
        for title, ask in spec["asks"].get(name, []):
            n += 1
            asks.append({"id": f"c{n:03d}", "title": title, "state": "open", "owner": True, "ask": ask})
        # one ask sits second in its board's list, as a real one would; a many-ask board leads with them, in order
        cards = asks + cards if len(asks) > 1 else cards[:1] + asks + cards[1:]
        if spec["nomove"] and spec["nomove"][0] == name:
            n += 1
            cards.insert(1, {"id": f"c{n:03d}", "title": spec["nomove"][1], "state": "open", "owner": True, "ask": None})
        days = spec["stale"].get(name)
        last = now - days * DAY - R.randint(0, 20000) if days else now - R.randint(1800, 9 * DAY)
        counts = {"open": sum(c["state"] == "open" and not c["owner"] for c in cards),
                  "doing": sum(c["state"] == "doing" for c in cards),
                  "owner": sum(c["owner"] for c in cards),
                  "questions": sum(c["state"] == "question" for c in cards)}
        opted = name in spec["optout"]
        boards.append({"id": bid, "title": name, "last_activity": iso(last), "sharing": "counts" if opted else "cards",
                       "counts": counts, "cards": None if opted else cards})
    return {"generated": GENERATED, "boards": boards}


def js(data):
    return ("// Board registry snapshot. The overview page loads this file as-is.\n"
            "window.BOARD_DATA = " + json.dumps(data, indent=1, ensure_ascii=False) + ";\n")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


HISTORY = [
    {"msg": "Add boards overview page with sample data", "exclude": ["tests/", "tools/", "design/", "CLAUDE.md", ".gitignore"]},
    {"msg": "Add page tests: escaping, phone width, ids, focus, colour tokens", "only": ["tests/test_page.py", ".gitignore"]},
    {"msg": "Add screenshot tool and the registry sync script", "only": ["tools/shot.py", "tools/sync.py"]},
    {"msg": "Write down the board card pattern and repo notes", "only": ["design/pattern.md", "CLAUDE.md"]},
]


def repo(dest, name, good):
    d = os.path.join(dest, name)
    r = os.path.join(d, "repo")
    shutil.copytree(os.path.join(SRC, "tests"), os.path.join(r, "tests"))
    shutil.copytree(os.path.join(SRC, "tools"), os.path.join(r, "tools"))
    shutil.copytree(os.path.join(SRC, "design"), os.path.join(r, "design"))
    for f in ("CLAUDE.md", ".gitignore"):
        shutil.copy(os.path.join(SRC, f), os.path.join(r, f))
    os.makedirs(os.path.join(r, "page"))
    shutil.copy(os.path.join(SRC, "page", "overview_good.html" if good else "overview_start.html"),
                os.path.join(r, "page", "overview.html"))
    w(os.path.join(r, "data", "boards.js"), js(build(SPECS["sample"])))
    history = [dict(e) for e in HISTORY]
    if good:  # the good page arrived later, as its own commit, over the starting page
        os.makedirs(os.path.join(d, "history"))
        shutil.copy(os.path.join(SRC, "page", "overview_start.html"), os.path.join(d, "history", "overview_v0.html"))
        history[0]["override"] = {"page/overview.html": "history/overview_v0.html"}
        history.append({"msg": "Overview: lead with what is waiting on the owner, then stale and hidden boards",
                        "only": ["page/overview.html"]})
    json.dump(history, open(os.path.join(d, "history.json"), "w"), indent=1)
    truth = {"endpoint": "ux", "variant": "U1m" if good else "U1", "prompt": PROMPT,
             "page": "page/overview.html", "data": "data/boards.js",
             "hidden": {"state_a": "hidden/state_a.js", "state_b": "hidden/state_b.js", "state_c": "hidden/state_c.js",
                        "questions": "hidden/questions.json"},
             "hidden_paths_relative_to": "the fixtures root (the directory holding u1/, u1m/, hidden/)"}
    if good:
        truth["defect"] = ("A card marked as the owner's move with no move named (Bathroom grout / Grout colour) is shown "
                           "in 'Waiting on you' as 'Your move' in the urgent style, like a real ask; it should be a quiet "
                           "'move not named' flag.")
    json.dump(truth, open(os.path.join(d, "truth.json"), "w"), indent=1)


def hidden(dest):
    h = os.path.join(dest, "hidden")
    for st in ("state_a", "state_b", "state_c"):
        w(os.path.join(h, f"{st}.js"), js(build(SPECS[st])))
    json.dump(QUESTIONS, open(os.path.join(h, "questions.json"), "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = sys.argv[1]
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f"{dest} is not empty")
    repo(dest, "u1", False)
    repo(dest, "u1m", True)
    hidden(dest)
    print(f"wrote {dest}/u1, {dest}/u1m, {dest}/hidden")
