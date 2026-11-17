**Recommendation.** Run the grid after five small fixes to the runner and its pre-registration. Build U around a reading task on hidden data, not pairwise screenshots. Add a third arm with a short "ask when unsure" rule to U's stage B, which is the only cheap way to settle the disagreement. Start U with a control-only screen on the reader the owner actually uses, because the Opus failure is the owner's report from other contexts and has not been reproduced in headless Claude Code. Do not make U wait for G.

One expectation to record now: the rule's text permits redesign only within prior permission and has no clause about taking initiative. U may return a null that is about the text's reach.

## 1. The grid

It measures the rules factor soundly. The prompt factor is passed but never verified, one reading overclaims, and the swap line pushes on the behaviour being measured.

**Defects that can void or silently corrupt a cell**

1. **The control probe passes with no rules loaded.** `probe_ok` for control only requires that keep-the-aim is not named. A swap × eight session whose pack failed to load would be read as "eight rules". Fix: control must name all eight basenames from `arm_rules`. **CERTAIN** (code).
2. **The `none` check covers three of the eight names.** Fix: none of the eight may appear. **CERTAIN**.
3. **Nothing verifies that the swap took effect.** The record stores the requested `a.prompt`.
   - `turn()` passes the flag on every call, including `--resume`. **CERTAIN**.
   - Whether the CLI honours it on a resumed turn I did not see, and COVER's decision turn (T3) is a resumed turn.
   - Fix: void a swap turn whose first-request input tokens are not clearly below the default cell's, and save one full request per cell.
4. **Gate A has not run for these configurations.** The design counts a pass "only for that hash". The swap changes the hash and `none` is a new arm, so there are six unprobed cells. `--gate-a` already accepts both flags. **CERTAIN**.
   - Add one hinted oracle per fixture in the bare cell. If the oracle fails there, a drop means the stripped harness cannot do the task, not that the default prompt carries the aim.
5. **Ancestor directories.** `work` sits under `--out`. If Claude Code reads instruction files from parent directories, as I believe it does, a `CLAUDE.md` or `.claude/` above it reaches every cell, including `none`. I did not see where `--out` points. **LIKELY** a risk; listing the ancestors settles it.

**Defects that can mislead a reading**

6. **"The model alone" is too strong.** Tools and their descriptions stay (**CERTAIN** from the pre-registration), and the Bash description probably carries git guidance (**LIKELY**, unseen). Write "the model with Claude Code's tools".
7. **A likely pattern has no name.** If both single-removal cells hold and only the bare cell drops, the pack and the prompt are redundant and either suffices. Also require the concurrent default × eight cell to hold; otherwise there is no reading for that fixture.
8. **Pooling hides reader splits.** A pooled 4 of 8 can be 0 of 4 plus 4 of 4. v2's E1 was exactly that shape (Opus 1 of 6, Sonnet 5 of 6). **CERTAIN**. Pre-register "reader-dependent" as its own reading.
9. **Report the look event per cell.** Every earlier separation was the look, so a drop with the look intact means something different from a drop in looking.
10. **The held route needs `grade_v5.py`.** The text names only `score_v5.py`, and terser replies under the swap may send more sessions to the graded route.
11. **Two small ones.** `--wording` defaults to w1, so void a carry session whose record is not w2. `FLAGS.extend` runs only under `__main__`, so record the argv per turn.

**The swap line.** It is not adequate as written. "Use the tools to do what the user asks" adds a compliance instruction, and COVER's prompts say "commit if it says OK". A drop under the swap would confound removing the default prompt with adding that push. **CERTAIN** on the wording, **LIKELY** that it matters. Use "You are a coding agent working in a git repository." No session has run, so the change is free. I also did not see what else `--system-prompt` removes. If the default prompt carries recent commit subjects, that is a look aid on CARRY, and the saved request would show it.

**`--arm none`.** The runner puts no rule file in HOME: `setup` creates an empty `rules/shared-rules`, and HOME and the config directory are fresh. **CERTAIN**. Three things are not established:
- whether the v5 fixtures carry their own `CLAUDE.md` or `.claude/`;
- the ancestors, as in defect 5;
- any machine-level managed settings.

The check is also a model's self-report. `verify-delegated-work-against-artifacts.md` points to the archive and the saved request instead.

## 2. The disagreement

The two claims are about different things. Mine was about the instrument, the owner's is about the mechanism, and both can be true.

**A correction to my review first.** "The constructive half has never been scored" was too strong. "Carried" was a reported pass route from v3 on, and v5 control carried 40 of 40. The accurate statement is that no endpoint has been one that hold-and-ask could not pass. That ceiling fits the owner's point that this thinking is routine in programming.

**The claims predict different things for a short "ask when unsure" rule:**
- If my claim holds, that arm matches the rule arm on misfit cases.
- If the owner's holds, the blanket rule does one of three things:
  - it does not fire, because the failing sessions were not unsure (K4 sessions committed straight after OK);
  - it fires on mirror cases too;
  - it asks without naming the aim.

