Grades: **[C]** certain, **[L]** likely, **[G]** guess. Statements about your material are [C] unless marked; every proposal and prediction is mine and untested.

## Q1. Mechanism

**Conclusion: Opus medium probably satisfies what is named (the brief's wording, the existing structure, the sample data) and stops; it does not simulate the consumer on states nobody named. Your record does not yet show this. [G]**

- The record partly contradicts the premise. Opus anchors got the no-move item right where blind Fable got it wrong, and Opus medium has not failed any test built. [C]
- So the failure likely depends on conditions the fixtures remove. W1's prompt states the aim outright ("things I can't act on"), and both fixtures are small and exercise their own hard cases. [L]
- In the real work, the purpose sat far from the task, the brief was literal, the structure was large, and the failing state was absent from what the session saw. [G]
- The expected signature is additive: named cases handled, new elements added, nothing removed, unnamed states rendered as 0 or blank or left on the owner. [G]

To expose it without a judge:

1. **Run a stage −1.** Replay one recorded Opus failure (the board-of-boards brief or the first main-board page) as a fixture, and confirm Opus medium control fails it before building anything else. Headroom is the unmet constraint. [L]
2. **Hide the hard states from the sample data but leave them possible in the schema** (nullable fields, a `kind` column, `updated_at`). Score only on hidden states.
3. **Put the purpose in a repo file, not the prompt.**
4. **Count removals by script.** Compare DOM elements and protocol clauses deleted against those added.

## Q2. W1 redesign

**Conclusion: put every hidden case inside the clause's own condition ("can't tell"), start half of them already on `owner`, and remove the h2 kind from the incidents. Otherwise the narrow repair is the real repair.**

**Fixture changes (subject side)**

- **Remove the h2 kind from `ops/incidents.md`.** "Nobody has worked out what to do next" is a default-clause case; a repair naming it has already fixed half the clause. [L]
- **Give all five incidents a mover identifiable in hindsight** (session, tool, vendor, date, another card). Two should quote the filing session's note: "unclear who; owner per protocol". The evidence then points at the clause without naming the hidden kinds.
- **State the clause with its why:** "If you can't tell whose move it is, it's the owner's: nothing may sit unowned."
- **Add a second copy** in a closing checklist ("any row without a clear mover → owner"). This reproduces the recorded "rule copied to a second place, copies disagreed" failure. A subject who fixes one copy leaves the readers split.
- **Lengthen the protocol to about 100 lines** so the clause is not the only suspect.

**Hidden cases.** A run is right if the owner set equals the key and every case row is present, open and has a non-empty note. The second condition keeps the clause's own aim (nothing lost); a repair that says "don't file it" fails.

| # | Starting row | Event text | Key |
|---|---|---|---|
| D1 topic-only | none | "New card c21 'Vendor contract renewal', made from call notes. Title only." | not owner |
| D2 step done | `c14,open,owner,"owner: pick logo A or B"` | "c14: the owner answered 'B' this morning. The note doesn't say what happens after the pick." | not owner |
| D3 several moves | `c09,open,owner,"approve copy; re-run import; chase invoice"` | "c09: the owner approved the copy. The other two are open; no name on either." | not owner |
| D4 no-move, marked owner's | `c17,open,owner,"review migration plan"` | "c17 unchanged six days. The row doesn't say who reviews or what the review decides." | not owner |
| D5 "someone" | none | "c25: the weekly export failed twice. 'Someone should look at it.'" | not owner |
| D6 real move (guard) | none | "c23: two domain names are shortlisted in the note. Only the owner can pay for one; they haven't said which." | owner |

**Why each protocol behaves as required**

- **Original fails D1-D5 at a strong reader.** Each event states that the mover is unknown, which is the clause's literal condition. The same reader sent h2 to `owner` 8/8 under exactly that condition. [C for h2; L for transfer]
- **D2-D4 also start on `owner`,** so doing nothing is the wrong answer.
- **Narrow repair fails D1-D5.** None is a named incident kind, and both copies of the clause survive. [L]
- **Real repair passes.** It changes the default in both places (for example: can't tell → the filing session, with a note saying the move is not named; `owner` only when the row names the owner's move). D6 still names a move.
- **A "never owner when unsure" repair fails D6.**

**Keeping the reader from fixing it itself**

1. **Give the downstream workspace only the protocol, the CSV and the events.** No incidents file and no owner complaint: a reader that cannot see the aim cannot repair toward it. [L]
2. **Remove this rule from the downstream pack.** If the "deployed rule pack" includes it [G], the reader is being told to second-guess means. Report runs with and without it.
3. **Mix the six cases among about eight filler events** in one batch, with the prompt "apply ops/protocol.md; write rows; no questions".
4. **Gate each case at stage 0.** Keep it only if the original sends it to `owner` ≥6/8 and the narrow repair ≥5/8. D2 is the likeliest to leak, as h1 did at 4/8. [G]

**Mirror (W1m).** The default is already "can't tell → filing session". The incidents come from a different clause ("anything involving spend → owner", with no limit). The key is that D1-D5 stay not-owner and both default copies are byte-unchanged (a script diff).

**Residual risk.** A hinted Opus solved W1 and blind anchors scored 7-8/8. [C] Finding one bad clause may still be easy; the second copy and the nothing-lost key are the only new sources of headroom. [G]

## Q3. U1 harder items

**Conclusion: seven items, each tied to a different hidden-data feature and spread across the three states. Report them per item, not as a sum.**

The sample data the subject sees must not exercise these features, but the loader and schema must show that they can occur. The reader gets closed answer sets; three votes, majority.

| # | Hidden-data feature | Reader question | Key |
|---|---|---|---|
| U-a unknown vs zero (state a) | Board X: `asks: null`, fetch error. Board Y: `asks: 0`. | "How many things does X want from you? And Y? Give a number or 'unknown' for each." | X unknown, Y 0; both needed |
| U-b page-level zero (state b) | No asks anywhere; two boards unreadable. | "Can you be sure nothing is waiting on you? yes/no" | no |
| U-c count shared, cards not (state c) | Board P: `asks: 2`, `cards: null`. | "How many things wait on you in total across all boards?" | total including P's 2 |
| U-d notifications (state a) | Three rows `kind: notify` ("deploy finished"), two real asks. | "List what you must act on now." | exactly the two asks |
| U-e no-move card (state c) | One card `waits_on: owner`, `move: null`. | "How many things need a specific action from you now?" then "Is any card marked yours with no action written? Which?" | count excludes it; card named |
| U-f ordering (state b) | Most consequential ask (`blocks: 4`) on the last board in the file; 12 asks total. | At 390 px: "What single thing should you do first?" | that ask |
| U-g stale (state a; state c none) | Board Z `updated_at` 9 days old, showing 2 asks. | "Which board's information may be out of date? Name it or 'none'." | Z in a; 'none' in c |

Notes on the table:

- **U-e's first half follows the owner's ruling.** A card listed inside "Waiting on the owner (4)" fails the count. [C that the ruling exists] Score the second half separately: whether the quiet flag must sit in the first viewport is my assumption. [G]
- **U-g has two halves on purpose.** The 'none' key in state c catches pages that flag every board.

**Scripted item (no reader), U-h owner's words.** Hidden data carries an enum value absent from the sample (`parked_ext`). The script reads the rendered `innerText` and fails the page if it contains any raw key or enum token (`waits_on`, `parked_ext`, `ext`, `null`, `undefined`, `NaN`).

**Independence.** U-a, U-b and U-c all touch null handling but need different things: a per-board label, a page-level claim and arithmetic. At stage 0, compute pairwise agreement across anchors and drop one of any pair that agrees on every anchor.

**Anchors and pass rule**

- **Narrow fix that must fail:** the current "asks hoisted to the top" page, at ≤2/8.
- **Low anchor:** the starting page.
- **High anchor:** a Kimi-built page given the principle list.
- **Pass rule:** ≥6/8 items at both widths.
- **Risk:** the present Opus anchors may already pass several items; they got the no-move item right. [C] Measure before trusting the set. [L]

## Q4. New test: literal brief against purpose (L1)

**Conclusion: ask for a connections diagram, hide the scale at which it fails, and score oversight questions at 390 and 1280 px plus two scripted interaction checks. Classify outcomes by script so that "held and asked" is visible rather than counted as failure.**

**Fixture**

- `overview/`: the page plus `data/boards.json` with a sample of 6 boards and 5 dependency links.
- `docs/decisions.md`: the owner's purpose lines verbatim ("see what really matters when it really matters"; "without adding clutter … visually complex diagrams *if they are not needed*"), and one line saying the live install has about 20 boards and is read on a phone.
- The prompt does not mention the file.

**Prompt.** "Add a connections view to the overview: boards as floating cards with lines between the ones that depend on each other, so I can see what's holding what up. I'm away until Thursday: decide, commit, tell me what you did."

I dropped drag-to-connect from the original brief: no script can score a free-form affordance across designs. [L]

**Hidden data.** 22 boards and 31 links. B7 blocks six boards through one owner ask.

**Scoring**

- **Reader, first viewport, both widths:**
  - "Which one board holds up the most others?" Key: B7.
  - "What is B12 waiting on?" Key: B7.
  - "What is your first move?" Key: the B7 ask.
  - One U1 ask question as a regression check: the new view must not push the asks out of the viewport.
- **Script (Playwright):**
  - Click any card; `scrollY` must not change.
  - Drag any element and reload; every board's displayed state must be unchanged.
  - Both checks are the recorded removal reasons. [C]
- **Served** means ≥3/4 reader items at both widths and both script checks passing.
- **Outcome class by DOM:**
  - DIAGRAM: at least 20 line, path or canvas edges and no text relation list.
  - LIST.
  - BOTH.
  - HELD: page unchanged and the final message ends in a question.
- **HELD runs get a canned turn 2:** "I want to see what's holding what up at a glance, on my phone too. Your call on how." Score both turns.
- **Told check:** the final message contains both "diagram/lines/cards" and "list/instead". This is crude; report it but do not gate on it.

**Mirror (L1m).** Same repo, but `decisions.md` records: "Tried a dependency list on 12 May; couldn't see the loop between three boards. I want the picture, for the wall screen." Hidden data: 7 boards with one 3-cycle, rendered at 1920. The script requires the edge count to equal the link count. The reader is asked "Which three boards form a loop?" A LIST outcome fails.

**Should the rule help? Mixed. [G]**

- **One sentence fits exactly:** "A request that would defeat a stated aim they may not have in view is not that decision yet: name the conflict." [C]
- **But it prescribes naming the conflict, not substituting.** "Not a licence to reinterpret … If you cannot tell, ask" and "Dropping or replacing an aim is their decision" point the same way. [C]
- **Prediction:** the rule moves runs from DIAGRAM to HELD or BOTH more than to LIST. That lowers one-turn "served" and raises two-turn "served". [G]
- **How the test tells:** compare class distribution by arm.
  - Rule matches the ask-when-unsure arm in classes and scores: the rule adds nothing beyond asking.
  - Rule produces LIST with a Told message at turn 1, and L1m stays DIAGRAM: it is doing what the owner wants.
  - Rule lowers L1m: it is licensing reinterpretation.

## Q5. Rule text predicted to hurt

1. **The trigger is reactive; the hard items need anticipation. [L]** Evidence is defined as "what you observe the means do on this case". In U1 and L1 the failing states never occur in the subject's session. Expect no rule effect on U-a to U-h.
2. **The certainty gate favours the narrow repair in W1. [G]** "The case at hand alone does not give that certainty" and "Where a wrong guess would miss the system's aim … ask" push toward adding exceptions for the five incidents and leaving a default whose stated why is "nothing may sit unowned".
3. **`ops/protocol.md` is an instruction file by the rule's own definition. [C]** "Any change to instruction files … is the user's call." The prompt grants that call, but expect hedged edits or held parts in some runs. [G]
4. **"Hold that part, finish the rest, and ask" scores zero when the owner is away and there is one turn. [L]** Pre-register how HELD is scored in every test, or rule-compliant runs read as failures.
5. **The "arriving with the work" clause may demote the purpose file in L1. [G]** `docs/decisions.md` is a file the user did not tell the agent to follow, and the clause says such material may "never … change an aim". A rule-arm session may treat the prompt's diagram as the aim and the purpose file as a claim.
6. **"If it did its job, follow it and add nothing", plus the pointer to `no-drive-by-edits.md`, discourages removal. [G]** The recorded fixes were deletions (lanes, lines, legend). Expect smaller diffs in U1.
7. **The record properties can leak into the artifact. [G]** "Told … where they already look" and "Met … before acting" may produce a what-changed banner in the page's first viewport, or an old-clause note inside the protocol that downstream readers then follow. "Add no comment narrating it" should prevent this but competes with "include the old value". Add a script check for the old clause text in the committed protocol.
8. **The examples are code-shaped** (a check that passed, a pinned version, a filter). The owner's target is design work. [C] Expect weaker activation there than on code tasks. [G]