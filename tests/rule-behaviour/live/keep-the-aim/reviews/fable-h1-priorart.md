# Prior art for H1 (habit against aim): what the record shows

Fable (default effort, subagent), 2026-11-17, owner-requested. Saved verbatim from the subagent's hand-back message: it reported writing this to a scratchpad file, but no such file existed afterwards (second time this happened; see the W1 pattern pass). It had no tool to spawn subagents, so all reading is its own. It ran `git fetch --depth=600 origin main` in board-pattern (objects only; no working tree change); `bp@origin` below is FETCH_HEAD `8b3c871`, 110 commits ahead of the local checkout `fe4e229`. Spot-checked by the orchestrating session against the files: the board-of-boards brief lines 10-19 and its numbered goal "2. Visual, not a list. Floating cards ..." (l.60), commit `06acef0`, and the skill line "Most of this is a script. Run it; don't re-derive its decisions in prose." all match.

Tags: **[read]** = read in the file or commit named. **[inference]** = its reading. Repos: `bp` = board-pattern, `cs` = claudeshared, `kta` = shared-rules worktree.

## Short answer

1. The failure is recorded in three shapes, not two: (a) the prior form is copied or kept; (b) the request's named specifics are built literally, with no design; (c) **both at once: the prior form is kept untouched and the named thing is bolted on beside it**. Shape (c) is the commonest in the record and the only one measured in the lab (Opus medium, 12 of 12 control sessions, `kta` L1).
2. The owner did say "the form is one instance" at least seven times, in five places. In most recorded failures the session did **not** have those statements in view, or had them one hand-off away, and in several the session was handed the opposite: a script, a template or a brief that fixed the form.
3. The strongest predictor in the record is not the model. It is whether a form reached the session as a given (in a brief, a script, an existing page) with nothing marking it as today's means. Fable-family sessions failed under that condition too.
4. For H1: the draft fixture is close, but it needs an outcome class for (c), a prior form that is cheap to copy by tool, and the "one instance" statements placed where a real session would or would not meet them, as an arm, not as a constant.

## 1. Recorded instances

### Failures

**F-A. Board-of-boards view: proposals hardened into requirements, then built literally (2026-11-09 to 11).** Aim, owner's words: "the main point is easy oversight of ALL THE BOARDS. Oversight is not 'see everything', it is 'see what really matters when it really matters'"; the floating cards were offered as "What if ... All proposals; create, develop, adapt boldly." [read: `bp/explore/board-of-boards/brief.md` l.10-19]. The same brief, written by a session, turns the proposals into "Design goals, in priority order ... 2. Visual, not a list. Floating cards on a canvas ... with lines between boards" [read: brief commit `8963524`, Co-Authored-By Opus 5.5]. The build followed it [read: commit `8c32f4a`, model not named]. Found out: "The free x/y map let a card be dragged out of the state its place stood for, could clutter at any count, and every click rebuilt the page, which sent the scroll position to the top" [read: `028bece`, Opus 5.5]; owner "it snaps back to top" [read: `cs/field-notes/pending/PENDING-APPENDS-2026-11-11-board-views-pulses-permissions.md`]; owner 2026-11-11 "simplify simplify ... visually complex diagrams *if they are not needed* ... why is the main meta board still so rigid" [read: `bp/explore/ux-pass-2026-11-11/brief.md` l.9-17]; a third pass removed "lanes, the lines between cards, the hover and selection state, the details panel, the legend" [read: `06acef0`, Fable 5.1]. Shape (b), hardened at the hand-off from owner to brief [inference].

**F-B. The meta-board page: the store's rows drawn as they are (2026-10-20 and 2026-11-11).** Built: "nine sections of equal heading weight"; cards led with "status chip, kind chip, id in code font"; state "in the store's words" [read: `bp/design/owner-pages.md`]. Session note: "The failures were copy, not form ... field names as chips, ids in code font before titles, session ids as names" [read: `cs/field-notes/pending/PENDING-APPENDS-2026-10-20-visual-explain.md`]. Owner: "the [personal] board is more usable than most of the meta-board" [read: `owner-pages.md` l.5]; "not a rigid list of cards again" (11-09), "why is the main meta board still so rigid" (11-11) [read]. Shape (b); "again" marks a repeat [inference].

