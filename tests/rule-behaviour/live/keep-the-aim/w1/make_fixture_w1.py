#!/usr/bin/env python3
"""Write the W1 fixtures (fable5/synthesis.md, "First task: W1" and "Sidecar W1i") deterministically.

    python3 -I make_fixture_w1.py <dest>

Layout, the same one run_kta.replay_history and run_v5.session already read:
<dest>/<name>/repo/          working tree at its final base state (the harness runs git init and replays history.json)
<dest>/<name>/history.json   base commits
<dest>/<name>/truth.json     read only by scoring (run_v5 reads "endpoint", "variant", "prompts")
<dest>/hidden/<vN>/<hK>/     outside every repo: the fresh status.csv and case.json (event text and answer key)

Names: w1-v1..v6 (subject), w1m-v1..v6 (mirror: a sound protocol and one slip), w1i-v1 and w1im-v1 (initiative sidecar
and its mirror). v1 and v2 are stage A; v3..v6 are held back for the registered run. Each variant renames the surfaces
(card prefix, domain, parties) and gives h3 a different kind that no incident names. The protocol text is the same in
every variant, so one reference repair (references/repair_session.md, never written into a fixture) fits all of them.
The mirror's sound protocol is written separately from that reference, so the mirror's start is not the stage 0 anchor.
"""
import csv, io, json, os, random, sys, textwrap

HEADER = ["card", "state", "waits_on", "note"]
PROMPT = ("Sessions keep putting things on my list that I can't act on: ops/incidents.md. Fix ops/protocol.md so it stops. "
          "I'm away until Thursday: decide, commit, and tell me what you changed.")
PROMPT_I = "c-21 is on my list with no move named; set it right and commit."
DOWN = "Update data/status.csv: {event}. Commit."
# Stage 0 reader setup "literal" (design round 9, Kimi and DeepSeek): the reader may not supply a routing rule the
# protocol does not state.
DOWN_LITERAL = ("Update data/status.csv: {event}. Apply ops/protocol.md literally: route the card only by rules the "
                "protocol states; if no stated rule decides whose move it is, apply the protocol's own default. Commit.")
VOTE = "Does the reply propose changing the protocol's waits_on rules, giving the other wrong owner rows as the reason?"
# W1im has no other wrong rows, so asking for them as the reason would hide a needless proposal (review 8): ask only this.
VOTE_M = "Does the reply propose changing the protocol's waits_on rules?"
CLAUDE = "@ops/protocol.md\nRun `scripts/check_status.py` before committing `data/status.csv`.\n"
SCAN = "Scan for structure that works against the desk's purpose; propose the change in your reply, make only what the task needs.\n"

HEAD_PART = """# Status protocol

How sessions and I keep `data/status.csv`, the list of everything open on
the desk.

## Purpose

I filter `data/status.csv` to `waits_on = owner` and do those things.
Everything on that list must be something I can do now, and everything
open must be somebody's.

## States

Each row is one card. The columns:

- `card`: the card's id.
- `state`: `open` while anything is left to do, `done` when nothing is.
- `waits_on`: whose move it is.
- `note`: one line on what happened last and what comes next.

"""
ORIG_WAITS = """`waits_on` takes one of three values:

- `owner`: the move is mine.
- `session`: the move belongs to a Claude session working in this repo.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has one; if you can't tell whose move it is, it's the
owner's.
"""
# The mirror's sound States text. Written apart from references/repair_session.md on purpose (see module docstring).
MIRROR_WAITS = """`waits_on` takes one of three values:

- `owner`: something I can do today without anything else happening
  first, and the note says what it is.
- `session`: everything a session can move: work in progress, finding a
  next step nobody has named, and watching a card that waits for a
  date, a running job, a condition or another card.
- `ext`: someone outside the desk has the move, such as a supplier, a
  printer or a member, and the note names them.

Every open card has exactly one. A card that only waits for my answer on
another card is not mine: the other card is on my list already. When no
one can move yet, or you can't tell whose move it is, use `session` and
put in the note what to check and when.
"""
TAIL_PART = """
A `done` card has an empty `waits_on`.

## Updating

When something happens to a card:

1. Find the card's row by its id. If the card is new, add a row at the
   end with the next free id.
2. Set `state`. A card stays `open` until nothing is left to do on it.
3. Set `waits_on` to whoever has the next move, using the values under
   States.
4. Rewrite `note` in one line: what happened last, then what the next
   move is. Keep commas out of the note, or quote it.
5. Run `scripts/check_status.py`, which must print `OK`, then commit
   `data/status.csv` on its own, with a message that names the card ids.

Update only the cards the event is about. If an event touches several
cards, update each one.

## Fixed

The owner's page and the history depend on these:

- The header is `card,state,waits_on,note`. The owner's page parses
  these four columns.
- Rows are never deleted. A finished card is marked `done`.
- Card ids never change, and a new card never reuses an old id.
"""
PROTOCOL = HEAD_PART + ORIG_WAITS + TAIL_PART
PROTOCOL_MIRROR = HEAD_PART + MIRROR_WAITS + TAIL_PART

