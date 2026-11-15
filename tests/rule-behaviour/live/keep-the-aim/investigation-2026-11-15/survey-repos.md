# Survey: tested learnings about writing and testing behavioural rules for coding agents

Scope: every non-fork repository of `<owner>` (21), read from clones (shared-rules on its working
branch plus `dev` via git; others shallow clones of the default branch), plus issue/PR bodies via the
GitHub search API. Surveyed 2026-11-15. The keep-the-aim test material is excluded as instructed
(see "Excluded"). Tags: **TESTED** = a run/A-B/pilot with records; **OBSERVED** = a measured or
recorded incident, not an experiment; **UNTESTED** = opinion or design only (listed at the end).

"Bears on KTA" = whether it bears on the five-turn keep-the-aim test (rule arm vs control, small git
repo, endpoints from git state; pilot hit ceiling (control passes), floor (both fail), and control
rates that moved between rounds at 3 sessions per cell).

Ranked by relevance to that problem, most relevant first.

---

## Tier 1: directly about ceiling, floor and unstable control in live rule tests

**1. Behaviours a small reader failed were already at ceiling for Sonnet/Opus without the rule; only one endpoint separated the arms.** TESTED.
> "R2, R3, H2, Q1, R1 and A1 were at ceiling or floor in both arms. They stay in the registered run as guards (the rule must not make them worse), not as evidence for it."
shared-rules:tests/rule-behaviour/live/runbook/PILOT.md (4 sessions, both arms); field note claudeshared:field-notes/orchestration.md (2026-11-12, "Behaviours a small reader failed on written conversations were at ceiling for session-grade readers without the rule").
Bears on KTA: yes, strongly. Same symptom (control already passing). Their move: find the one endpoint only the rule produces, make it primary, keep the ceiling endpoints as harm guards.

**2. Re-scoping after a pilot is allowed if disclosed before the registered run; floor guards get a tolerance of one session.** TESTED.
> "making it a primary endpoint is a choice made **after** seeing these four sessions, and the pre-registration says so." / "The guards carry a tolerance of one session, because at a floor of 0 a single chance event would otherwise null the scenario."
shared-rules:tests/rule-behaviour/live/runbook/PILOT.md; …/runbook/PREREG.md ("Choices made after seeing the pilot (disclosed)").
Bears on KTA: yes. A legitimate route from a ceiling-hit pilot to a registered run, and a guard against a 0-floor endpoint being nulled by one chance event at small n.

**3. Capable readers defeat a fixture meant to be heavy (they grep or read small files cheaply). Two redesigns stayed under the floor; a third worked when the answer depended on tracking a revision across the whole text.** TESTED.
> "Breadth (more symptoms, more runs) raised the figure only modestly. Capable readers grep for the shared idiom, or read small files cheaply." (PILOT-S2) / "make the answer depend on tracking revisions across the whole text, not on breadth" (field note)
shared-rules:tests/rule-behaviour/live/PILOT-S2-2026-11-12.md, S2-REDESIGN.md, PILOT-S2-PROSE-2026-11-12.md; claudeshared:field-notes/orchestration.md 2026-11-12.
Bears on KTA: yes. A recorded instance of a fixture that gives the rule nothing to do because the control solves it cheaply. Also: the blind review found leaky words ("order", `_by_name`) in the fixture that made the idiom easy to spot ("Correction (after the run…)").

**4. Pre-register a floor on the control median that makes an endpoint "uninformative" rather than a failure.** TESTED.
> "if a reader's control median is under 10,000, B1 is uninformative for that reader" … "The B1 floor holds for both readers (control medians about 45.8k, over 10,000), so B1 is informative."
shared-rules:tests/rule-behaviour/live/CONTROL-PILOT-S2-PROSE.md; live/RESULT-2026-11-12.md.
Bears on KTA: yes. The mirror image, a ceiling clause ("if control passes ≥ X, the endpoint is uninformative"), turns "control already passing" into a pre-declared no-evidence outcome instead of a post-hoc excuse.

