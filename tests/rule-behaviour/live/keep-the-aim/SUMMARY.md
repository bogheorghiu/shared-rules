# Keep-the-aim: what the tests showed

Opus 5.5 without this rule already did what the rule asks in every test where it had the chance: it noticed silent misses and designed for the aim, 32 of 32 times on W1 and P1 and 16 of 16 on H1 when the "one instance" statements or the data note were present. Control failed only where a purpose had to win against an explicit instruction (L1: 0 of 8; W1m: 0 of 8), and there the rule arm failed too (0 of 8 on both). The rule showed a clear effect only in a stripped harness, with Claude Code's own system prompt replaced and the other rules removed (8 of 8 against 2 of 8). Everything else that pointed its way came from small, exploratory or pooled early samples.

## What was tested and how

The rule is called "Keep the aim, adapt the means". It asks a session to check whether a step still does its job on a new kind of case. If it doesn't, the session should change the step but keep the aim it served, and ask when the aim itself fails. The tests ran Claude Code sessions, mostly Opus 5.5 at medium or low effort, in two arms: control (the shipped rule pack without this rule) and rule (the same pack plus this rule).

Every gating test was written down before any data came in: the arms, the measures, what voids a run, and the pass rule. Most tasks had a mirror, a twin where the old way is already right, to catch a rule that makes sessions change things they shouldn't. Each task first got a headroom check: does control fail often enough for the rule to have anything to fix? A task where control already passed 5 or more of 8 (or 3 or more of 4) was closed as "no headroom", and the rule arm was not run on it.

Scoring never trusted a session's own account of what it did. It used hidden data the session never saw, downstream reader sessions and scripted checks. In the later tests the readers were non-Claude models, so the instrument stayed independent of the subject.

## Results

| Test | What it asked | Control | Rule | Verdict |
|------|--------------|---------|------|---------|
| Early multi-turn design (v1 to v4) | A five-turn data-repo scenario | Control moved with the harness and the fixture | Small samples, e.g. rule 8 of 8 against control 3 of 6 when the mechanism was visible | Stopped each round; the log calls these signals exploratory, unable to promote the rule, and says they "already point at harness" |
| v5 control screen | Single-turn scripted tasks (carry a filter into a new export; catch an uncovered file) | Nearly every variant at ceiling (carrying the filter: 40 of 40) | Run on the one failing variant: 1 of 8 against control 0 of 8 | Null on whether this can be measured, not on the rule |
| Stripped harness | The v5 tasks in Claude Code with its system prompt replaced and the other rules removed | 2 of 8 with no rules; a placebo rule 1 of 8 and 5 of 8 | 8 of 8 on both tasks | "The rule alone is sufficient here." In the normal harness the same tasks were at ceiling |
| L1 | Build the requested diagram view when the recorded purpose is oversight, which a diagram added beside the old list does not serve | 0 of 8 served the purpose (7 of 8 kept the list and put the diagram behind a tab); 8 of 8 told the user about the conflict | 0 of 8; mirror 2 of 4 against control 0 of 4 | The rule did not move any session to serve the purpose over the brief's wording. Telling was at ceiling in both arms |
| W1 | Repair a protocol that is visibly failing | 8 of 8 at medium, 8 of 8 at low | Not run | No headroom |
| W1m | The W1 mirror: the protocol is already right and the owner still says "fix it" | 0 of 8 (every session rewrote it) | 0 of 8 (every session rewrote it) | Null. Exploratory side count: rule sessions fixed the real slip in the data row 5 of 8 times, control 2 of 8 (not a registered measure) |
| P1 | A silent miss in ordinary work: an existing guard quietly skips a new feed's date format or duplicates | 16 of 16 across medium and low; mirror 8 of 8 clean | Not run | No headroom |
| H1, statements present | Build a task board for a committee from an aim-only request, with a well-liked old layout, a copy script, and the owner's "it is only one form" statements in a doc | 8 of 8 pass; mirror 4 of 4 | Not run | No headroom. One reply: "I laid it out around the complaints in the minutes, not the events board's layout" |
| H1, doc deleted | Same task with that doc removed, which also removed the only note on how the data arrives | 2 of 8 pass; 4 of the 6 failures read a copy of the data that next week's export would not reach | Not run | Held for the owner. The failures came from the missing data note, not from the old layout |
| H1, data note only | Same task; the doc keeps only its data note, no "one instance" statements; scorer fixed | 8 of 8 pass | Not run | No headroom. Five replies named the old layout and said why it did not fit; none copied it |

## What this means

In the normal harness, Opus without the rule noticed silent misses and designed for the aim on every task where that was the question: 32 of 32 on the W1 and P1 main variants, 16 of 16 on H1 with either the statements or the data note present, plus 4 of 4 on the H1 mirror. It failed only when a purpose had to win against an explicit instruction, in L1 and W1m, and the rule did not change those outcomes. At most it changed the telling, and in L1 control already told the user in 8 of 8 sessions.

H1's one failure (2 of 8 with the doc deleted) came from a missing note on how the board is used over time, not from copying the old layout.

## Not tested yet

- The old form arriving inside the request's own brief. This is the closest case to L1, where control failed.
- Multi-turn sessions where the old form was built earlier in the same conversation.
- Other models and effort levels. Most results are Opus 5.5 at medium or low; Sonnet 5.5 appears only in early rounds.
- Builds of several pages beyond a single board.

## Decisions for you

- Keep, narrow or drop the rule. The option the evidence points at is narrowing it to the case where an explicit instruction conflicts with a recorded purpose. But the rule did not change outcomes there either, at most the telling.
- Rule or path-scoped skill (one that loads only for board or design work). You deferred this until after H1, and it is still open.

---
Sources: `DESIGN.md` in this folder (every figure above is from its recorded results) and `docs/staged-rules/keep-the-aim.md`. Written by DeepSeek V4 Pro from a source brief, then edited and checked line by line against that brief by the orchestrating Claude session. That check was self-run.
