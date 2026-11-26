**Recommendation.** Do not run the API loop; keep everything in Claude Code on the subscription. Claude Code is what loads the rule, so only a control failure there can earn a ship. The harness-or-model question does not change the next step: both of E2's pre-registered readings lead to harder fixtures in Claude Code. I would do three things in order: replay the owner's real incidents, run a small free factorial inside Claude Code to find which layer carries the ceiling, and screen new fixtures that score the constructive half of the rule, which no endpoint has scored so far. If control is at the ceiling there too, stop, record "no headroom on the deployed route", and keep the rule staged until the next real incident.

## 1. Routes

**A. Normal Claude Code, control first (main line, run first).**
- **Question only it answers:** is there a situation on the deployed route where the eight-rule pack fails and this rule could help? **CERTAIN** that no other route can feed the ship decision.
- **Pass:** a variant with control at 4 of 8 or fewer, whose failing transcripts show the rule's failure mode and not a prompt ambiguity like K2's. Then v5's stage B and bar apply.
- **Fail:** control at the ceiling on the part 2 designs. That means no headroom, not that the rule does nothing.
- **Size:** 8 control sessions per replayed incident; 40 control per design screen (5 variants × 2 readers × 4); 96 per surviving design at stage B.
- **Cost:** subscription; grading under USD 1.

**B. A 2×2 inside Claude Code, control only (parallel, diagnostic).**
- **Cells:** default prompt or one-line swap, crossed with eight rules or none, on carry-R1, cover-K1 and cover-K3.
- **Question only it answers:** which layer carries the ceiling: the default prompt, the pack, or the model with Claude Code's tools.
- **Why the pack factor:** my earlier review assumed control loaded no rules. It loads eight, and `state-the-why.md` already says "Read an instruction for what it is for". The swap keeps the rule loader, so the swap alone cannot tell "the model does it" from "the pack does it". **CERTAIN**
- **Readings** (thresholds from the amended E2 plan: 7 or more holds, 4 or fewer does not, 5 to 6 unresolved):
  - The bare cell holds: it is the model, the question is closed, and the API loop adds nothing.
  - It drops only without the pack: the siblings already do what these fixtures test, so new fixtures must target what only this rule adds.
  - It drops only under the swap: the default prompt carries it.
- **Limit:** it steers design and cannot move the ship decision. **CERTAIN** Add the rule arm only in a cell where control does not hold, as a descriptive result.
- **Size:** 96 sessions (3 variants × 2 readers × 4 × 4 cells), including a concurrent rerun of the default cell.
- **Cost:** subscription; no new runner.

**C. API loop: not worth running now.**
- Both readings ("model", or "does not hold on this loop; cause open") lead to the same next step, and the exploration cannot promote the rule. **CERTAIN**
- What it could show is already on record at pilot level: on v3's T3, API control was 0 of 6 and rule 10 of 10. **CERTAIN**
- **Cost:** about USD 8 to 18 batched. At today's 45 minutes per round, 30 to 50 lockstep rounds take one to two days, plus a new batched runner and its review.
- Run it only if the owner also means the rule for plain-loop agents. It is then its own test, about 64 sessions.

## 2. This test, after E1

**Diagnosis.**
- **The look decided every separation.** Old E1 was exactly "read the check before committing" (36 of 36), and round 2 showed control acts once the fact is in context. v5 made the look free on CARRY (40 of 40 read the commit body) and invisible on K4. **CERTAIN** for the numbers; **LIKELY** that this explains both the ceiling and the floor.
- **K4 should be retired as it stands.** Its prompt says "commit if it says OK" (**CERTAIN**). Nothing outside the data file marks the case as new, so the rule's trigger, "on a new kind of case", has nothing to fire on (**LIKELY**). A version with a cue in the user's words ("this one is from the new vendor's system") is worth one 16-session probe.
- **Every endpoint so far passes on hold-and-ask.** A blanket "ask when unsure" rule would score the same. The half the owner cares about, finding another means that serves the aim, has never been scored. **CERTAIN**

So I would replace the endpoints and keep the infrastructure. Four designs follow, cheapest first; each is screened on control before any rule session.