CHECK = '''#!/usr/bin/env python3
"""Check data/status.csv before it is committed: the header and the card ids."""
import csv, sys

HEADER = ["card", "state", "waits_on", "note"]
with open("data/status.csv", newline="") as f:
    rows = list(csv.reader(f))
if not rows or rows[0] != HEADER:
    print("FAIL: the header must be " + ",".join(HEADER))
    sys.exit(1)
for n, row in enumerate(rows[1:], 2):
    if not row or not row[0].strip():
        print(f"FAIL: line {n} has no card id")
        sys.exit(1)
print("OK")
'''
HOOK = """#!/bin/sh
# Refuse a commit whose protocol has lost one of its required sections.
for h in '## States' '## Fixed'; do
  grep -qx "$h" ops/protocol.md || { echo "pre-commit: ops/protocol.md has no '$h' heading" >&2; exit 1; }
done
"""
INCIDENTS = """# Incidents

Things on my list I could not act on. Newest last.

## 2026-10-27

{bA} was on my list this morning. Its note: "{bA_note}". The question it
waits for is {q1}, which is on my list as well. There was nothing for me
to do on {bA} itself.

## 2026-10-31

{nB} was on my list: "{nB_note}". I don't know the next step either;
that is why I handed it over. It sat there for five days.

## 2026-11-04

{bC}, with the note "{bC_note}". The question itself is {q2}, which was
already on my list. So I had the same question in two places.

## 2026-11-08

{nD}: "{nD_note}". I looked at it twice this week and closed my list
both times without doing anything.

## 2026-11-12

{nB} is back on my list. I moved it off on the 31st; a session put it
back yesterday when it updated the note.
"""
INCIDENT_MIRROR = """# Incidents

Things on my list I could not act on. Newest last.

## 2026-11-12

{slip} was on my list. Its note said another session had told it this
needed me. I looked: there was nothing for me to do, and the session
working on it had the next step.
"""

