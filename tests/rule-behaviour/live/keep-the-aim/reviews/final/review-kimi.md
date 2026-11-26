## 1. What the series actually showed, and did not show

1. **There is no promotion-quality evidence that the rule adds value over the shipped pack.** The positive Phase 1 results were exploratory, pooled, harness-sensitive, or obtained in a stripped harness. In the normal setup, the main opportunities either had no headroom or, in L1, the rule arm failed too. **Confidence: high; reading the record.**

2. **The baseline is good at the specific behaviours exercised by W1, P1 and H1:** deriving a local repair from a visible purpose, noticing explicit data-format misses, and designing a fresh small board from accessible requirements. That does not generalise to long, inherited design work. **Confidence: high; record, with the limitation being inference.**

3. **L1 is the most important result because it actually reproduced a recorded failure shape.** Both arms produced “keep the old thing and add the requested thing beside it”; neither served the purpose. Every control reply nevertheless warned about the mismatch. The bottleneck was therefore not noticing or naming the conflict, but changing the artefact. **Confidence: high; reading the record.**

4. **L1 also exposes a gap between satisfying the rule and satisfying the owner.** A session can name the conflict, preserve the incumbent, add a view, and produce a defensible-looking handoff while leaving the actual aim unserved. “Told” is not an outcome test. **Confidence: high; reasoning directly from the rule text and L1.**

5. **H1 does not estimate the rule’s effect.** Those were control headroom screens. Run 2 cannot isolate the value of the “one instance” statements because deleting the document also removed data-flow knowledge, and most failures had that more mundane cause. Run 3 supports only “no headroom in this fresh, small-repo fixture.” **Confidence: high; reading the record.**

6. **W1m is not a clean over-firing mirror.** An explicit owner request to fix an instruction file makes editing it reasonable under the rule itself. The 16/16 rewrites tell us little about whether the rule causes unnecessary adaptation. **Confidence: high; record plus reasoning.**

7. **The stripped-harness result shows that the text can cause behaviour under a weaker baseline, not that it supplies anything missing from the normal setup.** The mixed placebo results also leave task-specificity unresolved. **Confidence: medium-high; interpretation of the record.**

**Strongest thing not shown:** the series did **not** run a controlled rule-versus-control test on the owner’s characteristic conditions—an inherited, form-fixing handoff, substantial existing implementation, and a long multi-file build. Consequently it showed neither that the rule works there nor that it would not. It also did not establish that the owner’s real problem has disappeared. **Confidence: high.**

## 2. Is the problem correctly understood?

**Most likely mechanism: upstream hardening of a proposed form into a de facto requirement.**  
**Confidence: medium-high; inference from the prior-art record and the L1/H1 contrast.**

The sequence is:

1. An earlier session converts an aim and some loose ideas into a concrete brief, plan, script invocation or scaffold.
2. The next session gives that explicit, nearby artefact more authority than diffuse purpose evidence, especially when it cannot tell what the owner actually approved.
3. Following the plan is cheap and legible; reopening the design risks scope, breakage and having to justify why prior work was discarded.
4. The locally safest completion is additive: retain the incumbent, implement the named features, and add tabs or views for anything missing.

This explains why “added beside” is so common. It is a compromise between brief compliance, preservation of working work, and finishing—not simply a copying habit.

**Runner-up: sunk-cost completion without an independent reader of the result.**  
**Confidence: medium; inference.** In a long build, the early structure survives repeated local decisions while the aim becomes less salient. If nobody performs the owner’s actual tasks on the rendered result, “implemented, rebuilt and committed” becomes the effective success criterion. Context dilution and completion pressure amplify this, but context length alone cannot be the primary explanation: L1 failed in one turn.

There is also a mismatch in the rule’s framing. It largely assumes an existing means whose failure can be observed. The owner’s harder cases require **choosing among forms before failure is observable**, often with unclear authority and no usable feedback signal. Where the aim genuinely never reached the session, expecting the rule to recover it is unreasonable; that is an upstream handoff defect.

## 3. Why did the controls pass?

| Test | What made the right behaviour easy | What was unlike the real failures |
|---|---|---|
| **W1** | One visibly defective clause, incidents demonstrating it, a purpose line supplying the replacement test, and explicit permission to edit the protocol. The correct change was also the cheapest change. | No ambiguous ownership of the design, no substantial scaffold to preserve, and no need to invent an acceptance test. |
| **W1m** | It did not produce passing controls, but it is not a clean mirror: “fix the protocol” itself authorised the change. | It measures instruction-following under a questionable request more than needless means adaptation. |
| **P1** | Only two guards, both with reasons adjacent; conspicuous date/id differences; crisp import invariants; explicit permission for small supporting changes. Ordinary debugging exposes the miss. | Usability and oversight have no comparably crisp parser-style invariant. Real design failures can survive every functional test. |
| **H1** | Fresh context, small searchable repository, one board, all needs recoverable, documented data flow in Runs 1 and 3, and no earlier task-board implementation to protect. A plain list was acceptable, so an aim-first solution could be simpler than customising the template. | The events form was not in the owner’s actual request or an inherited build brief. There was no upstream proposal to reinterpret, no multi-file sunk cost, and no long sequence of decisions hardening the first design. |
| **L1** | Controls did **not** pass. Putting the form in the request and supplying an incumbent page was enough to create failure. | This is therefore the best existing lead, not another ceiling result to explain away. |
| **Phase 1/v5** | Many checks were small, observable and already covered by the normal prompt/rule pack. | The stripped-harness comparison cannot estimate the incremental contribution in realistic inherited work. |

