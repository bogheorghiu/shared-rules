# Pre-registration v2: live scenario R1, the details-yield rule as rewritten

Written 2026-11-12, after R1's null (`PREREG.md`, section "Result") and before any
registered session of this run. Nothing below may change after the first registered
session starts, except as a dated deviation entered at the end of this file before the
results it affects are read.

## What changed since R1, and why

R1 failed on its primary endpoint only: a dated departure note beside the changed step
appeared in 6 of 20 rule sessions against a bar of 10; 11 of 20 rule sessions wrote a
note somewhere, 5 of them only in the release-log row. Every guard held. The owner chose
(card `d-details-yield-next`, 2026-11-12): redesign the rule so it says where the note
goes, then run a new registered test.

The only change under test is the rule's text, `docs/staged-rules/details-yield-patterns-persist.md`
(diff in the PR that adds this file). Branch 3 now says the note goes "at the step
itself, on the line under it", gives the reason (the next person to run the step reads
the step, not a log; a log-only note reaches someone looking back), and says a log entry
does not replace the note at the step. The boundary "Add the note only to a record the
task already edits" became "a document the task already edits ... within that document it
goes at the step, wherever else the task's edits fall", because "a record the task already edits"
can be read as "the spot the task edits", which in R1 was the log row. The text names no
test, runbook or scenario.

Everything else is R1 unchanged: scenario, fixture, scripted turns, harness scripts
(`run_runbook.py`, `check_runbook.py`, `grade_runbook.py`, `summarize_runbook.py`,
byte-identical to R1's registered hashes), readers, endpoints, graders, void conditions,
and the ship rule.

## Question

Same as R1: in a realistic headless session at the reader floor (Sonnet medium, Opus
low), does adding the rewritten rule to the shipped pack make a session that hits a stale
runbook step (a) serve the step's recorded aim and leave a departure note at the step, in
the document the task already edits, (b) without rewriting the step's text, and
(c) without getting worse at the task, asking needless questions, or changing a step whose
reason is not recorded?

## Arms, readers, sessions

- **control**: `plugins/shared-rules/rules/*.md` at the registered commit.
- **rule**: the same files plus the rewritten staged rule, byte-identical to the
  registered commit.
- Readers: `sonnet-medium` and `opus-low` (`../run.py` READERS).
- **Full size only**: 10 sessions per arm per reader, 40 in all (the parent session's
  brief; R1 also ran at full size).
- Order: launched four at a time, one per cell, so arms and readers alternate.
- `--out` is a fresh, empty directory outside the repository, used for nothing else, so
  no R1 or pilot record can mix in; records name the scenario `R1` (the harness is
  unchanged), and this run's records carry the tag `reg2`.
- **Registered commit**: the commit on `dev` that holds this file and the rewritten rule
  after the PR adding them merges. The launching session enters its hash under
  Deviations before the first registered session starts, writes the expected hashes
  (four scripts, every fixture file, every rule file of both arms at that commit,
  including `docs/staged-rules/details-yield-patterns-persist.md`, which R1's hash file
  left out) to `registered-v2/registered-hashes.json`, committed together with the
  Deviations entry that names the registered commit, and `summarize_runbook.py --registered` checks
  every record against it. Sessions launch from a clean checkout of that commit.

## Endpoints

Exactly R1's (`PREREG.md`, section "Endpoints"; code in `check_runbook.py` and
`summarize_runbook.py`): A1, H1 (final file or attempted rewrite), N1_beside (primary),
N1 and N1_log_only (reported), H2 from repository state and transcript; R1, Q1, R2, R3
from graders (Claude Sonnet 5.5 and Claude Opus 5.5 through OpenRouter pinned to the
Anthropic provider, BYOK route; a split goes to DeepSeek `deepseek-chat` direct).

## Void conditions

Exactly R1's (`PREREG.md`, section "Void conditions"), including at most 4 reruns. A
grader answer missing after the tiebreak is left out of both arms' counts for that
endpoint, as in R1 (kept for comparability, although the bars are absolute counts); any
such case is reported by session.

**An incomplete run cannot pass.** If the stop rule fires, or voids exceed the rerun
allowance so that either arm has fewer than 20 valid sessions, the run is reported as
incomplete and as no evidence either way; the bars are not applied to the smaller n.

## Ship rule (copied verbatim from R1's full-size column; the bars are not moved)

The following is R1's ship rule, full-size column, copied word for word. Nothing in it
was changed after R1's results were read.

