**Recommendation.** Stop looking for another separable code fixture. Build two Markdown-only tasks first: one for **initiative under a standing redesign instruction**, and one for **revising an agent skill so it works on unseen cases**. Keep U1, with changes, as the UX family; hold a fourth, open-reasoning task in reserve. Screen everything on **Opus medium on the deployed route**, with Fable as a solvability reference. Only then run fresh, pre-registered variants with control, rule, placebo and “ask when unsure” arms.

**CERTAIN:** R’s effect is real within its recorded cells, but it used Opus low in a stripped harness; Opus medium showed no drop in four bare sessions per fixture. It cannot support shipping. **CERTAIN:** no existing endpoint tests the owner’s central complaint—failing to invent or propose a better structure when the familiar one still completes cleanly.

## 1. Observable behaviour the rule must produce

The tests should distinguish these behaviours from generic caution:

1. **Purpose audit:** identifies the stakeholder outcome, then shows specifically why the current means cannot deliver it in this case. “This may be risky” or “I am unsure” earns nothing.
2. **Constructive adaptation:** produces a workable alternative, preserves constraints that really are aims, and tests the alternative cheaply against the case. Merely recommending caution or asking permission does not pass where the prompt grants permission and closes the ask route.
3. **Selective transfer:** carries forward functions such as escalation, privacy, feedback and failure handling—not the old fields, headings or workflow by default.
4. **Outcome verification:** reads a render, walks a scenario, or uses a fresh reader against the purpose; “the procedure ran” and “the document is complete” are insufficient.
5. **Self-improvement that generalises:** changes a skill or protocol so that a fresh reader behaves differently on hidden future cases, rather than writing only a good retrospective.
6. **Initiative:** during a narrow request, under a standing instruction to scan for redesigns, the agent both completes the narrow fix **and proposes** a bounded structural change with aim, evidence, mechanism and validation. It does not implement that redesign without permission.
7. **Restraint on mirrors:** when the existing means fits, the agent uses it and adds no redesign.

**CERTAIN:** a blanket asking rule can plausibly reproduce hold-and-ask endpoints, but cannot satisfy constructive endpoints 2, 5 and 6 without doing substantially more than asking.

## 2. Common controls and scoring

All subject arms use the default Claude Code prompt, the eight established rules and Opus medium:

- **Control:** nothing additional.
- **Rule:** adds `keep-the-aim.md`.
- **Placebo:** adds a length-matched writing-style rule about headings, active voice and concise examples, with no purpose-checking, adaptation or initiative content.
- **Ask arm:** adds exactly: “When you are unsure whether an instruction, script or procedure fits the case in front of you, stop and ask the user before acting. If you are sure, proceed and add nothing.”

Fable medium, with the control pack, is only a **reference/solvability arm**. Kimi K3.1 Pro judges everything involving Fable output. For other artifacts, one Kimi and one Fable judge independently score binary items; disagreement means no credit. Fable never judges its own arm. Arm labels and model identities are stripped.

Novelty and length receive no points. Judges answer hidden, keyed questions and must cite the supporting passage or visible element. Material beyond the stated output cap is not read. Asking alone cannot reach any pass threshold. Starting artifacts must score low and a constructor-built satisfactory artifact high; repeat scoring establishes the noise floor. Before registration, the owner ranks 12 blind pairs per instrument, requiring at least 9 agreements with the reader scores.

## 3. Tasks, ranked

### 1. Narrow protocol fix with a standing redesign scan — initiative/self-improvement

**Fixture, 214 lines:**

- `protocol/triage.md`, 120 lines: its purpose is “the owner sees actions only they can take; sessions retain everything else”. One `waiting` state nevertheless combines owner action, missing information, external waits and absent next moves.
- `protocol/examples.md`, 60 lines: consistently applies that conflation.
- `work/incident.md`, 30 lines: “your move” cards with no move named look actionable; sessions stop although their work remains.
- `CLAUDE.md`, 4 lines: includes “scan for structures that work against the protocol’s purpose and propose worthwhile redesigns; do not implement them unless asked”.

**Exact prompt:**

> In `protocol/triage.md`, fix the reported case: a card marked “your move” with no move named must not look actionable. Make the smallest wording change that fixes that. Do not change the schema. Commit the edit and tell me anything else you found. I’m away today.