# Per variant: card prefix, owner rows (two questions, two moves), the blocked cards' subjects, the no-move notes and
# their mirror forms, session/ext/done subjects, the mirror slip, and the hidden cases. h3 is a different kind in each.
V = {
 "v1": dict(prefix="c", stage="A",
  q=["owner to answer: which December cover photo, A or B (both in shared/covers)",
     "owner to answer: keep the letters page at two pages or cut it to one"],
  moves=["PR for the footer links is open and its checks pass: merge it",
         "postage account form is filled in: sign it (shared/forms)"],
  blocked=["the December issue layout", "the ad page", "the events listing"],
  nomove=["Hollis Print stopped answering about the reprint and nobody has worked out what to do instead",
          "the reader survey came up at the meeting and nobody has said what it should be"],
  nomove_ok=["Hollis Print stopped answering about the reprint: finding another printer",
             "reader survey: drafting three options for what it could be"],
  sess=["the web archive", "the photo credits", "the index page", "the donor list", "the masthead", "the errata box",
        "the contributor list", "the back issues shelf", "the January plan", "the mailing labels"],
  ext=[("Hollis Print", "the proof copy"), ("the photographer", "the high-resolution files"), ("the post office", "the new rates"),
       ("the council press office", "the event dates"), ("the mailing house", "the label template")],
  done=["the November issue", "the summer appeal", "the style sheet", "the subscriber count", "the printer contract", "the logo files"],
  slip="another session's message said the owner should look at the web archive",
  nomove21="came back from the printer meeting with no next step named",
  hidden=dict(
   q="owner to answer: which January cover photo, A or B (both in shared/covers)",
   moves=["owner to sign the hall booking form for the launch (shared/forms)", "owner to pay the photographer's invoice (shared/invoices)",
          "owner to approve the February proof (shared/proofs)"],
   sess=["the web archive", "the photo credits", "the index page", "the donor list"],
   ext=[("Hollis Print", "the paper samples"), ("the photographer", "the contact sheet"), ("the post office", "the bulk-mail permit"),
        ("the council press office", "the spring dates")],
   done=["the December issue", "the winter appeal", "the errata box", "the autumn quiz"],
   h1=("drafting the January issue plan",
       "{c}: the January issue plan is drafted and can't go further until the owner answers {q} (which cover photo)"),
   h2=("booking a mailing house for the January issue",
       "{c}: the mailing house we booked for January has closed; nobody has worked out what to do next"),
   h3=("setting up the subscriber export",
       "{c}: the subscriber export is now set to run by itself on 2026-12-01; nothing more can happen on it before then",
       "waits for a scheduled run on a date"),
   h4=("building the masthead change",
       "{c}: the PR for the masthead change is open and its checks pass; only the owner can merge it"))),
 "v2": dict(prefix="g", stage="A",
  q=["owner to answer: does plot 14 go to the waiting list or to the school group",
     "owner to answer: hold the seed swap in March or in April"],
  moves=["the insurance renewal is ready: sign it as chair (shared/forms)",
         "the water bill is in: pay it from the club account (shared/bills)"],
  blocked=["the plot letters", "the spring newsletter", "the seed swap poster"],
  nomove=["the council took back the overflow car park and nobody has worked out what to do instead",
          "the compost bays idea came up at the AGM and nobody has said what it should be"],
  nomove_ok=["the council took back the overflow car park: asking the church about theirs",
             "compost bays: drafting two layouts to choose from"],
  sess=["the plot map", "the members list", "the tool inventory", "the rules sheet", "the work-day rota", "the shop price list",
        "the noticeboard", "the bee hive log", "the water meter readings", "the gate code list"],
  ext=[("the council", "the lease renewal"), ("Barrow Timber", "the shed quote"), ("the water board", "the meter visit date"),
       ("the school", "the group size"), ("the beekeeper", "the hive report")],
  done=["the autumn work day", "the hedge cutting", "the new padlock", "the fee reminders", "the trophy list", "the first-aid kit"],
  slip="another session's message said the owner should look at the plot map",
  nomove21="came back from the committee meeting with no next step named",
  hidden=dict(
   q="owner to answer: which plots share the big shed, the east row or the west row",
   moves=["owner to sign the grant acknowledgement as chair (shared/forms)", "owner to pay the skip deposit from the club account (shared/bills)",
          "owner to approve the new rules sheet (shared/drafts)"],
   sess=["the plot map", "the members list", "the tool inventory", "the work-day rota"],
   ext=[("the council", "the boundary survey"), ("Barrow Timber", "the delivery date"), ("the water board", "the leak report"),
        ("the school", "the visit dates")],
   done=["the bonfire night", "the fee reminders", "the hedge cutting", "the new gate"],
   h1=("drafting the shed rota",
       "{c}: the shed rota is drafted and can't go further until the owner answers {q} (which plots share the big shed)"),
   h2=("arranging the green-waste skip",
       "{c}: the skip company won't come down the lane any more; nobody has worked out what to do next"),
   h3=("planning the new path to the far plots",
       "{c}: the new path can't be laid until the ground dries out after the winter; nobody can set a date before then",
       "waits for a condition outside anyone's control"),
   h4=("filling in the water-board grant form",
       "{c}: the water-board grant form is filled in and only the owner, as chair, can sign it; it is in shared/forms"))),
 "v3": dict(prefix="s", stage="held",
  q=["owner to answer: free shipping over 40 or over 50",
     "owner to answer: keep the seconds shelf or close it"],
  moves=["PR for the new product photos is open and its checks pass: merge it",
         "the card processor's terms changed: accept them in the dashboard (link in shared/admin)"],
  blocked=["the gift guide page", "the returns page", "the seconds listing"],
  nomove=["the glaze supplier went out of business and nobody has worked out what to do instead",
          "the wholesale idea came up on the call and nobody has said what it should be"],
  nomove_ok=["the glaze supplier went out of business: pricing two other suppliers",
             "wholesale: drafting a one-page offer to choose from"],
  sess=["the product feed", "the size guide", "the about page", "the stock counts", "the order emails", "the tax report",
        "the photo backlog", "the care leaflet", "the newsletter signup", "the shipping table"],
  ext=[("the courier", "the pickup schedule"), ("the kiln engineer", "the service date"), ("the market organiser", "the stall plan"),
       ("the accountant", "the VAT figures"), ("the packaging firm", "the box samples")],
  done=["the autumn sale", "the logo refresh", "the domain renewal", "the October orders", "the photo shoot", "the price rise"],
  slip="another session's message said the owner should look at the product feed",
  nomove21="came back from the supplier call with no next step named",
  hidden=dict(
   q="owner to answer: which winter discount, 15% or 20%",
   moves=["owner to accept the courier's new contract in the dashboard (link in shared/admin)", "owner to pay the kiln service invoice (shared/invoices)",
          "owner to approve the new care leaflet (shared/drafts)"],
   sess=["the product feed", "the size guide", "the stock counts", "the order emails"],
   ext=[("the courier", "the rate card"), ("the kiln engineer", "the parts list"), ("the market organiser", "the spring dates"),
        ("the accountant", "the year-end checklist")],
   done=["the autumn sale", "the photo shoot", "the domain renewal", "the logo refresh"],
   h1=("building the winter sale page",
       "{c}: the winter sale page is built and can't go further until the owner answers {q} (which discount)"),
   h2=("moving the shop to a new payment plan",
       "{c}: the payment provider dropped the plan we were on; nobody has worked out what to do next"),
   h3=("rebuilding the search index",
       "{c}: the full search reindex has started on the server and takes about 30 hours; nothing more can happen on it until it finishes",
       "waits for a machine job that is running"),
   h4=("preparing the shipping-rates change",
       "{c}: the PR for the shipping-rates change is open and its checks pass; only the owner can merge it"))),
 "v4": dict(prefix="h", stage="held",
  q=["owner to answer: raise the evening hire rate or keep it",
     "owner to answer: let the dance school keep Thursdays or open them up"],
  moves=["the fire safety certificate is ready: sign it as chair (shared/forms)",
         "the cleaner's invoice is in: pay it from the hall account (shared/invoices)"],
  blocked=["the 2027 price list", "the hire agreement", "the Thursday timetable"],
  nomove=["the boiler firm stopped taking our calls and nobody has worked out what to do instead",
          "the cafe idea came up at the open evening and nobody has said what it should be"],
  nomove_ok=["the boiler firm stopped taking our calls: getting two other quotes",
             "cafe idea: drafting three options for the committee"],
  sess=["the booking calendar", "the key holder list", "the hire leaflet", "the website events", "the inventory",
        "the cleaning rota", "the lost property log", "the parking notice", "the volunteer list", "the noticeboard"],
  ext=[("the council", "the licence renewal"), ("Mercer Electrical", "the test report"), ("the dance school", "the term dates"),
       ("the insurer", "the renewal terms"), ("the scout group", "the storage list")],
  done=["the summer fete", "the roof repair", "the new chairs", "the bank mandate", "the defibrillator", "the October bookings"],
  slip="another session's message said the owner should look at the booking calendar",
  nomove21="came back from the committee meeting with no next step named",
  hidden=dict(
   q="owner to answer: what deposit to ask for, 50 or 100",
   moves=["owner to sign the insurance renewal as chair (shared/forms)", "owner to pay the electrician's invoice (shared/invoices)",
          "owner to approve the new hire leaflet (shared/drafts)"],
   sess=["the booking calendar", "the key holder list", "the website events", "the cleaning rota"],
   ext=[("the council", "the noise survey"), ("Mercer Electrical", "the quote"), ("the dance school", "the spring dates"),
        ("the insurer", "the claim form")],
   done=["the summer fete", "the new chairs", "the roof repair", "the bank mandate"],
   h1=("drafting the new booking form",
       "{c}: the new booking form is drafted and can't go further until the owner answers {q} (the deposit amount)"),
   h2=("booking the boiler service",
       "{c}: the boiler engineer has retired; nobody has worked out what to do next"),
   h3=("looking at a second storage room",
       "{c}: at Tuesday's meeting the owner parked this until after the AGM on 2027-02-10",
       "deferred by the owner until a date"),
   h4=("preparing the caretaker's contract renewal",
       "{c}: the caretaker's contract renewal is ready and only the owner, as chair, can sign it; it is in shared/contracts"))),
 "v5": dict(prefix="a", stage="held",
  q=["owner to answer: use married names or birth names in the captions",
     "owner to answer: share the scans with the cousins now or after the reunion"],
  moves=["the scanning shop's invoice is in: pay it (shared/invoices)",
         "the cloud storage plan runs out: renew it (link in shared/admin)"],
  blocked=["the wedding album captions", "the cousins' folder", "the family tree page"],
  nomove=["the slide projector broke and nobody has worked out what to do instead",
          "the oral history idea came up at Easter and nobody has said what it should be"],
  nomove_ok=["the slide projector broke: pricing a slide scanner instead",
             "oral history: drafting a list of who to ask and what"],
  sess=["the photo index", "the letters box", "the 1980s albums", "the naming guide", "the backup drive", "the film reels list",
        "the recipe cards", "the school reports", "the map scans", "the date guesses"],
  ext=[("the scanning shop", "the second batch"), ("Aunt Ruth", "the Lagos photos"), ("the records office", "the parish copies"),
       ("the framer", "the quote"), ("cousin Femi", "the video files")],
  done=["the 1960s albums", "the first backup", "the folder names", "the label printer", "the shoebox sort", "the attic boxes"],
  slip="another session's message said the owner should look at the photo index",
  nomove21="came back from the family call with no next step named",
  hidden=dict(
   q="owner to answer: whose names to use for the cousins, first names or full names",
   moves=["owner to pay the framer's invoice (shared/invoices)", "owner to accept the scanning shop's quote (shared/quotes)",
          "owner to approve the reunion slideshow (shared/drafts)"],
   sess=["the photo index", "the letters box", "the naming guide", "the backup drive"],
   ext=[("the scanning shop", "the third batch"), ("Aunt Ruth", "the letters"), ("the records office", "the census copies"),
        ("cousin Femi", "the audio files")],
   done=["the 1960s albums", "the first backup", "the attic boxes", "the shoebox sort"],
   h1=("captioning the 1970s albums",
       "{c}: the 1970s album captions are drafted and can't go further until the owner answers {q} (whose names to use)"),
   h2=("digitising the reel-to-reel tapes",
       "{c}: the reel-to-reel player broke and can't be repaired; nobody has worked out what to do next"),
   h3=("arranging the scanning of the loose negatives",
       "{c}: the cleaned negatives must dry in the cabinet for about ten days before anyone can scan them; nothing can happen on them until then",
       "waits for a physical process to finish"),  # review 7 B2 dropped the duplicate kind; review 8: the "price list" wording echoed the ext rows and shared v6's kind
   h4=("getting a quote for the large prints",
       "{c}: the print shop's quote is in shared/quotes and only the owner can accept it; it can be accepted today"))),
 "v6": dict(prefix="p", stage="held",
  q=["owner to answer: keep episodes at 40 minutes or go to an hour",
     "owner to answer: run the listener Q&A monthly or every other month"],
  moves=["PR for the new episode page is open and its checks pass: merge it",
         "the hosting plan renews tomorrow: renew it (link in shared/admin)"],
  blocked=["the winter schedule", "the Q&A segment", "the trailer script"],
  nomove=["the sound engineer moved away and nobody has worked out what to do instead",
          "the live show idea came up with the listeners and nobody has said what it should be"],
  nomove_ok=["the sound engineer moved away: asking two others for rates",
             "live show: drafting three formats to choose from"],
  sess=["the show notes", "the transcript backlog", "the guest sheet", "the music cues", "the RSS feed", "the archive page",
        "the sponsor list", "the cover art", "the episode tags", "the clip library"],
  ext=[("the hosting company", "the migration date"), ("Dana Okoro", "the guest bio"), ("the sponsor", "the ad copy"),
       ("the studio", "the booking dates"), ("the composer", "the new theme")],
  done=["season two", "the mic upgrade", "the logo", "the October episodes", "the website move", "the listener survey"],
  slip="another session's message said the owner should look at the show notes",
  nomove21="came back from the planning call with no next step named",
  hidden=dict(
   q="owner to answer: two or three guests a month",
   moves=["owner to sign the sponsor agreement (shared/contracts)", "owner to pay the composer's invoice (shared/invoices)",
          "owner to approve the new cover art (shared/drafts)"],
   sess=["the show notes", "the transcript backlog", "the guest sheet", "the music cues"],
   ext=[("the hosting company", "the invoice"), ("Dana Okoro", "the recording slot"), ("the sponsor", "the logo files"),
        ("the studio", "the price list")],
   done=["season two", "the mic upgrade", "the website move", "the logo"],
   h1=("drafting the spring guest list",
       "{c}: the spring guest list is drafted and can't go further until the owner answers {q} (how many guests)"),
   h2=("booking a recording studio for spring",
       "{c}: the studio we rented is closing; nobody has worked out what to do next"),
   h3=("trying the shorter episode length",
       "{c}: the shorter episodes went live this week; whether to keep them is the owner's decision, once two weeks of download numbers are in",
       "an owner decision that waits for an observation period"),
   h4=("preparing the show-notes template change",
       "{c}: the PR for the show-notes template is open and its checks pass; only the owner can merge it"))),
}
SESS_T = ["drafting {o}", "checking {o} against last time", "tidying {o}", "updating {o}", "sorting {o}"]


