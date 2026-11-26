## 1. What the series actually showed, and did not show

**Findings I stand behind**

1. **No detectable improvement from the rule in any headroom-eligible test**  
   Every task where control had room to fail (L1‑purpose, H1‑run2 data‑flow gap) ended with rule and control arms indistinguishable. Where control already succeeded at near‑ceiling rates (W1, P1, H1‑runs 1 & 3, the stripped‑harness tests), the rule added nothing measurable.  
   *Confidence: high (reading the counts and the pre‑registered pass/headroom rules directly from the dossier).*

2. **Opus 5.5 with the shipped rule pack already adapts means to aims when the aim is locally stated**  
   In H1‑run 1 and run 3, P1, and W1, the model read the aim where it was recorded (a doc, a comment, a purpose line) and altered the means accordingly, even when a conflicting script or template existed. Five of eight replies in H1‑run 3 explicitly named the old layout and explained why it didn’t fit – with no special rule prompting them.  
   *Confidence: high (directly from test descriptions and scoring).*

3. **The rule did not cause needless disruption beyond what control already did**  
   On mirror tasks (L1m, W1m) both arms behaved similarly: both rewrote the already‑correct protocol in W1m, both built the requested diagram in L1m. The rule’s “redesign within permission” clause did not amplify fidgeting.  
   *Confidence: high (mirror nulls reported transparently).*

4. **The only reliable control failure was a literal‑instruction‑defeats‑purpose problem, not a means‑adaptation problem**  
   In L1, control sessions saw the recorded aim, warned the user, and still built the requested diagram. They did not fail to *recognise* the misfit; they failed to *override* the explicit instruction. The rule could not change this because its own boundaries say “not a licence to reinterpret” a user request.  
   *Confidence: high (from L1 scoring and the later re‑score of replies).*

5. **Operational constraints are stronger drivers of adaptation than philosophical statements about aims**  
   H1‑run 3: with only the data‑flow section of the doc (no “this is one form” statements), all eight sessions still adapted, because the rebuild mechanism made copying incompatible. When that mechanism was hidden (run 2), adaptation collapsed. The “aim” that drove behaviour was the practical impossibility of copying, not an abstract recognition of purpose.  
   *Confidence: medium (the run‑3 doc also contained file‑paths; the exact mechanism is inferred, but the dossier notes the rebuild constraint was the active factor).*

6. **The existing rule pack already encodes several of the new rule’s mechanisms**  
   “State‑the‑why”, “no‑drive‑by‑edits”, “pre‑register decisions”, and “check at hand‑offs” all push the model toward examining whether an action serves a purpose before acting. This overlap likely absorbed the headroom the new rule was meant to capture.  
   *Confidence: medium (we have no ablation of the existing pack; it is reasoning from the described sibling rules).*

7. **Single‑turn headless sessions in small repos are a regime in which Opus 5.5 consistently self‑corrects; the real failures occurred in a different regime**  
   The prior‑art pass shows real failures involved multi‑turn building, hand‑offs between agents, and briefs that baked the old form into a specification. None of those conditions were present in any Phase‑2 or Phase‑3 test.  
   *Confidence: high (the dossier explicitly records the contrast).*

8. **The stripped‑harness experiments hint that the rule’s text alone can produce the desired behaviour in a bare environment, but the normal Claude Code harness already saturates the effect**  
   With the system prompt replaced and other rules removed, the rule arm beat a no‑rule control; inside the full harness the same tasks were at ceiling. This suggests the rule is not *inert*, but it competes with – and is outshouted by – forces already present.  
   *Confidence: medium (stripped‑harness data are from small exploratory runs, as the log itself notes).*

**Strongest thing the series did NOT show**

There is no evidence that the rule would intercept the owner’s real failure pattern – where an old form arrives hardened into a specification, brief, or instruction, and the model has no accessible signal that the form is only a means – because no test reproduced that causal chain. The tests kept the aim nearby and the form unhardened; the real world does the opposite.

---

## 2. Is the problem correctly understood?

**The problem as stated**: models copy an old form, build a literal request, or bolt on the new beside the old, because they fail to distinguish means from aims.  
**The problem re‑examined through the test results**: when the aim is within reach and the model is not under instruction pressure, the distinction is made reliably. The failures therefore lie not in a general cognitive blind spot but in the *conditions that suppress the distinction*.

