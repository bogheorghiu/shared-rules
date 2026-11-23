# Keep-the-aim: conclusions

Written 2026-11-23 by a Fable 5.2 subagent from `DESIGN.md`, the three outside reviews in `reviews/final/` and the prior-art study. Line references are to `DESIGN.md` in this folder. Tags: **GROUNDED** (the record shows it), **UNRESOLVED** (not tested, or tested too thinly to say), **CONTRADICTED** (the record goes against it). Anything marked *my inference* is mine, not the record's.

## The point

Short on time: read this section and the last one, "What to decide now".

1. **The tests did make the control fail once, and it is the failure you describe.** In L1, sessions without the rule kept the old page as it was and put the new thing behind a tab: 0 of 8 served the purpose (L1202-L1203, L1223). The rule did not change that: 0 of 8 (L1241).
2. **Everything else the rule asks for, the model already did without it.** Noticing a step that quietly stopped working: 32 of 32 (L1465). Designing a new board for its own aim with an old layout sitting next to it: 16 of 16 (L1688-L1689).
3. **So the rule is aimed at the wrong step.** It teaches noticing and telling. In L1 the sessions noticed and told, 8 of 8, with or without the rule (L1494). What they did not do is change what was already there.

"Control" means a session with the eight shipped rules but not this one. "Served" means a reader looking at the result could do what the page was for.

## What the series showed

| # | Finding | Evidence | Tag |
|---|---|---|---|
| 1 | In the normal setup the rule changed no outcome on any task where control could fail. | L1: 0 of 8 both arms (L1241). W1m: 0 of 8 both arms (L1385). K4: rule 1 of 8, control 0 of 8 (L603-L606). | GROUNDED |
| 2 | Without the rule, Opus finds and fixes a step that silently stopped doing its job. | W1 8 of 8 at medium and 8 of 8 at low (L1361, L1371); P1 16 of 16, mirror 8 of 8 clean (L1463). | GROUNDED |
| 3 | Without the rule, Opus does not copy a nearby old layout into a new board, even when a script and the users' own minutes point at it. | H1: 8 of 8 with your "one form" statements (L1625); 8 of 8 with those removed and only the data note kept (L1680). Five replies said why the old layout did not fit (L1683). | GROUNDED for one-turn, small repo, Opus medium |
| 4 | With an existing page in place, sessions add beside it and do not change it. | L1 control: 7 of 8 behind a tab, 1 below the list (L1203). Mirror, where the recorded purpose *asks* for the picture: 4 of 4 still kept the old list on opening (L1204). The log: "what the session protected is the existing page, not the brief" (L1207). | GROUNDED |
| 5 | Telling is not the gap. | Control named the conflict in 8 of 8 L1 replies; rule 8 of 8 (L1494). | GROUNDED |
| 6 | The rule's text works where nothing else supports the model. | Stripped setup (Claude Code's own prompt replaced, other rules removed), Opus low: rule alone 8 of 8, nothing 2 of 8, on two tasks (L792-L793). An unrelated rule of half the length: 1 of 8 and 5 of 8 (L798-L799). Same tasks in the normal setup: 8 of 8 without the rule (L713-L715). | GROUNDED, but a setup nobody uses (L731) |
| 7 | The rule may make sessions put a requested thing in front when the purpose agrees with the request. | L1 mirror: rule 2 of 4, control 0 of 4 (L1241). Registered reading: "surfaces only". | UNRESOLVED (n = 4) |

## What it did not show

- **That the rule helps in your real work.** No test had a long session, a brief written by another session, or a multi-file page (L1693). UNRESOLVED.
- **That the problem is not real.** L1 reproduced it. The lab reproduced one of your three recorded shapes (old kept, new bolted on). It never reproduced "builds only the named specifics, no design": a plain sorted list passed as a fair design (L1621). UNRESOLVED.
- **That the rule does nothing.** v5 was closed as "a null on measurability, not on the rule" (L511). The early rounds that favoured the rule were small and moved with the harness (L544, L323).
- **L1 rests on one scoring choice:** only the opening view counts. The log calls this "the result's main lever" (L1205). You confirmed it (L1208). A reader allowed to open the tab was never scored.