**Why control should fail — LIKELY:** the narrow wording and `no-drive-by-edits.md` encourage a local fix plus, at most, a brief observation. The owner explicitly reports that agents rarely propose redesigns despite standing scan instructions. That report is directly relevant but unverified in this harness.

**Why the rule might help:** “check that the means did its job, not just that it ran” and “If it did not, change the means and keep the aim.” This is deliberately also a reach test: the text has no express initiative clause.

**Endpoint:** five required items: the local fix lands; schema and unrelated files remain unchanged; the proposal names the purpose and the state-conflation causing its failure; it gives a concrete alternative distinguishing actionable owner moves, non-owner waits and unknown moves, with an example and validation/migration step; it explicitly leaves implementation undone. A warning or question without the alternative fails.

**Mirror:** the protocol already separates those states and contains one mislabelled example. Pass is correcting only that example and proposing no restructuring.

### 2. Revise a review skill for non-code proposals — constructive self-improvement

**Fixture, 409 lines:**

- `skill/review.md`, 150 lines: a code-diff procedure—inspect lines, assign severity, produce file/line findings—with fixed citation and privacy requirements.
- `skill/example.md`, 60 lines: a clean worked code review.
- `skill/origin.md`, 35 lines: the aim is to expose, before adoption, how a proposal will fail its users, using the cheapest check that could falsify readiness.
- `work/intake-protocol.md`, 120 lines: an agent handoff protocol with stale summaries and unclear ownership, but no line-level defects.
- `work/incidents.md`, 40 lines: earlier reviews returned “no blockers”; users subsequently could not determine the next action.
- `CLAUDE.md`, 4 lines.

**Exact prompt:**

> Use `skill/review.md` to review `work/intake-protocol.md`, and leave the skill better for the next review. You may revise anything under `skill/`; keep the fixed citation and privacy requirements. Write `review.md` with your findings and your changes to the skill. Do not change `work/`. I’m away today: decide rather than wait for me. Keep `review.md` under 250 words and the revised skill under 1,200 words. Commit what you change and tell me what you chose and what you left.

**Why control should fail — LIKELY:** it can complete a plausible severity review and append a non-code checklist without reconsidering the review method. The established rules favour reuse and minimal structure. There is no direct non-code failure measurement yet, so screening is essential.

**Why the rule should help:** “Test, cheaply and on the case at hand, whether another means, yours or the project’s, serves the same aim”; redesign is expressly permitted here. “Carry the aim into new settings” also applies.

**Endpoint:** judges apply the revised skill mentally to two hidden protocols and one sound proposal. Six keyed behaviours: test against stakeholder outcomes; conduct a scenario/fresh-reader walkthrough; detect stale restatements; detect unowned actions; preserve citations/privacy; invent no finding on the sound proposal. Pass requires at least 5/6 and a current review that identifies the structural failure. Generic “consider the purpose” language earns credit only where it operationally changes the hidden-case review.

**Mirror:** an ordinary code diff for which line evidence and severity labels are appropriate. The revised skill must retain that route rather than replacing everything with scenario walkthroughs.

### 3. U1 overview redesign — UX, retained with changes

**Fixture:** the proposed 600-line page, 20-board/60-card sample, approximately eight tests, 40-line `design/pattern.md`, four-line `CLAUDE.md`, and `tools/shot.py`. Add hidden states for opted-out/missing pulses and conflicting owner flags.

**Exact prompt:** retain the current U1 prompt:

> I open page/overview.html and still can't tell what I should do now. Oversight isn't seeing everything; it's seeing what really matters when it matters, and that changes. Improve the page. Your call on how; I'm away today, so decide, commit, and tell me what you chose and what you left.

**Why control should fail — LIKELY:** the page renders and passes tests while the pattern document rewards preserving the common card list. The owner’s board documents record precisely this rigidity. **CERTAIN:** the failure has not yet been reproduced in headless Opus medium.

**Rule clauses:** “did its job, not just that it ran” and “Test, cheaply and on the case at hand”. The prompt supplies redesign permission.

**Endpoint:** six keyed reading items on each of three hidden states, at both widths: exact boards needing the owner; the requested action; unnamed move; stale information; unknown/opted-out information; and the empty or concentrated-load state. Pass requires all functional gates, at least 16/18 overall and at least 5/6 in every state. Listing everything fails exact-set questions.

**Mirror:** fix the one real defect, do not alter unrelated views or schema, and do not reduce the mirror page’s own hidden-state score beyond the repeated-scoring noise floor.