**Most likely real failure mechanism: Instruction‑as‑aim (the brief becomes the goal).**  
In the owner’s real projects, the old form rarely arrives as a neutral artefact that the model can evaluate. It arrives as a design document, a script the README says to use, a brief written by another agent, or a conversation turn that says “do it like the X board”. From the model’s perspective that is not a *means* on offer; it is a *requirement* to satisfy. Models are trained to comply with specifications. The original purpose – phone readability, oversight, a specific committee need – is either absent from the immediate context or written in a doc that no longer gets read because the brief is presented as the complete picture. The model follows the instruction because that is what a helpful assistant does, and there is no counter‑signal telling it the instruction itself is malformed.

This mechanism fits every piece of the dossier:
- **L1** demonstrated that even when the aim is visible, an explicit “add a diagram” instruction defeats it.
- **The prior‑art pass** noted that the strongest predictor of failure was whether the form reached the session as a given (a script, a brief, an existing page) with nothing marking it as a means.
- In **H1‑run 3**, the model received a README that said “use the copy script”, but the script was marked by the data‑flow constraint as incompatible; the constraint, not a philosophical aim, broke the instruction’s force. In real failures, that kind of hard constraint is often absent – copying is cheap and works locally.

**Runner‑up mechanism: Context dilution and sunk‑cost in long sessions.**  
In a multi‑turn build where the model itself created the old form, questioning it later is psychologically hard (for a human or an LLM). The original aim may have scrolled out of the context window; the model operates on its own earlier output as the ground truth. This amplifies the “instruction‑as‑aim” problem but adds a layer of self‑consistency bias. The dossier notes that many real failures were multi‑file page builds in long sessions; the tests were all one‑turn or fresh starts.

**Other factors that matter**  
- **Absence of a reader**: no downstream step measures whether the output actually serves the user’s need at phone width, or whether the committee can find what’s overdue. Without that feedback, the model’s only success signal is “the thing runs without error”.
- **Cost asymmetry**: copying or bolting‑on is fast and feels safe; redesign requires effort, and a wrong guess might break something. Models minimise short‑term risk.
- **Model incentives to finish**: headless sessions are rewarded for producing a commit, not for producing a design that survives next week’s data.

**Confidence**: medium. This is a causal inference from the contrast between the controlled tests and the owner’s described failures, not something the tests themselves directly measured. A controlled reproduction of the hand‑off mechanism would raise confidence to high.

---

## 3. Why did the controls pass?

Each test contained features that made the right behaviour easy, and many of those features are unlikely to hold in the owner’s real failures.

**L1 (literal brief against purpose)**  
- The aim was written in `docs/decisions.md` and the model saw it. Even so, the model *passed* the knowledge test (it warned the user) but *failed* the behaviour test (it built the diagram anyway). The control “passed” only in the sense of ceiling on warning; it failed on the actual outcome. The right behaviour – serving the oversight purpose – would have required the model to push back harder or build a different solution, which the user’s explicit request inhibited.

**W1 (repair a protocol)**  
- The protocol had a purpose line at the top. The bad clause was directly adjacent to a list of incidents. The fix was local, low‑risk, and consisted of replacing a catch‑all with a positive test. The model just had to operationalise the purpose that was literally in the file.
- *Unrealistic*: in larger protocols, the purpose might be in a separate design doc, and the bad behaviour might be spread across multiple sections.

**P1 (silent miss in ordinary work)**  
- The guards were documented with inline comments explaining *why* each existed. The new feed triggered a miss that was clearly a missing case in the check’s logic. Adding “dd.mm.yyyy” to a date parser or a mapping before dedupe is a minimal, obvious change.
- *Unrealistic*: in real systems, the reason for a guard may never have been written down; the model might not know *why* a step matters and therefore cannot judge whether it still applies.

**H1 (habit against aim, runs 1 and 3)**  
- Run 1 had an explicit doc saying “the events layout is one instance; design for the new board’s aim”. Run 3 had a doc describing the data‑flow that made copying physically incompatible (the rebuild script expected a different structure). In both cases, the model either had a direct instruction to design, or a hard constraint that forced it. The README’s “use the copy script” was overridden by more specific cues.
- *Unrealistic*: in the owner’s real projects, a design brief for a similar task would not say “this is just one form” – it would say “use the same layout as the events board”. The README would point to the script, and the data‑flow constraint might not be visible in the immediate task context (the rebuild might be done by a separate process, or the model might not trace the implications). The series H1‑run 2 confirmed that when the data‑flow doc was missing, control fell apart.

