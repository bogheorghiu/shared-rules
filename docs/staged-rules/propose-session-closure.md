# Propose closing the session — work each session toward its end

**The failure mode.** A session with no finish line. It starts on one task, absorbs the
next, and the next, until nobody can say what it is for. Two things degrade together.
The *context* does: older decisions get compacted or crowded out, and the session acts
on a blurred copy of what it was told. The *operator* does too: an open session is an
open loop, something they have to remember, re-read and steer, and a pile of half-done
sessions costs attention even while nobody is working in them.

**The stance: a session is an inbox item, designed around closing it.** Opening it means
taking on one job; finishing that job means closing it, not looking for the next one to
put in it. This is the single-responsibility principle applied to sessions: one session,
one reason to exist. The aim is short, effective, to-the-point work. The aim is never
speed: a session closed early with its job half-verified only moves the open loop
somewhere harder to see.

**How to apply.**

- **At the start, name the closing condition**: one sentence on what "done" means here.
  When it is unclear, ask, since a session can't close on a goal nobody stated.
- **Work toward it.** Out-of-scope finds become notes, issues or board items, not
  extra work in this session (`no-drive-by-edits.md`).
- **Propose closure at a seam when a signal fires**, never mid-step:
  1. the closing condition is met and verified;
  2. the work has turned into a second, separable job, so the rest belongs in a new
     session;
  3. the context has grown heavy: it has been compacted, or you are re-reading what
     you already read to recover decisions;
  4. what is left is waiting on something outside the session, and nothing else is
     left to do.
- **A proposal is one short line with its reason and a ready handoff:** the state, the
  pointers (files, PRs, decisions) and the next action, written so a fresh session
  can start from it alone. Check that handoff against its sources, not against your
  memory of them (`falsification-station-per-handoff.md`).
- **Propose; never enforce.** The operator decides. If they decline, carry on and stay
  quiet until a *new* signal fires: repeating the same proposal is nagging, and nagging
  is the attention cost this rule exists to cut.

**Boundaries, so the rule doesn't over-fire.**

- **Length is not the signal; coherence is.** A long session on one hard job (a deep
  debugging session, say) is fine. A short one doing three unrelated jobs is not.
- **Closing never skips the finish.** Tests, verification and the stated why come
  before the proposal, not after it.
- **Open work stays reachable.** With a PR or a running job still open, the proposal
  says who will watch it, or the session stays open until it is handed over.
- **One-shot exchanges** (a question and its answer) have nothing to close. Don't
  propose there.

**Lineage.** *Getting Things Done* (David Allen): an open loop holds attention until it
is closed or written down somewhere trusted. The inbox framing comes from how a T3 Code
developer described its sessions view: an item you open is designed around closing it
(the user's paraphrase, not a checked quote). Single responsibility comes from Robert
C. Martin's SOLID principles.

**Siblings.** `no-drive-by-edits.md` and `no-speculative-structure.md` keep a session's
scope to what was asked; this rule ends the session once that scope is met.
`falsification-station-per-handoff.md` covers the handoff a closure produces.
