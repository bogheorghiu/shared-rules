# Board-pattern learnings relevant to keep-the-aim (2026-11-17)

Provenance: a Sonnet subagent read `bogheorghiu/board-pattern` at `fe4e229` (commits since 2026-11-08:
design/owner-pages.md, representation.md, board-family.md; explore/ux-pass-2026-11-11/*,
explore/board-of-boards/brief.md, explore/ambient-ai*; rules.md; pattern.md; ops/mine-trial.md) and returned
the distillation below. Spot-checked at the source by this session: the waits audit classes MOVE/UNNAMED/NOT_OWNER
(waits-audit.md), the owner's 2026-11-11 quote (ux-pass brief.md l.14-17), "Oversight is not 'see everything'"
(board-of-boards/brief.md l.18), and commit 028bece's account of the removed floating-card map. Not checked: the
model attribution of individual commits (028bece's author field reads "Claude"); every other line is the
subagent's reading, UNRESOLVED until used. It is the input to `reviews/design9-ask.md` §3.

## Why it bears on the test
- The owner's own failure case (UX and board work) has a record: designs that followed the brief's literal
  structure (floating cards with connections) or the existing structure, added copies and features where a
  pointer or a removal sufficed, and missed states nobody named (unknown counts, cards with no move named,
  stale reads). That is the "means followed, aim missed" failure the rule names.
- The waits audit gives the real distribution W1 is about: of 65 cards marked as the owner's, 39 real moves,
  11 with no move named, 15 not the owner's (session or tool work, waiting on time or another item). Patterns:
  blocked or session-side work marked as the owner's; topic-only cards; several moves in one row; a card left
  on the owner after its step was done.
- No page-design comparison between Fable, Opus, Kimi and Sonnet is recorded in that repo (not found in the files
  read). The owner's "Fable succeeds, Opus falls short" stands on the owner's word, not on a recorded A/B.

## Principles, failures, owner statements, tensions, reusable fixtures
See `reviews/design9-ask.md` §3 for the checked subset sent to the models. Reusable fixtures in that repo:
`explore/ux-pass-2026-11-11/gate-fixture.json` (synthetic rows incl. an UNNAMED owner card),
`explore/board-of-boards/fixture.json` (23 registry rows, 19 pulses with null/stale/partial counts),
`explore/ux-pass-2026-11-11/waits-audit.md` (labelled classes by board, ids only),
`explore/ambient-ai/run-2026-11-16/research/X-attention-personas.md` (seven personas, usable as a rubric).
