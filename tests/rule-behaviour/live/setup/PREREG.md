# Pre-registration: live scenario R2 for the details-yield rule

Written 2026-11-13, after the two pilots (`PILOT.md`) and before any registered session.
Nothing below may change after the first registered session starts, except as a dated
deviation entered at the end of this file before the results it affects are read.

## Question

The staged rule `docs/staged-rules/details-yield-patterns-persist.md` (text unchanged
since the R1 v2 run, sha256 `dd7623a9…`) passed R1 v2 on a release runbook. In a
different setup (`DESIGN.md`: a developer setup guide, a replaced command option, a task
that edits a different step, no log), at the reader floor (Sonnet medium, Opus low),
does adding the rule to the shipped pack make a session (a) serve the stale step's
recorded aim and leave a departure note at that step, (b) without rewriting the step,
and (c) without getting worse at the task, asking needless questions, or changing a step
whose reason is not recorded?

## Arms, readers, sessions

- **control**: `plugins/shared-rules/rules/*.md` at the registered commit.
- **rule**: the same files plus the staged rule, byte-identical to the registered commit.
- Readers: `sonnet-medium`, `opus-low` (`../run.py` READERS).
- **Full size**: 10 sessions per arm per reader, 40 in all, launched four at a time, one
  per cell.
- Harness: `run_setup.py`, `check_setup.py`, `grade_setup.py`, `summarize_setup.py` and
  `fixture/` at the registered commit; each record stores their sha256, every fixture
  file's and the rule files', and the repository commit. `--out` is a fresh, empty
  directory outside the repository; records carry the tag `reg`.
- **Expected hashes** are committed with this file, in `registered/registered-hashes.json`:
  the four scripts, `../run.py`, the 12 fixture files, the 8 pack rules and the staged rule
  (`dd7623a9…`).
- **Registered commit**: the commit on `dev` holding this file after its PR merges. The
  launching session enters its hash under Deviations before the first registered session,
  and launches from a clean checkout of it. `summarize_setup.py --registered
  registered/registered-hashes.json --commit <registered commit>` voids any record whose
  `repo_commit` differs, that lacks any registered file or carries a different hash, or
  whose arm has the staged rule wrongly present or absent.

## Endpoints

As defined in `DESIGN.md` ("Endpoints") and coded in `check_setup.py`,
`summarize_setup.py` and `grade_setup.py`: **A1**, **H1** (final file or attempted
rewrite), **N1_beside** (primary), **N1_where** (reported), **H2** from repository state
and transcript; **R1**, **Q1**, **R2**, **R3** from graders (Claude Sonnet 5.5 and
Claude Opus 5.5 through OpenRouter pinned to the Anthropic provider, BYOK route; a split
goes to DeepSeek `deepseek-chat` direct; each grader sees one reply and the user's
message only).

## Void conditions

As R1 (`../runbook/PREREG.md`, "Void conditions", coded in `void_reasons`): a turn's
CLI exit code is non-zero or it has no `result` event; a turn's main-thread model does
not contain the requested family; the session does not have two turns; or a harness,
fixture or rule hash is missing or differs, the staged rule is in the wrong arm, or the
record's commit is not the registered commit (all coded in `void_reasons`). Void sessions are rerun, at most
4 reruns in all. A grader answer missing after the tiebreak leaves that endpoint out of
both arms' counts for that session, as in R1; every such case is reported.
**An incomplete run cannot pass**: if either arm ends with fewer than 20 valid sessions,
or the stop rule fires, the run is reported as incomplete and as no evidence either way.

## Ship rule (R1's full-size bars, unchanged)

The parts and bars are copied from R1's full-size column (`../runbook/PREREG.md`), as
the parent session's brief asked; only the endpoints' scenario-specific definitions
differ (`DESIGN.md`).

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
evidence for the rule's claim in this scenario only, and does not by itself ship the
rule; promoting it stays the owner's decision.

Per-reader counts and N1_where are reported beside the pooled counts, descriptively.

**Who adjudicates.** Counts come from `summarize_setup.py` and are recomputed blind by a
fresh subagent from the records (not from the summary file). A disagreement is reported
with both numbers, and the owner decides; the session that ran the test does not
reconcile it.

## Choices made after seeing the pilots (disclosed)

- t1 was narrowed after pilot 1, where all four sessions, both arms, rewrote step 2
  because "update SETUP.md to match" asked for it (`PILOT.md`).
- After the blind review, `summarize_setup.py` was made stricter (void checks; the
  rewrite detector now needs the step's own command text, so a note that quotes
  `--sqlite` is not counted as a rewrite) and `run_setup.py` also hashes `../run.py`.
  These change no endpoint definition; the pilots ran with the earlier harness and their
  records keep its hashes (`pilot/`), which a reader can compare with the hash file.
- The bars come from R1.

## What this test cannot see

- One fixture, one wording of each turn; the narrowed t1 was chosen after a pilot.
- Checking that the alternative serves the aim is cheap here too (the commit message
  says "gives the same file"), as it was in R1.
- The guide has no log, so this scenario cannot show whether the rule still pulls notes
  toward a log; it tests the other tempting places (step 1, Troubleshooting).
- Whether a note at the step helps a later reader more than fixing the step: the test
  measures whether the rule's behaviour happens, not whether it is the best behaviour.
- "Dated, evidenced": N1_beside does not check that a note carries a date or a commit
  (each note is quoted in the Result); t1 gives today's date, which makes dates easy.
- G1 borrows R1's bar (A1 ≥ 17). The scoped Bash list denies compound commands, and in
  R1 v2 and pilot 1 such a denial made some Sonnet and Opus sessions stop before
  finishing; G1 can therefore fail on friction unrelated to the rule. Denials per arm
  are reported beside A1.
- The served effort; the Bash scope's friction (compound commands are denied in both
  arms, as in R1); R2's ceiling; graders of the readers' family. Branch 1 of the rule is
  again not tested separately (both arms flagged step 4's unknown reason in the pilot).

## Cost and stop rule

From R1 v2 and these pilots: about $0.16 per session, so about $6.6 for 40, grading about
$0.55. Job budget $15 including this session's own cost (not visible to the session;
estimated, not measured). Pilots so far: $1.28. Stop rule: if the running CLI estimate of
the registered run passes $8, stop launching and report as incomplete. OpenRouter key and
budgets are read and recorded before grading.

## Blind review (2026-11-13, before any registered session)

A fresh subagent (Claude Sonnet, open question, the files and code only) checked this
file, the design, the pilots, the scripts and the fixture. It found the ship-rule table
equal to R1's full-size column, ran the checks on synthetic work trees (a note beside
step 2, at step 1, under Troubleshooting, a rewritten step 2, a note appended to step 2's
own line, a note under step 4) and found each endpoint computed as `DESIGN.md` defines
it, and found no leak of the expected behaviour beyond what R1 also had (the commit
message names the alternative; the work folder's path carries the arm name).
One blocking finding, fixed: the void check let a record pass with a registered file
missing, never compared the commit, and did not hash `../run.py`; it is now strict
(Arms, Void conditions). Minor findings taken: the expected hashes are committed with
this file; the rewrite detector needs the step's own text; dates and G1's friction are
named under "cannot see"; the post-pilot harness change is disclosed above.

## Deviations

## Result
