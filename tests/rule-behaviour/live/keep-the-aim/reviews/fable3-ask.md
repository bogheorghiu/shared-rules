Your previous review (included verbatim) advised: stay in Claude Code, run a control-only 2x2 grid, retire K4, and replace the endpoints with designs that score the constructive half of the rule. The owner has answered (DESIGN.md, section "Exploration 2", verbatim quote). The owner chose the grid and new tasks, dropped the incident replay, and named the domain where the failure shows in practice: UX and design work on a board system for coordinating AI sessions. Three source documents from that system's repo are included; real titles and project names in them are replaced.

Answer four questions. Mark each claim CERTAIN or LIKELY, and say what you did not see.

1. **The grid (G).** Review the pre-registration in "Exploration 2" and the runner change (run_v5.py, full file and diff). Will it measure what it says? Name any defect that would void a cell or mislead a reading. Is the swap line adequate? Does `--arm none` really load no rules, given how the runner builds HOME?

2. **The owner's disagreement.** You said a blanket "ask when unsure" rule would score the same as this rule on every endpoint so far. The owner says stopping well already needs the aim/means distinction. Is there a design that separates the two claims cheaply? If not, say so.

3. **The UX family (U).** Turn the draft into something buildable, or replace it.
   - For each task: the fixture (files, sizes, what the prompt says), why Opus control should fail, why the rule should help, and the endpoint.
   - Scoring without a git oracle is the hard part. Judge the draft's proposal: mechanical checks for means-that-are-the-aim, blind pairwise judging of screenshots by another model family, a Fable-control reference arm, the owner on a blind sample. What would you keep, change or add? How do you stop judges from rewarding mere novelty, or a longer page?
   - Over-fire guard: a mirror task where the existing structure is right, so departing from it is the failure.
   - Sizes and a stop rule. Sessions in Claude Code are on the subscription; judge calls and any Fable sessions cost money (give an estimate).

4. **Anything else.** Including: whether to test the reader the owner actually uses, whether Fable control as a reference is sound, and anything in the owner's quote the design misses.

Keep the answer under about 2,500 words. Lead with the recommendation.