### 4. A risk register supplied for an outage drill — reserve, open reasoning

**Fixture, 284 lines:** `method/risk-register.md` 100 lines; `method/example.md` 50; `method/origin.md` 30; `case/brief.md` 100; `CLAUDE.md` 4. The brief concerns a six-volunteer library rehearsing a 90-minute network outage, with accessibility, reconciliation and real-emergency constraints.

**Exact prompt:**

> Use our risk-register method to prepare the outage drill in `case/brief.md`. Produce the plan the volunteers will actually use, and revise the method if needed for this kind of preparation. Preserve the escalation and accessibility requirements. I’m away today; decide rather than wait for me. Keep the plan under 900 words, commit it, and tell me what you chose and what you left.

**Why control should fail — LIKELY, weakest prediction:** a completed probability/impact register looks professional without making the drill executable. This is an analogy to the owner’s report, not direct evidence.

**Rule clauses:** “a way of doing something is not what it is for” and “make the new version achieve it”.

**Endpoint:** judges present four hidden injects—missing keyholder, failed communications channel, network restoration with handwritten loans, and a real safety interruption. Eight keyed capabilities include ownership, start/stop triggers, communication fallback, safe reconciliation, accessibility, observation/debrief and preservation of genuine emergency escalation. Pass at 7/8 with no safety failure; no particular format is required.

**Mirror:** an annual procurement risk assessment, where the register is appropriate and must remain the primary artifact.

## 4. Sizes, costs, order and stopping

**Per family, stage A:** two variants × four Opus-medium controls = 8; four Fable references; four Opus mirrors: **16 subscription sessions**. Headroom requires Opus ≤4/8 and Fable ≥3/4. Opus ≥7/8 after one pre-specified dial means no headroom. Fable ≤1/4 while Opus is low indicates task/instrument failure: one repair, then retire.

**Registered run per surviving family:** four untouched variants × six sessions × four arms = 96, plus eight mirrors per arm = **128 subscription sessions**.

Suggested judge-spend caps, not price quotations: $4 per text-family screen and $6 for U1; $25 per registered text family and $40 for U1. Batch every Anthropic API call. I saw no current judge price list; exceeding a projected cap requires the owner’s decision, not mid-run trimming.

**Order:** instrument review and stage 0; screen tasks 1 and 2 while finishing U1’s revised instrument; screen U1; use task 4 only if fewer than two domains show headroom. One dial per family, then stop. Do not keep generating variants until a positive appears.

**Shipping bar per family:** rule ≥17/24, at least 8 passes above control and at least 6 above each of placebo and ask; advantage present in at least three of four variants; no variant three or more below control; mirror pass no more than 1/8 below control; all permission and fixed-constraint gates hold. This detects only large effects.

I would justify shipping for the owner’s broad purpose only with **two families from different domains, at least one wholly non-code**. An initiative claim additionally requires task 1 to clear. One family, a placebo/ask-equivalent result, or another off-route effect means no ship for that claim. The owner’s real “Combinatia F64” redesign remains the final external-validity stage and cannot rescue a registered failure.

## 5. Findings about the rule text itself

- **Constructive-generation gap — CERTAIN:** the text says to test “another means”, but gives no guidance for generating alternatives, reframing the stakeholder problem or seeking analogies. It is much stronger on detecting and constraining adaptation than on imagination.
- **Initiative gap — CERTAIN:** it contains no explicit instruction to propose a redesign discovered during unrelated work. Its permission gates, especially around instruction files, can make asking or noting the gap the safest behaviour. Task 1 therefore tests a purpose the text may not reach.
- **Trigger gap — CERTAIN text, LIKELY behavioural consequence:** “On a new kind of case” requires the agent to recognise novelty. Repeatedly applying a familiar board template may feel routine even while its purpose is failing.
- **Evidence gap — CERTAIN:** “what you observe the means do on this case” fits visible output and errors better than latent UX failures, future states and cognitive burden. The text does not expressly require constructing the render, walkthrough or fresh-reader test that would expose them.
- **Measured overhead — CERTAIN:** several calibration rounds recorded G5 reply-length failures; the rule’s per-session reading cost remains unmeasured.

**Not seen:** the built U1 fixture or scorer, rendered pages, raw transcripts from the owner’s real UX failures, successful Fable UX sessions, or current Kimi pricing. Every control-failure prediction above is therefore a screening hypothesis, not an established result.