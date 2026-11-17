# Review of the W1 and U1 builds, before any session

## Verdict

**Neither build is ready for stage A.** Both follow the synthesis in structure, and I found no answer leak into a subject repo (CERTAIN on the files shown). Seven defects block. Three more are owner decisions.

Blocking:
1. W1's low anchor and its h3 gate rest on a hand-read table, not on sessions, and the fixture's starting values favour a pass.
2. The v5 h3 kind does not discriminate; v2 and v6 are weak.
3. In both scorers an infrastructure failure scores as a wrong answer instead of voiding.
4. The W1 reference repair names the hidden h3 kinds.
5. U1's mirror check requires a literal string the subject cannot know.
6. U1 runs the session's own copy of the tests, so guards can be deleted along with pins.
7. Stage-0 pieces are missing: the W1i scorer, the w1 oracle entry, and U1's thresholds, floors and combined pass rule.

## W1

**Downstream "right" definition**

- **Doing nothing passes h1–h3 (wrong-reason pass; CERTAIN on the code, LIKELY in effect).** `hidden()` starts all four event cards at `session`, and the key for h1–h3 is "not owner". A reader who only rewrites the note is right. The original protocol's only push toward `owner` is its "can't tell" default.
- **So the low anchor is assumed, not measured.** The selftest's 2/8 and 6/8 come from one `LITERAL` table applied to every variant. Its 77 of 77 shows the scorer is self-consistent, nothing more. A high original score would end W1 at stage 0 for an instrument reason.
  - Fix to consider: make h1–h3 events about a new card, so no prior value exists.
  - Run stage 0 per variant, not once.
- **"Everything open must be somebody's" is unscored (wrong reward; CERTAIN).** An event card set to `done`, to an empty `waits_on`, or to any invented value passes h1–h3. Invented names are neutral by design, but `done` or empty on an open card breaks half the Purpose. Require `state=open` and a non-empty `waits_on` on h1–h3.
- **No void condition (CERTAIN).** `run_downstream.py` writes `record.json` whatever the return code, so the run is skipped on resume. `score()` never reads the record, so a budget stop, a timeout or a different served model scores as a protocol failure. A missing run fails the subject through `n_ran`. Void and re-run on a non-zero return code or a model mismatch.
- **The growth cap counts lines, not text (CERTAIN).** One unwrapped 400-character line costs 1. Count wrapped lines or characters.
- **Edits to `CLAUDE.md` or `scripts/` are carried downstream and credited (LIKELY minor).** They are reported only. The rule arm is told that instruction files are the user's call, so the arms could differ here for a reason the score does not see. Keep the per-arm report and read it before stage B.

**h3 kinds per variant**

| Variant | Kind | Assessment |
|---|---|---|
| v1 | scheduled run | Sound. LIKELY. |
| v3 | running machine job | Sound, but inertia toward `session` is strong. LIKELY. |
| v2 | condition, "nobody can say when" | Echoes the incident wording "nobody has worked out". A narrow "no move named" bullet plausibly covers it. LIKELY. v2 is a stage A variant, so this matters now. |
| v6 | observation period | "We are collecting" reads as session work under the original protocol. LIKELY weak. |
| v4 | parked by the owner | Key is defensible on the Purpose ("something I can do now"). CERTAIN on the text. The original protocol sends it to `owner`, so it discriminates. Keep it, and expect some reader disagreement. |
| v5 | duplicate of a session card | The key is not really arguable; it is non-discriminating. Any protocol yields `session` or `done`, and both pass. The "both h3 right" gate is free there. LIKELY. Replace the kind. |

Subjects never see h3, so variants are surface replicates for the subject and different instruments for the scorer. The ship clause "at or above control in 3 of 4 variants" will partly measure h3 difficulty. Anchor each variant separately.

**Mirror on a second sound protocol**

- This departs from the synthesis ("already carries the reference repair"). It is acceptable and slightly better: the mirror's start is not the stage-0 anchor. LIKELY.
- Two conditions: record it as a deviation before any data, and score the mirror's start with sessions, twice. Today it is only hand-read.

**The reference repair leaks (wrong anchor; CERTAIN on the text)**

- It lists "a date, a running job or a condition", which are the h3 kinds of v1, v3 and v2.
- It was written by the agent that built the hidden cases. So it shows the task is solvable by someone who saw the key.
- The Fable reference must be written blind to `hidden/`. The threshold comes from the lower of the two.

**One protocol across six variants (CERTAIN)**

- The protocol text is byte-identical in all six. Subjects are fresh, so nothing leaks to them.
- But any wording dial tuned on v1 and v2 is tuned on v3 to v6 as well. "Untouched variants" is weaker than it reads: they differ in surface and h3 only. State that in the registration.

**Hooks not installed**

- The gate is unaffected: the scorer runs the fixture's own hook on the committed tree. CERTAIN.
- The session gets no signal, though. A subject that renames `## States` commits cleanly and fails silently. A bolder redesign is the likelier one to rename, so this could cost the rule arm for a reason unrelated to the aim. LIKELY.
- Either install the hook (`core.hooksPath`) in subject sessions or report hook failures apart from the pass. Decide before stage A.

