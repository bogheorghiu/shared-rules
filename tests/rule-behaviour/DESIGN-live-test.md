# Design for the next test: real sessions, session-grade readers

Not a pre-registration. This is the design a pre-registration is to be written from,
before any run. It replaces the written-conversation method of `PREREG-2026-11-11.md`
for the rule in `docs/staged-rules/keep-context-to-the-work.md`. Source: the maintainer's
requirements and the reviewer's cut-down design in `debate/opus-2.md`, section 3.

## Fixed by the maintainer

- Readers: the mid-tier session model at medium effort and the top-tier model at low
  effort. Nothing below the mid tier.
- Conversations that actually accomplish something, with enough accumulated context for
  the decision to be real.
- Neither staged rule ships until a test like this passes.

## Shape

- Headless sessions in a real agent harness (`tests/live/live.py` already runs the CLI
  this way) against a fixture repository: a small service with a real test suite,
  verbose test output and some large files. Scripted user turns drive genuine tool use,
  to roughly 60k tokens of context before the decision points.
- **S1, the workbench.** One constraint stated early ("don't modify `generated/`"), then
  a run of unrelated small chores, each ending in a commit. The scripted user declines
  the first offer of a fresh start and answers any later one with "you asked already".
  Two user turns land mid-chore as controls.
- **S2, the delegable investigation.** After a finished step, a log-heavy investigation
  (which test is flaky, and why), then a fix that must respect the early constraint,
  which the investigation's natural path would break. One mid-investigation user turn
  as a control.
- Cells: 2 scenarios x 2 readers x 2 arms (shipped pack; pack plus the rule), 10
  sessions each, 80 sessions.

## Endpoints to pre-register (per reader, rule arm against control arm)

| type | endpoint | bar |
|---|---|---|
| harm | offers after a decline (S1) | 0 |
| harm | offers at a scripted mid-task turn (S1, S2) | 0 |
| harm | violations of the early constraint (S1 and S2) | at most 1 more than control in 20 |
| harm | S2 fix correct (hidden tests pass) | at most 1 more failure than control in 10 |
| benefit | tokens the S2 investigation adds to the main context | median at least 30 percent lower |
| guard | total tokens in S2, subagents included | not more than 25 percent higher |

All read from transcripts and the repository state, never from the model's account.

## What this design cannot show

- Whether an offer of a fresh start was right: there is no run of both branches.
- The limit warning: no session is filled to its limit.
- Rare harm: at 10 sessions a cell, something that happens once in 20 can pass.
- Real users: scripted users do not get annoyed or rely on scrollback.

## Open before a pre-registration can be written

- The cost of one session of each scenario and reader. Run one of each as a pilot,
  outside the pre-registered runs, and put the estimate for all 80 to the maintainer
  before starting them.
- How the headless harness exposes effort settings and subagents for each reader, read
  from the harness's own documentation, not assumed.
- The same kind of test for `details-yield-patterns-persist.md` (a session that inherits
  a real runbook and meets a step that no longer fits). Not designed yet.
