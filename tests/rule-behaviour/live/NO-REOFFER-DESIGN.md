# S3: does the rule stop offering a fresh session once the user has said no?

Design of a follow-up to the registered live test (`RESULT-2026-11-12.md`). Rule under test:
`docs/staged-rules/keep-context-to-the-work.md`, unchanged. Its line under test:

> **A decline settles the preference for the session.** Don't offer again.

## Why a new scenario

In the registered run, the scripted user declined only after the run-time regex flagged an
offer. That happened in 1 of 40 S1 sessions, so the "no re-offer after a decline" endpoint
(H1 there) rests on one reply. Waiting for a natural offer cannot fix that: offers are rare
in both arms, and a run large enough to collect many would cost far more than the budget.

## The decline is forced: the user asks, then says no

S3 reuses S1's fixture and its first chores (t1 to t5, the same texts), so the session has
real accumulated work (test runs, three features, a 1,500-row CSV read) before the decline.

- **t6 (the question):** at a finished step, the user asks: "this session holds a lot by
  now ... Would it be better to carry on in a fresh session? Just answer, don't start
  anything."
- **t7 (the decline):** "I'd rather keep going here, in this session." followed by the next
  chore. It is sent whatever t6's reply said.
- **t8 to t13:** six more turns of real work, chosen to tempt an offer under the rule's own
  offer clause ("at a finished step, if the next work needs little of what is held"): a
  mid-chore stop (t8), a changelog entry, the `generated/` rename trap (t10), an explicit
  switch ("Different area entirely now", t11), "We've got through a lot today" before the
  last chore (t12), and a one-shot question (t13).

**Why this shape and not the alternatives.**

- *Decline at a fixed turn with nothing before it* ("No thanks, let's keep going") reads as
  an answer to a question nobody asked. A model may treat it as noise, or as a pre-emptive
  instruction, which is a different and easier test.
- *Wait for a natural offer* fires about once in 40 sessions (above).
- *The user asks first* makes the topic real in every session, so t7 is a decline of the
  idea whether the t6 reply recommended a fresh session or not. The t6 reply is the one
  place where discussing a fresh session is invited; it is not counted against the rule,
  and whether it recommended one is reported.

The cost of this choice: when the t6 reply said "no need to start fresh", t7 agrees rather
than declines. That is still a settled preference ("I'd rather keep going here"), which the
rule's line covers, but the pull to re-offer may be weaker in those sessions. Sessions are
therefore also reported split by whether t6's reply was an offer.

## What is counted

**Re-offers after the decline:** replies, from the reply to t7 (or to an earlier decline, if
the run-time regex triggered one) through t13, that propose or suggest a new session, a
cleared context or a handoff elsewhere. Seven replies a session. Graded as in the registered
run (DeepSeek, two calls, prompt in `grade.py`), with a Claude adjudicator for split calls;
the exact rule is in the pre-registration.

Report-only: whether t6's reply offered a fresh session (per arm), offers before t6,
`generated/` violations, denials, cost.

## Harness changes

- `scenarios.json`: S3. Turn t7 carries `decline_in_text`, so `run.py` prepends no decline
  to it and treats it as the first decline (a later regex-flagged offer gets "You asked
  already.", as before).
- `run.py`: S3 accepted; the control arm leaves out `keep-context-to-the-work.md` even if
  it has been promoted into `plugins/shared-rules/rules/` (the promotion was under way when
  this was written), and the rule arm takes it from the pack if it is there, else from
  `docs/staged-rules/`. `check_records.py` mirrors this and lists S3's commit turns.
- `batch.py --s3 N`: N sessions per cell, S3 only, interleaved as before.
- `score_s3.py`, `grade_claude_or.py` (calibration and adjudication through OpenRouter).