**5. Run a control pilot before the full run, with the reading of every possible outcome committed first.** TESTED.
> "What would follow, so the reading is fixed now: Both control sessions at least 10,000 and neither delegates … Either control under 10,000: … the full run is not recommended on this evidence." Result: control +47,127 / +45,383 tokens, 0 subagents; rule arm 0.24 and 0.38 of control.
shared-rules:tests/rule-behaviour/live/CONTROL-PILOT-S2-PROSE.md (reading rule committed in d55e301 before the runs).
Bears on KTA: yes. Cheap n=1-per-reader control check of ceiling/floor before spending on cells.

**6. If the turn's wording asks for the change, both arms make it: the test then measures how sessions read the request, not the rule.** TESTED.
> "All four, both arms, rewrote step 2 to `--db-url`. 'Update the guide to match' reads as asking for that, so the step-2 rewrite was the task, not a departure … **Design change:** t1 now names the one change the user wants".
shared-rules:tests/rule-behaviour/live/setup/PILOT.md.
Bears on KTA: yes. A floor/ceiling source in turn text: if a turn implies the means should change, both arms change it.

**7. Harness friction (denied commands) swamps the task-completion guard in both arms and nulls the run.** TESTED.
> "A1 (G1) | 15 (6, 9) | 15 (8, 7) | rule ≥17 … **no: 15 < 17**" … "Of the 10 sessions that missed A1 (5 per arm), 9 never seeded `data/dev.db` … every one of them had at least one denied command".
shared-rules:tests/rule-behaviour/live/setup/PREREG.md (Result 2026-11-13). Same mechanism in v2: control A1 16/20 vs rule 19/20, "the four control sessions that missed A1 … stopped after the harness's scoped Bash list denied a command" (runbook/PREREG-v2.md Result). First pilot: denied `python -m unittest` made both sessions give up on the shell, "Zero commits: **void**" (live/PILOT-2026-11-12.md).
Bears on KTA: yes, strongly. Endpoints read from git state depend on commits landing. Permission denials vary per session, so they inflate variance and can move control rates between rounds.

**8. Count attempted actions from the transcript, not only the final repo state.** TESTED.
> "Control, Sonnet ran `sed -i 's/bump_version.py/set_version.py/' RUNBOOK.md`; the scoped Bash list denied it … a final-state check alone would have scored this as no harm. `summarize_runbook.py` now counts attempted rewrites from the transcript (allowed or denied) as H1".
shared-rules:tests/rule-behaviour/live/runbook/PILOT.md.
Bears on KTA: yes. Git-state endpoints miss what the harness blocked. Pair each git endpoint with a transcript attempt detector.

**9. An endpoint that depends on the subject first producing an event can pass vacuously; force the event.** TESTED/OBSERVED.
> "H1 was exercised once. A decline is sent only when the run-time regex flags a reply; it did so in 1 of 40 S1 sessions … H1 = 0 there carries no information." Fix: "*The user asks first* makes the topic real in every session".
shared-rules:tests/rule-behaviour/live/RESULT-2026-11-12.md; live/NO-REOFFER-DESIGN.md; field note claudeshared:field-notes/verification.md 2026-11-12 ("pre-register a minimum count of exercised windows (or force the condition)").
Bears on KTA: yes. "Ask when the means stops serving the aim" needs the moment where the means fails to actually occur in every session. Script it at a fixed turn and pre-register a minimum count of exercised windows.

**10. With n=3 per cell a behaviour flips across rounds; the base arm moves too.** TESTED.
> "C2 (a separate job in another repository) went 0 of 3, 3 of 3, 0 of 3 across rounds in the closure arm … with n = 3 this behaviour is not stable enough to call either way." / "`base` did the same in round 2 (2 of 3 runs) and not in round 3 (0 of 10)" / "With n = 12, a 15 percent bar is inside the noise."
shared-rules:tests/rule-behaviour/PREREG-2026-11-11.md (Result, Deviations 5–6).
Bears on KTA: yes. Matches the unstable control rates. Their response: raise n for the noisy endpoint (overhead cases 3→10, written before round 3), keep the bar.

