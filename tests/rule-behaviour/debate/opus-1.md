# Reply on the context-economics reframing

## A. Does the reframing answer the objection?

Half of it. The reframing contains two claims, and they differ in kind.

**The quality claim belongs in a default pack.** Accumulated context degrades the work. Superseded file contents get trusted over the current ones, refuted hypotheses resurface, and attention spreads thin across material that no longer matters. That claim is about the work itself, which is what the other seven rules govern. A stranger who installed the pack for no-drive-by-edits would endorse "don't act on a stale picture" without having chosen any working style. Under this claim my objection falls.

**The token claim is still a preference, now with a price attached.** Three things keep it the user's call, not the pack's:

1. **The user pays, and the model can't see the bill.** Flat subscription, metered API, or an employer's account: these lead to different answers. The model knows none of them.
2. **"Pays on every turn" is weaker than stated.** With prompt caching, an active session re-reads its prefix at a fraction of the price. The real token costs are elsewhere:
   - cache expiry after idle gaps, which the model can't see;
   - latency;
   - the approach to the context limit, where automatic compaction cuts at a point nobody chose.

   A rule that tells the model "the user pays for all of this every turn" will over-weight cost in exactly the sessions where caching makes it cheap.
3. **The user values things the cost model doesn't price.** Scrollback, one place to look, not re-explaining. These are legitimate goods, and they are invisible from inside.

**What would have to be true for the rule to ship in a default pack:**

- The rule's justification is quality and avoiding the compaction cliff. Token thrift is at most a secondary consequence.
- Its default actions are internal: don't pollute the context, delegate work whose details aren't needed. Those cost the user nothing and change nothing about how they work.
- The one user-facing action is rare, one line, and settled by the first answer. The user's answer is treated as information the model lacked, not resistance to overcome.

If those three hold, the rule governs the model's working memory, not the user's workflow.

**On your point 2, I disagree.** The framing does not protect the workbench user. Their chores often don't share context: chore 7 needs nothing from chore 2. Your own question, "does what comes next draw on this?", then answers no, and the model proposes closing. That is exactly the misfire I named. The workbench user keeps the session for continuity, not shared context. What protects them is the decline rule and the instruction that length and unrelatedness alone aren't enough. The framing doesn't.

**On your point 3, I'd change the ordering principle.** Order by fit, not by disturbance. The three remedies solve different problems:

- **Subagent:** prevents new weight. It does nothing about weight already held.
- **Compaction:** removes weight, but lossily and invisibly. Usually only the user can trigger it.
- **Fresh session with handoff:** removes weight, and the loss is visible because the user can read the handoff and correct it.

Ranking compaction above the handoff because it disturbs less ranks a silent loss above a visible one.

**Point 4: agreed.** I'd go further. The no-proposal part (delegate exploration, don't dump large outputs into the main context) is where most of the value is, and it should lead the rule.

## B. What a session-grade model can observe

| Signal | What it tells you | How it fails |
|---|---|---|
| The visible transcript (rough volume of large tool outputs: file reads, logs, test runs) | Order-of-magnitude weight | Models estimate their own token count badly. After compaction the transcript looks short and the weight is underestimated. |
| Harness messages (context-usage warnings, a "continued from a previous conversation" summary) | Actual limit pressure; that compaction happened | Harness-specific and often absent. Absence proves nothing. |
| Superseded material (files read and then edited, approaches abandoned, hypotheses refuted) | The "tax" share, and the risk of acting on stale state | Hard to know what is truly dead. A failed approach is sometimes the most valuable thing held ("we tried X, it broke Y"). |
| Overlap between the next request's files or modules and those already read | Whether the accumulation is relevant | Overlap with stale reads is a hazard, not an asset. Relevant constraints often have no file overlap. |
| Explicit back-reference in the request ("like before", "same as the auth fix") | Strong evidence the next work draws on the session | Users omit references to things they assume the model holds. Absence is weak evidence of separateness. |
| Constraints and preferences the user stated in the session | Hidden dependencies a fresh start would drop | They are easy to overlook in a long transcript, and they are exactly what handoffs omit. |
| Own confusion (re-reading the same file, contradicting an earlier decision, citing an old version) | Context rot already happening | A lagging indicator, and models rarely notice their own confusion. |
| Task boundary (tests green, commit made, "thanks, next") | When a proposal is permissible | Users' rhythms vary; "thanks" mid-task is common. |
| Tool list (a subagent tool, a model-invokable compaction tool) | Which remedies are the model's to use | Reliable when present. |

The model cannot see:

- token counts, unless the harness surfaces them;
- cache state or elapsed time;
- the user's billing;
- whether the user intends to return to earlier threads;
- why the user keeps the session open.

The rule should name these as unknowns so the reader defers on them.

## C. Where the cost model points the wrong way

**1. Relevant but polluted.** A long debugging session ends with the bug fixed. The next request is a related change in the same module, so "draws on this context" says yes, stay. But the relevant part is five facts buried under forty superseded reads and three refuted hypotheses. The risk is not cost but error: the model re-adopts a dead hypothesis or edits against a stale file version. A fresh start with a five-line handoff would do better work.

