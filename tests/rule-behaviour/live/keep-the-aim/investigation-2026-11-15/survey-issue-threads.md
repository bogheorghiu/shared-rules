# Survey: tested methodology for writing and testing agent rules (ex-cog-dev issues)

Read-only. Method: WebFetch of github.com pages (the unauthenticated GitHub API returned 403, and `gh` was refused for this repo, so hidden "Load more" items could not be opened).

Provenance limit. WebFetch returns a small model's summary of each page, not raw text. Strings in quotation marks below are ones that summary reproduced as quotes (it capped them near 125 characters). Everything else is paraphrase of that summary. Before relying on any number in a ship decision, open the linked comment. All authors are the repo owner (<owner>).

The reference problem: a five-turn rule-vs-control test in a small git repo. Rule: "keep a step's aim, change its means, ask when the means stops serving the aim". Endpoints come from git state. Pilots hit ceilings (control already passes), floors (both arms fail), and control rates that swing between rounds at 3 sessions per cell.

Ranked by relevance. Tier: tested = a run with counts; observed = seen in a run, no designed comparison; untested = opinion or plan.

---

## 1. The test must make the control fail first, or a both-pass says nothing about the rule (tested)

Claim: <owner> first read a both-pass as "block refuted", then withdrew it: the stimulus never produced the failure in the control, so the test was inadequate, not the rule redundant.
Quote: "unmeasured, not disproven" (paraphrased wording in the summary: block's value) and "refuted on this stimulus" (the retracted conclusion).
URLs: https://github.com/<owner>/ex-cog-dev/issues/160#issuecomment-4991629687 (Jul 16, 2026, both arms fired, both passed) and https://github.com/<owner>/ex-cog-dev/issues/160#issuecomment-4991649808 (Jul 16, 2026, the correction).
Evidence: a cued pair, both arms passed. Earlier E18 battery (41 strict-MCP runs): 40/40 scorable runs reached the committed resolution even at low effort (https://github.com/<owner>/ex-cog-dev/issues/160#issuecomment-5024356328, Jul 20, 2026).
Relevance: your ceiling pilots are this exact case. Before comparing arms, run a control-only screen on the stimulus and keep only stimuli where control fails at a stated rate. Then a rule-vs-control gap is measurable. A ceiling means "lift unmeasurable", not "rule inert".

## 2. The discriminating test: five arms, N=12, pre-registered, with a firing covariate (tested)

Claim: the arm without the block false-balanced 8/12 and the arm with the block 12/12 (direction against the block, not significant), so it was recorded as a null, not a cut. The larger finding was that the skill did not fire un-cued (0/12), so the bottleneck was firing, not wording. (Read from the per-arm triples below; the summary's own phrase "bare 8/12 vs block 12/12 biased" is ambiguous, so check the comment.)
Quote: "a skill-triggering issue" (verdict wording in the summary).
URL: https://github.com/<owner>/ex-cog-dev/issues/160#issuecomment-5080961971 (Jul 25, 2026).
Evidence: 60 runs, 48 scored, 0 voids, five arms at N=12. Per arm (false-balanced / block-held / unclear): R 12/0/0, C 8/3/1, T 12/0/0, V 12/0/0, RN 12/0/0. Fisher two-tailed p = 0.093. Spiral fired 12/12 when cued, 0/12 un-cued. Blind-reader disagreement 5.3% (about 2.5 of 48 rows could flip). Claude Code harness only; all turns on one pinned model (claude-opus-4-8); zero network attempts.
Relevance: report a firing/occurrence rate next to the outcome in every arm. In your test the equivalent is "did the situation where the means stops serving the aim actually occur in the session". Power the next round for grader disagreement, not just for effect size. Note p = 0.093 at N=12 is the scale at which a rate difference of 8/12 vs 12/12 stays unresolved; your 3-per-cell cells are far below that.

## 3. A baseline with the instrument absent: models credit the tool for what they do anyway (tested)

Claim: base runs with no skills loaded performed the same move 10/10, so crediting a loaded instrument for a "good move" is unsafe without an instrument-absent baseline.
URL: https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5024356125 (A13, Jul 20, 2026). Related A12 (Jul 21): guard-present runs cannot show a guard's value; base arms reached the same verdict 10/10; self-reports are worth roughly zero evidence. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583273
Evidence: 41-run battery (A13); base arms 10/10 (A12).
Relevance: an agent saying "I kept the aim and changed the means" is the self-report the thread discards. Score from git state, and keep a no-rule arm, because the control will often do the move unprompted (your ceiling).

## 4. Ceiling at base is a measurement limit, not a reason to cut (tested/observed)

Claim: if base at high effort already passes, lift is unmeasurable, so do not cut the rule for that reason.
URL: https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582516 (A3, Jul 21, 2026).
Evidence: the same pattern across the #160 runs above; also the ceiling-first design in #128 (item 8).
Relevance: pair with item 1. Raise difficulty (fewer hints, effort lower, a rule target that the model gets wrong at baseline) rather than adding runs at a stimulus the control passes.

## 5. Floor: a rule that never enters context cannot be tested by its wording (tested)

Claim: a directive placed in skill bodies had zero effect because in every such run the skill file was never read and no Skill call happened, so the text never reached context. The cue drove invocation, not the directive.
Quote (pre-registered rule as summarized): "Ship only if D1 > D0".
URL: https://github.com/<owner>/ex-cog-dev/issues/173#issuecomment-5029396431 (Jul 21, 2026).
Evidence: 9 runs, Opus medium, strict MCP, native web off, isolated packs. D0 (no directive, uncued) 0/3 invocations; D1 (directive, uncued) 0/3; D3 (directive, cued) 3/3; cued no-directive comparator 3/3. Floor (0/3) and ceiling (3/3) in one battery. D1 = D0, so it did not ship. Valid: 9/9 scorable, no drift, no network.
Relevance: for a floor in your test, first check by transcript that the rule text was in context and that the trigger situation occurred. In Claude Code a CLAUDE.md or `.claude/rules` rule loads deterministically, which removes this failure; a skill-routed rule does not. Also note the "rule fails the pre-registered bar, so it does not ship" move was executed cleanly here, at n=3 per arm, which also shows how little 0/3 vs 0/3 can say.

## 6. Verify firing from the raw log, not from prose (observed)

Claim: one session had 20 prose mentions of a skill it never invoked.
URL: https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582629 area (A4, Jul 21, 2026; summary gives anchor 5029582628): https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582628
Related (observed): B16, a CI reviewer ended mid-work on a promise and reported success; counting tool calls (24 vs 125) showed the cheaper arm never opened the file. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5090238433 (Jul 27, 2026). B12: a wall-clock cap truncated output files but the transcript held complete work; recovery rebuilt 6 of 8 "failed" runs. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5084887364
Relevance: endpoints from git state plus transcript tool-call counts. Run recovery from the transcript before declaring a run void or re-running.

## 7. Get the stimulus from real material; controls from the same session's correct work (tested)

Claim: three authored probes failed to induce the target bias. After two or more failed authored probes, harvest real source material. Controls taken from the same session's correct work turned "does it fire" into "does it discriminate" and removed three of four filter components.
URLs: https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582314 (A1) and https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582413 (A2), both Jul 21, 2026.
Relevance: you can script the trigger by building a git repo state where the planned means is actually blocked (the first approach fails or stops serving the aim), taken from a real session of an agent hitting that, rather than authoring an obviously contrived blocker. Mirror pairs (A5, direction flipped) separate directional priors from weak readers and catch over-correction; here that is a pair where the means should be kept versus changed, so a rule that just "always changes means" is exposed. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582729

## 8. Gate design: ceiling-first, pre-registered gates, and what the batch gates cost (tested)

Claim: an empty-room ceiling batch with a stated gate stopped a wasted competitive batch; the version that failed (0/40) was redesigned, and the second version passed.
URLs: https://github.com/<owner>/ex-cog-dev/issues/128#issuecomment-4693354550 (v1 FAIL, Jun 12, 2026), https://github.com/<owner>/ex-cog-dev/issues/128#issuecomment-4693555676 (v2 PASS, Jun 12, 2026), https://github.com/<owner>/ex-cog-dev/issues/129#issuecomment-4694012797 (Jun 12, 2026).
Evidence: v1: target 0/5 on every should-fire turn (40 reps), canary 0/5, traps 0/15; sibling skill captured 4/5, 1/5, 2/5 on three turns. v2 (N=5, claude-sonnet-4-6): should-fire 4/5, 0/5, 5/5, 5/5, canary 1/5; sibling turns 0/5 for target; false-fires 0/15. Gate: at least 3/5 should-fire turns fire, canary at least once, 0 sibling captures, at most 1/3 false-fires. Caveat the thread states: the v2 turn set was rewritten after v1 ("falsified as denominator design"), so v1 and v2 are not comparable.
Relevance: a first-round gate on the stimulus set (does anything fire/occur at all) before the rule-vs-control round. Changing the turn set between rounds resets the comparison; if your pilots changed the five turns between rounds, the round-to-round swings are partly a denominator change.

## 9. Variance and drift at the decisive cell: N=5 first, N=30 for the number that gates (tested)

Claim: the coding-regression cell was run at N=5, then N=30, and the N=30 figure was the decisive one; a cross-window drift check was added when a quota reset interrupted the run.
URLs: https://github.com/<owner>/ex-cog-dev/issues/129#issuecomment-4694012797 and https://github.com/<owner>/ex-cog-dev/issues/129#issuecomment-4695746223 (Jun 12, 2026).
Evidence: canary OLD 30/30 vs v2 19/30 (Fisher p = 0.0003); v3 26/30 (p = 0.11, "can't reject parity", not equality). Control canary 30/30 in both quota windows (drift check). N=5 spot-checks "lightly powered". Run-to-run variance beyond that drift check was not measured.
Relevance: this is the only place in the set where a control rate was re-measured across windows. Your unstable control at 3 per cell argues for running the control arm repeatedly in separate windows and pooling, and reporting the control's own interval, before reading any arm gap.

## 10. Cheap proxy cannot confirm; it missed a live regression (tested)

Claim: the blind-judge proxy scored the canary 3/3 in both arms while live firing fell from 100% to 63%; restoring anchors gave 87% live, again invisible to the proxy. Boundary-turn over-prediction was about 2/3 on the proxy vs about 1/5 live.
Quote: "can only screen, never confirm" (issue #72 body, on the router proxy).
URLs: https://github.com/<owner>/ex-cog-dev/issues/72 (body, Jun 7, 2026) and https://github.com/<owner>/ex-cog-dev/pull/127#issuecomment-4694014544 (Jun 12, 2026). Procedure harvest: #72, comment 7 (Jun 12, 2026), no separate anchor in the summary.
Relevance: a model-graded "would it keep the aim" screen over turns cannot replace running real sessions and reading git state.

## 11. Stochastic firing is the measured quantity; script the trigger as a planted moment (untested design plus a run it fed)

Claim: firing is p(fire | turn, context), so the unit of repetition is a simulated conversation: distractor turns dominate, one should-fire moment per conversation phrased obliquely with no lexical cue, over-fire traps included, the script hidden from the tested session, neutral cwd as a hard gate, scoring per moment with N at least 5.
Quote: "can only screen, never confirm" is the proxy line; the design's own reason for one moment per conversation (summary): within-conversation priming would confound attribution.
URLs: https://github.com/<owner>/ex-cog-dev/issues/72 (comments Jun 7, Jun 8, Jun 11, 2026; summary gave no per-comment anchors).
Driver choice (UNTESTED as stated, used later): nested `claude -p --resume` because each call is a real top-level session; a spawned subagent is unfaithful (different runtime context, shared log) and acceptable only as a held-constant A/B shortcut with the limit stated.
Relevance: a five-turn script with the trigger planted obliquely in turn 3 or 4 (the means stops serving the aim without saying so), earlier turns as distractors, run as separate `claude -p --resume` calls from a clean git repo.

## 12. Confounds from the environment: cwd, ambient files (observed)

Claim: the first pass ran from the scaffolding directory, so a deictic turn ("this design") read the harness files; re-run from an empty cwd, with the same verdict. Recommendation: empty cwd per rep, or turns that carry their own referent.
URLs: https://github.com/<owner>/ex-cog-dev/issues/128#issuecomment-4693354550 and https://github.com/<owner>/ex-cog-dev/issues/131 (body, Jun 12, 2026).
Relevance: your small git repo is the environment; its contents must carry the whole situation, and the harness files must not be inside it.

## 13. Record recall as sibling-capture vs silence vs fired; re-run silences with the response captured (observed/untested)

Claim: "0 recall" conflates a quiet description with turns another skill legitimately claims; name the expected winner per turn, and re-run silent turns with the full response to separate routing choice from error or an input request.
URL: https://github.com/<owner>/ex-cog-dev/issues/131 (body, Jun 12, 2026; closed Jun 13 via PR #132). The summary shows no comments on #131.
Tier: a lesson drawn from the #128 run, not tested separately.
Relevance: in your test a failure has at least three shapes: kept the means and stalled, changed the aim, and changed the means without asking. Score each as its own outcome class from git state and transcript.

## 14. Pre-registration practice and its use (tested/observed)

- Pre-register N/k and escalation, and compute power rather than eyeballing it (A8). https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582895
- Pre-register the ship decision itself; #173 gave 0/3 = 0/3, a clean non-ship with no goalpost motion (A14, Jul 21, 2026). https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583378
- Merge gates for #129 were written before the run, so the ship call was a lookup (#72 procedure harvest, Jun 12, 2026). Gates: coding recall NEW at least OLD; non-coding recall NEW > OLD; trap/false-fire NEW at most OLD + 1 turn; no displacement on no-signal turns. https://github.com/<owner>/ex-cog-dev/issues/129 (body)
- Failure of pre-registration in the record: #160's title changed on Jul 25, 2026 from "lift unproven; improve-or-cut (Fable-class), deferred" to "no measured lift; bottleneck is firing (M13), not wording; block kept"; the verdict was reached by the pre-registered rule, but the earlier cued-pair conclusion was first read as refutation then corrected, which is the reinterpretation drift the practice targets. https://github.com/<owner>/ex-cog-dev/issues/160
- Count mismatches I noticed in #71 (the reviewer, not <owner>): body says "32 sessions" while the design (9 turns at N=1 plus 8 turns at N=3) sums to 33; "negatives 9/9 silent" omits N1, which fired 3/3, so the full negative set was 9/12 silent. https://github.com/<owner>/ex-cog-dev/issues/71 (opened Jun 7, 2026)

## 15. Lower-ranked observations from the #172 harvest (observed, one line each)

- Over-application is acceptable at the trigger layer and a defect at enforcement; enforce only on facts. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582805 (A6)
- String matchers cannot tell using a word from quoting or forbidding it (use/mention). https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029582895 (A7; note the summary lists A7 and A8 anchors adjacently, check)
- Annotation theater: guidance that is acknowledged but not acted on yields a compliance record that certifies the failure; require a live behavior test. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583071 (A9)
- Register and effort are independent; condensing needs high effort. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583469 (B1)
- Constraints do not propagate on their own; restate at every hand-off. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583567 (B2)
- Judge liveness by artifact mtime, not process visibility. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5084887241 (B11)
- Label harness beliefs VERIFIED or ASSUMPTION; two confident beliefs were later disproven. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5084887364 (summary lists B12 and B13 anchors close together; verify)

---

## UNTESTED (opinions, plans, proposals)

- #52 taxonomy: skill structure is lint-able in CI; triggering is an LLM-judged activation A/B; behavior is "open"; an idea of a cheap deterministic proxy for descriptions is "open". https://github.com/<owner>/ex-cog-dev/issues/52 (Jun 6, 2026). UNTESTED.
- #52 comment 3: a functionality suite needs a fixed profile, gold outputs per turn, a per-field rubric (including whether a threshold came from the profile or was invented), adversarial cases, over-flag and under-verify tests, repetitions, a no-skill control. Its worked run (32 sessions, N=3, recall 12/12) was observational, not a scored suite. https://github.com/<owner>/ex-cog-dev/issues/52#issuecomment-4640308969 (Jun 6, 2026). UNTESTED as a suite.
- #74: functional testing needs a fixed profile, gold outputs, rubric scoring, adversarial cases, no-skill control; repetitions, graders and scripted triggers are not specified in the body. The only comment (Jul 12, 2026) plans an A/B of the register for the first consumer. https://github.com/<owner>/ex-cog-dev/issues/74. UNTESTED.
- Test-design discipline (one variable per arm, ceiling-first, over-fire traps, numerator not equal to denominator, name the validity limit) extracted into a shared sub-layer only at the second consumer (YAGNI). https://github.com/<owner>/ex-cog-dev/issues/52#issuecomment-4640277375 and https://github.com/<owner>/ex-cog-dev/issues/52#issuecomment-4642960229. UNTESTED.
- #172 A11, a resolution-quality rubric for non-binary cases, was marked tentative and orphaned in its own battery. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5029583175. UNTESTED.
- #160 comment 6 proposes an E17 spiral-then-guard chaining arm and scoring "correction-yield" (named in-run revisions) beside verdicts. https://github.com/<owner>/ex-cog-dev/issues/160#issuecomment-5024356328. UNTESTED.
- #173 revised plan: deliver the line through a situations layer, re-run D0 vs D1 with a synthetic cue, test false-positive cost. Self-replication was untested (0/9 runs spawned subagents). UNTESTED.
- #172 Aug 3 note: decouple CI review from the Anthropic-bound action; raw API calls have no tool surface to constrain. https://github.com/<owner>/ex-cog-dev/issues/172#issuecomment-5168371039. UNTESTED. The thread has no raw-API vs Claude Code comparison of rule behavior; the only harness differences recorded are headless `claude -p` being a leaner context than interactive use (#129), Claude Code results not transferring to Cowork (#160), and Opus vs Sonnet pins per test.

Gaps for this problem: no thread tests a multi-turn "keep the aim, change the means, ask" style rule; no thread reports a control rate measured across repeated rounds at small n beyond #129's two-window drift check; model/effort effects appear only as pins (Sonnet 4.6, Opus 4.8) and "even at low effort 40/40 pass" (#160).

---

## Coverage table

| Thread | Comments read / total | Hidden items left |
|---|---|---|
| issue #172 | 23 of unknown total (items 1-15 and 17-24 of the timeline; labels shown A13, A1-A9, A11, A12, A14, B1, B2, B10-B16, Aug 3 note) | 21 timeline items behind "Load more" between B2 and B10 (includes missing A10 and B3-B9); page truncated after the final event. Not opened. |
| issue #160 | 7 comments read / total not stated (no Load more shown), plus 1 title event | none shown |
| issue #72 | 6 comments read / total unknown (6 commit events not counted) | 17 items behind "Load more", unread; the summary also gave no per-comment anchors |
| issue #52 | 5 comments read of 5 listed, plus 4 commit events | none shown |
| issue #128 | 4 comments read of 4 listed (8 activity entries) | none shown |
| PR #127 | 4 owner comments read / total not stated, 3 commits | none shown; gate definitions live in #129 |
| #173 (extra) | 1 comment read / total unknown | page truncated; later comments and the second commit not seen |
| #129 (extra) | 4 comments read / 4 | none shown |
| #131 (extra) | 0 comments (none displayed); body read | comments may exist but were not displayed |
| #71 (extra) | 1 comment read / 1 shown, plus body | none shown |
| #74 (extra) | 1 comment read / 1 shown, plus body | none shown |
| #53, #68, #69, #73, #77, #130, #132, #133 | not read | n/a (extra cap of 6 used on #173, #129, #131, #71, #74 plus none; #53 and #77 left unread) |

Context pack: read in full (1971 lines, in three reads). Its method applied here: claims are per-claim confirmed-paraphrase or flagged, self-reports are discounted, tiers are separated, hidden items are reported rather than guessed.
