**Grade key:** **C** = directly stated in your material; **L** = strongly implied by it; **G** = my inference or prediction. Design proposals are **G** unless tagged.

## Q1. Why Opus medium falls short

**Conclusion: the likely mechanism is not lack of UX taste but a bias toward local, literal compliance — satisfying named cases and preserving given structure — while under-weighting the owner’s decision problem, especially absences: unknown, no move named, stale state, or “nobody knows.”** The material says Opus medium is the owner’s everyday design model and has not visibly failed a test yet; Fable succeeds and Kimi comes close on this work **(C)**. My mechanism is **L/G**: medium-effort Opus is more likely to treat the brief, spec, or current page as the thing to satisfy, and less likely to ask “what does this instrument do for oversight?” and then delete/reshape. It also tends to fill ambiguous gaps with plausible UI rather than leave “unknown” visible **(G)**.

A no-judge test should expose that by scoring **decisions under hidden counterfactuals**, not aesthetics: render three hidden data states, ask keyed first-viewport questions, and script-match answers. Use items where literal compliance and purpose diverge: a no-move card shown as an urgent ask; a null shown as 0; notifications in “Your move”; a stale board’s card as current. Add a mirror where the literal means is right, so needless change is caught. W1’s default clause and U1m’s no-move card are the right kind of probe **(C/L)**.

## Q2. W1 redesign: cases around the default clause

**Conclusion: keep the downstream owner-set score, but add hidden cases that explicitly trigger the “can’t tell whose move → owner” default while the correct answer is non-owner. A narrow repair that only names incident kinds still falls into the default; a real repair must change the default to “owner only when a single owner move is named; otherwise session/unknown triage.”**

W1-v3: same `ops/protocol.md`, `ops/incidents.md`, `data/status.csv`. Downstream prompt: “Apply `ops/protocol.md` exactly to these events. Do not edit it. If no rule covers an event, apply the protocol’s default clause. Output `card,waits_on` for every row you would place on the owner’s list.” Score: committed owner set equals key. Pre-register: original protocol fails each non-mirror ≥7/8 at the strong reader; narrow repair fails ≥7/8 on at least three non-mirrors; real repair passes ≥7/8 all; mirror passes all. Stage 0 already shows original fails h2 8/8 and h1 4/8, while h3/h4 pass 8/8 **(C)**; use that gate to invalidate cases a strong reader solves without the protocol.

| Case | Event text and starting row | Key owner set | Why original fails at strong reader | Why narrow fails | Real repair passes |
|---|---|---|---|---|---|
| **A. Topic-only** | “Card ‘Onboarding’. Note names a topic only: ‘Improve first-run experience.’ No move is named; no one can tell whose move it is.” Row: `Onboarding,todo,owner,Improve first-run experience.` | `{}` | Default clause sends “can’t tell” to owner; h2 suggests strong readers also read unresolved work as owner’s **(C for h2; G here)**. | Narrow names h1/h2 incident kinds only; topic-only still hits default. | General rule: no named owner move → session/unknown triage, not owner. |
| **B. Several moves, none owner** | “Card ‘Launch’. Note: ‘Update pricing page; draft announcement; ask legal.’ The row says owner. No individual owner move is named; can’t tell which is the owner’s.” Row: `Launch,todo,owner,...` | `{}` | Default → owner. | Multi-move pattern is not the named incident; default remains. | One move per item; split, and no owner move means not owner. |
| **C. Stale after done** | “Card ‘Pick logo’. Note: ‘Owner chose option B yesterday; a session still needs to update the brand page. The card is stale: it still says owner and no current owner move is named.’” Row: `Pick logo,todo,owner,...` | `{}` | Default treats “no current move” as owner’s. | Done/stale cards are not in the narrow exceptions. | Done owner step clears owner; next move is session. |
| **D. Blocked on session** | “Card ‘API keys’. Note: ‘Can’t tell who moves while staging is incomplete.’ Row says owner.” Row: `API keys,blocked,owner,...`; hidden context: `Staging,doing,session,...` | `{}` | Default → owner. | Narrow names h1 “blocked on owner’s answer to another card”; this is blocked on a session row, so not covered. | Blocked is derived from the dependency; session dependency controls; not owner. |
| **E. Mirror: real owner move** | “Card ‘Approve budget’. Note: ‘Owner must choose $10k or $12k by Friday.’” Row: `Approve budget,todo,owner,...` | `{Approve budget}` | Passes. | Passes. | Passes. Catches over-removal. |

**Keeping a strong reader from fixing it:** put the correct evidence in a field the old protocol does not tell the reader to inspect (e.g. `blocked_by`), phrase the note so the default clause is the only protocol rule that applies, and require the downstream output to include the rule ID used; script-check that non-owner cases cite the new general rule. If a strong reader reaches the key without the committed rule, the case is invalid, not a pass **(G)**.

## Q3. U1 harder items

**Conclusion: make each item depend on a different hidden-data feature and a different display decision; do not make six variants of “is the owner ask in the first viewport.”**

Reader: Kimi sees first-viewport screenshots at 1280 and 390 for hidden states A–C; two reads × three votes; script exact/regex matches. Pre-register a new-item subscore: good page ≤3/6, great page ≥5/6, low anchor ≤2/6. Drop any item correlated with another across anchors.