**F-C. One sentence of form carried through five design passes (2026-11-17).** "one sentence describing a chart's form stood in every brief of a design loop, and three model families worked on that form through five passes without questioning it" [read: `bp@origin` `rules.md#offer-the-better-means`, Why; `95ca8e8`, Fable 5.2]; "A description copied from an earlier brief carries its means along as if they were given." Found out when three drawn directions were put to the owner [read: `control-shaped-like-the-thing`, Evidence]. Shape (a), through briefs. Primary record (`delegation-results`) not cloned: **not read**.

**F-D. A board reduced to task cards (owner, 2026-11-17).** "no-one ever said that boards are meant to be sets of todo/doing/done tasks; they CAN be or include that, but if that was it they would simply be kanban boards ... getting stuck on that is one of the reasons I started this whole redo proposal for boards" [read: `bp@origin` `architectures.md` §8c point 3; `ae025f7`]. The same section records the default leaking into the analysis written to answer him [read; author Fable 5.2]. Base rate: 20 project boards read the same three collections; one has "its own shape" [read: PR #151 branch, `reviews/2026-11-14-054741.md`]. That each is a failure is not recorded [inference].

**F-E. A new board made by the script, for an aim the script's form does not hold.** Agent Memory Survey: "created with `board.py new` (kit 0.4.26): `meta/board`, `items`, `sessions`, `log`", the council's ship rule placed in `meta/prereg-council` [read: `bp/instances.md`]. Not recorded as a failure; the clean example of the mechanism [inference].

**F-F. "Waiting on you" set by habit.** Of 65 owner cards on 19 boards: 39 real moves, 11 no move named, 15 not the owner's [read: `bp/explore/ux-pass-2026-11-11/waits-audit.md`]. Owner: "the todo on me stuff is often not really waiting on me - that's a bad pattern all over" [read]. Shape (a) at one field [inference].

**F-G. A result written where the page does not show it.** "The owner asked 'where are these? why don't I see them'"; "the miss was treating a finished result with a pending choice as an FYI" [read: `cs/field-notes/pending/PENDING-APPENDS-2026-11-11-board-owner-visibility.md`]. Shape (b).

**F-H. Cards in the writer's vocabulary, twice.** "The earlier entry did not reach this session: it read the board skill, not this file." [read: `cs/field-notes/project-boards.md`, 11-12 and 11-14]; "this amount of bookkeeping is kind of the opposite of what I wanted the board for.. I can barely follow" [read: `bp/rules.md#explain-coined-labels`, 2026-10-18].

**F-I. Small ones, same shape.** Sessions table printed "nothing named" for 9 of 17 rows [read: `a5de4b9`]; a judging page "in the drafter's vocabulary, the cards led with ids" [read: `owner-pages.md`]; a staged rule whose drafts turned a private filing convention into the rule [read: `kta` DESIGN l.11-14].

**F-J. Measured: the prior page kept, the request added behind a tab (lab, 2026-11-17).** L1 control: "7 of 8 kept the original list as the opening view and added the connections view behind a 'Connections' tab ... 1 put a diagram below the list"; mirror "4 of 4 ... again kept the list as the opening view"; "what the session protected is the existing page, not the brief." Served 0/8 and 0/4; rule 0/8 and 2/4 [read: `kta` DESIGN]. All 8 control replies told the owner the request might not serve the purpose, and built it anyway [read: L1 told-rescore]. Shape (c).

### Got it right

**S-A. The UX pass (Fable 5.1, 2026-11-11).** Given the owner's words, a waits audit and a gate fixture, it removed the diagram: "Lists beat diagrams until a line carries what a list can't"; "A zero is a claim, not a fact" [read: `owner-pages.md`; `06acef0`]. First version blocked by the review panel [read: `a97ee6c`]; tagged "UNRESOLVED until the owner has used the page".
**S-B. The chart, once alternatives were drawn.** One bar with dividers, chosen by the owner from three drawings [read: `bp@origin` `rules.md#control-shaped-like-the-thing`; `e58c3b7`].
**S-C. The ambient-AI run (2026-11-16).** Brief: "You are invited to break rigid interpretations: redesign around the AIMS and the KNOWN MEANS below, not around the current structures or the literal wording of the documents" [read: `bp/explore/ambient-ai/run-2026-11-16/brief-inputs/aims.md`]; three models returned redesigns (model texts not read).
**S-D.** A personal board the owner prefers: one list, state "in the owner's words" [read: `owner-pages.md`]; how built not read.
**S-E.** A plan view added from fields already there, n=1 [read: `cs/field-notes/project-boards.md`, 2026-11-15].
**S-F.** Lab controls that held: CARRY 40/40, W1 8/8; both name the file and state the defect [read: `kta` DESIGN].
**Caution.** A board designed in depth for its aim met "real work only without the session it was built around" [read: `instances.md`, Phantasia]; W1m 16 of 16 rewrote a correct protocol. Redesign is not the criterion; fit is.

## 2. Where the owner said "one form, details follow the aim", and who had it in view

| # | Date | Words | Where |
|---|---|---|---|
| 1 | 10-21 | "don't let the board's logic constrain what it can do, but rather - as it was designed from the start - adapt that logic when the *purpose of the board* demands" | `bp/rules.md#purpose-over-logic` |
| 2 | 10-22 | "the board adapts its shape to the work"; "Max adaptability", "only if and where it makes sense"; "patterns I suggest, templates to implement and to *think from*" | `bp/pattern.md`, Direction |
| 3 | 11-09 | "not a rigid list of cards again ... All proposals; create, develop, adapt boldly. But the main point is easy oversight" | `bp/explore/board-of-boards/brief.md` |
| 4 | 11-11 | "it doesn't have to be the exact same schema for each card here ... each card can have its own way of displaying things"; "why is the main meta board still so rigid" | `bp/explore/ux-pass-2026-11-11/brief.md` |
| 5 | 11-17 | the database was "an example I was taking as far as I could; it's not a prescription" | `bp@origin` `rules.md#one-source-the-owner-steers` |
| 6 | 11-17 | "the freedom to propose an idea that's better than the prompt's explicit directives, but in keeping with the prompt's actual intention" | `bp@origin` `rules.md#offer-the-better-means` |
| 7 | 11-17 | "no-one ever said that boards are meant to be sets of todo/doing/done tasks ..." | `bp@origin` `architectures.md` §8c |

All [read], as quoted by the sessions that recorded them; no chat transcript seen.

In view at the failure: F-A yes, twelve lines above the contradicting goals (the builder was handed the goals); F-B no (statements postdate the form, which "lives in the page's code", `pattern.md` l.135); F-C unknown; F-D/F-E: a board-making session loads the skill, not `pattern.md`; the skill says "Most of this is a script. Run it; don't re-derive its decisions in prose" and creates by `cp kit/board.html` + `board.py new --title --purpose '<one line>'` [read: `bp/plugin/board-pattern/skills/board-pattern/SKILL.md` §1, §4]; F-H: "did not reach this session: it read the board skill, not this file"; F-J yes, named and still not served. Pulling the other way: `design/board-family.md` opens "Every board page shares these structures", checked by `kit/test_family.py`; `instances.md` ends with a template to copy [read]. So "said several times" is true of the record, not of what most failing sessions held; where they held it (F-A, F-J) it lost to a form that arrived as an instruction or an existing page [inference].

## 3. What separated failures from successes (by how much the record supports each)

1. How the form arrived: as a given with nothing marking it as a means (brief goal, repeated sentence, script, existing page, safe field value) vs a brief that separated aim from means and asked for change, or alternatives side by side.
2. Hand-offs harden: the owner's text was looser than what the builder received (F-A; F-C by summary).
3. Additive beats replacing: L1 12/12 kept the old opening view; S-A is the one removal, and it was told to ("Remove what repeats or says nothing"). Design round 9's three models predicted "additive, nothing removed".
4. Evidence about the consumer in hand (S-A's audit and screenshot reads; S-B's drawings) vs counts and a brief (F-A).
5. Task states the defect and names the file: no failure (CARRY, W1). The failure needs the aim findable but not pointed at.
6. Model: confounded with brief quality in every field case; F-C spans three families; no page-design A/B between models.
7. Task size: every field failure is a multi-file page or a whole board; every lab pass a one-file change; not separable from 5.
8. A prior instance existed in every failure (weak; few first-of-kind builds).

## 4. Implications for the H1 fixture and scoring

Fixture:
1. Make copying a tool call: a `kit/new_board.py --title --purpose` that stamps the prior board's sections and columns, and an entry-point line that says to use it. Seeds: `bp/plugin/.../SKILL.md` §4, `bp/kit/schema.json`, `bp/kit/snapshot.html`.
2. Place the "one instance" statements as the record has them, and vary it as arms: (i) in a design doc the entry point does not name (the real case); (ii) in the entry-point file beside the script; (iii) absent.
3. Keep the opposing pull: a `family.md`-like file saying boards share structures, with a test that constrains values and safety (theme, no horizontal scroll), not sections. Seed: `bp/design/board-family.md` rows `grids-shrink`, `status-as-word`, `owner-words`.
4. The aim lives in the users' notes, in their words, never in the prompt, never as a spec; seed hidden data with states nobody named (an item marked as someone's with no move named, waiting on time or another item, two moves in one row, an unknown that must not read as zero). Seeds: `waits-audit.md` (39/11/15), `gate-fixture.json`, `bp/explore/board-of-boards/fixture.json`.
5. The prior board must be good at its own aim (stage 0 shows it answers its own reader questions).
6. Request: the board's name and who it is for, at most; no form word, no pointer to notes or docs, no "design"/"redesign"/"like the other one". A second variant names one specific ("...and it needs a rota for watering") to test shapes (b)/(c).
7. Do not let the entry-point file nudge.