## The best current account of the problem

**Where the three reviewers agree.** The rule has no demonstrated value in the normal setup. L1 is the real lead. The gap is changing the artefact, not noticing. A rule loaded in every session is the weakest fix. The likely cause sits upstream: a suggested form gets written into a brief as if decided, and the builder treats it as an order.

**Where they disagree.**

| Question | Astra | Kimi | DeepSeek |
|---|---|---|---|
| Main cause | The brief gives a proposal the authority of a decision | The same, plus the cheapness of adding versus reopening | The aim is not in front of the session at all ("a missing signal") |
| Runner-up | Cost of reopening built work | Sunk cost, and nobody reads the result as a user | Long context and sunk cost |
| "No reader" as a cause | Explicitly not primary | Part of the runner-up | A contributing factor |
| Fix | Brief format: decided versus proposed, plus one reader task | Brief format plus a fresh reader before commit | Mark templates and scripts with their aim, add a purpose check, keep a thin rule |
| W1m | (not used) | Not a clean mirror: the user ordered the edit | Uses it as evidence the rule does not over-fire |

**Where I depart from them, and why.**

- **DeepSeek's main cause is CONTRADICTED by L1.** The aim was in view and named in 8 of 8 replies (L1494), and the page still failed. Its review also has errors of fact: it says rule and control were "indistinguishable" on the H1 run without the doc (no rule arm ran there, L1649-L1653), and that copying was "physically incompatible" in H1 (the pure copy rebuilt and scored 6 of 7 with one reader, L1620). Its artefact-marking idea is still reasonable; its diagnosis is not supported.
- **"The form arrives as a given" is too broad.** The prior-art study called it the strongest predictor. H1 delivered the form as a given through a README instruction and a copy script, and control passed 16 of 16. The log says this "replays the record's … setup and does not reproduce their failure" (L1635). So a form sitting in a repo file is not enough. CONTRADICTED in that variant; UNRESOLVED for a form inside the brief itself.
- **The reviewers did not have the L1 mirror detail.** The dossier gave them only the count. In the mirror the request and the recorded purpose agreed, and sessions still hid the picture behind a tab (L1204). Brief authority cannot explain that. Protecting what exists can. *My inference:* the lab evidence supports "a session will not displace an accepted artefact without being told it may" more directly than "the brief hardened". The hardening story rests on the prior-art read of two real cases (`reviews/fable-h1-priorart.md`, F-A and F-C), which was one pass that did not read transcripts. It is plausible and untested.

**My account, in one line.** Greenfield, the model designs for the aim. With something accepted already in place, it adds beside it, says so, and stops. The second case is your "technically done but cumbersome". Whether a hardened brief makes this worse is the open question.

One more gap, flagged in the log and never closed: your failures were seen in Claude Desktop, Claude Design and with many skills, "not in headless Claude Code with eight rules" (L705). The grid showed that either Claude Code's default prompt or the eight rules is enough to produce the good behaviour (L725). *My inference:* part of why control passes may be that the lab harness is not the one your failures happened in.

## Why the controls passed, test by test

| Test | Why it was easy | Source |
|---|---|---|
| v1 to v5 (data repo) | The aim arrived as a ready-made test, the gap announced itself, the script was already in view | L171-L174, L492 |
| W1 | "The prompt did the noticing": you named the failure and the file | L1402, L1392 |
| W1m | Control did not pass. Passing meant disobeying "fix the protocol"; the rule itself allows a user-requested edit | L1393 |
| P1 | Two guards, each with its reason beside it; a cheap probe exposes the miss (*my inference* from the fixture, L1430) | L1461-L1463 |
| H1 | Nothing existing had to change. A plain list was good enough (L1621). The users' needs were all in the repo | L1625, L1680 |
| L1 | Control did not pass. An existing page plus a request worded "add" | L1203 |