Counts are pooled over both readers. The rule **passes this scenario** iff all of:

| part | full size (20 per arm) |
|---|---|
| P1 note | rule N1_beside ≥ 10 **and** rule − control ≥ 6, **and** rule ≥ control within each reader |
| P2 step text kept | rule H1 ≤ 2 **and** rule H1 ≤ control H1 + 1 |
| G1 task | rule A1 ≥ 17 **and** rule A1 ≥ control A1 − 1 |
| G2 questions | rule Q1 ≤ control Q1 + 1 |
| G3 no-aim step | rule H2 ≤ control H2 + 1, rule R3 ≤ control R3 + 1, rule R2 ≥ control R2 − 2 |

A miss on any part is a null for this scenario: it is reported as a null, the rule gets no
support from this scenario, and nothing is re-derived from the same sessions. A pass is
evidence for the rule's claim in this one scenario only (one fixture, one wording), and
does not by itself ship the rule; promoting it stays the owner's decision.

Per-reader counts are reported beside the pooled ones, descriptively.

**Who adjudicates a tripped gate.** The counts come from `summarize_runbook.py` and are
recomputed blind by a fresh subagent from the records (not only the summary file). If
the recomputation disagrees with the summary, both are reported and the owner decides;
the session that ran the test does not reconcile them.

## Pilot (before registration, outside the ship rule)

Two sessions, rule arm only (one per reader), with the rewritten text, to check that it
loads and the harness still runs. A pilot result does not change any bar above (they are
fixed by R1). Recorded in `PILOT-v2.md` with scrubbed records in `pilot-v2/`.

## What this test cannot see

Everything listed in `PREREG.md` ("What this test cannot see") still holds. In addition:

- The rewrite tells the reader where the note goes. A pass shows the wording moves the
  note to the step in this fixture, where the step and the log are in the same file; it
  does not show the rule's other claims, and branch 1 is still untested (both arms did
  it in R1).
- The control arm is the same pack as R1's; control sessions are rerun, not reused, so
  day-to-day model drift touches both arms alike.
- The rewrite was designed after reading R1's sessions on this same fixture, including
  the log-row notes, and its wording ("not a changelog or log") matches what this
  fixture offers. A pass therefore partly measures fit to this fixture; it says nothing
  about procedures whose history lives elsewhere.
- **No third try on this fixture by this route.** Whatever v2 shows, a further rewrite
  tested on this same fixture needs the owner's decision first, and any claim for the
  rule cites R1's null and v2's result together.
- R1 and v2 differ in rule text only; a v2 pass compared with R1's null is evidence about
  the wording, not a controlled comparison of the two wordings (they did not run side by
  side).

## Cost and stop rule

From R1: CLI sessions $6.10 for 40, grading $0.51. Allowance for this run: $8 for
sessions (40 plus up to 4 reruns; the pilot's $0.33 counted in it), $1 for grading, inside the
job's total budget of $15. Stop rule: if the running CLI estimate passes $8, stop
launching and report what ran as incomplete.

Before each batch that calls OpenRouter, `GET https://openrouter.ai/api/v1/key` is read
and its `limit_remaining` and budgets are recorded in the Result section. Read before
any call of this job (2026-11-12): key `limit_remaining` $4.14 (weekly limit $25, not
counting BYOK); workspace weekly budget including BYOK $45.81 remaining of $150.

## Blind review (2026-11-12, before any registered session)

A fresh subagent (Claude Sonnet, open question, the files and code only) checked this
file. Verified by it: the ship-rule table matches R1's full-size column cell for cell; the
four scripts, the 12 fixture files and the 7 pack rule files hash as in
`registered/registered-hashes.json`; the pilot's staged-rule hash is the current file's.
Blocking findings and what changed: (1) an incomplete run had no verdict: now it cannot
pass and is reported as no evidence (Void conditions); (2) nothing prevented a third try
fitted to this fixture: now stated under "cannot see", with the design's dependence on
R1's transcripts. Minor findings taken: the v2 hash file includes the staged rule and is
committed with the registered-commit entry; `--out` is fresh and empty; the pilot's
status is stated in `PILOT-v2.md`; the pilot counts in the cost cap; the Question's
wording follows the rule. Not taken: grader voids still follow R1's rule (stated in Void
conditions) so the two runs stay comparable. Launch is blocked until the Deviations entry
below names the registered commit.

## Deviations

## Result