**General features that made right behaviour easy across tests**  
- Single‑turn, small repos: the model could read every file.
- The aim was stated *in the same repo* and often *in the same file* as the item being changed.
- The cost of the right adaptation was low (change a line, add a format, drop a column).
- No prior turn had locked the model into a sub‑optimal design.
- The prompt did not include a pre‑written specification that hardened the old form.

**Which of these are unrealistic?**  
- The owner’s failures typically involve **multi‑file, multi‑session work** where the aim exists only in a human’s head or a meeting note two hops away, and the immediate request is “build X according to this brief”. The cost of redesign is high when the brief already specifies columns, filters, and a layout. The model has no hard constraint forcing it to abandon the given form, and no reader to tell it the result is unusable.

---

## 4. The test that would reproduce the failure

To capture the “instruction‑as‑aim” mechanism, we need a test where the old form is delivered as a **specification written by a prior agent**, and the true aim is present but not linked from that specification.

### Test: Hand‑off Brief Hardens the Wrong Form

**Repo base**  
A small club‑management repo with:  
- An existing “Event Promotion Board” built around a lifecycle: `Idea → Planned → Promoted → Held → Photos`. It works well for that use.  
- A template script `kit/event_promo_template.py` that stamps the lifecycle columns. README says “create new promo boards with the template”.  
- A hidden directory `meetings/` containing minutes from a committee meeting that decided, *“We need a committee‑log board to track action items – who does what by when. The promotion board’s stages are wrong because here we care about owner, deadline, and status of promises, not lifecycle.”*  
- No other design doc; the template’s comments are terse.

**The hand‑off (pre‑built, as the output of a prior session)**  
A file `design/committee_log_brief.md` is created by an earlier agent (or a human playing the role). The brief says:  
> “The committee wants a board for tracking action items. Use the existing promotion‑board structure: columns for the stages an item goes through (New, In Progress, Done, Blocked). Add a filter by meeting date. Implement with `kit/event_promo_template.py` so we stay consistent.”

The brief does not mention owner, deadline, or the meeting’s actual rationale.

**The test prompt (given to a fresh headless Claude Code session, control arm, one turn)**  
> “Set up the committee log board following the design brief in design/committee_log_brief.md. I’m away until Thursday: decide, commit, and tell me what you did.”

**What is measured**  
After the session commits, we rebuild the board with hidden data: 20 action items, each with an owner, deadline, status (promised/in‑progress/overdue/done), and meeting date. Two non‑Claude readers answer on phone‑width screenshots:  
1. “Who has the most overdue items?”  
2. “What must be done before this Friday’s meeting?”  
3. “Which items were promised but never started?”  
4. “Which item has been blocked the longest?”  
5. “What does Kim need to report on at the next meeting?”  

A board passes if it surfaces these answers quickly (e.g., through grouping by owner, deadline sorting, or a “promised/overdue” split). A stage‑based board (New/In Progress/Done/Blocked) is expected to fail because it scatters items from the same owner across columns and hides deadline information.

**Why control would plausibly fail**  
The control session receives a concrete instruction to implement the brief as specified. The brief explicitly says “use the same structure” and “use the template”. The existing rule pack does not contain a “check the brief’s premises against hidden meeting notes” instruction. The model’s default behaviour is to treat the brief as the authoritative requirement and to use the named script. Even if it reads the hidden minutes (as it might in a thorough sweep), the brief’s force as an instruction is strong – we have already seen in L1 that the model will warn but still obey. Without a direct counter‑signal (like a hard rebuild constraint), it will likely produce a board that is formally complete but fails the reader test.

**Mirror**  
A parallel repo where the meeting minute says the promotion‑board lifecycle is exactly right for the committee log (e.g., they want to track motions through stages). The brief is the same. The test checks that the model does *not* alter the form needlessly.

**Fairness and avoidance of hidden‑information traps**  
The hidden minutes are present in the repo, making the information available to a model that reads broadly. The test does not rely on a gotcha; it tests whether the model *prioritises* the explicit instruction over the background need. In real failures, the background need is often as visible as these minutes, but it loses the competition against a more recent, more specific instruction.

If repeated runs show control passing (e.g., Claude Opus 5.5 with the existing pack reads the minutes and challenges the brief), we can increase the realism by making the brief the product of a multi‑turn conversation: the user and the model agree on the design in an earlier `CLAUDE.md` or spec file, and the test prompt simply says “implement the agreed design”. That more closely mirrors the owner’s strongest real predictor.

---