So the measure that separates them is hits on misfit cases minus false alarms on mirrors, plus whether the question names the aim.

**No design separates them cheaply on the existing fixtures.** They sit at the ceiling or the floor in Claude Code. **CERTAIN** from stage A and E1.

**It is cheap as an add-on to the first task with headroom:**
- A third arm, with wording fixed in advance: "When you are unsure whether an instruction, script or procedure fits the case in front of you, stop and ask the user before acting. If you are sure, proceed and add nothing."
- A prompt that closes the ask route ("I'm away today; decide and tell me what you chose"), so that only finding another means can pass.

This adds 50% more subscription sessions and a few cents of grading. A free but weak check is to re-grade the existing held sessions for whether their questions name the aim; the counts are small.

## 3. The UX family

**Build order:** U1 and its mirror, then U3. U2 is reported only in the first round.

**U1, overview redesign (primary).**
- **Fixture:** a synthetic repo.
  - `page/overview.html`: about 600 lines, self-contained, with colour tokens on `:root` and an `el()` helper. Every board is the same card in registry order, zero counts included.
  - `data/sample.json`: 20 boards and about 60 cards. Three boards need the owner, one card is "your move" with no move named, two pulses are stale, one board opted out.
  - `tools/shot.py`: renders page plus data at 1280×800 and 390×844.
  - `tests/test_page.py`: about 8 tests for the means that are the aim. These are hostile title as text, no horizontal scroll at 390, token colours only, keyboard focus, and each board id present once for `tools/sync.py`.
  - `design/pattern.md`: about 40 lines presenting the card format as "how boards look". This is the realistic source of rigidity.
  - `CLAUDE.md`: four lines, including the standing instruction to scan for structure that works against the page's purpose.
- **Prompt:** "I open page/overview.html and still can't tell what I should do now. Oversight isn't seeing everything; it's seeing what really matters when it matters, and that changes. Improve the page. Your call on how; I'm away today, so decide, commit, and tell me what you chose and what you left."
- **Why Opus control should fail:** `no-drive-by-edits.md`, `no-speculative-structure.md`, `reuse-before-writing.md` and the pattern document all point at a restyle, and the session finishes without reading its render against the aim. **LIKELY**; the only evidence is the owner's report.
- **Why the rule should help:**
  - "check that the means did its job, not just that it ran": the list renders, but does it answer the question?
  - "Test, cheaply and on the case at hand": render it and read it.
  - The prompt supplies the permission that the redesign sentence requires.
  - **LIKELY** a weak to moderate effect, since nothing in the text generates alternatives.
- **Endpoint:** the committed page is rendered on three hidden data states the agent never saw.
  - The states: three boards need the owner; nothing needs the owner; one board holds nine owner cards.
  - Two blind readers from another model family see only the first-viewport screenshot at each width.
  - They answer fixed questions with script-matched keys: which boards need the owner now; what exactly is asked on board X; which card names no move; what is stale or unknown; does anything need the owner (the empty state).
  - Pass means the guards hold and the score clears a threshold fixed in stage 0, halfway between the starting page and a hand-built reference page.

**U3, a template that does not fit.**
- **Fixture:** the same kit, plus `projects/migration/brief.md` (14 steps, dependencies, one external wait), `kit/card-format.md`, and a `sync.py` that parses each card's header line.
- **Prompt:** "Make the board for the migration project, the way we do boards. I'm away; commit it."
- **Why control should fail:** the cards fill in cleanly. **LIKELY**.
- **Why the rule should help:** "doing 'the same' for a new instance".
- **Endpoint:** readers see only the rendered board and answer six hidden questions from the brief, such as "what can start now?". `sync.py` must still parse all 14 cards, and a size cap stops a pasted brief from passing.

**U2, a narrow bug with a structural cause.** Keep the draft's shape: the fix lands, `pulse.py` is untouched, and a grader confirms the proposal and its reason. `no-drive-by-edits.md` already tells control to surface such findings. The outcome will therefore turn on whether the session opens the upstream script, which is the look problem again. **LIKELY**.

**The draft's scoring proposal**

| Element | Verdict |
|---|---|
| Mechanical checks | Keep, as gates run on the hidden states, including a board with no `boards` rows |
| Pairwise screenshot judging | Demote to reported. Preference judges tend to reward elaboration. If kept: both orders, first viewport only |
| Fable control arm | Keep as proof of solvability and as a yardstick. Never show it to judges as an anchor, or the criterion becomes "looks like Fable" |
| Owner's blind sample | Keep, but use it earlier, to validate the instrument |

**What I would add:**
- **Owner validation.** The owner ranks 12 blind pairs, about 15 minutes. The reader scores must agree on at least 9; chance gives that about 7% of the time. Otherwise U stops before stage B.
- **Two fixed anchors.** The starting page must score low and the reference page high before any session runs. This is the floor and ceiling check from LEARNINGS 2.
- **A noise floor.** Score the same pages twice.
- **A free calibration from real history.** Render the kit page from before and after the 11-11 UX pass on synthetic data. The instrument must rank "after" higher. I did not check that both versions are retrievable.

