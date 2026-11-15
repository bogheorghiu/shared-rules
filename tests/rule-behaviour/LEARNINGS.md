# What earlier rule tests taught about testing rules

Four lessons from earlier tests, each with the passage it rests on, so a new test design can use
them without re-reading every result. Most come from tests in this directory; three passages come
from tests in other repositories and are quoted here in full, so the evidence stays
readable where it is used. Each passage was checked against its source on 2026-11-15.

## 1. Force the situation the rule is about

An endpoint that waits for the situation to occur by itself can pass on almost no data. Script a
turn that makes it happen, and state in advance how many sessions must reach it.

> "it did so in 1 of 40 S1 sessions (Opus rule, above). In the other 39 the H1 window is empty,
> so H1 = 0 there carries no information. H1 rests on one reply."
> (`live/RESULT-2026-11-12.md`)

> "Waiting for a natural offer cannot fix that: offers are rare in both arms … ## The decline is
> forced: the user asks, then says no" (`live/NO-REOFFER-DESIGN.md`)

## 2. Say in advance when an endpoint carries no information

Write the bound into the pre-registration: if control falls outside it, the endpoint is
uninformative for that reader, not a pass or a fail. Write both sides of the bound:

- **Floor** (tested here): "if a reader's control median is under 10,000, B1 is uninformative
  for that reader." (`live/CONTROL-PILOT-S2-PROSE.md`)
- **Ceiling** (tested elsewhere): "Correctness hit ceiling: 35/36 on 40-100-line real tasks
  with Opus, so the pass gate carried no signal. The pre-registered verdict then turned on a
  single failed run. … Next time, pre-register a ceiling check: if more than about 90% of the
  pilot passes, harden the tasks before the scored runs." (claudeshared
  `field-notes/pending/PENDING-APPENDS-2026-10-15-blind-replication-walls.md`, from a
  replication in the phantasia repository, `prereg/2026-10-15-ruleset-delivery-replication.RESULT.md`)

## 3. Rule out floors that come from the harness or the turn's wording

A pass rate can fall in both arms for reasons that have nothing to do with the rule: the
harness denies commands, or the turn's wording asks for the very move the endpoint counts.
Read what the agent attempted from the transcript, not only the final files.

> "Of the 10 sessions that missed A1 (5 per arm), 9 never seeded `data/dev.db` … every one of
> them had at least one denied command" (`live/setup/PREREG.md`)

> "All four, both arms, rewrote step 2 to `--db-url`. 'Update the guide to match' reads as
> asking for that, so the step-2 rewrite was the task, not a departure" (`live/setup/PILOT.md`)

> "The final file shows no rewrite, so a final-state check alone would have scored this as no
> harm. `summarize_runbook.py` now counts attempted rewrites from the transcript (allowed or
> denied)" (`live/runbook/PILOT.md`)

## 4. More fixture variants beat more sessions on one fixture

Sessions on one fixture are correlated, sometimes identical, so three sessions per cell can
behave like one. Add variants of the fixture, and size the noise floor with a run that compares
two identical arms.

> "Runs within an arm were identical bit for bit, so the effective sample is per task, not per
> run." (claudeshared `field-notes/pending/PENDING-APPENDS-2026-11-07-fieldnotes-ab-test.md`)

> "add **cases**. More runs per case help much less, because repeats of one prompt are
> correlated." … "run the same cases twice, unchanged, and score `R1` against `R2`. The
> difference between two identical arms is your noise floor. A real delta must clear it."
> (ex-cog-dev `makers-toolkit/skills/skill-activation-testing/references/protocol.md`)

The first passage is one observation; the second is a stated method, not a measured result here.
