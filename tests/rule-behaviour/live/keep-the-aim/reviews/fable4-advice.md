**Recommendation.** Run R after three changes to the pre-registration. The runner change is correct as written.

1. Take the Opus-low baseline from 8 fresh concurrent `none` sessions per fixture, not the grid's 4 plus 4 new.
2. Add a placebo arm of one unrelated established rule alone, or rename the positive reading.
3. Define the swap void for `only`, which has no default-prompt comparator.

Treat cover-K1d as the primary fixture and carry-R1 as secondary. R cannot speak to the owner's case, so start U's stage A on Opus medium alongside it rather than after.

## 1. R's pre-registration

**Defects that can mislead a reading**

1. **The baseline reuses the sessions that selected the fixtures.** The two fixtures are in R because their grid bare cell dropped, and those 4 sessions then count toward "headroom". **CERTAIN** from the text.
   - On cover-K1d (grid 0 of 4), the gate passes unless the new four go 4 of 4. A concurrent 3 of 4 with `only` at 7 of 8 would read "the rule alone restores it".
   - Fix: 8 new `none` sessions per fixture as the baseline (8 more sessions), with the grid's 4 reported beside them.
2. **"The rule alone restores it" has no control for "any rule text restores it".** The grid showed that eight rules without keep-the-aim restore the look, and so does about 2,500 tokens of default prompt. **CERTAIN** from the G table. A pass in R therefore reads "a third sufficient support", not "this rule's content".
   - Fix: a `placebo` arm of one established rule alone, of similar length and with nothing about checking (`keep-context-to-the-work.md`), 8 per fixture on Opus low.
   - The "ask when unsure" rule is a second candidate. Its wording is already fixed and it bears on the recorded disagreement, but it is much shorter, so it does not control for length.
   - Without a placebo, rename the reading "the rule alone is sufficient here".
3. **"Voids: as in the grid" does not define the swap check for R.** The grid compared swap cells with concurrent default cells. R has none, and `only` has a context size nobody has measured. **CERTAIN**.
   - Fix: pre-register bands from the grid, per fixture and turn. `none` should fall in the grid's bare range (carry-R1 T1: 5,285–5,296).
   - `only` should equal that plus the rule file's tokens, counted before launch. I estimate about 1,100 to 1,400, which stays below `none` × default (7,818). **LIKELY**; the count is not in the material.
4. **"Does not restore" covers a clear partial effect.** `only` at 4 of 8 against a baseline of 0 of 8 is about 4% under chance, yet reads "does not restore". Fix: name a "partial" reading, for example `only` at least 4 above baseline but below 7.
5. **carry-R1 will probably not be read.** With the grid's 2 of 4, the gate needs 1 of 4 or fewer from the new sessions, which is 31% if the true rate is one half. **CERTAIN** arithmetic, **LIKELY** outcome. A fresh baseline of 8 does not help much either (3 or fewer of 8 is 36%).
6. **On carry-R1 the endpoint and the look come apart.** The bare cell has 6 passes and 3 looks, so at least 3 sessions passed without the look, at least one of them Sonnet. **CERTAIN** arithmetic.
   - Either the look detector misses a route, or the task passes by copying the customers script with its filter, without knowing why.
   - Report the look per reader and per pass or fail. A "restores" on this fixture would otherwise be ambiguous.

**Smaller**

- State the minimum scored count for `only` (the grid required 7), and report voids per arm.
- Four Opus-medium sessions cannot show a ceiling: 4 of 4 occurs 24% of the time at a true rate of 0.7. Write "no drop seen in 4".
- Report the held route separately from caught and carried. The rule tells the session to ask, so `only` may pass mostly by holding.

**Sound as written:** descriptive status, interleaving, Gate A for the new cells, and "what it cannot say".

## 2. The runner change

- **`setup()` is correct.** `none` copies nothing, `only` copies `RULE` alone, and other arms go through `arm_rules`. The dict lookup cannot fall through. **CERTAIN**.
- **The probe is correct.** `only` must match `keep[- ]the[- ]aim` and name none of the eight stems. No stem is a substring of "keep-the-aim", so there is no self-collision. **CERTAIN**.
- **The same destination directory served the `rule` arm,** so the loader will pick up the single file. **LIKELY**.

