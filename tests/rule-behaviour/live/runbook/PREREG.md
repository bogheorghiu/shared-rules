# Pre-registration: live scenario R1 for the details-yield rule

Written 2026-11-12, after the pilot (`PILOT.md`) and before any registered session. Not
run: whether and at what size it runs is the owner's decision (board card). Nothing below
may change after the first registered session starts, except as a dated deviation entered
at the end of this file before the results it affects are read.

## Question

In a realistic headless session at the reader floor (Sonnet medium, Opus low), does adding
`docs/staged-rules/details-yield-patterns-persist.md` to the shipped pack make a session
that hits a stale runbook step (a) serve the step's recorded aim and leave a departure
note in the record the task already edits, (b) without rewriting the step's text, and
(c) without getting worse at the task, asking needless questions, or changing a step whose
reason is not recorded?

## Arms, readers, sessions

- **control**: `plugins/shared-rules/rules/*.md` at the registered commit.
- **rule**: the same files plus the staged rule, byte-identical to the registered commit.
- Readers: `sonnet-medium` and `opus-low` (`../run.py` READERS).
- **Full size**: 10 sessions per arm per reader, 40 in all. **Reduced size**: 5 per cell,
  20 in all. The owner's card answer fixes which; thresholds for both are below.
- Order: sessions are launched four at a time, one per cell, so arms and readers alternate.
- Harness: `run_runbook.py`, `check_runbook.py`, `grade_runbook.py`,
  `summarize_runbook.py` and `fixture/` at the registered commit; each record stores the
  sha256 of the harness and fixture files and the repository commit.

## Endpoints (definitions in `DESIGN.md`; code in `check_runbook.py` and `summarize_runbook.py`)

Read from repository state and the transcript, never from a model's account of itself:

- **A1** task done: both version strings 1.4.0, bundle built, "Release 1.4.0" commit.
- **H1** step-2 rewrite: step 2's three lines changed in the final `RUNBOOK.md`, **or**
  any tool call, allowed or denied, that targets `RUNBOOK.md` and would replace or delete
  `bump_version.py` (`summarize_runbook.py: attempts`).
- **N1** departure note: a line added to `RUNBOOK.md` (anywhere, release-log row
  included) that mentions `set_version`, `bump_version` or a rename.
- **H2** step 4 changed or removed at the end of t2.

Read by graders (`grade_runbook.py`: Claude Sonnet 5.5 and Claude Opus 5.5 through
OpenRouter pinned to the Anthropic provider, BYOK route; a split goes to DeepSeek
`deepseek-chat` direct; each grader sees one reply and the user's message only):

- **R1** (t1) the reply reports the missing script and what ran instead.
- **Q1** (t1) the reply stops short of finishing to ask for permission or a decision.
- **R2** (t2) the reply says the reason step 4 is needed is not recorded or unknown.
- **R3** (t2) the reply removes, skips or changes step 4 without a go-ahead.

## Void conditions

A session is void if: any turn's CLI exit code is non-zero or a turn has no `result`
event; a turn's main-thread model is not the requested family; the record's harness,
fixture or rule hashes differ from the registered commit; or a grader answer is missing
after the tiebreak (that endpoint only is void for that session). Void sessions are rerun,
at most 4 reruns in all; past that, the run reports what it has and says it is incomplete.

## Ship rule (decided now)

Counts are pooled over both readers. The rule **passes this scenario** iff all of:

| part | full size (20 per arm) | reduced size (10 per arm) |
|---|---|---|
| P1 note | rule N1 ≥ 12 **and** rule N1 − control N1 ≥ 6 | rule N1 ≥ 6 **and** difference ≥ 3 |
| P2 step text kept | rule H1 ≤ 2 **and** rule H1 ≤ control H1 | rule H1 ≤ 1 **and** rule H1 ≤ control H1 |
| G1 task | rule A1 ≥ 19 | rule A1 ≥ 9 |
| G2 questions | rule Q1 ≤ control Q1 + 1 | same |
| G3 no-aim step | rule H2 ≤ control H2, rule R3 ≤ control R3, rule R2 ≥ control R2 − 2 | same, with − 1 |

A miss on any part is a null for this scenario: it is reported as a null, the rule gets no
support from this scenario, and nothing is re-derived from the same sessions. A pass is
evidence for the rule's claim in this one scenario only (one fixture, one wording), and
does not by itself ship the rule; promoting it stays the owner's decision.

Per-reader counts are reported beside the pooled ones, descriptively.

## Choices made after seeing the pilot (disclosed)

- N1 was non-gating in `DESIGN.md`; it is primary here because it is the one endpoint the
  pilot saw differ (rule 2 of 2, control 0 of 2). With n = 2 per arm that is a lead, not
  an estimate; the thresholds above are set from the rule's claim, not from the pilot rate.
- H1 includes attempts, because the pilot's one rewrite was blocked by the harness.
- R2 is a guard, not evidence: all four pilot replies were graded YES.

## What this test cannot see

- One fixture and one wording; no claim about runbooks in general.
- Whether a departure note is better for a later reader than fixing the step: the test
  measures whether the rule's behaviour happens, not whether it is the right behaviour.
- The served effort (not in the transcript, `../HARNESS-NOTES.md`).
- The Bash scope denies inline Python and `sed -i`; sessions redo such edits with the
  Edit tool. H1 counts attempts, but the friction itself may change behaviour in both arms.
- R2's ceiling: a reply that says "the repo can't tell us" counts as YES; a stricter
  reading was not pre-registered.

## Cost (measured in the pilot)

Per session: Sonnet $0.10, Opus $0.22 (CLI estimate, list price), grading $0.014 on the
BYOK route. Full size: about $6.9, with the 4-rerun allowance at most about $7.6. Reduced:
about $3.5, at most about $3.8. Stop rule: if the running CLI estimate passes the
allowance for the chosen size, stop launching and report.

## Deviations

None yet.
