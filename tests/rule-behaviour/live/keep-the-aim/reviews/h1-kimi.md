### 1. H1 reproduces the setup, but only partly the failure

The three surface conditions are present: an aim-only prompt, an unrejected prior board, and docs saying the form is only one instance. But:

- **The instruction has moved into the repo.** `pattern.md` says what to do three times and adds aim-first questions; `notes.md` closely previews the evaluation questions. This largely tests repository exploration and instruction following, not the owner’s habit under an underspecified request.
- **It is not obviously “complex enough.”** A small second-board fixture with a generic renderer is straightforward. Forty hidden tasks make evaluation denser, not the agent’s design task harder.
- **Copying is made too obviously wrong.** One-owner/laptop/sessions versus four-person/phones/committee is a stark mismatch. The original failure needs a plausible, accepted prior form with useful properties worth preserving—not merely an old example that is easy to reject.
- **F2 is weakly elicited.** The prompt contains no concrete subtask, such as importing tasks, that an agent can complete literally while avoiding the design problem.
- A single fixture can measure a default response, not the cross-iteration habit itself.

### 2. A strong no-rule model would probably pass often

It can find everything through ordinary exploration:

- `docs/pattern.md`: the adaptation instruction and design questions;
- `boards/allotment/notes.md`: phones, weekly use, ownership, deadlines and council blockers;
- `boards/studio/` plus `kit/board.py`: schema, implementation approach and prior art.

That is enough to produce a mobile weekly/ownership/exception view without the rule. H1’s proposed headroom gate may well fail.

Keep discovery fair: **do not hide the notes or require lucky file reads**. Instead, remove solution leakage—especially the extra aim-first checklist and any wording that mirrors scoring. Retain the naturally repeated “one instance” statements because they are part of the owner’s setup. Make the notes realistic minutes or correspondence requiring synthesis, with some genuine trade-offs, rather than a compact acceptance checklist. If controls still pass, accept the null result rather than manufacturing difficulty through obscurity.

### 3. The scoring is useful, but neither sufficient nor non-gameable

Hidden-data rendering and factual reader questions are the strongest parts; the mirror is a useful guard against indiscriminate redesign. However:

**False passes**

- Four attractive summary panels answering watering, overdue, Dana and council could pass while leaving the other tasks effectively inaccessible or the board impossible to maintain.
- Renaming sections or adding nominal grouping can escape `COPY`/`LITERAL` without improving usability.
- `FIT` is only a residual structural class: it does not establish aim-led adaptation. A generic mobile dashboard can pass without engaging the prior art.
- The final `Told` statement can be boilerplate and does not verify the reasoning—or the rule’s timely-notification requirement.

**False fails**

- A well-sorted, well-designed flat list may be the best phone interface but is automatically `LITERAL`.
- Good progressive disclosure may require a tap or more than one scroll.
- “This week’s items on the first screen” prescribes one means; another design may correctly prioritise overdue items or conflicts.
- A legitimate schema/renderer improvement could fail a harness coupled to the old representation.

Thus `COPY` and `LITERAL` are useful diagnostics, but poor pass/fail gates. The mirror does not fix these construct-validity problems.

### Top 3 changes

1. **Make the fixture faithful rather than more leading.** Mark Studio as accepted and in use; preserve some genuinely useful properties. Replace the requirement-like notes with realistic source material, remove the aim-first checklist, and add a neutral concrete chore such as importing `tasks.csv` so F2 has something literal to satisfy. Keep the design request otherwise aim-only.
2. **Score use, not shape.** Use a held-out bank of reader scenarios over multiple hidden datasets, measuring accuracy plus time/taps/scrolls, and check that all tasks remain reachable and a reassignment/update works. Demote `COPY/LITERAL/FIT` to diagnostics. Add anchors for a good flat design and an attractive but cumbersome bespoke design.
3. **Keep the mirror and enforce the headroom gate.** In H1m, pass any means that efficiently preserves Studio’s original answers, not only literal copying. Run strong no-rule controls first; if they pass beyond the threshold, discard or redesign H1 rather than hiding information. Verify reports against the diff/trajectory instead of scoring self-description alone.