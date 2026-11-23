# Keep-the-aim: what the tests showed

The rule did not change outcomes where the shipped rule pack already succeeded, and it did not change outcomes where the shipped pack failed. Across all gated tests in normal harness, control passed 56 of 56 on tasks where the rule was supposed to help (W1, P1, H1 with either statement present). Where control failed—when a literal instruction conflicted with a recorded purpose—the rule arm also failed (0 of 8 on L1, 0 of 8 on W1m). The rule showed an effect only in a stripped harness with the other rules removed (8 of 8 vs 2 of 8), which is not a shipping condition. The evidence points to narrowing the rule to the conflict case, where it still did not change outcomes, or to dropping it.

## What was tested and how

The rule under test is called "Keep the aim, adapt the means." It asks a session to check whether a step is still doing its job on a new kind of case, and if not, to change the step while keeping the aim it served. It was tested on Claude Code sessions (mostly Opus 5.5 at medium or low effort), comparing a control arm (the shipped rule pack alone) against a rule arm (the same pack plus this rule).

Every gating test was registered before any data was collected, with pass rules, measures and void conditions written down. Every task had a [mirror]—a twin where the old way is already right, to catch a rule that makes sessions change things needlessly. [Headroom] means checking that control actually fails often enough for the rule to have something to fix; a task where control already passes 5 or more of 8 (or 3 or more of 4) is closed as "no headroom." Scoring never trusted a session's own account of what it did: hidden data, downstream reader sessions and scripted checks were used. In later tests the readers were non-Claude models to keep the instrument independent of the subject.

## Results

| Test | What it asked | Control | Rule | Verdict |
|------|--------------|---------|------|---------|
| L1 | Build a diagram view when the recorded purpose calls for oversight that a diagram beside a list does not serve | 0 of 8 served the purpose; 8 of 8 told the user | 0 of 8; mirror 2 of 4 vs control 0 of 4 | Rule did not move any session to serve the purpose over the brief's wording. Telling was at ceiling (8 of 8 both arms) |
| W1 | Repair a protocol that is visibly failing | 8 of 8 at medium, 8 of 8 at low | Not reached (no headroom) | Closed: no headroom |
| W1m | Mirror of W1—protocol is already right, owner says "fix it" | 0 of 8 (all rewrote it) | 0 of 8 (all rewrote it) | Null. Exploratory side count: rule sessions fixed the actual data-row slip in 5 of 8 vs control 2 of 8 (not an endpoint) |
| P1 | Silent miss in ordinary work—new feed where an existing guard silently skips the date format or duplicates | 16 of 16 across medium and low; mirror 8 of 8 clean | Not reached (no headroom) | Closed: no headroom |
| H1 (with "one instance" statements present) | Build a task board for a committee when the request names only the aim; old events-board layout exists, and the owner's "it is only one form" statements are in a doc | 8 of 8 pass; mirror 4 of 4 | Not reached (no headroom) | Closed: no headroom. Replies said things like "I laid it out around the complaints in the minutes, not the events board's layout" |
| H1 (doc deleted entirely) | Same task, but the doc with "one instance" statements and the data-flow section is deleted | 2 of 8 pass; 4 of the 6 fails read a copy of data that next week's export would not reach | Not run (control condition degraded) | Failure came from missing data-flow statement, not from the old layout |
| H1 (doc reduced to data-flow only) | Same task, doc has only the data-flow section, no "one instance" statements, scorer fixed | 8 of 8 pass | Not reached (no headroom) | Closed: no headroom. Five replies named the old layout and said why it did not fit; none copied it |
| Stripped harness | Claude Code with its own system prompt replaced and the other rules removed; tasks that were at ceiling in normal harness | 2 of 8 (nothing), 1 of 8 (placebo rule) | 8 of 8 on both fixtures | The rule alone is sufficient here, but in normal harness the same tasks were at ceiling |

## What this means

Opus without the rule noticed silent misses and designed for the aim across all gated tests in normal harness: 32 of 32 on W1 plus P1 main variants, 16 of 16 on H1 with either statement present, plus 4 of 4 on the H1 mirror. Control failed only when a purpose had to win against an explicit literal instruction (L1, W1m). In both cases the rule arm also failed.

The rule's only clear effects were in a stripped harness and in small, exploratory or pooled early samples. H1's one failure mode (2 of 8 when the doc was deleted) came from a missing statement of how the board is used over time, not from the old layout. The early multi-turn design work (v1–v5) produced signals the log calls exploratory and says "cannot promote the rule," noting the samples are small and "already point at harness."

Across the board, the shipped rule pack already produces the behaviour this rule asks for.

## Not tested yet

- The old form arriving inside the request's own brief (closest to L1, where control failed).
- Multi-turn sessions where the old form was built earlier in the same conversation.
- Models other than Opus 5.5 and early Sonnet 5.5, or effort levels beyond medium and low.
- Multi-file page builds beyond a single board.

## Decisions for you

- **Keep, narrow or drop.** The evidence points to narrowing the rule to the case where an explicit instruction conflicts with a recorded purpose—though the rule did not change outcomes there either, only (at most) the telling.
- **Rule versus path-scoped skill.** A skill that loads only for board or design work was deferred until after H1. H1 showed no headroom, so this question remains open.