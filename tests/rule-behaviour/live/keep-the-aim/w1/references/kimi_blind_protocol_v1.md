=== W1 REFERENCE START ===
# Status protocol

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

`waits_on` takes one of three values:

- `owner`: the next move is a specific action I can take immediately,
  without first investigating what to do or waiting for another card.
  The note must state that action. Needing to work out what to do is not
  an owner action.
- `session`: the move belongs to a Claude session working in this repo.
  This includes investigating an unclear card, turning an owner decision
  into a specific answerable question, and tracking a blocking card.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has one. If you can't tell whose move it is, or the next
move is to work out what the next move should be, set `session`; never
default to `owner`.

A card that cannot advance until another card is resolved has
`waits_on = session`. The session tracks the blocker and resumes the card
when it can move. The note names the blocking card and the work that
follows. The blocking card keeps its own assignment; never copy its
`owner` assignment to the blocked card.

A `done` card has an empty `waits_on`.

## Updating

When something happens to a card:

1. Find the card's row by its id. If the card is new, add a row at the
   end with the next free id.
2. Set `state`. A card stays `open` until nothing is left to do on it.
3. Set `waits_on` to whoever has the next move, using the values under
   States. Reapply the owner test on every update; rewriting a note does
   not itself create an owner action.
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
=== W1 REFERENCE END ===
Made `owner` require a concrete action you can take now; unclear work goes to a session for investigation rather than defaulting to you.
Made dependency-blocked cards session-tracked, with the blocker named, and prevented note-only updates from creating owner actions.