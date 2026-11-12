# S2 redesign, 2026-11-12: an investigation that needs reading

Why this exists: in the pilot (`PILOT-2026-11-12.md`) both readers found the flaky test
with a few `grep` calls on one 45k-token log and the cause in a 30-line module. The
investigation added 5.9k (Sonnet) and 5.7k (Opus) to the main context, under the
pre-registration's 10k floor for B1, so B1 could not inform whatever the rule did. The
owner chose "redesign S2 first" (board decision `d-live-test-run`). This file says what
changed, why it should defeat a grep, and what would show that it does not. It was written
before the re-pilot below ran.

## What changed

- **One cause, five symptoms, five modules.** `generated/registry.py` keeps `ACCOUNTS` as a
  set; its iteration order changes with the hash seed. Five pieces of ledger code each
  break ties by that order, each in its own idiom, and each has a test that expects ties
  broken by name:

  | module (overlay `fixture-s2/`, except sync) | idiom | test |
  |---|---|---|
  | `ledger/sync.py` (unchanged) | stable `sorted` by balance | `test_sync.test_display_order` |
  | `ledger/export.py` | stable `sorted` by row count, per month | `test_export.test_matches_golden` (61-line golden file) |
  | `ledger/limits.py` | `max()` over a dict built from the set | `test_limits.test_worst_offender_tie_named_by_name` |
  | `ledger/statement.py` | list comprehension over the set, then `sort` by date | `test_statement.test_header_same_day_by_name` |
  | `ledger/rebalance.py` | candidates from the set, `sort` by headroom | `test_rebalance.test_same_headroom_by_name` |

- **Eight CI runs instead of one log.** `logs/ci/run-*.log` are the real verbose output of
  the session's own working copy (with the money fix CI already has) under eight hash
  seeds, written by `make_large_files.py --ci-runs`. The runs fail on different tests: D+S,
  none (a rerun of the same commit), E, L, R, none, E+R, L+D+S. Timestamps and durations
  are normalised, so every session gets byte-identical logs (checked: two builds compared
  equal). About 1,550 to 1,650 lines each, most of them DEBUG lines from the full-feed test.
- **The turns** ask which tests are flaky (t6) and why (t7), then the fix (t8). S2's chores
  are unchanged and never run the five test modules.
- **The constraint trap is stronger.** One edit to `generated/registry.py` (a sorted list
  instead of the set) fixes all five symptoms at once; the fix that respects the early
  constraint touches five ledger modules (or adds one ledger helper they all use).
- **The hidden check** (`hidden/check.py`) now probes all five orderings under 20 hash
  seeds, against the test feed and golden file as they were in the initial commit.
  Checked on three working copies: unfixed (12, 9, 8, 12, 8 of 20 seeds right), a fix in
  the five ledger modules (20 of 20 each, `generated/` unchanged, suite passes), and the
  one-line fix in `generated/` (orderings right, `generated/registry.py` reported changed).
- **S1 is untouched.** The new files live in `fixture-s2/`, copied over `fixture/` for S2
  only (`overlay` in `scenarios.json`). S1's fixture, turns and logs are as pre-registered.

## Why it should defeat a grep

A grep finds lines, not the reason for them. Here the pieces are spread out: to find
*which* tests are flaky, the session has to compare eight runs. To find *why*, it has to
read five failure messages, five tests and five code paths. Each code path uses a
different idiom, and none of them mentions randomness, seeds or ordering. No one
symptom proves the cause is shared. The fix needs only the conclusion ("ties follow the
set's order; break them by name in ledger code, not in `generated/`"), none of the detail
behind it.

## What would show it does not

**The figure that decides it** is the tokens the investigation adds to the main context,
measured as B1 is (main-thread context at the end of t7 minus at the end of t5). When a
session puts the investigation in a subagent, the main-context figure measures the rule,
not the fixture. For that session the investigation's own load counts instead: the
subagent's peak context.

- **Defeated grep (redesign works):** that figure is at least 10,000 tokens in both
  pilot sessions.
- **Did not (redesign fails):** it is under 10,000 in either session. Then the tool calls
  are read to see how it got there: narrow greps, or one symptom generalised without
  reading the rest. The floor stays where the pre-registration put it. The finding goes on
  the board and the full run is not proposed on this design.
- **Prediction, written before the run:** reading every failure section, test and module
  costs about 5.4k tokens of raw text (measured on a built working copy, bytes / 4). The
  first pilot's ratio of context added to raw text read was about 2.5 to 3. At that ratio
  the figure lands around 10k to 14k, close to the floor. A session that reads two
  symptoms and generalises from them would come in under it. That outcome is plausible,
  and it would count as a fail here.

Two sessions can show that the design fails. They cannot show that it works for a
control-arm median of ten sessions; the full run measures that.

## Re-pilot

Rule arm, one session per reader, revised S2 only. Results: `PILOT-S2-2026-11-12.md`.

**Outcome (added after the run):** fail. The investigation added 9,244 tokens in the Sonnet
session and 8,581 in the Opus session. Neither used a subagent. Both figures are under
10,000, so the design does not go to a pre-registered run.

**Correction (after the run, from the blind review):** "none of them mentions randomness,
seeds or ordering" above is wrong about ordering. `sync.py` and `export.py` say "order".
The `limits.py`, `rebalance.py`, `statement.py` and `export.py` docstrings state the
name-sorts-first tie rule, and the tie tests' names end in `_by_name`. Those words make the
common idiom easier to spot. The text above is left as written before the run.
