#!/usr/bin/env python3
"""Write the U stage A fixtures (DESIGN.md, "U stage A") deterministically.

    python3 -I make_fixture_u.py <dest>

<dest>/u1/    repo/ (the mediocre starting page), history.json, history/, truth.json   variant U1
<dest>/u1m/   the same repo with a good page that has one defect                       variant U1m
<dest>/u1-v2/ U1 whose tests/test_page.py also pins the old card structure             variant U1v2
<dest>/hidden/state_a.js, state_b.js, state_c.js, questions.json, scoring.json   never inside a repo; read only
              by score_u.py

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
# recede=True puts the stale and opted-out boards last in registry order. Why: the starting page renders
# in registry order, and in the first anchor read it earned points only because those boards happened to
# sit in its first viewport; at the end of the list they sit below the first viewport at 1280 and at 390
# (checked by score_u.py --selftest), so only a page that surfaces them shows them.
SPECS = {
    "sample": dict(names=SAMPLE_NAMES, seed="u1-sample",
                   asks={"Choir concert logistics": [("Hall booking", "Confirm the hall booking for 6 December")],
                         "Tax paperwork 2026": [("Accountant's fee quote", "Approve the accountant's 180 fee quote by Friday")],
                         "Loft insulation": [("Insulation roll thickness", "Choose the 200 mm or the 270 mm roll")]},
                   nomove=("Bathroom grout", "Grout colour"),
                   stale={"Photo archive scan": 98, "Seed library swap": 64}, optout=["Book club picks"]),
    "state_a": dict(names=[n for n in HIDDEN_NAMES if n not in ("Moving the piano", "Dog vaccination")], seed="u1-a", recede=True,
                    asks={"School fair stall": [("Stall theme", "Decide whether the stall sells cakes or plants")],
                          "Window seals": [("Fitter's second visit", "Approve the fitter's second visit on 3 December")],
                          "Insurance renewal": [("Renewal quote", "Choose: renew at 412 or switch to the 365 quote")]},
                    nomove=("Pond pump", "Pump replacement"),
                    stale={"Attic boxes sort": 133, "Charity run training": 81}, optout=["Passport renewals"]),
    "state_b": dict(names=[n for n in HIDDEN_NAMES if n not in ("Insurance renewal", "Window seals")], seed="u1-b", recede=True,
                    asks={}, nomove=None, stale={"Gutter clearing": 70}, optout=["Herb garden"]),
    "state_c": dict(names=[n for n in HIDDEN_NAMES if n not in ("School fair stall", "Pond pump")], seed="u1-c", recede=True,
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

# role: "score" counts toward the score; "gate" is pass/fail and never a point (its honest answer is
# "none", which the starting page earned for free in the first anchor read); "report" is recorded only;
# "fixed" decides the mirror (the no-move card must not be read as something the owner can do now) and is
# reported for U1. State b is the gate state: nothing there needs the owner.
# Review 7 (owner D1): the stale and opted-out items reward one layout choice, so they are "report"; state a
# q7 repeats q1's count, so it is "report" too; four layout-independent items about the asks' content were
# added. The score comes from states a and c: 13 items (at least 12 keeps one-item vote noise small).
# Review 8: a "fixed" item is asked alone, in its own request (asked beside q1/q3 it was primed by them), and is
# right when its "absent" board (the no-move card's) is not listed and at least one key board is: exact set
# equality failed it for unrelated misses. Its wording avoids "something the owner can do right now", which
# state b q1 had dropped as ambiguous.
# Question texts never name a board or card that is another question's key in the same request
# (score_u.py refuses a request that contains a key).
QUESTIONS = {
    "state_a": [
        {"id": "q1", "role": "score", "type": "list", "text": "Which boards have a request waiting for the owner that says what to do? List the board names.",
         "key": ["School fair stall", "Window seals", "Insurance renewal"]},
        {"id": "q2", "role": "score", "type": "text", "text": "What is the owner asked to approve, and for what date?",
         "key": [["second visit"], ["3 december", "3 dec", "december 3", "dec 3", "3rd december", "december 3rd",
                                    "2026 12 03", "3 12 2026"]]},
        {"id": "q3", "role": "score", "type": "card", "text": "Which card is marked as the owner's move but does not say what the move is? Give the card title.",
         "key": "Pump replacement"},
        {"id": "q4", "role": "report", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Attic boxes sort", "Charity run training"]},
        {"id": "q5", "role": "report", "type": "list", "text": "Which boards do not share their cards, so only their counts are known? List the board names.",
         "key": ["Passport renewals"]},
        {"id": "q6", "role": "score", "type": "text", "text": "The owner is asked to choose between two prices. Which two?",
         "key": [["412"], ["365"]]},
        {"id": "q7", "role": "report", "type": "number", "text": "In total, how many requests that say what to do are waiting for the owner?",
         "key": 3},
        {"id": "q8", "role": "score", "type": "text", "text": "One request asks the owner to choose what a stall sells. What are the two options?",
         "key": [["cake"], ["plant"]]},
        {"id": "q9", "role": "fixed", "type": "list", "text": "Which boards need the owner to act now? List the board names.",
         "key": ["School fair stall", "Window seals", "Insurance renewal"], "absent": "Pond pump"},
    ],
    "state_b": [
        {"id": "q1", "role": "gate", "type": "yesno", "text": "Is there a request waiting for the owner right now? Answer yes or no.", "key": "no"},
        {"id": "q2", "role": "gate", "type": "list", "text": "Which boards have a request waiting for the owner? List the board names (empty list if none).",
         "key": []},
        {"id": "q3", "role": "report", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Gutter clearing"]},
        {"id": "q4", "role": "report", "type": "list", "text": "Which boards do not share their cards, so only their counts are known? List the board names.",
         "key": ["Herb garden"]},
    ],
    "state_c": [
        {"id": "q1", "role": "score", "type": "list", "text": "Which boards have a request waiting for the owner that says what to do? List the board names.",
         "key": ["Moving the piano"]},
        {"id": "q2", "role": "score", "type": "number", "text": "In total, how many requests that say what to do are waiting for the owner?",
         "key": 9},
        {"id": "q3", "role": "score", "type": "text", "text": "What is the owner asked to do about the movers?",
         "key": [["confirm"], ["saturday"]]},
        {"id": "q4", "role": "score", "type": "card", "text": "Which card is marked as the owner's move but does not say what the move is? Give the card title.",
         "key": "Colour sample"},
        {"id": "q5", "role": "report", "type": "list", "text": "Which boards are stale (no activity for weeks)? List the board names.",
         "key": ["Library returns"]},
        {"id": "q6", "role": "score", "type": "text", "text": "What amount is the owner asked to approve for the removal?",
         "key": [["240"]]},
        {"id": "q7", "role": "report", "type": "list", "text": "Which boards do not share their cards, so only their counts are known? List the board names.",
         "key": ["Dog vaccination"]},
        {"id": "q8", "role": "score", "type": "text", "text": "By which day must the hallway be cleared?", "key": [["friday"]]},
        {"id": "q9", "role": "score", "type": "text", "text": "The owner is asked to choose a room for something. Which two rooms?",
         "key": [["lounge"], ["study"]]},
        {"id": "q10", "role": "score", "type": "text", "text": "What document is the owner asked to sign?", "key": [["waiver"]]},
        {"id": "q11", "role": "fixed", "type": "list", "text": "Which boards need the owner to act now? List the board names.",
         "key": ["Moving the piano"], "absent": "Spare room paint"},
    ],
}

# Read by score_u.py grade. Floors are set from the anchors' scores, not carried over from the first read;
# null means not set yet and grade reports the floor as "unset".
SCORING = {"score_states": ["state_a", "state_c"], "floors": {"state_a": None, "state_c": None}, "threshold": None,
           "mirror_not_worse": None,
           "gate_rule": "two votes: a gate passes if every gate item is right in both; if any item-vote is wrong, a "
                        "third vote is sent and each gate item must be right in at least 2 of 3 (review 7: a perfect "
                        "page failed about 1 time in 8 under the both-votes rule)",
           "pass_rule": "U1: render gates (fixture guard tests, hostile text, no horizontal scroll) AND the state b "
                        "gate AND every floor AND mean score >= threshold. U1m (owner D3): render gates AND every "
                        "'fixed' item right in a majority of votes AND the state b gate AND mean score >= mirror_not_worse (the starting "
                        "page's anchor score less the noise floor). A void vote (API error or unparsed reply) is "
                        "resent alone, never scored as wrong; a valid vote is never resent. The mean score is over votes 1 and 2 "
                        "only; a third vote serves the gate and fixed items."}

# The mirror's own check (score_u.py render, gates.json "mirror"). Why: the reading score cannot see the
# mirror defect; in the first anchor read the judge named the no-move card correctly with the defect present.
MIRROR = {
    "states": ["state_a", "state_c"],
    "cards": "every card in that state's data with owner true and ask null "
             "(state_a: Pond pump / Pump replacement; state_c: Spare room paint / Colour sample)",
    "holder": "each element whose own text node contains the card title exactly (script and style excluded)",
    "container": "holder.closest('li, article, tr'), else the holder itself",
    "flag_text": "move not named",
    "flag_selector": "[data-flag~=\"move-not-named\"]",
    "flagged": "the container's textContent contains flag_text (any case), or the container matches flag_selector or "
               "has a descendant that does",
    "urgent_tokens": ["--urgent", "--urgent-bg", "--urgent-border"],
    "urgent": "a holder, or any ancestor of it below <body>, whose computed color, background-color, or a border colour "
              "on a side with nonzero width and a style other than none equals the computed value of one of "
              "urgent_tokens (a card drawn inside the urgent box reads as urgent)",
    "skeleton": [["waiting", "Waiting on you"], ["attention", "Needs a look"], ["others", "Other boards"]],
    "skeleton_rule": "each id exists, its first h2 reads the given text, they come in this document order, and "
                     "--urgent still resolves to a colour on :root (so the urgent test cannot be dodged by deleting it)",
    "pass": "skeleton holds AND on every listed state each such card has at least one holder, at least one of its "
            "containers is flagged, and no holder is urgent",
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
    names = spec["names"]
    if spec.get("recede"):
        back = set(spec["stale"]) | set(spec["optout"])
        names = [x for x in names if x not in back] + [x for x in names if x in back]
    for name in names:
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


def pin_structure(test_file):
    """U1v2: add the tests that pin the old card structure into tests/test_page.py, as PageTest methods."""
    text = open(test_file).read()
    extra = open(os.path.join(SRC, "v2_structure_tests.py")).read()
    extra = extra[extra.index("    def test_"):]  # the file's header comment stays out of the repo
    tail = '\n\nif __name__ == "__main__":'
    assert text.count(tail) == 1
    open(test_file, "w").write(text.replace(tail, "\n" + extra.rstrip() + "\n" + tail))


def repo(dest, name, good, page=None, pin=False):
    """page: a page file to use instead of the starting/good one (references, for score_u.py --selftest)."""
    d = os.path.join(dest, name)
    r = os.path.join(d, "repo")
    shutil.copytree(os.path.join(SRC, "tests"), os.path.join(r, "tests"))
    if pin:
        pin_structure(os.path.join(r, "tests", "test_page.py"))
    shutil.copytree(os.path.join(SRC, "tools"), os.path.join(r, "tools"))
    shutil.copytree(os.path.join(SRC, "design"), os.path.join(r, "design"))
    for f in ("CLAUDE.md", ".gitignore"):
        shutil.copy(os.path.join(SRC, f), os.path.join(r, f))
    os.makedirs(os.path.join(r, "page"))
    shutil.copy(page or os.path.join(SRC, "page", "overview_good.html" if good else "overview_start.html"),
                os.path.join(r, "page", "overview.html"))
    w(os.path.join(r, "data", "boards.js"), js(build(SPECS["sample"])))
    history = [dict(e) for e in HISTORY]
    if pin:
        history[1]["msg"] = "Add page tests: escaping, phone width, ids, focus, colour tokens, card layout"
    if good:  # the good page arrived later, as its own commit, over the starting page
        os.makedirs(os.path.join(d, "history"))
        shutil.copy(os.path.join(SRC, "page", "overview_start.html"), os.path.join(d, "history", "overview_v0.html"))
        history[0]["override"] = {"page/overview.html": "history/overview_v0.html"}
        history.append({"msg": "Overview: lead with what is waiting on the owner, then stale and hidden boards",
                        "only": ["page/overview.html"]})
    json.dump(history, open(os.path.join(d, "history.json"), "w"), indent=1)
    truth = {"endpoint": "ux", "variant": "U1m" if good else ("U1v2" if pin else "U1"), "prompt": PROMPT,
             "page": "page/overview.html", "data": "data/boards.js",
             "hidden": {"state_a": "hidden/state_a.js", "state_b": "hidden/state_b.js", "state_c": "hidden/state_c.js",
                        "questions": "hidden/questions.json", "scoring": "hidden/scoring.json"},
             "hidden_paths_relative_to": "the fixtures root (the directory holding u1/, u1m/, hidden/)"}
    if good:
        truth["defect"] = ("A card marked as the owner's move with no move named (Bathroom grout / Grout colour) is shown "
                           "in 'Waiting on you' as 'Your move' in the urgent style, like a real ask; it should be a quiet "
                           "'move not named' flag.")
        truth["mirror_check"] = MIRROR
    if pin:
        truth["pinned"] = ("tests/test_page.py also pins the old card structure (test_board_card_layout, "
                           "test_counts_all_four_in_order, test_registry_order) beside the guard tests.")
    json.dump(truth, open(os.path.join(d, "truth.json"), "w"), indent=1)


def hidden(dest):
    h = os.path.join(dest, "hidden")
    for st in ("state_a", "state_b", "state_c"):
        w(os.path.join(h, f"{st}.js"), js(build(SPECS[st])))
    json.dump(QUESTIONS, open(os.path.join(h, "questions.json"), "w"), indent=1)
    json.dump(dict(SCORING, mirror=MIRROR), open(os.path.join(h, "scoring.json"), "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = sys.argv[1]
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f"{dest} is not empty")
    repo(dest, "u1", False)
    repo(dest, "u1m", True)
    repo(dest, "u1-v2", False, pin=True)
    hidden(dest)
    print(f"wrote {dest}/u1, {dest}/u1m, {dest}/u1-v2, {dest}/hidden")
