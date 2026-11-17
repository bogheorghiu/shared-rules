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

- `owner`: a move I can make now, from the note alone, such as merge,
  sign, pay, choose or answer. The note says what to do.
- `session`: the move belongs to a Claude session working in this repo.
  That includes working out a next move nobody has named, picking a card
  up again once what it waits for has happened, and checking back on a
  date, a running job or a condition.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has one. Before writing `owner`, ask: could I do this
today, with nothing else having to happen first? If not, it is not mine.
That holds when the card waits for my answer on another card: that card
is already on my list, so this one is `session`, and its note names the
card it waits for. If nobody can move until a date, a run, a condition
or another card, or you can't tell whose move it is, it is `session`,
and the note says what to check and when.

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