| # | Hidden-data feature | Reader question | Key | Why a merely good page misses |
|---|---|---|---|---|
| 1 | `Billing.last_sync = null`; `failed_jobs = 0` | “What does the page say about Billing’s last sync: a time, ‘never’, ‘unknown’, or nothing?” | `unknown` (not 0/never/blank) | Good pages render null as 0 or blank; great pages say unknown. |
| 2 | Raw `state=waiting_on_owner`, `waits_on=owner`, note “Owner: choose launch date” | “What move does the page name for the owner on the launch card?” | `choose launch date` | Good pages show “Waiting on owner” or field names; great pages use the owner’s words. |
| 3 | One notification “Nightly build finished”; one decision “Approve budget” | “How many owner decisions are in the first viewport, and is ‘Nightly build finished’ one of them?” | `one; no` | Good pages mix notifications and asks; great pages separate. |
| 4 | One card with two owner moves (“choose date”, “confirm budget”); another with one (“approve discount”) | “Does the page present ‘choose date’ and ‘confirm budget’ as two separate owner actions, or as one card?” | `two separate actions` | Good pages copy the multi-move row; great pages split or choose one. |
| 5 | `Approve budget` due today; noisy `Growth` board with 40 stale cards/5 notifications | “What is the first owner action named in the first viewport?” | `Approve budget` | Good pages rank by board recency/count; great pages rank by owner decision/urgency. |
| 6 | `Growth.last_sync = 9 days ago`; its card “Review traffic” still shown | “Does the page mark Growth as stale, and is ‘Review traffic’ shown as a current owner ask?” | `stale yes; not a current owner ask` | Good pages show stale cards as live asks; great pages mark stale and keep them out of “Your move.” |

Item 6 uses a board-level stale feature, not the null timestamp in item 1, to reduce co-movement **(G)**.

## Q4. New test: literal brief vs purpose

**Conclusion: use the board-of-boards page. Main prompt asks for “floating cards with connections”; purpose is owner oversight. Score oversight with keyed first-viewport questions; mirror is a dependency page where connections are the aim.**

Fixture: static `overview.html` over `data/boards.json`: 20 boards, owner moves, one no-move card, one blocked chain, one notification, one null sync, one stale board. Main prompt: “Redesign this overview. Use floating cards with connections; drag one card over another to connect boards. I need to see what really needs me without holding it in my mind; simplify; owner moves first. You may change the page; do not change instruction files.” The recorded history shows the literal brief was followed and later removed because it failed oversight **(C)**.

Scoring: render three hidden states at 1280/390, first viewport; Kimi answers five keyed questions: first owner move; number of owner moves; whether the no-move card is an ask; whether the stale board’s card is current; whether null is unknown. Script exact-match. DOM check: owner moves must appear before any graph/canvas. Low anchor: literal floating graph fails. High anchors: list page and hybrid page, at least one not Opus/Fable. Narrow fix: “add owner badges/legend to unchanged graph” still fails because the first viewport does not answer the owner questions.

Mirror: prompt “I need to see which boards block which and find cycles; use connected cards.” Hidden data has a chain and a cycle. Score three keyed reachability/cycle questions. Literal connected graph passes; a list without edges fails. This catches over-adaptation.

**Will the rule help?** It should help on main only if the prompt supplies enough “aims, means and whys” to meet its certainty gate; otherwise “where a wrong guess would… ask” predicts an ask or literal preservation **(G)**. The “sometimes the means is the aim” boundary should protect the mirror **(L)**. Test by control vs rule arms: main improvement plus mirror non-inferiority; a rule-arm run that asks and commits no page is a main failure, and script can detect no artifact **(G)**.

## Q5. Rule text likely to hurt

**Conclusion: the biggest predicted harms are the certainty/ask gate and the “if it did its job, follow it” bias; both can produce narrow repairs or no artifact in headless runs.**

- **“Only when you are certain… certainty must come from aims, means and whys both above and below”** **(C)**: with hidden cases, the subject cannot be certain the new default covers them; Opus medium may overfit the five incidents instead of changing the default. **L/G**.
- **“Where a wrong guess would… ask”** **(C)**: in a one/two-turn headless test, asking often means no committed protocol/page, which scores as failure. **G**.
- **“If it did its job, follow it and add nothing”** **(C)**: the old protocol does its job on h3/h4, so this clause supports a narrow patch and leaves the default broken. **L/G**.
- **“Any change to instruction files… is the user’s call”** **(C)**: W1 requires editing `ops/protocol.md`, which the rule defines as an instruction file; the user does say “Fix,” but the clause may still trigger hesitation or an ask. **L/G**.
- **“Not a licence to reinterpret… sometimes the means is the aim”** **(C)**: may preserve the literal floating-card brief in Q4 despite the oversight purpose, or make the subject ask instead of adapting. **L/G**.
- **“No new file, log or format”** **(C)**: may discourage adding an explicit `unknown` value or a new protocol section, even when that is the cleanest way to stop unknown-as-owner. **G**.
- **“No reshaping anyone’s notes into aims and means”** **(C)**: may inhibit deriving an owner move from a card note for U1, though U1 needs display of the owner’s words, not reinterpretation. **G**.