The flaw is that your question is binary. The real quantity is how much of what's held is relevant, current, and correct.

**2. Looks separate, isn't.** At turn 15 the user said "never touch the generated client" or "we target Python 3.9." At turn 120 they ask for something unrelated-looking. The model judges it separate, proposes a fresh session, and writes a handoff of decisions and open items. The handoff omits the constraint because it was stated once, early, in passing. The fresh session violates it.

The model will misjudge separateness in exactly this direction: dependencies that are unreferenced and unremembered. The handoff must list stated constraints explicitly, and the bar for proposing must account for this risk.

**3. Relevant, but near the cliff.** The next work genuinely draws on everything held, so the framing says stay. But the context is near its limit, and automatic compaction will fire mid-task at an arbitrary point, summarizing away whatever the summarizer judges minor. A deliberate cut now, at a finished step with a handoff the user can check, beats a lossy cut later.

The cost model has no term for this because it treats cost as linear. It has a cliff.

**Honorable mention: the workbench run of unrelated chores (from A).** The framing says leave, and the user is right to stay.

## D. The rule

**Keep the context to the work at hand**

**Failure mode.** The session's context is your working memory; every turn re-reads all of it. It is an asset while the work draws on it. Once it is mostly superseded file versions, refuted hypotheses and finished tasks, it blurs the picture: stale reads get trusted, dead ideas return. The failure is not a long session. It is carrying weight the next work doesn't use, or letting an automatic compaction choose the cut mid-task.

**How to apply.** Before new work, weigh what it needs from this session against how much of what is held is now wrong or idle.

- Don't add weight you won't use. A sub-task whose result you need but whose working you don't (a broad search, a long log) can run in a fresh context where your tools allow. No need to ask.
- At a finished step, if the next work needs little of what is held, or much of it is superseded, offer once, in one line, a fresh start with a handoff. The handoff names decisions, open items, and every constraint the user stated, since those are what handoffs drop.
- If the harness shows the context nearing its limit, a cut at a finished step beats an automatic one mid-task; say so.

**Boundaries.** Length is never the reason by itself. The user may keep a session for things you cannot see: continuity, scrollback, how they are billed. Their answer settles it for the session; don't raise it again. Never mid-task, mid-debugging, or after a one-shot question. Don't end anything yourself.

**Lineage.** Denning's working set: hold what the current work references; the rest costs without helping. Sibling of no-drive-by-edits: that bounds what you touch, this what you carry.

*(About 290 words.)*

Two deliberate choices:

- **Billing is a boundary, not the failure mode.** It sits in the boundaries as something the model can't see.
- **A decline outranks the limit bullet.** After a decline, the limit warning is the harness's job, not the rule's.

## E. A test that isn't artificial

**Make the accumulation real.** Run actual long tasks in a real agent harness on a real repository, then branch at a finished step. Examples:

- debug a genuine failing test, with dead ends;
- a multi-file refactor;
- a feature with a design discussion in which the user states constraints.

Transcripts from the maintainer's own sessions, truncated at a natural boundary, are better still. Target 60–150k tokens of context, including superseded reads.

**Vary the next request across the cases that matter:**

1. A continuation that needs the state.
2. Related work in a polluted context (case C1).
3. A separate-looking task that depends on an early stated constraint (case C2).
4. A run of unrelated chores in a deliberate workbench.
5. Work that is relevant, with the context near the limit (case C3).
6. Controls: mid-task, mid-debugging, a one-shot question.

**Get ground truth empirically, not from the tester's opinion.** For each state, run both branches:

- continue in the session;
- start fresh with the model's own handoff.

Score the next task on:

- correctness (tests, review against a rubric);
- violations of earlier-stated constraints;
- total tokens across the whole workflow, counting cached and uncached separately and including the fresh session's re-reading;
- wall time.

The better branch is the right answer for that state.

**Measure the rule against that ground truth, with and without the rule, on both tiers.** The earlier 0/3, 3/3, 0/3 spread says three runs is noise, so use at least 20 per cell. Measure:

- proposal precision and recall;
- handoff fidelity: did the fresh branch violate a stated constraint?
- repeats after a decline;
- proposals in the controls;
- whether delegation increased and whether delegated sub-tasks went wrong for lack of context.

**Field trial.** Give the rule to a handful of real users for a week. Log proposals, accepts and declines, and ask decliners why.

**The rule is harmful if any of these holds:**

- Proposals in workbench sessions are mostly declined.
- Fresh-start branches the rule chose score worse than continuing, especially through constraint violations in case C2.
- Net workflow tokens rise because fresh sessions re-read everything.
- Any proposal repeats after a decline.
- Any proposal fires mid-task.
- The rule makes the model spend visible turns reasoning about its own context instead of working.

A rule whose main measurable effect is more interruptions and no better outcomes is a preference, however it is framed.