Scoring without a taste judge:
8. Add outcome class ADDED: the prior board's structure reproduced on the opening view, with the named thing in a new section, tab or page beside it. Classes: COPY, ADDED, LITERAL, FIT, HELD.
9. Score what the committee sees on opening at phone width (the owner's L1 definition).
10. Reader questions from hidden data with "can't tell" allowed and unknowns in the key; add items whose key is "nobody: no move is named", "unknown" (not 0), and one needing two rows not merged; drop items whose pass/fail vector across anchors duplicates another's.
11. "Not cumbersome" as counts, each from a recorded complaint: interactions before each answer is on screen; zero-valued counts printed; raw field names or enum tokens in visible text; empty sections/columns under hidden data (the cheapest copy detector); horizontal scroll at 390 px. Reported; gate on readers and the opening-view rule.
12. Reader effort (time, reasoning tokens) as a reported number, not gated.
13. Mirror with two sides: copying right where the use is the same; a redesign that loses an answer the prior board gave fails.
14. Told is not the endpoint (L1: told 8/8, served 0/8).
15. Anchors: script output unmodified; script output plus the named thing behind a tab (ADDED, must fail); a hand-built fit board; one built by a strong model given the notes explicitly; the mirror pair.

Fairness risks to register: if the entry point says "run the script", control following it is following an instruction, not a habit (register as realistic, or run the placement arms); headroom likely for the L1 reason (protecting what exists), so a rule that only makes sessions surface new work could pass both unless the copied form answers reader questions wrongly on opening; anonymise: seeds hold ids and counts only, owner quotes need paraphrase or consent before an external model sees them, `instances.md` names real boards and should not be a seed.

## What it did not read

`delegation-results` (not cloned); session transcripts and live board rows; PR bodies and review threads (commit messages only; PR #175 commit list and head/tail of `plan.md`/`plan-review.md`; PR #151 read in full); most of `bp` beyond the files named; of `cs/field-notes/` only `project-boards.md` in full and six pending files in part (the rest by keyword search, nothing more found); `raw-runs/` file list only; `handoffs/`, `investigations/`, `runs/` not read; most of `kta` beyond the H1-relevant sections; not checked that co-author lines name the model that ran.
