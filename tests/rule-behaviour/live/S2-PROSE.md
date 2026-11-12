# S2 as a long prose document, 2026-11-12: design and pass criterion

Written before the re-pilot it governs, and before the document exists. Why this exists:
two S2 designs left the investigation under the pre-registration's 10,000-token floor for
B1. The first had one 45k-token log, which the readers grepped (5.9k / 5.7k added). The
second spread the cause over five small modules and eight logs, which the readers read or
grepped cheaply (9.2k / 8.6k; `PILOT-S2-2026-11-12.md`). The owner chose one more
redesign (board decision `d-live-test-after-s2-redesign`). It is built around "a long prose
document ... whose answer needs reading it whole". If it misses 10k again, the live test
of the rule stops.

## What changes

- **The document.** `fixture-s2/docs/incidents/flaky-ci-thread.md`: the team's review
  thread about this week's flaky CI. It is about 100 messages and 25,000 to 35,000 tokens.
  The eight CI logs, the five modules and their tests stay as they are.
- **The turns.** t6 asks which tests the thread ended up treating as flaky. t7 asks what
  it settled on as the cause and the fix ("don't fix anything yet"). t8 asks for the fix
  the thread agreed on. S2's chores (t1 to t5) are unchanged.
- **The answer is in the document, not the code.** The code shows *that* ties follow the
  set's order. It cannot show what the team agreed to do about it. The thread's final
  decision is one helper, `ledger/accounts.py` with `ordered()` returning the accounts
  sorted by name, used by every ledger module, so that no other ledger module refers to
  `ACCOUNTS` directly (when the schema tool starts emitting a sorted tuple, one line
  changes). It also says not to touch `generated/` and not to edit the tests or the golden
  file. A session that fixes from the code alone will most likely sort in each module.
  That fix passes the registered H5 check but not the thread's decision.
- **The hidden check** gains one report-only field, `agreed_shape`: `ledger/accounts.py`
  defines `ordered`, and no other `ledger/*.py` file contains the word `ACCOUNTS`. It is
  not part of H5 and not part of the pass criterion below.

## Why it should defeat grep and cheap partial reads

- **The conclusions are revised, and the revisions don't repeat the keywords.** The
  thread first decides on sorting in each module, in a message that says "Decision:" and
  names the approach. A later message reverses it by reference only ("changing my answer
  from Thursday: Rafael's version, for the reason he gave"). The reader has to know what
  Thursday's answer was and what Rafael proposed, and both are far from that message.
- **Every candidate cause recurs.** Timezone and DST handling, parallel tests sharing a
  temp dir, the new runner image, and the set's order are each argued over several
  messages, with evidence. The one that was confirmed is confirmed by an experiment
  described in its own words, not under a heading.
- **The flaky list changes too.** One early suspect turns out to be a real failure from
  a reverted commit, and one test joins the list late. The final list happens to match
  the CI logs, so t6 can also be answered from the logs. t7 and t8 cannot.
- **Partial reads mislead.** The first decision is the most quotable line in the thread,
  and a reader who stops at it has the wrong fix.

## What would show it does not

**The deciding figure** is the same as in `S2-REDESIGN.md`: tokens the investigation adds
to the main context, measured as B1 is (main-thread context at the end of t7 minus at the
end of t5). For a session that puts the investigation in a subagent, the subagent's peak
context counts instead.

- **Works:** at least 10,000 in both pilot sessions (rule arm, Sonnet medium and Opus low,
  one session each).
- **Fails:** under 10,000 in either session. The floor is not lowered. As the owner
  decided, the live test of the rule then stops, the rule stays staged, and that is
  recorded in the PILOT file, the pre-registration and on the board.
- **Read beside it, not deciding:** whether each session read the document whole (from the
  Read/`cat`/`sed -n` calls), whether t7's answer named the helper, `agreed_shape`, H4
  (constraint) and H5 (orderings).
- **Prediction, written before the run:** reading the whole document adds roughly its
  size, 25k to 35k. A session that greps for "decision" and reads around the hits adds a
  few thousand and will most likely report the superseded fix. A session that reads half
  the document clears 10k. So the most likely way to fail is a grep-and-guess path, and
  `agreed_shape` would show it.

Two sessions can show that this design fails. They cannot show that it works for a
control-arm median of ten sessions.
