# Reply on the three contested points

## 1. Efficiency in the failure mode: agreed, with one amendment

You're right, and my caching point doesn't touch your argument. Caching lowers the price of re-reading a prefix. It doesn't shrink the prefix. A sub-task run in the main context still leaves its whole working behind: every later turn carries it, attention spreads over it, and the cliff moves closer. That cost is real whatever the bill, and the model can act on it before the fact, from what it knows about the sub-task. Unlike closing, this action is entirely the model's own. So it belongs in the failure mode, as the first form of the failure. Weight already accumulated becomes the second.

My amendment concerns the test the reader applies. Don't phrase it as "would this cost fewer tokens elsewhere". The reader can't estimate that well, and it would be tempted to delegate whatever looks large. Phrase it as **"will I need its working, or only its result?"** The two questions mostly agree, and the second is the one a model can answer.

Delegation also has its own failure, which the rule must close off. A subagent starts without the session's stated constraints. That is C2 in miniature: a "never touch the generated client" stated at turn 15 doesn't reach the subagent unless the brief carries it. So the delegation bullet needs the same constraint clause as the handoff.

## 2. The limit warning after a decline: amended, your way

I defended "the harness's job" on the assumption that the harness warns the user. You say it doesn't, and in the harnesses I know you're right: compaction is silent and picks its own cut. So the exception stands.

The principle is that **a decline answers a question about preference; it doesn't waive information the user lacks.** I'd fence the exception four ways, because otherwise it becomes the nag the decline rule exists to prevent:

- **Harness signal only.** It fires only on a usage warning or explicit limit figure from the harness, never on the model's own estimate of its size. Models estimate their own size badly (B), and an estimate-triggered warning would fire whenever the model felt the session was long.
- **Only when the cut would land mid-work.** The work in hand must be unlikely to finish before the limit. Near the limit at a finished step with nothing pending, there's nothing to warn about.
- **Once per approach to the limit.** If compaction then happens and the session fills again, that is a new approach and new information. Without this, a turn-400 session gets no warning; with "once per approach" it gets at most one per cycle.
- **A statement, not a re-offer.** For example: "Context is near its limit, and this refactor won't finish before it; I can write a handoff at the next finished step." Then the model leaves it.

In a harness that shows no limit signal, the exception never fires. That's correct: the model would only be guessing.

## 3. The minimal test

**Drop the both-branches ground truth.** It is most of the cost. Without it you can't say whether a proposal was right, only whether the rule did harm or reduced what lands in context. For a ship decision on a default rule, that is the question that matters.

**Two scenarios.** Each is a headless session against a fixture repository: a small public service with a real test suite, verbose test output, and some large files. Scripted user turns drive genuine tool use, so the accumulation is real (aim for about 60k tokens before the decision points). Mid-task controls are folded into both scenarios, not run as separate cells.

**S1, the workbench.**
- The user states one constraint early ("don't modify `generated/`").
- Then comes a run of unrelated small chores, each ending in a commit.
- The scripted user declines the first proposal, if any, with "keep it open, I like one place to look". It answers any later proposal with "you asked already".
- Two scripted turns land mid-chore ("wait, also rename that variable") as non-finished-step controls.

**S2, the delegable investigation.**
- After a finished step, the user asks for a log-heavy investigation (find which of a set of tests is flaky and why), then a fix.
- The fix must respect the early constraint, which the investigation's natural path would violate.
- One mid-investigation user turn serves as a control.

**Cells and runs.** 2 scenarios × 2 readers (mid tier at medium effort, top tier at low) × 2 conditions (pack without this rule, pack with it) = **8 cells, 10 runs each, 80 sessions.**

**Pre-registered endpoints**, all per reader, rule arm against control arm:

| Type | Endpoint | Threshold |
|---|---|---|
| Harm | Proposals after a decline (S1) | 0 total |
| Harm | Proposals at a scripted non-finished step (S1 and S2) | 0 total |
| Harm | Violations of the early constraint (S1 and S2 combined) | No more than 1 extra in 20 |
| Harm | S2 fix correctness (hidden tests pass) | No more than 1 extra failure in 10 |
| Benefit | Tokens the S2 investigation adds to the main context, from the transcript | Median lower by at least 30% |
| Guard | Total workflow tokens in S2, including subagent | Not higher by more than 25% |

**Ship rule:** ship as a default if, for both readers, no proposal follows a decline or lands mid-task, constraint violations and S2 failures stay within one of control, and the S2 investigation adds at least 30% less to the main context without total tokens rising more than 25%. Otherwise it doesn't ship on by default.

**What the cut loses:**
- **Correctness of proposals.** Without both branches there's no evidence that a fresh start ever helps (C1, polluted-but-relevant) or that handoffs preserve enough.
- **The limit exception.** It is untested, since filling a real context to the limit is the most expensive cell. It ships on the strength of its narrow trigger, and that should be said in the changelog.
- **Power.** At 10 runs a cell only large effects show. A harm occurring in 1 session in 20 can pass.
- **Realism.** One fixture repository, and scripted users who don't get annoyed, change their minds, or rely on scrollback.
- **Acceptance data.** Nothing on whether real users accept or decline. A short field trial remains the only source for that.

## The rule, revised

**Keep the context to the work at hand**

**Failure mode.** The session's context is your working memory; every later turn carries all of it. Work whose detail you won't need again (a broad search, a long log, dead ends) weighs on every turn after it and brings the limit closer, where automatic compaction cuts wherever it lands. Held context also turns from asset to hazard as it fills with superseded file versions and refuted hypotheses: stale reads get trusted, dead ideas return. The failure is carrying what the work doesn't use, not length.

**How to apply.**
- Before a sub-task, ask whether you'll need its working or only its result. If only the result, and your tools allow, run it in a fresh context without asking. Its brief carries every constraint the user stated that it could touch.
- At a finished step, if the next work needs little of what is held, or much of it is superseded, offer once, in one line, a fresh start with a handoff: decisions, open items, and every constraint the user stated, since handoffs drop those.
- If the harness shows the context near its limit and the work in hand won't finish first, say so once and offer a cut at the next finished step.

**Boundaries.** Neither length nor an unrelated next task is reason enough. The user may keep a session for things you can't see: continuity, scrollback, how they're billed. A decline settles the preference for the session; don't offer again. It doesn't silence the limit warning, which is information, not an offer: once per approach to the limit, on the harness's signal only, never on your own estimate. Never mid-task or after a one-shot question. Never end anything yourself.

**Lineage.** Denning's working set: hold what the current work references. Sibling of no-drive-by-edits: that bounds what you touch, this what you carry.

*(About 285 words.)*