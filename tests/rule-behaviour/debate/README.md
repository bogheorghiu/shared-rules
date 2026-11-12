# Debate on the closure rule's framing (2026-11-12)

After the null result (`../PREREG-2026-11-11.md`), the maintainer set three things:

- The floor for readers is the mid-tier session model. A small model is orchestrated by
  other models and does not run sessions, so it is the wrong reader for these rules.
- The rule's point is context efficiency in sessions that really are getting things
  done: accumulated context costs on every turn, and scoping a sub-task to its own
  context can be cheaper and sharper. The written test conversations were artificial
  because nothing in them had accumulated.
- Where a long session is justified is what the rule's framing should let the model
  decide well; the answer to "this is a workflow preference" is a better framing, not
  an opt-in switch.

One reviewer (`anthropic/claude-opus-5.5`) had called the rule a workflow preference.
These files are the exchange with that reviewer on the maintainer's answer:
`brief-1.md` and `opus-1.md`, then `brief-2.md` and `opus-2.md` (generation ids in the
`.meta.json` files).

Where it ended:

- **Agreed.** The claim that belongs in a default pack is about the quality of the
  picture the session acts on, and about what a sub-task adds to every later turn. Both
  can be acted on without seeing the user's bill. The first move is internal (run a
  sub-task whose working you won't need in a fresh context); offering a fresh session is
  the rare, user-facing move.
- **Conceded by the session.** The question "does the next work draw on this context?"
  does not protect a user who keeps one session open as a workbench for unrelated
  chores. The decline rule and "neither length nor an unrelated next task is reason
  enough" do.
- **Conceded by the reviewer.** Token cost is not only a billing matter: a sub-task's
  working stays in the context whatever the price of re-reading it. And a decline does
  not waive one warning that an uncontrolled cut is close, since automatic compaction is
  silent.
- **Left open.** Whether a fresh start ever beats continuing in a polluted but relevant
  context, and whether handoffs keep enough; the cut-down test below cannot show either.

The rule text that came out of it, lightly edited into this repository's pattern, is
`docs/staged-rules/keep-context-to-the-work.md`. It is an untested draft.

Claims in the exchange about harness behaviour (prompt caching prices, silent automatic
compaction, what a session can see of its own size) are the participants' statements,
not checked against any harness's documentation here.