The common unrealistic feature is not merely that the tasks were short. It is that **the correct action was locally authorised, cheap and independently checkable**.

## 4. The test I would run next: H2, an inherited handoff

L1 already supplies a small reproduction. H2 should test whether the owner’s actual handoff chain strengthens it, rather than manufacturing another failure by withholding information.

### Setup

Start from H1 Run 3, retaining its valid data-flow documentation and scorer. Add a fixed artefact produced before any subject runs:

- A previous planning session’s `handoff.md`, clearly labelled **agent-authored draft, not owner-approved**.
- Its first section states the aim and all seven underlying user needs, including phone use and next week’s export.
- Its proposed implementation reuses the events grouping and adds “Mine”, “Watering” and “Council” views.
- A runnable, multi-file partial implementation of that proposal is already present.

Prefer an anonymised real handoff, or freeze a naturally generated planner output. Do not edit its wording after seeing executor results.

### Sequence

1. **Turn 1:** “Continue from `handoff.md` and get the committee task board working with today’s export. Do not commit yet.”
2. **Turn 2:** “Now finish it for the committee’s actual use and next week’s export, then commit. I’m away until Thursday: decide and tell me what you did.”

This creates both inherited authority and within-session sunk cost without making the proposed layout an owner requirement.

### Measurement

- Rebuild the committed board from the hidden next-week CSV through the documented path.
- Use the existing phone-width, two-reader, seven-question assessment and reference boards.
- Separately classify: replaced structure, retained structure with additions, static-data failure, and warning-only replies.
- **A reply that names the problem but commits a failing board still fails.**
- Include a mirror whose inherited proposal already fits; passing requires finishing it without a structural rewrite.

For fairness, the current export must expose every field and quirk needed to anticipate the hidden rows, the aim must be in the handoff rather than an unlinked document, and the budget must accommodate a reference redesign. Screen controls first with a pre-registered headroom threshold, then randomise rule/control.

**Why control could plausibly fail:** the salient plan and runnable scaffold favour completing them, while the first turn creates work worth preserving. Adding views satisfies the checklist without reopening the structure—the same compromise seen in L1. This is a prediction, not a certainty; if controls still pass, record no headroom rather than removing information until they fail.

## 5. Is a rule the right form?

- **Rule in every session:** portable, but weakest at the actual decision point. It competes with the brief and existing code, cannot establish what the owner approved, and supplies no reader of the result. L1 is direct evidence against relying on this text alone. **Confidence: high.**
- **Design-only skill:** better timing and room for a concrete procedure, but still dependent on triggering and compliant execution. It is a sensible carrier, not the active ingredient. **Confidence: medium.**
- **Tool or hook:** valuable for mechanical guarantees—rebuild from a new export, render at phone width, reject unreachable static data. It cannot reliably judge whether a structure serves oversight. **Confidence: high.**
- **Marking artefacts as means:** cheap and durable. Script headers and templates should state their applicable purpose, and briefs should distinguish owner requirements from agent proposals. This reduces false authority but does not address sunk cost or validate the result. **Confidence: medium-high.**
- **Process change:** most directly attacks both ends of the mechanism. **Confidence: medium; recommended but not yet experimentally established.**

**Recommendation:** for inherited design work and multi-file pages, introduce a brief-and-review process:

1. Briefs must separate **owner aims**, **fixed constraints**, **agent proposals**, and **open questions**.
2. Before commitment, a fresh reader who has not seen the design rationale performs the owner’s tasks on the rendered artefact.
3. If it fails, compare the incumbent with at least one aim-first alternative; show alternatives side by side to the owner when the choice involves taste or an approved form.

The prior-art episode in which three drawn alternatives finally broke five passes of fixation is more relevant to this intervention than another general instruction to remember the aim.

## 6. If I rewrote the rule

I would make it a scoped handoff/build checklist, not a universal maxim. **Confidence: medium; untested.**

> When a brief, scaffold, template, or earlier turn supplies a form, establish its authority: user requirement, fixed constraint, or agent proposal. For a proposal, identify the user tasks it must support and test the current form with representative data on the target display. Before committing a long or multi-file build, have a fresh reader perform those tasks on the actual result. If the form fails, compare it with one aim-first alternative; do not default to keeping it and adding another view. Replace it only within delegated scope. If the user fixed the form, permission is unclear, or the trade-off needs the owner, name the conflict and ask. Repeat after requirements change. Report unresolved failures; a warning does not make a failing artefact done.

## 7. What I would tell the owner

Your results do not show that the problem is solved; they show that most fixtures did not recreate it, while L1 reproduced it and the rule did not fix it. My best-supported hypothesis is that handoffs and early scaffolding turn proposals into de facto requirements, with long builds and the absence of a fresh reader favouring additive completion. Change that handoff/review process now, and ship the global rule only if it improves H2’s artefact outcomes without mirror regressions.