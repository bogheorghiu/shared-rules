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

- `owner`: the move is mine. The note must name a specific action I can
  take now, without waiting for another card and without first having to
  investigate or define the task. A future owner decision does not make a
  blocked card actionable.
- `session`: the move belongs to a Claude session working in this repo.
  This includes investigating an unclear next step and tracking a card
  blocked by another card until it can be routed again.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has one. If you can't tell whose move it is, or the next
step is to work out what should be done, use `session` and name a concrete
investigation as the next move. Never default to `owner` or use it as a
parking place.

A `done` card has an empty `waits_on`.

A card that cannot advance until another open card changes is `session`,
not `owner`, even when the blocking card is waiting on me. Its note must
name the blocking card's id and what a session will do when it clears. Do
not repeat the blocker's owner action as though it were an action on the
blocked card.

## Updating

When something happens to a card:

1. Find the card's row by its id. If the card is new, add a row at the
   end with the next free id.
2. Set `state`. A card stays `open` until nothing is left to do on it.
3. Set `waits_on` to whoever has the next move, using the values and
   routing rules under States. Rewriting a note is not itself a hand-off
   and is never, by itself, a reason to move a card to `owner`.
4. Rewrite `note` in one line: what happened last, then what the next
   move is. Keep commas out of the note, or quote it.
5. If the event changes or clears a card named as a blocker, find every
   open card whose note names its id and update each dependent card for
   its new next move.
6. Run `scripts/check_status.py`, which must print `OK`, then commit
   `data/status.csv` on its own, with a message that names the card ids.

Update only the cards the event is about, including dependent cards when
their blocker changes. If an event touches several cards, update each one.

## Fixed

The owner's page and the history depend on these:

- The header is `card,state,waits_on,note`. The owner's page parses
  these four columns.
- Rows are never deleted. A finished card is marked `done`.
- Card ids never change, and a new card never reuses an old id.
=== W1 REFERENCE END ===
Restricted `owner` to concrete actions the owner can take now; unclear work now goes to `session` for investigation instead of defaulting to `owner`.
Made dependency-blocked cards `session`-owned, with blocker ids in their notes and mandatory rerouting when those blockers change.
Clarified that note-only edits are not hand-offs, preventing unclear cards from being bounced back onto the owner list.