Three residual points, none blocking:

- **A false-void risk on `only` alone.** The rule's text names `state-the-why.md` and `no-drive-by-edits.md` as siblings. A probe reply that mentions them, even as "referenced, not loaded", voids the session. **CERTAIN** it would void, **LIKELY** rare. The check fails closed, but only in the treatment arm, so read every `only` void by hand before replacing it.
- **`config_sha` does not include the arm, reader or effort.** (only, swap) and (none, swap) share a hash, and the `cell` field in `gate_a.json` omits the prompt. **CERTAIN**. Record the prompt in `cell`, so a Gate A pass can be tied to its configuration.
- **The probe turn is not kept.** Its flags and served model are not written to the record. **CERTAIN**, and it predates this change.

## 3. The grid record

The pre-registered readings are applied correctly for cover-K3d (holds bare), cover-K1d (reader-dependent) and carry-R1 (unresolved). **CERTAIN** against the table. The 2,500-token swap gap is consistent across arms (14,228 − 11,670 and 7,818 − 5,285).

**Overclaims**

- **The within-Opus "redundant" pattern sits under "as pre-registered".** That reading was defined on pooled cells of 8. Applied to one reader at 4 per cell, it is a post-hoc extension, though a fair description. Move it to the session's reading.
- **"On these fixtures the ceiling is carried redundantly."** This holds for one reader on one fixture, at 4 sessions per cell. cover-K3d holds with both supports removed. carry-R1 is unresolved, and its Opus bare cell is 2 of 4. Your summary, "Opus low fails only when both are removed", has the same reach: clearly on cover-K1d, half on carry-R1, not on cover-K3d.
- **"Sonnet medium needs neither."** This is true of the endpoint only (12 of 12). On carry-R1 the look fell in the bare cell for at least one Sonnet session.
- **The look erodes even where the endpoint holds.** carry-R1 shows 8, 6, 7, 3 across the cells. "Redundant" describes the endpoint; the look data lean towards additive. The numbers are small.
- **"The first cell in the suite where control fails ... for a reason the rule names."** Review 3 records earlier floors (v2 E1, Opus 1 of 6). The bare cell is also not "control" as the suite uses the word, which is the eight rules. I cannot verify "first" from this material.

**Worth adding to the record.** The bare cell still carries about 5,300 tokens of Claude Code text, mostly tool descriptions. What the removed 2,500 tokens contain is unseen, since no request was saved. R cannot say which part of the default prompt carries the look.

The closing sentence, that it is a harness nobody deploys and cannot feed the ship decision, is right.

## 4. Opus medium, and what else to run

- **Keep Opus low as R's reader.** It is the only place with headroom so far. Opus medium was 3 of 3 everywhere in v4, so it will probably hold bare. **LIKELY**.
- **Pre-register a conditional now.** If Opus medium bare is 2 of 4 or fewer on a fixture, run `only` 8 and `none` 4 more on Opus medium there, with the same readings. Otherwise a surprising drop on the owner's reader would lead to a design made after the data.
- **Record R's distance from the owner's case.** It is three removes away: a rarely used effort level, an undeployed harness, and code fixtures that hold-and-ask can pass. The owner's stated case is the constructive half in UX work. A "restores" here is not evidence for it, and a null is not evidence against it.
- **Start U's stage A alongside.** It is a control-only screen and its reader is now known: Opus medium. It is the first step that tests whether the owner's failure reproduces in headless Claude Code at all. It still needs the fix for the conflict between Fable as judge and Fable as reference, and the owner's go.
- **Free, in parallel:** re-grade the four held grid sessions for whether the question names the aim.

**Size after the changes:** `only` 16, `none` 16, placebo 16, Opus medium 8. That is 56 sessions, all on subscription.

## What I did not see

- The grid's records, transcripts or probe replies.
- `score_v5.py`, `grade_v5.py`, `run.parse`, and how the look event is detected.
- The launch script, the `setup()` check and the first buggy version.
- Gate A outputs.
- The rule file's token count.
- The default prompt's content.
- The earlier DESIGN sections, in this pass.
- How the CLI treats `--system-prompt` beyond the context sizes reported.