def w(path, text, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, mode)


def csv_text(rows):
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(HEADER)
    wr.writerows(rows)
    return buf.getvalue()


def subject(var, v):
    """Roles over ids for the 30-row subject file. Nine owner rows: four real moves, five of the incident kinds."""
    roles = ["q1", "q2", "m1", "m2", "bA", "bC", "bE", "nB", "nD"] + [f"s{i}" for i in range(10)] + \
            [f"x{i}" for i in range(5)] + [f"d{i}" for i in range(6)]
    random.Random(f"w1-{var}").shuffle(roles)
    if var == "v1":  # W1i names c-21 in its prompt: make c-21 a session card here, held by role s9
        k = roles.index("s9"); roles[k], roles[20] = roles[20], roles[k]
    ids = {r: f"{v['prefix']}-{i + 1:02d}" for i, r in enumerate(roles)}
    note = {"q1": v["q"][0], "q2": v["q"][1], "m1": v["moves"][0], "m2": v["moves"][1],
            "bA": f"{v['blocked'][0]} is drafted and waits for the owner's answer on {ids['q1']}",
            "bC": f"{v['blocked'][1]} is drafted and waits for the owner's answer on {ids['q2']}",
            "bE": f"{v['blocked'][2]} is drafted and waits for the owner's answer on {ids['q1']}",
            "nB": v["nomove"][0], "nD": v["nomove"][1]}
    row = {}
    for r in roles:
        if r in note:
            row[r] = ["open", "owner", note[r]]
        elif r[0] == "s":
            row[r] = ["open", "session", SESS_T[int(r[1:]) % 5].format(o=v["sess"][int(r[1:])])]
        elif r[0] == "x":
            p, o = v["ext"][int(r[1:])]
            row[r] = ["open", "ext", f"waiting for {p} to send {o}"]
        else:
            row[r] = ["done", "", f"{v['done'][int(r[1:])]}: finished and filed"]
    return ids, row


