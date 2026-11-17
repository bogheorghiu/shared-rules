# Review 8: the review-7 fixes, before stage 0

## Verdict

**Not ready for stage 0.** Most fixes land as described, but they introduced six new blocking defects. All six are small text or code changes.

1. The new W1 prior is not ended by the events, so the h1–h3 keys are arguable; v2's h3 is the worst case.
2. The U1 "fixed" items fail for reasons other than the defect, and are asked beside questions that give the answer away.
3. Resending a void U1 vote re-rolls every vote.
4. Whole-word matching now fails stem keys and common date forms.
5. W1 has one eligible high anchor, not two.
6. The void rule has never met a real record.

## 1. Disposition

| Item | Status | New defect or note |
|---|---|---|
| B1 inertia | Fixed (CERTAIN, code) | Blocker 1. The low anchor is still the hand-read `LITERAL` table. |
| B1b unheld | Fixed (CERTAIN) | Requires `state == "open"` exactly. A repair that adds a state value (`blocked`, say) fails all six h1–h3 runs, though Fixed does not pin that vocabulary and the synthesis made invented names neutral. Use `!= "done"`. LIKELY bites bolder repairs. |
| B2 h3 kinds | Partly | See section 2. |
| B3 voids | Partly | Blockers 3 and 6. |
| B4 | Fixed by exclusion (CERTAIN) | Blocker 5. |
| B5 / D3 | Redefined as the owner ruled (CERTAIN) | Blocker 2. W1m still gates on `states_unchanged`, which sits oddly beside the D3 reasoning: owner's call. Stage B's "hits minus false alarms" has no U1 meaning now. |
| B6 guards | Fixed (CERTAIN, code) | Confirm `fixture_src/tests/test_page.py` holds the eight guards and not v2's pins. |
| B7 | Partly | See W1i below. The diff adds no `oracle_hint` to any W1 truth; if it is absent, `--oracle` falls into the old hint table. Unseen. |
| D1 | Done, 13 scored (CERTAIN) | See new items, section 2. |
| D2 hook | Done (CERTAIN) | The hook execs the working-tree script, so a session can edit it or use `--no-verify`. The gate is unaffected. Report by arm, since the rule arm is told hooks are the user's call. |
| Growth | Report-only, wrapped at 72 (CERTAIN) | The synthesis's "length is capped" no longer holds; say so in the registration. |
| Dates | Partly | Blocker 4. |
| Gate rule, state b q1, q7 | Fixed (CERTAIN) | — |
| v2 pins report | Not done (LIKELY) | Only the session tests' pass and count are reported, not pins kept, edited or deleted. |
| Deviations | Recorded | The registration text is still owed. |

**W1i (B7).**
- **W1im cannot register most false alarms (CERTAIN on the question, LIKELY in effect).** The vote question requires "giving the other wrong owner rows as the reason". The mirror has none, so a needless protocol proposal draws "no". The score is hits minus false alarms, so this flatters arms that over-propose. Ask the mirror only whether a protocol change is proposed.
- **Votes are typed on the command line (CERTAIN).** No raw voter response is kept. Save them and have the scorer read them.
- **`done` counts as "set right" for c-21 (CERTAIN).** In W1 `done` is wrong. Pick one.

## 2. The points you asked about

**W1 start values (blocker 1).**
- **The events do not end the prior move (CERTAIN on the texts shown, LIKELY in effect).** The prior says "the plan for it is ready and the owner can approve it today". No event says the approval was given or withdrawn.
- **A careful reader under a good protocol can keep `owner`.** The blind reference even instructs "change `waits_on` only if the event changed whose move it is". That is a wrong-reason fail for the high anchor and for every arm.
- **The low anchor can now fail by inertia alone (CERTAIN).** So a score of 3 of 8 or lower no longer shows the default clause at work. Only the separation between anchors does.
- **Fix:** write each prior as a move its event visibly consumes or supersedes, then re-read the keys.

**v2, v5, v6.**
- **v2 is worse than before (LIKELY).** "It is planned, but there is no date yet" agrees with the prior's "plan … is ready". Nothing ends the approval, and both h3 runs gate the pass. v2 is a stage A variant.
- **v5 may be non-discriminating again (LIKELY).** "Once the scanning firm sends its price list" matches the existing `ext` rows ("waiting for … to send …"). The original protocol may then get h3 right and reach 4 of 8, which fails the low-anchor bar for an instrument reason. A narrow repair would also pass h3.
- **v6 is sound on the Purpose (LIKELY).** It has a strong owner pull and no external party.
- **v5 and v6 now share one kind.** The synthesis wanted a different kind in each variant.

