# Staged rules

Draft rules kept here until they're approved. Nothing in this folder ships: the plugin
installs only `plugins/shared-rules/rules/`, and the tests check only that folder.

To ship a staged rule, move it into `plugins/shared-rules/rules/` and follow the
maintainer steps in the root `README.md` (record its text in the rules history, raise
the plugin version). It changes what every user's sessions do, so before shipping,
write down the check it must pass (`preregister-ship-decision.md`).

## Status

| file | status |
|---|---|
| `propose-session-closure.md` | Tested 2026-11-11, three rounds: **did not pass** its ship rule. Text here is the round-3 text. |
| `keep-context-to-the-work.md` | Passed its registered live test 2026-11-12 (`tests/rule-behaviour/live/RESULT-2026-11-12.md`); owner chose to promote it. Moved to `plugins/shared-rules/rules/`; ships at the next release. |
| `details-yield-patterns-persist.md` | Tested 2026-11-11, three rounds: **did not pass** its ship rule. Text here is the round-3 text.  Superseded by `keep-the-aim.md`. |
| `keep-the-aim.md` | Drafted 2026-11-13, not tested. Test design: `tests/rule-behaviour/live/keep-the-aim/DESIGN.md`. |

The test, its ship rule, every reply and the result are in `tests/rule-behaviour/`
(`PREREG-2026-11-11.md`, section "Result").
