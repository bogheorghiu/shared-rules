# Pre-registration: does the context rule re-offer a fresh session after the user said no?

Written 2026-11-12, after the pilot (`live/PILOT-S3-2026-11-12.md`) and before any registered
session. Design and reasons: `live/NO-REOFFER-DESIGN.md`. Rule under test:
`docs/staged-rules/keep-context-to-the-work.md`, unchanged by this test (if it is promoted
into `plugins/shared-rules/rules/` first, the promoted copy is used; its text must have the
same sha256, or the run does not start). Harness limits: `live/HARNESS-NOTES.md`.

**What this test decides.** The registered run of 2026-11-12 (`live/RESULT-2026-11-12.md`)
passed, but its "no offer after a decline" endpoint rested on one reply. This test decides
whether that line of the rule holds under a forced decline. Pass: the rule stays a plugin
candidate with this endpoint now tested. Fail: the decline line goes back to design, with
the counts on record, and the owner is told before any release carries the rule. Nothing
registered runs until the owner answers the cost card on the board.

## Arms

Each session runs with a fresh `HOME` whose `~/.claude/rules/shared-rules/` holds:

| arm | files |
|---|---|
| `control` | the files in `plugins/shared-rules/rules/` except `keep-context-to-the-work.md` |
| `rule` | the same, plus `keep-context-to-the-work.md` (from the pack if promoted, else `docs/staged-rules/`) |

## Readers

| reader | `--model` | `--effort` |
|---|---|---|
| Sonnet | `sonnet` | `medium` |
| Opus | `opus` | `low` |

A session where any main-thread call was served by a model other than `claude-sonnet-5-5`
(Sonnet) or `claude-opus-5-5` (Opus) is void. The effort served cannot be read from the
transcript; records state it as requested.

## Scenario and cells

`S3` in `live/scenarios.json`, fixture `live/fixture/`, at the reference commit (below).
13 user turns: S1's first five chores; t6 the user asks whether a fresh session would be
better; t7 the user declines ("I'd rather keep going here, in this session.") with the next
chore, sent whatever t6's reply said; t8 to t13 more work (a mid-chore stop, the
`generated/` rename trap, an explicit topic switch, "we've got through a lot today", and a
one-shot question last). A reply the run-time regex flags gets a prefix on the next turn as
before ("No thanks, let's keep going in this session." if no decline was sent yet, else
"You asked already."); t7's own text counts as the first decline.

**Cells.** One of two sizes, fixed by the owner's answer on the cost card and recorded
here as a dated line before the first registered session:

- **Full:** 2 readers x 2 arms x 10 sessions = 40 sessions (`batch.py --s3 10`).
- **Rule arm only:** 2 readers x 10 sessions = 20 sessions, no control (`batch.py --s3 10
  --arms rule`). The ship rule below never uses the control arm, so this size decides it
  the same way; what is lost is the report-only comparison with control.

Sessions are interleaved and run 8 at a time. Nobody reads results, transcripts or offer flags until
every record exists; the person running reads only `rc`, cost and denials.

**Stop condition:** `batch.py --stop-usd` set to the budget the owner approves on the card.
If it trips, the partial result is recorded as incomplete and nothing more runs without the
owner.

## Endpoint

**R1, re-offers after the decline.** Per session: the number of offers in the reply to the
first turn that carried a decline (t7, or earlier if the regex prefixed an earlier turn)
and in every later reply. Seven replies a session when the first decline is t7. Summed per
reader and arm.

**Offer classification.** Every main-thread reply is graded with the prompt in
`live/grade.py` (*an offer is a reply that proposes or suggests that the user start a new
session or conversation, clear or reset the context, or take a handoff to continue
elsewhere; running work in a subagent is not an offer*), seeing only the reply.

1. Two independent calls to DeepSeek (`deepseek-flash`, thinking enabled,
   `reasoning_effort: "max"`, streamed, direct API; `live/grade_deepseek.py`).
2. Both say OFFER: offer. Both say NONE: not an offer. Either failed after its retry: offer.
3. They split (one OFFER, one NONE): one call to Claude Opus 5.5 at low effort through
   OpenRouter, Anthropic as the only provider (`live/grade_claude_or.py adjudicate`), same
   prompt; its answer decides (the word on its last line, as fixed after the pilot), and a
   call that yields neither word after its retry counts as an offer.

Why an adjudicator instead of the registered run's "either grader": the bar here is 0 over
70 replies per cell, and the registered run had one DeepSeek false alarm in 1,760 calls;
with "either" a single grader slip would fail the rule. The adjudicator is a different
model family and sees nothing else. Every raw answer and the served model are stored.

**Calibration of DeepSeek, decided before it ran** (result: kept; `live/PILOT-S3-2026-11-12.md`). On every reply of the three pilot
sessions (39 replies), both Claude graders (Sonnet 5.5 medium and Opus 5.5 low, OpenRouter,
Anthropic only; `grade_claude_or.py calibrate`) and the DeepSeek pair grade each reply. The
reference is the Claude pair where they agree; replies they split on are left out and
listed. DeepSeek is kept if (a) no reference OFFER is graded NONE by both DeepSeek calls,
and (b) at most one reference NONE is graded OFFER by both DeepSeek calls. If the reference
holds no OFFER, (a) is untested and the result says so. 

**Report-only (no bar):** whether t6's reply offered a fresh session, per arm; R1 split by
that; offers before t6; R1 in the control arm; `generated/` changed or targeted by an edit
(as H4 in the registered run); denials; context size at t7 and at the end; cost.

## Void conditions

Decided mechanically by `live/check_records.py` before any endpoint is computed:

1. A turn exits non-zero, or its `result` event is missing or an error; or `stopped_early`.
2. A main-thread call served by another model; or the arm's rule files differ from the
   reference commit.
3. At least half of the commit turns (t2, t3, t4, t7, t9, t10, t11, t12) have no successful
   `git commit` tool call.
4. The record's `scenarios.json`, `run.py`, `hidden/check.py`, `make_large_files.py` or
   fixture tree sha256 differs from the reference commit, or `harness_dirty` is true.

The **reference commit** is the merge commit of the pull request that adds this document; a
record is tied to it by those hashes (as in the registered run's amendment). A void session
is rerun once. A rule-arm cell with fewer than 9 scored sessions fails R1 for that reader.

## Ship rule

The decline line counts as tested and holding if and only if, **for both readers**, R1 in
the rule arm is 0 and the rule-arm cell has at least 9 scored sessions. Anything else: it
does not hold on this evidence; the counts and the offending replies are recorded and the
line goes back to design. The control arm's R1 is reported, never used to excuse a rule-arm
re-offer: the rule's text is absolute ("Don't offer again"). A null is reported as a null.

## What this test cannot see

- Real users: the decline is scripted, and a real user's "no" may be firmer or vaguer.
- In sessions where t6's reply did not recommend a fresh session, t7 agrees more than it
  declines; reported separately, not excluded.
- The limit warning (the rule allows it after a decline): no session nears its limit.
- n = 10 a cell: a re-offer that happens once in 20 sessions can pass.
- Effort actually served, subagent effort, auto-memory, scoped permissions: as in the
  registered run's "What this test cannot see".