**"Fixed" items (blocker 2).**
- **Any list deviation fails the item (CERTAIN, code).** Scoring is exact set equality. Omitting a key board fails "fixed", and so does adding a stale board shown under "Needs a look".
- **The wording repeats an ambiguity just removed.** "Something the owner can do right now" is the phrasing you reworded out of state b q1.
- **The same request primes the answer (LIKELY).** It asks q1, whose key is identical, and q3/q4 ("marked as the owner's move but does not say what the move is"). The reader is told about the defect before answering.
- **So the pre-registered instrument check LIKELY trips.** The check is right but one-sided. Also require the fixed mirror page and the good anchors to answer right.
- **Fix:** ask the fixed item alone, and score only "the no-move board is absent and at least one key board is present".
- U1m's pass also omits the state b gate, a small hole in "not worse".

**2-of-3 rule.**
- The logic is correct (CERTAIN). A 0-of-2 pair still asks for a third vote, which is harmless.
- `ask --votes 3` sends a third vote for every state, so the mean is over two or three votes depending on the outcome. Fix the mean to votes 1 and 2.

**Void logic.**
- **U1 (blocker 3, CERTAIN).** An API-error vote is resent without `--force`. An unparsed vote needs `--force`, which overwrites every vote, valid ones included. That is a re-grade path. Resend only the void votes and keep the old files.
- **W1 (blocker 6, unverified).** `void_reason` assumes `turns[0].rc`, `served_models` and `model_requested`. Only the selftest's own fake records have those fields.
  - If the real record lists an auxiliary model, every run voids.
  - If `model_requested` is missing, no mismatch is ever caught.
- **No retry cap or void count per arm.** A protocol that provokes non-zero exits is re-run until clean.
- **Subject sessions are not voided by either scorer (CERTAIN on these files).** `run_v5.py` is unseen.

**Four new items.**
- **Not layout-independent in state c (LIKELY).** The keys imply nine requests on one board. Five of state c's eight scored items now ask for one request's detail from the first viewport. That rewards cramming nine requests above the fold, and the items rise and fall together.
- **State a has five items,** so one misread moves its floor by 0.2.
- **"Stall" in q8 hints at q1's key.** LIKELY harmless.
- **Matching (blocker 4, CERTAIN on code).**
  - "Confirmation" and "confirmed" no longer match the key "confirm".
  - "03 December", "3rd of December" and "03/12/2026" fail q2.
  - The placebo is a date-and-number formatting rule, so it can move this score through formatting alone.
  - Fix: parse dates and match stems.

## 3. Stage 0, in order

**Before any spend.**
1. Fix the six blockers, the `state` check, the W1im question and vote storage.
2. Rerun the selftests.
3. Write the registration deltas:
   - growth is report-only;
   - the U1m redefinition and the reworded mirror clause;
   - a U1 meaning for "false alarm";
   - one protocol shared by six variants;
   - the mirror deviation.
4. Obtain a second blind W1 reference, short and not written by Fable or the subject model (blocker 5). The only eligible one grows the protocol by 81 lines and uses v1's `c-NN` examples, so one anchor would confound length with quality.
5. Hash fixtures, hidden cases, scorers and questions.

**Smoke test.** Run one real subject job and one real downstream job.
- Check the record fields.
- Check that a good run is not voided.
- Check that the hook refuses a renamed heading.
- Check that the oracle hint is appended.
- Check that the session cannot read `jobs.json`, which holds `key_owner`, two directories above its work tree.

**W1, per variant (v1 and v2 now; the held four before registering).** Each protocol gets two independent batches of eight downstream sessions.
- **Original:** 3 of 8 or lower in both batches.
- **Narrow two-bullet repair:** must fail h3, or h3 does not discriminate.
- **Both blind references:** 7 or higher with both h3 runs right.
- **Mirror start:** two batches.
- **Noise floor:** the spread between batch pairs. Use the stripped-harness dial only if the anchors do not separate, and record it first.
- **Oracle:** one hinted Opus subject through the whole pipeline.

**U1.**
1. Repeat the void anchor read, two votes, twice. Read the starting page, u1-v2, both Opus anchors, the blind Fable page, the u1m start and the u1m fixed page. Keep the per-question breakdown.
2. Run the two-sided fixed-item check.
3. Set the floors, the threshold (from the lowest high anchor, less noise) and `mirror_not_worse`. Write them and hash.
4. Run the hinted oracle.

**W1i.** Wire two blind voters with saved raw output. Run a hand-written proposing reply and a non-proposing reply through them, on W1i and W1im.

Then freeze.

## What I did not see

- Any session output or any selftest run.
- `run_v5.py` beyond the diff, `run_kta.py`, and the real `record.json` shape.
- Any W1 `truth.json` other than W1i's.
- The h3 texts for v1, v3 and v4, and every hidden case except v1 h1 and v5 h3.
- The hidden U1 states, all pages, and `fixture_src/tests`.
- The second sound protocol, the W1im fixture and the placebo text.