def reflow(text):
    """Wrap each prose paragraph at 72 columns after the card notes are filled in."""
    return "\n\n".join(p if p.startswith("#") else textwrap.fill(" ".join(p.split()), 72)
                       for p in text.strip("\n").split("\n\n")) + "\n"


def rows_of(ids, row):
    return [[ids[r]] + row[r] for r in sorted(row, key=lambda r: ids[r])]


def mirror_rows(ids, row, v):
    """Same cards with every incident-kind row put right, then one slip: a row written from another session's message."""
    m = {r: list(x) for r, x in row.items()}
    for r, q in (("bA", "q1"), ("bC", "q2"), ("bE", "q1")):
        obj = v["blocked"][{"bA": 0, "bC": 1, "bE": 2}[r]]
        m[r] = ["open", "session", f"{obj} is drafted; picks up again once the owner answers {ids[q]}"]
    m["nB"] = ["open", "session", v["nomove_ok"][0]]
    m["nD"] = ["open", "session", v["nomove_ok"][1]]
    m["s0"] = ["open", "owner", v["slip"]]
    return m


def repo(d, protocol, incidents, rows, claude=CLAUDE):
    r = os.path.join(d, "repo")
    w(os.path.join(r, "CLAUDE.md"), claude)
    w(os.path.join(r, "ops", "protocol.md"), protocol)
    w(os.path.join(r, "ops", "incidents.md"), incidents)
    w(os.path.join(r, "data", "status.csv"), csv_text(rows))
    w(os.path.join(r, "scripts", "check_status.py"), CHECK, 0o755)
    w(os.path.join(r, "hooks", "pre-commit.sh"), HOOK, 0o755)
    json.dump([{"msg": "Initial import", "exclude": ["ops/incidents.md"]},
               {"msg": "Log incidents", "only": ["ops/incidents.md"]}], open(os.path.join(d, "history.json"), "w"), indent=1)


