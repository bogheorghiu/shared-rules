=== W1 REFERENCE START ===
# Status protocol

How sessions and I keep `data/status.csv`, the list of everything open on
the desk.

## Purpose

I filter `data/status.csv` to `waits_on = owner` and do those things.
Everything on that list must be something I can do now, and everything
open must be somebody's.

That filtered list is the only part of the file I read, and I read it to
act. A card I can't act on costs me a look every time I open the list, and
it sits there for days because looking at it changes nothing. So a card
being stuck or unclear is not a reason to give it to me. It is a reason
for a session to do the work that turns it into something I can act on.

## States

Each row is one card. The columns:

- `card`: the card's id.
- `state`: `open` while anything is left to do, `done` when nothing is.
- `waits_on`: whose move it is.
- `note`: one line on what happened last and what comes next.

`waits_on` takes one of three values:

- `owner`: the move is mine and I can make it now. The test is under
  "My list" below.
- `session`: the move belongs to a Claude session working in this repo.
  This includes cards where nobody has worked out the next step yet, and
  cards that are blocked on another card.
- `ext`: the move belongs to someone outside the desk, such as a
  supplier, a printer or a member, and the note names them.

Every open card has one. If you can't tell whose move it is, it's the
session's, and the move is to work out what the next step is.

A `done` card has an empty `waits_on`.

## My list

Set `waits_on` to `owner` only when all three of these hold:

1. The next move needs me: my decision, my signature, my approval, or
   access only I have.
2. I can make that move now. Nothing else has to happen first.
3. The note says exactly what the move is. That is either the question
   with the options to choose between, or the action to take, plus where
   the material is.

Notes like these pass:

- `postage account form is filled in: sign it (shared/forms)`
- `owner to answer: keep the letters page at two pages or cut it to one`
- `printer has not replied since 20 Oct: choose between phoning them / moving the job to another printer / dropping it (options in shared/reprint.md)`

Three kinds of card have been landing on my list and don't belong there.

**A card waiting on another card.** If a card can't move until a question
on another card is answered, only the question card goes on my list. The
waiting card is `session`, and its note starts `blocked on c-NN:` followed
by what happens once c-NN is settled. For example:
`blocked on c-19: layout is drafted; drop in the chosen cover and send to proof`.
A question should appear on my list once, however many cards hang on it.
The same goes for a card blocked on an `ext` or `session` card. A blocked
card needs nothing from anyone until its blocker is settled.

**A card where nobody knows the next step.** Sometimes an outside party
has gone quiet, or something came up at a meeting and nobody said what it
should be. I don't know the next step either, so the card is `session`.
The session's move is to work out the options, do whatever can be done
from inside the repo (a draft, a comparison, a proposal), and then bring
it to me as a question I can answer or an action I can take. If the
missing piece is a fact only I have, or a call only I can make to someone
outside, ask for exactly that. A specific question or a named person to
contact with what to ask them passes the test.

**A card I moved off my list.** If I've moved a card off, I couldn't act
on it as written. It comes back only with something new that passes the
test. Updating or rewording the note is not that. In general, when you
update a card, change `waits_on` only if the event changed whose move it
is.

## Updating

When something happens to a card:

1. Find the card's row by its id. If the card is new, add a row at the
   end with the next free id.
2. Set `state`. A card stays `open` until nothing is left to do on it.
3. Set `waits_on` to whoever has the next move, using the values under
   States. Before setting `owner`, check the card against the three
   conditions under My list. If it fails any of them, it is `session`.
4. Rewrite `note` in one line: what happened last, then what the next
   move is. For an `owner` card the next move is the question or action
   itself. For a blocked card the note starts `blocked on c-NN:`. For an
   `ext` card it names who we are waiting for. Keep commas out of the
   note, or quote it.
5. If the event settled the card (I answered, the thing arrived, the work
   finished), search the notes for the card's id and update every card
   blocked on it. Each one loses its `blocked on` prefix and gets its real
   next move and `waits_on`.
6. Run `scripts/check_status.py`, which must print `OK`, then commit
   `data/status.csv` on its own, with a message that names the card ids.
   The script checks only the header and the ids. `OK` does not mean
   `waits_on` is right, so step 3 is yours to get right.

Update only the cards the event is about. If an event touches several
cards, update each one.

There is one exception. Whenever you edit the file, read the `owner` rows.
If an open one fails the test under My list, or a card is still marked
`blocked on` a card that is now `done`, fix it in the same commit and name
it in the message.

## Fixed

The owner's page and the history depend on these:

- The header is `card,state,waits_on,note`. The owner's page parses
  these four columns.
- Rows are never deleted. A finished card is marked `done`.
- Card ids never change, and a new card never reuses an old id.
=== W1 REFERENCE END ===

Nothing is committed yet: I couldn't run commands in this session, so the file above still needs committing and the pre-commit hook hasn't run on it (both headings it requires are there).

**What I changed**
- **Default flipped.** "If you can't tell whose move it is, it's the owner's" was the source of c-05 and c-23. It is now the session's, and the move is to work out the next step.
- **Test for your list.** A card is `owner` only if it needs you, you can do it now, and the note states the exact question or action.
- **Blocked cards.** A card waiting on another card (c-20, c-25) is `session` with a note starting `blocked on c-NN:`. Whoever settles the blocker unblocks the cards that name it.
- **Cards you moved off.** They come back only with something new that passes the test; rewording the note doesn't count (the c-05 return on the 12th).
- **Sweep.** Any session editing the file also fixes `owner` rows that fail the test.

**What I left**
- **`waits_on` values.** I kept the three existing values instead of adding a "blocked" one, because your page parses that column and I couldn't check how it handles a new value. The cost is that blocked cards sit in the `session` rows.
- **Fixed section.** It is unchanged.
- **`data/status.csv`.** c-05, c-20, c-23, c-25 and c-29 are still on your list. c-29 has the same problem as c-25 but isn't in the incidents yet. The sweep rule means the next session to edit the file should move them.
- **`scripts/check_status.py`.** It still checks only the header and ids, so nothing mechanical enforces the new rules. Say if you want it to reject `owner` rows whose note says `blocked on` or waits on another card.