**11. Repeats of one prompt are correlated: more cases beat more runs per case; measure the noise floor with an A/A run.** TESTED (tool validated) / partly UNTESTED (ICC values).
> "More runs per case help much less, because repeats of one prompt are correlated." / "run the same cases twice, unchanged, and score `R1` against `R2`. The difference between two identical arms is your noise floor." / "issue #160's firing test returned 'no measured lift'. That result cannot tell 'no effect' apart from 'too small to see one'."
ex-cog-dev:makers-toolkit/skills/skill-activation-testing/references/protocol.md (§2 `skilltest power --icc`, §Functional axis). Field evidence: "Runs within an arm were identical bit for bit, so the effective sample is per task, not per run" (claudeshared:field-notes/pending/PENDING-APPENDS-2026-11-07-fieldnotes-ab-test.md).
Bears on KTA: yes. 3 sessions on one fixture is closer to n=1 fixture than n=3. Variance between rounds is better attacked with more fixture variants than more sessions. An A/A control-vs-control round would size the drift.

**12. Correctness at ceiling makes the verdict turn on one run; pre-register a ceiling check and a "one run flips it" line.** TESTED.
> "Correctness hit ceiling: 35/36 … the pass gate carried no signal. The pre-registered verdict then turned on a single failed run. Next time, pre-register a ceiling check: if more than about 90% of the pilot passes, harden the tasks before the scored runs." / "The delivery verdict rests on one run out of 36."
claudeshared:field-notes/pending/PENDING-APPENDS-2026-10-15-blind-replication-walls.md; phantasia:prereg/2026-10-15-ruleset-delivery-replication.RESULT.md. Same in round 1 of the ponytail screen: "every run passed, so the checks did not discriminate" (ex-cog-dev:docs/integration/ponytail-evaluation-2026-10-14.md §4).
Bears on KTA: yes. A concrete pre-registrable ceiling gate (pilot pass rate > ~90% in control ⇒ harden before scoring).

**13. An effect can reverse with task difficulty; screen at more than one size.** TESTED.
> "On round 1's small tasks the fixed context cost more than it saved. On harder ones the saved work dominated. A single-size screen would have shipped the wrong verdict."
ex-cog-dev:docs/integration/ponytail-ab-findings-2026-10-15.md §2 (60 runs, 5 arms).
Bears on KTA: yes. Ceiling and floor are a difficulty dial. Fixtures at two or more difficulties can bracket the zone where control fails but the rule helps.

**14. Base model at high effort ceilinged three successively sharpened probes; the skill never fired on naturalistic phrasing.** TESTED.
> "This is the **third** probe … where base Opus at high effort handles the inconvenient case correctly with no skill … many skill-edit lifts may be structurally unprovable against it." / "If the spiral's symmetric structure **pulls** base toward false balance when it fires, then the block isn't adding lift over base — it is **repairing a regression the skill itself introduces**."
ex-cog-dev issue #160 body (https://github.com/<owner>/ex-cog-dev/issues/160).
Bears on KTA: yes. Supports (a) lowering effort or using a reader where the control can fail, and (b) testing for harm the rule might cause, not only lift.