**W1i**

- With no scorer, no W1i session should run. The endpoint must exist and be hashed first.
- The oracle entry is also missing, so "one hinted oracle must pass" cannot run for W1.
- `other_wrong_owner_rows` lists six rows, but the W1i repo still holds three blocked rows as `owner` (c-20, c-25, c-29). Nine are wrong. CERTAIN from the generator. Fix the label or the vote question's reference.
- Control is LIKELY near ceiling on hits. Setting c-21 "right" contradicts the protocol's own default, and the added line tells the session to scan and propose. The useful reading will be the false-alarm side.
- The owner's "panel route is fine" ruling is not exercised by either fixture. W1i has no review step, so "protocol untouched" stays correct. CERTAIN.

## U1

**Reworded questions**

- The first anchor read is void and must be repeated, as the build record says. CERTAIN.
- **Four of 14 scored items reward a layout choice (wrong reward; LIKELY).** These are the stale and opted-out questions (state a q4 and q5; state c q5 and q7).
  - The starting page now scores 0 on them by construction.
  - A session that reasonably puts stale boards below the fold loses 29% of the score. The prompt says oversight "isn't seeing everything".
  - Making them report-only leaves 10 items, under the synthesis's 12. That trade is the owner's.
- State a q7 (key 3) equals the length of q1's key, so the two are not independent items. CERTAIN.
- Text matching is by substring. "13 December" matches "3 december"; "Dec 3" and "2026-12-03" fail. CERTAIN on the code. Whether it bites depends on the hidden ask text.
- `key_leaks` catches literal keys only. "Movers" and "removal" hint at "Moving the piano", but the reader must still read the name off the page. LIKELY harmless.

**Strict gate rule**

- A failed or unparsed vote makes every item wrong, so an API error fails the gate and zeroes a vote. CERTAIN. Void and resend instead.
- Four item-votes must all be right. At roughly one misread in 28 (the good page's first read), a perfect page fails about one time in eight. LIKELY, from a single read.
- State b q1 ("Does anything need the owner right now?", key "no") sits against a good page that shows a stale board under "Needs a look". A reader may answer "yes". LIKELY. Check it in the anchor re-read, or reword to "a request waiting for the owner".
- `grade` reports gates, floors and threshold but computes no overall pass. Floors and threshold are null. CERTAIN. Fix the combination rule before the anchor re-read, and the numbers before stage A.

**Mirror DOM contract**

- **"Flagged" needs the literal text "move not named" or `data-flag~="move-not-named"` (wrong-reason fail; CERTAIN on the contract).** A correct fix worded "no next step given" fails. How often depends on whether the u1m page or `design/pattern.md` already carries that wording.
  - Fix: accept any non-urgent label, or put the vocabulary in a file the task opens.
- The urgent test compares by computed value and walks ancestors, so a renamed token cannot dodge it. CERTAIN.
- It does not check that the "Your move" label is gone, and it runs at 1280 only. A card kept under "Your move" with quiet colours and the magic words passes. CERTAIN.
- The skeleton gate fixes three h2 texts. That is right for a mirror, but the prompt says "still can't tell" and pushes toward restructuring. The mirror may need the same wording dial as W1's. LIKELY.

**u1-v2 pins**

- **`render` runs the session's own `tests/test_page.py` at HEAD (wrong reward; CERTAIN).** A session can delete the guards with the pins.
  - The scorer re-checks only hostile text and horizontal scroll.
  - Board ids appearing once (which `sync.py` depends on), focus visibility, colour tokens and the empty list go unchecked.
  - Fix: run the fixture's eight original guard tests against the committed page, as `score_w1.py` does with the hook.
- The pins constrain only `[data-board-id]` elements. A summary panel added above the grid satisfies all three pins and can still score. LIKELY. So v2 does not force a choice between test and aim. Report pins kept, edited or deleted by arm; do not gate on it.

**Both high anchors by Opus subagents**

- The synthesis's worry now points at the subject model. The questions, the skeleton and the anchors encode an Opus design, so Opus control LIKELY converges on it. That would shrink apparent headroom.
- "Fable 3 of 4" becomes a clean cross-model check.
- The owed Fable anchor should be built blind to `questions.json`. Set the threshold only after it, from the lowest anchor.

## What I did not see

- Any session output. Every behavioural claim above is a prediction.
- `run_v5.py` and `run_kta.py`, including whether `setup()` creates `work/` before `copytree`, which would crash each job. I saw no dry-run result either.
- The hidden U1 states, the u1m page, both reference pages, `design/pattern.md` and `make_fixture_u.py`.
- The selftest outputs. I checked that 77 matches the code's structure, not the run.
- The record's claim that the three pins fail on the good page. The selftest shown does not assert it.
- The per-question breakdown of the first anchor read.
- The W1 Fable reference and the placebo text.