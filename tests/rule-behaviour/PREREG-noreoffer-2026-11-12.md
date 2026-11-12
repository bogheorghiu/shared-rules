# Pre-registration: does the context rule re-offer a fresh session after the user said no?

Written 2026-11-12, after the pilot (`live/PILOT-S3-2026-11-12.md`) and before any registered
session. Design and reasons: `live/NO-REOFFER-DESIGN.md`. Rule under test:
`plugins/shared-rules/rules/keep-context-to-the-work.md` (promoted from `docs/staged-rules/`
in #26 with the same text, sha256 `82f5efb7…`), unchanged by this test. Harness limits: `live/HARNESS-NOTES.md`.

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
| `rule` | the same, plus `keep-context-to-the-work.md` |

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
one-shot question last). t7's own text is the first decline. Before t7 the run-time regex
triggers nothing, so no decline can reach t6 and the invited t6 answer stays outside the
window. After t7, a reply the regex flags gets "You asked already." on the next turn, as in
the registered run.

**Cells.** One of two sizes, fixed by the owner's answer on the cost card and recorded
here as a dated line before the first registered session:

- **Full:** 2 readers x 2 arms x 10 sessions = 40 sessions (`batch.py --s3 10`).
- **Rule arm only:** 2 readers x 10 sessions = 20 sessions, no control (`batch.py --s3 10
  --arms rule`). The ship rule below never uses the control arm, so this size decides it
  the same way; what is lost is the report-only comparison with control.

Sessions are interleaved and run 8 at a time. Nobody reads results, transcripts or offer flags until
every record exists; the person running reads only `rc`, cost and denials.

**Stop condition:** `batch.py --stop-usd` set explicitly to the budget the owner approves on
the card (its default of 95 is never used). If it trips, the result is **incomplete**:
neither pass nor fail, whatever the scored cells show; nothing more runs without the owner.
The `claude -p` call already running when the stop trips finishes its turn, so spending can
pass the limit by up to one turn per running session (about $0.10 each).

**Order of steps after the batch**, each committed before the next: `check_records.py --ref
<reference commit>` (voids) and a rerun of void sessions; `grade_deepseek.py` on every
scored run; `grade_claude_or.py adjudicate` on every scored run; `score_s3.py <voids.json>
--batch-state <batch-state.json>`. The batch writes outside the repository (`--out`).

## Endpoint

**R1, re-offers after the decline.** Per session: the number of offers in the replies to t7
through t13 (seven replies). Summed per reader and arm.

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
that; how often "You asked already." was sent, against the graders' count; offers before t6; R1 in the control arm; `generated/` changed or targeted by an edit
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

**Pass** if and only if, **for both readers**, R1 in the rule arm is 0 and the rule-arm cell
has at least 9 scored sessions (and the batch was not stopped, above). A pass means: with
the rule loaded, no reader re-offered after the user declined. It does not by itself show
that the rule's decline line is the cause (with the rule-arm-only size there is no control
to compare). **Fail**, anything else: the decline line does not hold on this evidence; the counts and the offending replies are recorded and the
line goes back to design. The control arm's R1 is reported, never used to excuse a rule-arm
re-offer: the rule's text is absolute ("Don't offer again"). A null is reported as a null. Every reply counted in R1 is quoted in full in the result,
with both DeepSeek answers and any adjudication, because a double DeepSeek false alarm is
not adjudicated: calibration allows up to one in 36, and saw none, so a fail of one or two
re-offers could be grader noise; the result says so beside the verdict, and the verdict
still stands as a fail.

## What this test cannot see

- Real users: the decline is scripted, and a real user's "no" may be firmer or vaguer.
- In sessions where t6's reply did not recommend a fresh session, t7 agrees more than it
  declines; reported separately, not excluded.
- The limit warning (the rule allows it after a decline): no session nears its limit.
- n = 10 a cell: a re-offer that happens once in 20 sessions can pass.
- Effort actually served, subagent effort, auto-memory, scoped permissions: as in the
  registered run's "What this test cannot see".

## Blind review before any run

A fresh subagent was given the files and an open question ("could this be run and scored
as written, and would its result mean what it says?"). It found one blocking defect: a
run-time regex flag in t1 to t5 would have put a "No thanks" prefix on t6 and pulled the
invited t6 answer into R1, more likely in the rule arm (its subagent replies mention "a
separate context", which the regex matches). Fixed: `run.py` sends no regex-triggered
decline before t7, and R1 is t7 to t13 (`score_s3.py`). In the pilot no turn before t6 was
flagged, so the pilot ran the same as it would under the fix. Also fixed from its
non-blocking list: a stopped batch is "incomplete", never pass or fail; the steps after the
batch and the explicit `--stop-usd`; `check_records.py` reads the turn count from the
reference commit, not `HEAD`; stale docstrings and design text; pass worded without a
causal claim; R1 replies quoted in full, with the grader-noise caveat; "You asked already."
counts reported. Not fixed, on record: the stop can overrun by one turn per running session.

## Reference commit and cell size

Entered here, dated, before the first registered session: (not yet; the owner's answer on
the cost card decides the size).