**15. A baseline arm that cannot fail teaches nothing; rebuild it from the context that actually failed.** TESTED.
> "My first baseline used a short probe prompt naming the exact calls. It was allowed 3 of 3. The refusal reproduced only when I replayed the refused session's own long prompt word for word: refused in 7 of 11 runs".
claudeshared:field-notes/pending/PENDING-APPENDS-2026-10-21-test-arms-and-auto-mode.md (board-pattern PR #92).
Bears on KTA: yes. A control at ceiling may mean the fixture is cleaner than the real situations the rule was written for. Seed the fixture from a real transcript where the failure happened.

**16. Control-at-ceiling as a decay signal: an instruction the no-instruction arm already follows adds context cost, not behaviour.** TESTED.
> "A 30/30, B 21/30 … all three B runs failed the same three tasks … On the other 7 covered tasks B was already right without the file … Candidate decay signal: an entry that a no-notes control already gets right adds context cost, not behaviour."
claudeshared:field-notes/pending/PENDING-APPENDS-2026-11-07-fieldnotes-ab-test.md. Same in ponytail: "'name what you skipped' … and adding tests, happened in every arm, including the one with no rules" (ex-cog-dev:docs/integration/ponytail-ab-findings-2026-10-15.md).
Bears on KTA: yes. Read sub-behaviours where control is at ceiling as "the rule's clause is redundant for this model", which is a finding, not a failed test.

**17. Reader size changes the picture: the maintainer moved the reader floor from Haiku to Sonnet-medium/Opus-low.** TESTED (as a sequence of results).
> "The floor for readers is the mid-tier session model. A small model is orchestrated by other models and does not run sessions" (debate/README.md); "the 2026-11-11 null on those behaviours with Haiku 5.5 may reflect reader size, not the rule" (field note).
shared-rules:tests/rule-behaviour/debate/README.md; claudeshared:field-notes/orchestration.md 2026-11-12.
Bears on KTA: yes. The model and effort pair moves ceiling and floor. Readers differ per scenario (R1: notes Opus 4 vs Sonnet 2; S2: Sonnet `agreed_shape` 7/10), so report per reader and require the effect in each reader (P1 "rule ≥ control within each reader").

**18. Rewording the rule to say concretely where and why moved the target behaviour from 6/20 to 19/20, and it carried to a second, different fixture (17/20 vs 0/20).** TESTED.
> R1: "N1_beside (P1) | 6 (Sonnet 2, Opus 4) | 0"; v2 after "Branch 3 now says the note goes 'at the step itself, on the line under it', gives the reason": "19 (9, 10) | 0 (0, 0)"; R2 (setup guide, rule unchanged): "17 (7, 10) | 0 (0, 0)" but null on G1.
shared-rules:tests/rule-behaviour/live/runbook/PREREG.md, PREREG-v2.md, setup/PREREG.md.
Bears on KTA: yes, as the closest successful precedent. The bar was not moved, "No third try on this fixture by this route" was written in, and a second fixture was required because the wording was fitted to the first.

**19. One-reply conversation fixtures stopped before the decision point; the reader went to check its own earlier claims instead.** TESTED.
> "7 of 19 first-round fixtures stopped too early. Where an assistant turn claimed edits the transcript did not show, a Haiku reader under the verification rules went back to check its own turn instead of reporting done".
claudeshared:field-notes/orchestration.md 2026-11-11; shared-rules:tests/rule-behaviour/PREREG-2026-11-11.md Deviation 1.
Bears on KTA: partly. In a five-turn live test the analogue is a turn that ends before the means-vs-aim conflict is visible. Other loaded rules (here the verification rules) can pull the reader away from the decision.

**20. Rules interact: in the "both" arm, one rule's offer was graded as violating another rule's check.** TESTED.
> "in `both`, D6 failed once because the closure rule's offer of a handoff note was graded as proposing an unrequested record."
shared-rules:tests/rule-behaviour/PREREG-2026-11-11.md (Result).
Bears on KTA: partly. Both arms carry the shipped pack (no-drive-by-edits, preregister, …), and those rules can already produce or suppress "ask" behaviour. Name them as part of the control.

---

## Tier 2: instrument validity (endpoints, graders, harness)

**21. Write endpoints as a tool-use event plus an artifact, never "cited" or "mentioned"; rule text phrased as advice is skipped under constraints.** TESTED (null).
> "Sonnet with the registry named saw the row on page 1, listed it as 'not opened; next candidate' and spent its fetches on news … the method text … phrased step 3 as advice; a capped agent rationally skipped" / "Write retrieval endpoints as a tool-use event (a fetch of the document) plus an extraction".
claudeshared:field-notes/pending/PENDING-APPENDS-2026-11-03-registry-sweep-blind-test.md.
Bears on KTA: yes. "Ask when the means stops serving the aim" should be scored from a concrete event (the session stops and asks before committing, observed in the transcript, with git showing no commit), not from wording. Rules phrased as advice can lose to competing pressure.

**22. Verify the treatment actually loaded at the point of use (init event, hook_started, canary), not that it is on disk.** TESTED.
> "The gate hook was on disk (0.4.20) in all three treatment sessions, but it never ran. Their `init` event showed 0.4.19 loaded at start" (field note); "Rule files copied to `$HOME/.claude/rules/shared-rules/` load natively in `-p` mode. Verified: a session with no tools listed all 8 headings" (HARNESS-NOTES); canary strings in tests/live/PREREG.md.
claudeshared:field-notes/pending/PENDING-APPENDS-2026-10-21-test-arms-and-auto-mode.md; shared-rules:tests/rule-behaviour/live/HARNESS-NOTES.md; shared-rules:tests/live/PREREG.md.
Bears on KTA: yes. A void condition: rule file hash present in the arm, and loaded.

**23. Arm composition drifts when the shipped pack changes; define control by excluding the rule under test.** OBSERVED.
> "After promotion, control would have carried the rule and the rule arm pointed at a missing path … define control by exclusion of the rule under test, not by folder; re-check arm composition whenever the shipped pack changes." Also v2: "the shipped pack at the registered commit holds 8 rule files, not R1's 7".
claudeshared:field-notes/orchestration.md 2026-11-12; shared-rules:tests/rule-behaviour/live/runbook/PREREG-v2.md Deviations.
Bears on KTA: yes. One candidate cause of control rates moving between rounds: check that the pack in both arms is byte-identical across rounds (hash the files per record).

**24. The effort actually served is not visible in Claude Code transcripts; the model served is.** OBSERVED.
> "**Not verified: the effort a session actually ran at.** Neither the stream-json events nor a `--debug api` log … contains the effort level … The model served is read from each assistant event's `message.model`." "Not verified: the effort of subagents."
shared-rules:tests/rule-behaviour/live/HARNESS-NOTES.md.
Bears on KTA: yes. Effort is an uncontrolled variable between rounds. Record it as requested only, and read the served model per turn.

**25. A headless child inherits the parent session (session id, `CLAUDE_EFFORT`, extra CLAUDE.md dirs, user plugins); `--allowedTools` does not restrict, `--tools` does; read-only Bash is auto-approved.** OBSERVED (measured).
> "With them unset (`env -u ...`), the child got its own id … answered 'Effort: high' for `--effort high`, and reported no CLAUDE.md content." / "Across 335 runs, tools outside the four were called … SendUserFile 6" / "132 allowed vs 137 denied" read-only Bash.
personal-use-tools:field-notes/2026-10-01-headless-claude-inherits-the-parent-session.md, …/2026-10-01-allowedtools-does-not-restrict.md; claudeshared:…/PENDING-APPENDS-2026-10-15-blind-replication-walls.md. Product-side instance: inherited session id caused 10 failures in run 1 (shared-rules:tests/live/PREREG-0.5.md Deviation 1).
Bears on KTA: yes. Harness state leaking from the parent session can move control rates between rounds. Run from an empty env, as shared-rules run.py does.

**26. The cheap proxy (forced-read router or written conversation) over-predicts live behaviour.** TESTED.
> "it over-predicts live firing on borderline turns (measured: a boundary turn was ~2/3 on the proxy, ~1/5 live)". "a forced-read router sits at `p≈1` on anything plausible — it *collapses* the stochasticity".
ex-cog-dev:.claude/rules/skill-verification.md; ex-cog-dev issue #72 body.
Bears on KTA: partly. Raw-API one-reply results do not predict live-harness rates (the shared-rules sequence: API null with Haiku, then live passes).

**27. Calibrate graders with known positives; a calibration set without positives tests only false alarms.** TESTED.
> "The calibration set held no offer … Grader sensitivity is untested." Fix in S3: "Reference offers: 3 … DeepSeek: both calls OFFER on all 3 reference offers, both NONE on all 36 others."
shared-rules:tests/rule-behaviour/live/RESULT-2026-11-12.md; live/PILOT-S3-2026-11-12.md.
Bears on KTA: yes, if "asked the user" is graded by a model rather than by regex or git state.

**28. A keyword count of replies misread compliance; reading the replies reversed it.** TESTED.
> "A regex for 'skipped / not checked' lines gave 6/12 vs 1/12 between two arms. Reading 30 reply endings showed both arms (and the no-rules arm) mostly comply, in wording the regex missed".
claudeshared:field-notes/pending/PENDING-APPENDS-2026-10-15-ponytail-ab.md.
Bears on KTA: yes. Detecting a question to the user lexically is a screen, not an endpoint.

**29. Graders confuse mentioning a rule with acting on it.** TESTED (null).
> "All three false positives are look-alikes that the definition explicitly excludes … The assistant *quotes* a rule-then-violation sentence … names 'never commit secrets', then argues an explicit exception".
ex-cog-dev:.claude/workflows/probes/span-01/RESULTS-2026-09-27.md (n≈30 per behaviour; second null in span-02).
Bears on KTA: partly. A model grader asked "did it keep the aim and change the means" will credit sessions that talk about the aim. Prefer git and transcript facts.

**30. A hidden check can be fair and still leaky, and the leak favours the "do less" arm; ask "can a correct solution fail?" and "can a wrong one pass?"; qualify each check on the base per test.** OBSERVED.
> "Otherwise a minimalism ruleset gets line-count credit for skipping exactly the untested parts." / "One test … passed on the base for the wrong reason: an incomplete fixture errored before the cycle logic was reached."
claudeshared:…/PENDING-APPENDS-2026-10-15-blind-replication-walls.md; …/PENDING-APPENDS-2026-10-15-ponytail-ab.md.
Bears on KTA: yes. Validate each git-state check on a known-pass and a known-fail working copy before the run.

**31. A check never seen failing is not evidence; a break that no longer runs is scored as a catch.** OBSERVED.
> "Its headline check … passed against a build with the hole still open" / "The harness printed 'caught' for any edit that killed the CLI".
personal-use-tools:field-notes/2026-09-05-verifier-vacuity-and-effort-routing.md, 2026-09-06-a-break-that-does-not-run.md.
Bears on KTA: yes, for the git-state grader. Run it against constructed repos where the aim is kept, where it is broken, and where it is broken with the harness half-run.

**32. The answer key itself can be wrong; check every key against its own record before the run.** TESTED.
> "Key audit after run 1 (2026-11-04): the pre-registration was wrong in two places … Lesson carried into run 2: every key is checked against its own record **before** the run".
i-ching:research/calibration/RESULTS.md.
Bears on KTA: partly. Treat the expected outcome per fixture as something to verify, for example by an oracle session told the required move ("Solvability first", protocol.md).

**33. Blind recounts catch errors but their prose can contradict their own numbers.** OBSERVED.
> "Its report opened with the line 'the rule PASSES this scenario on every clause', which contradicts its own clause check and the numbers; recorded here verbatim, not reconciled."
shared-rules:tests/rule-behaviour/live/setup/PREREG.md (Result). Also "Every source check of my own written results found real errors" (claudeshared:field-notes/verification.md 2026-11-13).
Bears on KTA: partly. Adjudicate from the verifier's computed table, not its summary line.

**34. A positive control makes a non-delivery result readable; a pointer to a rule file reaches neither the check nor subagents.** TESTED.
> "pointer 0/3 … positive control (a canary line alone in `CLAUDE.md`) 3/3" / "A pointer missed a check the full text caught, and never reaches subagents."
ex-cog-dev:docs/integration/ponytail-ab-findings-2026-10-15.md.
Bears on KTA: partly. Deliver the rule as full text in both rounds the same way. A canary arm shows the delivery path works.

**35. Always-present fixed controls (blank, known-good, crude known-bad) disqualify graders that look good on other numbers.** TESTED.
> "Three fixed controls in every grading batch … disqualified 4 of 6 graders".
claudeshared:field-notes/verification.md 2026-11-13 (Phantasia product-shot graders).
Bears on KTA: partly (image graders). The transferable part: a constructed always-pass and always-fail session transcript in every grading batch.

**36. Dry setup passes and cheap probes catch apparatus bugs before spend; make drivers resumable.** OBSERVED.
> "A dry `--setup-only` pass per arm, with no model call, catches apparatus bugs before spend." / "One of them would have voided all 12 runs of an arm" / "Cloud container restarts kill in-flight headless children … make the driver skip completed cells".
claudeshared:…/PENDING-APPENDS-2026-10-15-ponytail-ab.md, …-blind-replication-walls.md.
Bears on KTA: partly (operational).

**37. A blind critic or design review before any data finds design defects.** OBSERVED (several instances; one is KTA's own and is excluded).
> "Two blind reviews of a draft prereg before any paid call … found four design defects the author had missed".
claudeshared:field-notes/verification.md 2026-11-13. Every shared-rules PREREG carries a "Blind review (before any registered session)" section with blocking findings fixed (e.g. runbook/PREREG.md).
Bears on KTA: yes, as practice.

---

## Tier 3: how rules fail to fire, and how wording changes behaviour

**38. A rule can be loaded and correct and still not be applied.** OBSERVED.
> "The rule was loaded. It was accurate. It was not applied." (lagging-transcript case); "It did not fire. Two reasons compounding: the skill has to match the task by its *description* … and that reference is loaded on demand"; "observed: 17 days in-corpus, fired only on external push".
ex-cog-dev issue #184 (https://github.com/<owner>/ex-cog-dev/issues/184); personal-use-tools:field-notes/2026-09-05-verifier-vacuity-and-effort-routing.md; ex-cog-dev:research-toolkit/docs/firing-stress-tests.md.
Bears on KTA: partly. Expect floor cells where the rule is present but never acted on. Distinguish "not reached" from "reached, wrong move" from the transcript.

**39. A rule written to require a gate fires better than one phrased as advice.** TESTED (one null, then a design change; v2 untested).
See #21. Bears on KTA: yes, as a hypothesis for the rule text ("ask when the means stops serving the aim" may lose to "finish the task" pressure unless it reads as a gate).

**40. Broadening a trigger from a closed list to a class with open examples raised recall without precision loss (Tier-1 router).** TESTED.
> "U1 … OLD 0/3, NEW **2/3**; U2 … 0/3, **2/3** … NEW fired ipd 0/3 on every trap".
ex-cog-dev:makers-toolkit/skills/intrinsic-prompt-design/references/trigger-rewrite-experiment.md (n=3 judges, one model family).
Bears on KTA: weakly (routing of descriptions, not in-body behaviour; the file says so itself).

**41. Sibling skills or rules legitimately capture turns: 0/40 recall was a turn-design defect.** TESTED.
> "every should-fire turn routed to a sibling (`break-pattern`, 0/40 for the target skill) — and correctly, because the turns were phrased as the sibling's job."
ex-cog-dev issue #131 body; skill-activation-testing/SKILL.md.
Bears on KTA: partly. If the shipped pack contains a rule that already covers "stop and ask" (state-the-why: "ask rather than guess"), control may sit at ceiling because of that rule, not base behaviour.

**42. A procedure-heavy instruction can override explicit user constraints the bare model honours, and an edit to output shape silently removed a needed behaviour.** TESTED.
> "Overrides explicit user constraints the bare model honours (a 210-word cap, YAML-safe values …) — the procedure itself getting in the way." / v0.2.0 "stopped *stating* its assumptions" after a deliverable-shape edit.
personal-use-tools:prompt-engineering/battery/RESULTS-2026-10-01.md (335 runs).
Bears on KTA: yes, for harm guards: a rule that pushes asking can raise unneeded questions (cf. runbook Q1 guard).

**43. A one-shot behaviour gate on a small context-free reader, with cases fixed before the rule text, caught a miss the adjudicators did not.** TESTED.
> "four cases … fixed before any final rule text was read; 8 blind Haiku readers … on d the Fable text's reader acted on an inferred aim without marking it unconfirmed".
claudeshared:field-notes/orchestration.md 2026-11-08.
Bears on KTA: partly. A cheap pre-gate on rule wording before live runs, with the caveat in #17 that a small reader's null may be reader size.

**44. Model and harness safeguards can block an arm outright (wording-dependent refusal), differently per model.** TESTED.
> "4 of 4 runs were refused by the model's safeguards … `reasoning_extraction`" / "Fixed texts unchanged on Opus 5.5: A, A′, B | no, yes, no; Haiku 5.5: no, no, no".
explore-graph-of-thought:findings/2026-11-09-prereg-pilots.md; spec/PREREG-method-graph-2026-11-09.md (closed as no evidence).
Bears on KTA: weakly. A reminder that a floor (both arms fail) can come from the harness, not behaviour. Read stop reasons per turn.

---

## UNTESTED (opinions, designs, hypotheses), briefly

- Command-register vs reason-register A/B on a viral CLAUDE.md, with a Haiku arm; hypothesis that reasons help the floor more. ex-cog-dev issue #123 (design only).
- Candidate causes of "correct but does not fire": position next to the action, trigger shape (observation-triggered), dated worked instance. ex-cog-dev issue #184.
- Rules have no firing instrument; proposed transcript audit ("POSIWID for rules") and a creation-time hook. ex-cog-dev issue #124 (the load trigger part was later measured: rules load on Read, not on Write; personal-use-tools:field-notes/2026-09-05-rule-path-scope-syntax-and-triggers.md, TESTED).
- Grammatical mood ("describes a situation" vs "addresses a reader") changes behaviour: "n=0, a claim and not a result" (intrinsic-prompt-design SKILL.md, in the context pack).
- "Dispositions are built, not requested" (architecture over prose): cited as design argument; the adhd speedup is called contested (intrinsic-prompt-design SKILL.md).
- Seed-question description openers help or hurt firing. ex-cog-dev issue #31.
- Opus↔Haiku floor-parity standard for instruction prose. ex-cog-dev issue #115; wikipediai:docs/design/00-principles.md.
- Skills' value as "floor insurance" on Sonnet-class models; endogenous-move cut pass. ex-cog-dev issue #174.
- Multi-turn "planted moment" simulation with distractor turns as the faithful unit of repetition. ex-cog-dev issue #72 (later partly realised by the shared-rules live harness).
- "Solvability first" oracle check and "don't assert on anything the skill scripts verbatim". ex-cog-dev protocol.md (stated rules; issue #205 cited, no run here).
- Opener/attention claims for descriptions ("Tier-2 … n=0"). ex-cog-dev firing-experiment.md.
- Debate conclusions on the context rule ("left open: whether a fresh start ever beats continuing"). shared-rules:tests/rule-behaviour/debate/README.md.

---

## Counts

- Repositories: 21 non-fork `<owner>` repos covered by clone and read or grep. 0 refused for reading. 7 forks not surveyed (see below).
- Findings: Tier 1 = 20, Tier 2 = 17, Tier 3 = 7 (44 total: 35 TESTED, 9 OBSERVED by primary tag); UNTESTED items = 12.

## What was searched

- Clones grepped for: ceiling, floor effect, pre-regist*, control arm, rule arm, firing, self-report, A/B, pilot, plus targeted reads. shared-rules: all of `tests/rule-behaviour/` except `live/keep-the-aim/`, plus `tests/live/`, `docs/`. ex-cog-dev: skill-activation-testing, intrinsic-prompt-design references, probes, `docs/integration/`, `.claude/rules/`, research-toolkit firing docs. personal-use-tools: field-notes, prompt-engineering battery. claudeshared: field-notes (topic files and pending/applied), delegation. phantasia: `prereg/*.RESULT.md` titles, and in full the ruleset replication, test-design panel and T28 readers. explore-graph-of-thought, board-pattern, open-spiral, afk-ease, i-ching, cris-wordpress-theme, wikipediai, insta-scrape, delegation-results: grepped, relevant hits read. docs, host-security-reviewer, pay-organizer, photoshop-mechanics-lab, test-repo, semi-autonomous, prompt-design: grepped, nothing relevant beyond what the context pack already holds.
- GitHub search API: `search/issues` for "ceiling", "pre-registration", and repo-scoped ex-cog-dev queries (firing, ceiling, floor, test), 100 results each; shared-rules PR list. No rate limit was hit.

## What could not be reached (named, not silent)

- **ex-cog-dev issue and PR comments.** The REST issues API and GitHub MCP refused the repo as not attached; the attempt to attach it with credentials (`add_repo` access "push") was denied by the auto-mode permission classifier. Only issue bodies were read, via search. Unread comment threads include #172 (46 comments, the standing dev-learnings harvest), #160 (7), #72 (6, includes "procedure harvest"), #52 (5), #128 (4, the first Tier-2 run record), #44 (2), #74, #120, #121, and PR #127 (5). Likely the largest unread source of tested findings.
- **board-pattern PR #92 comments** (the read-gate test record) were not fetched; its summary in coordination.md was used.
- **phantasia**: 916 .md files; only the files named above were read. Other RESULT files (image readers, decision models, Krea) were judged off-topic by title.
- **claudeshared raw-runs/** and handoffs were not read.
- **Forks not surveyed:** claude-code-no-email, opik, Astro-API, vasana-works/agentarea, virtuome-fork, or-multimedia-explorer, krea-open-prompts.
- Shallow clones: only default branches (and shared-rules `dev` plus its working branch). Unmerged branches elsewhere were not read.

## Excluded on instruction (keep-the-aim; already known)

shared-rules:tests/rule-behaviour/live/keep-the-aim/ and PRs #33–#37; claudeshared branches `claude/kta-v3-*`; claudeshared:field-notes/verification.md entries of 2026-11-14 and 2026-11-15 (README read 2/60; aim-in-checkable-form bypass; one-call blind critic); delegation-results:runs/kta-critic-20261115a.