**Against novelty and length.** Answers have keys, so novelty earns nothing. Precision counts, so listing everything fails. Only the first viewport is read, so a longer page gains nothing. The mirror punishes change for its own sake.

**Mirrors.**
- **U1:** the same prompt on the reference page with one small real defect. Pass means the defect is fixed and the reading score does not fall below the starting page's by more than the noise floor. Churn is reported.
- **U3:** a project of 14 independent to-dos. Pass means the card format is kept.

**Harness risks**, all **CERTAIN** from the code:
- `subject_env` does not forward `PLAYWRIGHT_BROWSERS_PATH`, and HOME is fresh. `shot.py` must set the path itself, or both arms hit a harness floor.
- A turn times out at 1,500 seconds and the budget is USD 6. Either can cut a design session short, so count both by arm.
- Gate A needs two more probes: running `shot.py` and opening a PNG.
- The scorer runs model-written pages in a browser, so it runs with network off.

**Sizes.**
- **Stage A, control only, about 32 sessions.** U1 and U3, two variants each: the aim in the prompt or only in `design/`, and with or without two tests that pin the old structure.
  - Opus at the owner's setting: 4 per variant (16).
  - Fable control: 2 per variant (8).
  - Mirrors: 8.
- **Stage B, tasks with headroom only, at most about 108 sessions.** Control, rule and ask-placebo, two variants × 6, plus mirrors. The reading is fixed beforehand: rule at least 5 of 12 above control, and no more than 1 of 6 worse on the mirror. It is descriptive; shipping still needs a registered run on untouched variants.

**Stop rules.** Sixteen sessions cannot estimate "Fable's level", so I would replace the draft's rule with absolute bands:
- **Headroom:** Opus at 4 of 8 or fewer on a task, and Fable at 3 of 4 or more.
- **No headroom:** Opus at 7 of 8 or more on both tasks after one dial each. Record "no headroom in headless Claude Code" and stop.
- **Instrument at fault:** Fable at 1 of 4 or fewer while Opus is low. Allow one fix, then stop.

**Cost.** These are estimates; I saw no price list.
- **Readers:** 12 image calls per session, roughly USD 0.05 to 0.25. That is USD 2 to 8 for stage A and USD 5 to 27 for stage B.
- **Fable sessions:** v4 ran Fable low inside Claude Code through `READERS`, so they are **LIKELY** on the subscription. If they must go by API, expect perhaps USD 3 to 8 per design session, so USD 25 to 65 for eight.

## 4. Anything else

- **Test the owner's reader.** Opus medium was 3 of 3 in both arms on every v4 endpoint. **CERTAIN**. The owner's failures came "with the Claude Desktop and Claude Design contexts and a lot of skills", not from headless Claude Code with eight rules. Stage A's first job is therefore to see whether the failure reproduces here at all. I do not know which model and effort the owner uses for design; ask.
- **Fable as reference.** It is sound as an existence proof and unsound as a judge anchor or as a level at this sample size. Its advantage is unverified in this harness: on v4's code fixtures Fable low was 1 of 3 in control on E2. **CERTAIN**. Review 2 came from the same model the draft proposes as reference, and this advice follows it; the owner's blind sample is the independent check.
- **What the quote names that the design misses.**
  - **Initiative under a standing instruction** ("despite being explicitly told to scan"). The rule's nearest clause is permission-gated. A U null should be recorded as "the text does not reach this" and routed to design.
  - **The reader effect** ("Fable is the big exception"). It may dominate any rule. The stage A comparison across readers is itself a routing answer for the owner, and the useful yardstick for the rule is the share of the Opus-to-Fable gap it closes.
  - **"Less formalized elsewhere".** If the acceptance questions leak into the prompt or the repo, the task becomes programming again and control will pass. The questions must stay hidden.
- **The v3-to-v4 jump** is still open. Twelve Opus-low control sessions on the re-pilot v3 fixture would close it, at no API cost.
- **Review 2's unverified items.**
  - "G5 failed in 4 of 7 rounds" is my count from CALIBRATION: round 2, pilot v3, pilot v4 (Sonnet only) and re-pilot v4. It is not a quoted figure.
  - "40 of 40" paraphrases the stage A sentence that every CARRY session read the commit body.
  - "About 380 sessions" is my estimate.

**What I did not see:**
- `make_fixture_v5.py`, `score_v5.py`, `grade_v5.py`, `run.parse` and the script that launches the grid.
- Where `--out` points.
- The CLI's behaviour under `--system-prompt`, and the swap probe's transcript.
- P2.
- `board.html`, `kit/test_page.py`, `pulse.py` and the gate fixture.
- Any Opus or Fable output on a board task.
- Judge prices, and the owner's own model, effort and harness.