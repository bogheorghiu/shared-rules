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

- `owner`: one thing I can do today, with nothing else having to happen
  first, and the note says what it is: sign this, merge that, answer
  this question between these choices.
- `session`: a Claude session working in this repo holds the card. That
  is work in progress, and also every card nobody can move yet: the
  session keeps it, and the note says what it waits for and when to
  look again.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has exactly one, and `owner` is never the default: a
card that is not plainly `owner` or `ext` by the lines above is
`session`, and so is one whose move you can't tell. That covers a card
that waits for my answer on another card (the question is on my list
once, on its own card, and the note names it), a card where nobody has
worked out the next move (working it out is the session's move; a
choice only I can make comes back as a question with its options), and
a card that waits for a date, a running job, a condition, a result or
anything I have put off. A card I took off my list goes back only when
it passes the `owner` line again, not because its note was updated.

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