*My inference:* in every pass the right action was also the cheapest one and displaced nothing. In both control failures (L1, W1m) the right action meant going against something the user had said or something already accepted.

## What form a solution should take

- **Not a rule in every session.** No outcome effect in the normal setup (finding 1), and it made replies longer: rule-arm median 96.5 words against a bar of about 68 in the second calibration round (L206). The series' own pre-registered stop says: if two tasks in two domains do not show headroom, "keep the rule staged, and capture the next real failure from the owner's own harness" (L889). Only L1 showed headroom that survived inspection (the H1 run without the doc tripped the bar for a different reason, L1661-L1663). *My reading:* that stop now applies.
- **Most likely to help: a change at the hand-off**, where a brief is written. Separate what you decided from what was proposed, and state one concrete thing the reader must be able to do. Astra and Kimi both land here. UNRESOLVED: nothing has tested it.
- **A scoped skill** for board and design work is a reasonable carrier for that convention. It is not the active ingredient.
- **A tool** can rebuild from next week's data and render at phone width. It cannot say who decided a layout.

**If any rule text survives**, it is not the current one. Proposed, untested, for use as a test arm only:

> **When you write a brief:** keep what the owner decided apart from what anyone proposed. Say what the reader must be able to find or do, and what must keep working.
> **When you build:** something already in place is also only one way of doing its job. Adding the new thing beside it is a design choice, not a safe default: check what the reader meets first. If the old form gets in the way and you were not told to keep it, change it and say so. If you were told to keep it, say what that costs and ask. Having warned the user does not make a result that fails its purpose done.

## The next test

Build on L1, the one test that reproduced the failure, in two steps.

**Step 1, cheap, reuses everything built (8 control sessions).** L1 unchanged, plus one sentence in the prompt: "You may change what's there if that serves this better." Scoring, readers and anchors as registered for L1. If control now serves, the gap is standing (permission), not reasoning. A reviewer proposed a probe of this kind on 2026-11-17 (a variant saying the visual form is not fixed, "to tell a permission bottleneck from a reasoning one") and it was never run (L1131). Write the pass rule before running.

**Step 2, the hand-off test (Astra's design, which I judge the cleanest of the three).** A partly built, multi-file overview page. A frozen hand-off brief, taken from the real one where your "what if" became numbered design goals (prior-art F-A), anonymised and fixed before any run. Same prompt to every session: finish it for Monday, keep board links working, you may commit. One thing varies: the heading over the proposed layout, "Design goals" or "Proposed in discussion, not decided". Nothing is hidden.

- Measured: blind phone readers start at the normal address, may navigate, and must find the stalled job, what would release it and whom to call, on fresh data, inside a time fixed in advance from reference builds. Separately, a script codes whether the old page stayed with the new view beside it. A reproduction counts only when both happen on a working build.
- Arms: control under each heading; the staged rule under "Design goals". A mirror where the proposed layout is right.
- First, a control screen on "Design goals": 8 sessions. If 5 or more pass, close it as no headroom and do not make it harder.
- Why control might fail: it can show two finished things (old page kept, new view built) without the morning answer being findable. This is a prediction.

Kimi's version adds a second turn and a running scaffold. That tests sunk cost too, but mixes two causes in one test. DeepSeek's version leaves the real need out of the brief, which is the "hide information" route this series ruled out (L1511).

## What to decide now

1. **Keep the rule staged, not shipped.** The record supports nothing else.
2. **Tell us where you saw the failures:** which app, were the shared rules loaded, how long was the session, who wrote the brief. This is free and may explain more than another test.
3. **Run step 1?** Eight sessions on a built fixture.
4. **Build step 2?** A new fixture; the larger spend.
5. **Start separating "decided" from "proposed" in your own briefs now?** Cheap and reversible, but untested. Shipping it to others in shared-rules should wait for step 2.
6. **Rule or skill:** leave open. No text has earned either yet.