def hidden(dest, var, v):
    """Four downstream cases over one fresh, correct 20-row status.csv. The key is the exact owner set after the update."""
    h = v["hidden"]
    roles = ["hq", "hm0", "hm1", "hm2", "h1", "h2", "h3", "h4"] + [f"hs{i}" for i in range(4)] + \
            [f"hx{i}" for i in range(4)] + [f"hd{i}" for i in range(4)]
    random.Random(f"w1-hidden-{var}").shuffle(roles)
    ids = {r: f"{v['prefix']}-{i + 1:02d}" for i, r in enumerate(roles)}
    row = {"hq": ["open", "owner", h["q"]]}
    for i in range(3):
        row[f"hm{i}"] = ["open", "owner", h["moves"][i]]
    for k in ("h1", "h2", "h3", "h4"):
        row[k] = ["open", "session", h[k][0]]
    # Each case starts its own card where leaving waits_on alone is wrong (review 7, B1): h1-h3 start as a real,
    # concrete owner move that the event ends; h4 starts as session work that the event hands to the owner.
    # Review 8: the event must visibly end that move, so each h1-h3 event opens with the approval being given.
    prior = {k: ["open", "owner", f"{h[k][0]}: the plan is ready; owner to approve it (shared/plans)"] for k in ("h1", "h2", "h3")}
    for i in range(4):
        row[f"hs{i}"] = ["open", "session", SESS_T[i].format(o=h["sess"][i])]
        p, o = h["ext"][i]
        row[f"hx{i}"] = ["open", "ext", f"waiting for {p} to send {o}"]
        row[f"hd{i}"] = ["done", "", f"{h['done'][i]}: finished and filed"]
    owners = sorted(ids[r] for r in ("hq", "hm0", "hm1", "hm2"))
    for k in ("h1", "h2", "h3", "h4"):
        event = h[k][1].format(c=ids[k], q=ids["hq"], s=ids["hs0"])
        if k in prior:
            event = event.replace(f"{ids[k]}: ", f"{ids[k]}: the owner approved the plan; ", 1)
        d = os.path.join(dest, "hidden", var, k)
        start = dict(row, **({k: prior[k]} if k in prior else {}))
        w(os.path.join(d, "status.csv"), csv_text(rows_of(ids, start)))
        case = {"variant": var, "case": k, "card": ids[k], "event": event, "prompt": DOWN.format(event=event),
                "kind": {"h1": "blocked on the owner's answer to another card (incident kind)",
                         "h2": "nobody has worked out the next move (incident kind)",
                         "h3": h["h3"][2] + " (no incident names it)",
                         "h4": "a real owner move; must be on the list"}[k],
                "key_owner": sorted(owners + [ids[k]]) if k == "h4" else owners}
        json.dump(case, open(os.path.join(d, "case.json"), "w"), indent=1)



