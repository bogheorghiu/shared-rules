# S3: does the rule stop offering a fresh session once the user has said no?

Design of a follow-up to the registered live test (`RESULT-2026-11-12.md`). Rule under test:
`keep-context-to-the-work.md` (now in `plugins/shared-rules/rules/`), unchanged. Its line under test:

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

**Re-offers after the decline:** replies to t7 through t13 (the run-time regex sends no
decline before t7, so the invited t6 answer is never counted), that propose or suggest a new session, a
cleared context or a handoff elsewhere. Seven replies a session. Graded as in the registered
run (DeepSeek, two calls, prompt in `grade.py`), with a Claude adjudicator for split calls;
the exact rule is in the pre-registration.

Report-only: whether t6's reply offered a fresh session (per arm), offers before t6,
`generated/` violations, denials, cost.

## Harness changes

- `scenarios.json`: S3. Turn t7 carries `decline_in_text`, so `run.py` prepends no decline
  to it, sends no regex-triggered decline before it, and treats it as the first decline (a later regex-flagged offer gets "You asked
  already.", as before).
- `run.py`: S3 accepted. Which files each arm loads is `run.py`'s `arm_rules` as on `dev`
  after the rule's promotion (#26): control is the pack without `keep-context-to-the-work.md`,
  the rule arm adds it. `check_records.py` lists S3's commit turns.
- `batch.py --s3 N [--arms rule]`: N sessions per cell, S3 only, interleaved as before; `--arms` limits the arms.
- `score_s3.py`, `grade_claude_or.py` (calibration and adjudication through OpenRouter).
