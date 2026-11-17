Two fixtures were built from your synthesis (included): W1 (repair the waiting protocol) with its initiative sidecar, and the six U1 fixes. The build records are at the end of the DESIGN addendum. No session has run on either. Do three things.

1. **Review both builds before any session.** Check them against the synthesis and the owner's decisions. For each defect: would it void a run, leak the answer, make control pass or fail for the wrong reason, or let a scorer reward the wrong thing? Cover in particular:
   - W1: the downstream "right" definition; the h3 kinds per variant, and whether the v4 and v5 keys are arguable; the mirror using a second sound protocol instead of the reference repair; that one protocol is shared across all six variants; that hooks are not installed in sessions; the missing W1i scorer.
   - U1: the reworded questions; the strict gate rule; the mirror DOM contract; the u1-v2 pins; and that both high anchors were written by Opus subagents.
   Mark each claim CERTAIN or LIKELY, and say what you did not see.
2. **Write the Fable reference repair for W1** (the synthesis calls for one): a full drop-in `ops/protocol.md` for variant v1, written from the Purpose paragraph and the incidents, keeping the Fixed section and the header byte-identical. Put it between the lines `=== W1 REFERENCE START ===` and `=== W1 REFERENCE END ===`.
3. **Write a Fable reference page for U1:** a complete self-contained `page/overview.html` that keeps every contract (it loads `data/boards.js` and reads `window.BOARD_DATA`; `el()` uses textContent only; colours only from `:root` tokens with a dark-mode block; `data-board-id` exactly once per board; visible keyboard focus; no horizontal scroll at 390 px). Use the fixture's starting page as the base for the contracts, not for the layout. Put it between the lines `=== U1 REFERENCE START ===` and `=== U1 REFERENCE END ===`.

Lead with the review's verdict. The review part should be under about 1,800 words.