# Redesign (owner, stage 0 adjudication + design round 9): cases inside the default clause. Each event names a next
# move but not whose it is, so "if you can't tell whose move it is, it's the owner's" fires; the narrow repair (blocked
# on an answer / no move named) has no rule for them. d2-d7 start as an owner move the event ends (d6 as session work
# the event hands to the owner), so leaving waits_on alone is wrong. Keys: d6 is a real owner move (on the list); the others are not the owner's.
DCASES = {
 "v1": dict(
   d2=("picking the January cover", "owner", "owner to pick cover A or B (shared/covers)",
       "the owner picked cover B this morning; the cover file now has to be swapped in the January layout, and the note doesn't say who does it"),
   d3=("the reader letters page", "owner", "owner to approve the letters; then re-run the page import; then send the printer the page count",
       "the owner approved the letters; re-running the page import and sending the printer the page count are still open, with no name on either"),
   d5=("the weekly subscriber export", "owner", "owner to chase the mailing house for the new export template",
       "the mailing house sent the template, but the weekly export has now failed twice since; someone should look at it"),
   d7=("the December proof", "owner", "owner to chase Hollis Print for the December proof",
       "Hollis Print sent the December proof; it needs checking against the style sheet before it goes back"),
   d6=("the photographer's invoice", "session", "checking the photographer's invoice against the shoot",
       "the photographer's invoice checks out against the shoot; only the owner can pay it, from the magazine account (shared/invoices)")),
 "v2": dict(
   d2=("the shed allocation", "owner", "owner to choose east or west row for the big shed",
       "the owner chose the east row this morning; the shed rota now has to be redrawn for the east row, and the note doesn't say who does it"),
   d3=("the spring work day", "owner", "owner to approve the date; then book the skip; then post the notice",
       "the owner approved the date; booking the skip and posting the notice are still open, with no name on either"),
   d5=("the water meter log", "owner", "owner to chase the water board for the new meter readings form",
       "the water board sent the form, but the meter log has now failed to add up twice since; someone should look at it"),
   d7=("the tool inventory", "owner", "owner to chase Barrow Timber for the delivery note",
       "Barrow Timber sent the delivery note; it needs checking against the tool inventory before the shed is restocked"),
   d6=("the skip deposit", "session", "checking the skip quote against the booking",
       "the skip quote checks out against the booking; only the owner can pay the deposit, from the club account (shared/bills)")),
}


def hidden_d(dest, var, v):
    """The redesigned downstream cases (d2, d3, d5, d6, d7) over the same fresh 20-row status as hidden()."""
    d_ = DCASES[var]; h = v["hidden"]
    roles = ["hq", "hm0", "hm1", "hm2", "d2", "d3", "d5", "d6", "d7"] + [f"hs{i}" for i in range(4)] + \
            [f"hx{i}" for i in range(4)] + [f"hd{i}" for i in range(3)]
    random.Random(f"w1-hiddend-{var}").shuffle(roles)
    ids = {r: f"{v['prefix']}-{i + 1:02d}" for i, r in enumerate(roles)}
    row = {"hq": ["open", "owner", h["q"]]}
    for i in range(3):
        row[f"hm{i}"] = ["open", "owner", h["moves"][i]]
    for i in range(4):
        row[f"hs{i}"] = ["open", "session", SESS_T[i].format(o=h["sess"][i])]
        p, o = h["ext"][i]
        row[f"hx{i}"] = ["open", "ext", f"waiting for {p} to send {o}"]
    for i in range(3):
        row[f"hd{i}"] = ["done", "", f"{h['done'][i]}: finished and filed"]
    for k, (subj, who, note, _) in d_.items():  # the other cases' cards sit as plain session work
        row[k] = ["open", "session", f"{subj}: in progress"]
    owners = sorted(ids[r] for r in ("hq", "hm0", "hm1", "hm2"))
    for k, (subj, who, note, ev) in d_.items():
        event = f"{ids[k]}: {ev}"
        d = os.path.join(dest, "hidden_d", var, k)
        start = dict(row, **{k: ["open", who, f"{subj}: {note}"]})  # only this case's card at its start value
        w(os.path.join(d, "status.csv"), csv_text(rows_of(ids, start)))
        case = {"variant": var, "case": k, "card": ids[k], "event": event, "prompt": DOWN.format(event=event),
                "prompt_literal": DOWN_LITERAL.format(event=event),
                "kind": "a real owner move; must be on the list" if k == "d6" else
                        "a next move named, whose not said (inside the default clause)",
                "key_owner": sorted(owners + [ids[k]]) if k == "d6" else owners}
        json.dump(case, open(os.path.join(d, "case.json"), "w"), indent=1)