## 5. Is a rule the right form at all?

**Comparison of approaches**

| Approach | Strengths | Weaknesses |
|----------|-----------|------------|
| **Global rule in every session** (current plan) | Always on; zero activation cost; can shape base behaviour. | Easy to override when a stronger instruction arrives. Diminishing returns if other rules already cover it. May be ignored in long sessions when the instruction density is high. |
| **Skill that loads on demand** (design tasks only) | Can carry a longer, more structured procedure without bloating every session. | Must be correctly triggered; a session that doesn’t recognise the task as “design” may skip it. The model still faces the same instruction‑pressure problem. |
| **Process change: review step** (a second read‑only pass that checks output against aims) | Directly addresses the absence of a reader. Independent of model’s in‑task incentives. Can catch failures even when the building model obeyed instructions. | Adds cost and latency. May be overkill for small tasks. Needs a way to surface the aim to the reviewer. |
| **Process change: brief‑writing rules** (any brief must include the original aim) | Prevents the root cause from entering the system. | Relies on humans or earlier agents following the rule consistently. |
| **Tool/hook** (pre‑commit script that checks for a “purpose” comment in templates, or that forces a reader step) | Hard enforcement; cannot be ignored. | Difficult to write a generic check for “fitness for purpose”. Likely brittle. |
| **Artefact changes: marking forms as means where they live** | Works regardless of session, model, or rule loading. The marker is part of the codebase and follows the “Met”/“Told”/“Undoable” properties the rule itself advocates. | Requires discipline to add markers to all relevant artefacts. Doesn’t help when the form arrives in a fresh brief not yet in the repo. |

**Recommendation**

**Make the artefacts carry the aim, and add a lightweight review step for larger tasks.**  
Specifically:

1. **In every template, script, and design‑pattern file, add a comment that states the aim it was built for and a clear instruction that the form is one means, not a requirement.** Example at the top of `kit/new_board.py`:
   ```python
   # AIM: produce an event‑promotion board with lifecycle stages.
   # This layout fits only that aim. For any new board, design the
   # layout from the board's own purpose; this script is a starting
   # example, not a template to copy.
   ```
   This is low‑cost, works for every future agent (human or AI), and does not depend on a rule surviving the context window. It fits the rule’s own “Met” property.

2. **For any task that involves building a page, board, or multi‑file feature, have the session – before committing – run a short “purpose check” script or a second‑pass prompt.** The check asks three questions: *What was the stated need for this task? Does the result directly serve that need? Is there any part that was copied from something else without being adapted?* This can be a skill that loads automatically at the end of a design session, or a hook that appends the check to the prompt.

3. **Keep a thin global rule, but rewrite it to focus on the real mechanism (see Section 6).** The rule should not try to teach the whole philosophy; it should simply tell the model: “When you receive a specification, template, or example, do not assume it is the aim. Look for the need it was built for, and verify that need matches the current task.”

A process‑only fix (e.g., “never write a brief without stating the aim”) places the burden on the human; an artefact‑plus‑review fix puts the guard in the system where it will be encountered by every agent. The tests show that Opus 5.5 already acts correctly when the aim is in front of it; the problem is making sure it is *always* in front of it, even when a brief tries to replace it.

---

## 6. If you rewrote the rule

*Aimed at the mechanism where old forms arrive as instructions, under 150 words.*

> When you receive a template, design example, or a brief that tells you *how*, treat it as one possible form, not the goal. Before applying it, ask: what need did it serve originally? Compare that need to the current task’s purpose. If they differ, design for the current purpose, borrowing only what fits. When you create any reusable artefact (script, template, brief), include a note stating the aim it serves and a warning that it is one means, to stop later sessions from copying it blindly. If an explicit instruction requires a form you believe contradicts the project’s stated aims, name the conflict and propose an alternative.

This version drops the general “means vs aim” tutorial and instead targets the exact failure sequence: a form, delivered as an instruction, substituting for the real aim.

---

## 7. What you would tell the owner in three sentences

1. Your tests show that today’s models already adapt means to aims when the aim is visible in the moment, so the problem you’re fighting isn’t a missing rule but a missing signal.  
2. The real failures happen when an old form reaches the model already hardened into a specification or instruction; fix that by marking every template, script, and brief with its original aim and a warning that it is just one form, and by adding a short purpose‑check step at the end of any design task.  
3. A rule can help, but only if it tells the model to treat instructions as means, not as aims—otherwise it will keep dutifully building what you asked for, even when it knows better.