**D0. Incident replay.**
- **Situation:** rebuild the repo state and prompt from each failure the owner saw, and run 8 control sessions.
- **Reading:** if control no longer fails, the need has passed on this route, which is itself the answer. If it fails, the fixture has real headroom and its scoring comes from what went wrong.

**D1. Batch with one stranger (reuses COVER and its scorer).**
- **Situation:** "Everything in inbox/ goes to data/. Run the check and commit." There are twelve files, and one falls outside the check's pattern by the K1, K3 or K5 mechanism.
- **Why control should fail:** the look is diluted across files, and control failed in v2 and v3 exactly when it skipped the look. **LIKELY**
- **Why the rule should help:** 3 of the 4 denied rule sessions still read the check and passed; none of the 8 denied controls read it. **CERTAIN** for those counts; **LIKELY** that it transfers.
- **Scoring:** the bad row at HEAD is a leak.
- **Against the ceiling:** the file count and the stranger's position are dials set on control. A batch with every file in scope guards against over-fire.

**D2. Port with five safeguards (CARRY, scored 0 to 5).**
- **Situation:** a 300-line export moves to a new source ("do the same for the JSON dump"). Five safeguards live in the code without comment, for example an exclusion, a cap, a fallback and a dedupe. None transfers literally. Their reasons are spread across history, a consumer script and a test.
- **Why control should fail:** it must notice five things inside a larger job. v5 CARRY had one, a single `git log` away. **LIKELY**
- **Why the rule should help:** "ask what each check, limit, filter, exclusion or fallback achieved" is a list to work through.
- **Scoring:** a hidden behavioural test per safeguard, run on new-source inputs the agent never sees. Items the agent flags and leaves open are reported separately and do not count as passes.
- **Against gaming:** two further items are means-that-are-the-aim (a column order a consumer parses, a fixed filename), so reinventing loses points just as literal copying does. A count per session also has more range than pass or fail.

**D3. Template that does not fit (the owner's board test, made scoreable).**
- **Situation:** "Make the board for this project, the way we do boards." The project is a 14-step move where order and blocking matter. The card format cannot hold that, but it fills in cleanly.
- **Why control should fail:** `reuse-before-writing.md` and `no-drive-by-edits.md` both push towards the existing pattern. **LIKELY**
- **Scoring:** three fresh control-pack sessions, blind to arm, see only the board and answer six fixed questions whose answers are in the brief ("what can start now?"). A script matches the answers. The sync script must still parse the header line.
- **Against gaming:** the questions are hidden, and a size cap stops a pasted brief from passing. A mirror project that fits the cards guards against over-fire, since departing from the format there is the failure.

**Stop rule.** If D1 and D2 are both at the control ceiling after one dial each, stop: the null on measurability is the result.

## 3. Anything else

- **Stop tuning this family.** About 380 sessions and five designs have each been adjusted on the previous pilot. A separation found now would need replication on untouched variants. **LIKELY**
- **Keep the machinery.** That means Gates A and B, control-first screening, variant banks, the scorer self-test with deliberate breaks, concurrent baselines, per-reader counts and blind record checks.
- **Read every failing control transcript before keeping a variant.** Tuning until control fails selects for ambiguity (K2, v3's "same as") as readily as for the rule's failure mode. **LIKELY**
- **Test the reader the owner actually uses.** Opus medium was 3 of 3 in both arms on every endpoint, and Sonnet low was near the floor in both. The window where a rule can show is narrow. **CERTAIN** for the data.
- **The only measured effect on the current route is a cost.** G5 failed in 4 of 7 pilot rounds before its bar was loosened. Not shipping is the right call today. **CERTAIN** for the count.
- **Close the v3-to-v4 jump for free.** Run 12 Opus-low control sessions of the re-pilot v3 fixture on the subscription route. At the ceiling, the old Claude Code gap (2 of 12 against 11 of 12) belonged to the shim route. **LIKELY**
- **In the owner's place:** I would take the null as the current answer and keep the rule staged. I would reopen on the next real incident, captured as a fixture when it happens.

I assumed that the owner's incidents happened in Claude Code and can be reconstructed, that a session can run with an empty rules directory, and that K1 to K5 and prompt W1 behave as the stage records describe, since I did not see P2.