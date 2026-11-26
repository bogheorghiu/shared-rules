# Name a state by what it is now — never relative to another version

**The failure mode.** Labels, buttons, status lines and summaries written as corrections
to an earlier version of the thing: "What-if: 1 reason set aside · not your rules",
"Back to your rules", "Changed from default", "Undo", "No longer Choosing", "Was within,
now above". Each one makes the reader rebuild the history to understand the present: what
"your rules" were, what the default is, what was undone. They pile up as a chain of
corrections over versions the reader may never have seen, and they define things by what
they are not, which says nothing about what they are. The reader has to hold two states in
mind to read one.

**The test, applied per label:** could a reader who never saw any earlier version say what
this state or button is, and what pressing it does, from the words alone? If the words only
make sense against another version ("not", "back to", "un-", "changed", "no longer",
"previous"), rename it by what it is now.

**How to apply.**

- **Name each state positively, as a thing in its own right.** Two settings the reader owns
  both are "theirs": call them by role, not by ownership or by negation. Example (an
  exclusion-reasons panel, 26 Nov 2026): "Saved exclusions" and "Preview · 18 of 20 reasons
  on", not "your rules" and "not your rules".
- **Name each action by its result.** "Save these exclusions", "Close preview", "All
  reasons on" (a named starting set the reader can preview and save), not "Back to your
  rules" or "Undo".
- **A change is reported as the new state plus its cause, dated**, not as a diff:
  "Above your limit since 26 Nov: holdings updated" rather than "was within, now above".
  Where the previous state matters to a decision, show it as a dated line in a record the
  reader opens, not in the label.
- **Same for documents and handoffs.** A spec, brief or report states the current design
  as it stands; corrections are folded in, not appended as "Update:", "Correction:",
  "v2 changes" sections stacked over the old text. The change log, if needed, lives in its
  own place (history, commit messages, a dated log), never in the reading path.

**Boundaries, so the rule doesn't over-fire.**

- **Provenance stays.** "Excluded by your ruling of 23 Nov" names a cause and a date; that
  is the present state of knowledge, not a correction chain. Keep it.
- **A correction to something the reader already acted on is owed and stays visible**
  until acknowledged: a figure they used, a decision they made on it. Say it once, plainly,
  where they will see it; then fold it into the current text.
- **History views are allowed to be historical.** A log, a diff viewer or a "what changed
  since your decision" filter exists to show change; the rule governs labels and reading
  text, not tools built to compare.
- **Negation is fine when it is the state itself.** "Not for me" is a decision the reader
  made, named in their own words; "Can't buy" is a fact. The test is whether the words
  need another version to be understood, not whether they contain "not".

**Why.** A label is read in the present by someone who may have missed every earlier
version; each relative label taxes that reader with reconstructing history, and
correction-chains grow with every revision. Naming by present role scales: the text stays
the same length however many versions came before. It is also the honest form: the
present state of knowledge, not the biography of it (the owner's preferences, CORE).

**Lineage.** Plain-language and UX-writing practice (name controls by their effect; avoid
double negatives); the "single source of truth" habit of folding corrections into the
document. Observed case: Funds Desk redesign, Applied Post-Capitalism project, 26 Nov
2026 — the owner rejected "What-if: 1 reason set aside · not your rules" and "Back to
your rules"; two independent model reviewers (Gemini 4 Neon, Kimi K3.1 Pro), given this
principle, both produced "Saved exclusions / Preview / Save these exclusions / Close
preview / All reasons on".

**Siblings.** `state-the-why.md` (a decision carries its reason; this rule says the
reason and the state are named in the present). Possible overlap with staged
`keep-the-aim.md` and `details-yield-patterns-persist.md`: those keep the aim when details
change; this keeps the reader's wording free of the details' history. Whoever reconciles
the staged set should treat this file as the latest example of the pattern.

**Ship check (to be pre-registered before shipping).** Proposed: in a blind A/B on 10
interface-copy and 10 spec-revision tasks, the rule arm produces relative or correction-
chain labels in at most half as many items as the control arm, with no loss of required
provenance lines.