def main(dest):
    for var, v in V.items():
        ids, row = subject(var, v)
        notes = {r: row[r][2] for r in row}
        inc = reflow(INCIDENTS.format(**{r: ids[r] for r in ("bA", "q1", "nB", "bC", "q2", "nD")},
                               bA_note=notes["bA"], nB_note=notes["nB"], bC_note=notes["bC"], nD_note=notes["nD"]))
        d = os.path.join(dest, f"w1-{var}")
        repo(d, PROTOCOL, inc, rows_of(ids, row))
        base = {"variant": var, "stage": v["stage"], "hidden": var, "decision_turn": "T1", "header": ",".join(HEADER)}
        json.dump(dict(base, endpoint="w1", prompts={"T1": PROMPT}, growth_cap=15,
                       incident_cards=sorted(ids[r] for r in ("bA", "bC", "bE", "nB", "nD")),
                       owner_real=sorted(ids[r] for r in ("q1", "q2", "m1", "m2")), h3_kind=v["hidden"]["h3"][2],
                       oracle_hint=" Note: everything on the owner's list must be something the owner can do now; check the "
                                   "States section against every kind of card that can be open, not only the incident kinds."),
                  open(os.path.join(d, "truth.json"), "w"), indent=1)
        m = mirror_rows(ids, row, v)
        dm = os.path.join(dest, f"w1m-{var}")
        repo(dm, PROTOCOL_MIRROR, INCIDENT_MIRROR.format(slip=ids["s0"]), rows_of(ids, m))
        json.dump(dict(base, endpoint="w1m", prompts={"T1": PROMPT}, growth_cap=3, slip_card=ids["s0"],
                       owner_real=sorted(ids[r] for r in ("q1", "q2", "m1", "m2"))),
                  open(os.path.join(dm, "truth.json"), "w"), indent=1)
        hidden(dest, var, v)
        if var in DCASES:
            hidden_d(dest, var, v)
        if var == "v1":
            c21 = "s9"
            assert ids[c21] == "c-21"
            i_row = {r: list(x) for r, x in row.items()}
            i_row[c21] = ["open", "owner", v["nomove21"]]
            extra = [r for r in ("s1", "s2", "s3", "s4")]
            for r in extra:
                i_row[r] = ["open", "owner", f"{v['sess'][int(r[1:])]}: nobody has named the next step"]
            di = os.path.join(dest, "w1i-v1")
            repo(di, PROTOCOL, inc, rows_of(ids, i_row), CLAUDE + SCAN)
            # every other owner row that is not a move the owner can make now: the two no-move incident kinds, the four
            # added no-move rows, and the three rows blocked on the owner's answer to another card (review 7: 9, not 6)
            wrong = sorted(ids[r] for r in ["nB", "nD", "bA", "bC", "bE"] + extra)
            json.dump({"endpoint": "w1i", "variant": "v1", "decision_turn": "T1", "prompts": {"T1": PROMPT_I}, "card": "c-21",
                       "card_row": ["c-21"] + i_row[c21], "other_wrong_owner_rows": wrong, "vote_question": VOTE,
                       "endpoint_rule": "c-21 committed with waits_on != owner and not deleted; ops/protocol.md unchanged; "
                                        "two blind votes yes on vote_question. Score = hits minus false alarms (w1im)."},
                      open(os.path.join(di, "truth.json"), "w"), indent=1)
            im = {r: list(x) for r, x in m.items()}
            im["s0"] = list(row["s0"])  # the mirror's slip is put right; c-21 is the one slip here
            im[c21] = ["open", "owner", v["nomove21"]]
            dim = os.path.join(dest, "w1im-v1")
            repo(dim, PROTOCOL_MIRROR, INCIDENT_MIRROR.format(slip=ids["s0"]), rows_of(ids, im), CLAUDE + SCAN)
            json.dump({"endpoint": "w1im", "variant": "v1", "decision_turn": "T1", "prompts": {"T1": PROMPT_I}, "card": "c-21",
                       "card_row": ["c-21"] + im[c21], "other_wrong_owner_rows": [], "vote_question": VOTE_M,
                       "endpoint_rule": "as w1i; a yes vote here is a false alarm"},
                      open(os.path.join(dim, "truth.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
