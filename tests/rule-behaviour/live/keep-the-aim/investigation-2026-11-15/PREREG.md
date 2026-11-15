# Pre-registration: investigation council (written 2026-11-15, before launch)

Run: council_hub.py, roster Fable 5.2 high (decider, BYOK, provider pinned to Anthropic) + DeepSeek Flash (optional, direct API).
Caps: BYOK upstream USD 15; OpenRouter-credit side USD 2 (DeepSeek direct is estimated into it); max 80 calls per participant; 1200 s per call.
Context: brief + context-pack.md (prompt-design, intrinsic-prompt-design, 8 dev rules, adhd, frame-rotation, dialectic-spiral, standpoint-pass, check-assumptions, break-pattern, vasana; owner identifiers replaced).

What this run gates: nothing ships from it. Its output is a design that goes to the owner, then to a pilot with its own pre-registered targets.

Ending: decider's FINAL naming a posted PROPOSAL = complete. Cap or max-turns without FINAL = incomplete; reported as such, the last proposal (if any) labelled draft, not re-labelled final.

Check after the run (falsification station): a fresh verifier with no stake (different model family, given the record tools or the files, not this conversation) checks each causal claim in Part 1 against the record, per claim: confirmed / not found / contradicted with the evidence. Pass for Part 1 to be relayed as findings: no claim graded GROUNDED by Fable comes back contradicted. A contradicted claim is reported to the owner beside Fable's version, never reconciled by me. Adjudicator of a disputed claim: the owner.

## Deviation recorded before the continuation run (2026-11-15, after the first run ended at its cap, before any Part 2 data)
First run: cap reached (BYOK USD 15.97), no FINAL → incomplete, as pre-registered. Owner chose (chat, AskUserQuestion): a focused Fable 5.2 high call for Part 2, and the blind Part 1 check now. Continuation: Fable alone as decider, brief = original + first room verbatim + orchestrator's self-run E1 grep + issue-thread appendix; max_tokens 64000; BYOK cap USD 7 for this run; max 20 calls. Ending rule unchanged (FINAL naming a posted PROPOSAL = complete; cap or turns without FINAL = incomplete). The hub now logs finish_reason per call.

## Part 1 check, as run (written before the checker runs)
Checker: GPT-6.1 Sol (medium), OpenRouter credits, cap USD 2, record tools only, questions in inv/verify/brief.md phrased as open questions with no expected answers. Confirms a Part 1 claim: the checker's evidence agrees with it. Disconfirms: evidence against it. Null: UNRESOLVED answers, reported as such. Fable's F1–F5 and Flash's E1 claims are compared to the answers by the orchestrator after both runs; every disagreement goes to the owner with both versions; the owner adjudicates.

## Outcomes (recorded after the runs)
- Run 1 (council, Fable 5.2 high decider + DeepSeek Flash): cap reached at BYOK USD 15.97 with no FINAL → **incomplete**, as pre-registered. Fable posted Part 1 findings once (`run1/room.md` [1]); DeepSeek Flash posted five messages, including the `$?` lead.
- Part 1 check (GPT-6.1 Sol, OpenRouter credits USD 1.49): `check/answers.md`. Disagreement found: the orchestrator's own note to run 2 said the `$?` mechanism was overstated (grep for `rc=$?` only); the checker and a re-count found `$?` in 12 of 13 T1 denials. The orchestrator's note was wrong; Fable was told and withdrew its part-1 finding 2 (`run2/batch-parts-2-3.md`, "Corrections").
- Run 2 (Fable alone, live tool loop): cap reached at BYOK USD 8.95 after part 1 of 3 → incomplete. Each drafting call spent about 25–34k output tokens, mostly thinking.
- Run 2 continuation (owner's choice: Anthropic batch via OpenRouter, effort high, no tools): one request, USD 0.956 on BYOK (`service_tier: batch`; half the live price for the same tokens), `stop_reason: end_turn`, ends with `FINAL: P2` → **complete**. PROPOSAL P2 = `run2/room.md` (part 1) + `run2/batch-parts-2-3.md` (corrections, parts 2 and 3).
- Not yet done: a blind check of Part 2's factual claims against the record; the owner's decisions listed in Part 2.

## Owner's decisions on PROPOSAL P2 (2026-11-15, chat, AskUserQuestion)
1. Ship rule: the "SHIP, narrow claim" row is allowed, labelled one-endpoint evidence.
2. Harness denials: the file-room pilot's rule replaces P2's void rule: prevent (probe gate per cell before scoring), never void for a denial, score every completed session, cap denials before the first decision-turn commit; over the cap = "harness-confounded: no result" (`fileroom-pilot/room.md` [19], plus Fable's four post-FINAL amendments: the container branch is probed by Gate A, the effective config is hashed, Gate B's limits are stated in full, branch c is chosen per cell by lookup).
3. G5 factor: 1.5x control's median.
4. Next: a blind check of P2's factual claims before DESIGN v5 is written.

## P2 check, as run (written before the checker runs)
Same checker and route as the Part 1 check (GPT-6.1 Sol medium, record tools, cap USD 2); questions in `check-p2/questions.md`, open, no expected answers. A P2 claim the checker contradicts goes to the owner beside P2's version; the owner adjudicates. Arithmetic claims (power) are recomputed by the checker independently.

## P2 check, outcome
GPT-6.1 Sol, USD 0.89 credits (`check-p2/answers.md`). Every P2 factual claim checked was confirmed except one wording slip: "the `$?` first command fell from 8 of 12 to 2 of 12". `$?` was in the first T1 command in 2 of 12 v2/v3 controls; the 8 are `$?` in a denied T1 command. New: rule Opus sessions were denied in 4 of 12, and 3 of those 4 still read and passed. Power, from the checker's exact formula, computed by the orchestrator: 0.968 / 0.638 / 0.012; old bar 0.639. DESIGN.md "Redesign v5" carries the corrections.
