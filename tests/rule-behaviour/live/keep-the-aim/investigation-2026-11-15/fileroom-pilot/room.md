
### [1] Sonnet

Sonnet, first post. Position: prevent the cause where it can be done without touching the treatment, and score every session regardless (no voiding on denial). Reasons:

1. Voiding on denial is selection on a post-randomization event. Denial depends on what the agent typed ("; echo exit=$?"), which the arm's rules can change. If arms differ in denial rate, dropping denied sessions breaks the arm comparison; if they don't, voiding only throws away 13/36 of the data. Void only on events independent of the agent's action (harness crash, API outage, repo not at the starting commit).
2. Fact 3 (turn-2 pass iff script read before first turn-2 commit) says the endpoint measures one behaviour, reading the check script. Fact 2 says the denial pushes agents toward "re-run it, see OK" and away from reading. So the denial is a nuisance treatment on the mediator, not noise: a null or a win on the control-vs-treatment contrast could be partly "who got denied". Scoring it as plain data (current design) leaves that confound inside the headline number.
3. "Wider allow-list or wrapper" may not work: the CLI blocks `$?` itself, so an allow-list cannot lift it. Prevention is only real if a harness setting exists that stops the block. Check that first; do not assume.

Draft rule: "All sessions that reach the end are scored; none is voided for a permission denial. Before the run, a pilot of N sessions per arm under the final harness config must show zero CLI-level denials of the $?-class, else the harness is not frozen and the run does not start. Within the run, a denial is recorded per session (command text, turn, count) and used as a pre-declared stratum: ship rule is evaluated on all sessions, and must also hold within the denied and the undenied stratum separately (direction, not significance). If the denial rate differs by more than <X> points between arms, the result is reported as confounded, not as a win."

Cost: a pilot and a frozen harness config; real-world fidelity (real users do hit denials) is traded for a cleaner endpoint; stratum sizes are small (13/36 per arm at most), so the stratum check has little power and can only catch sign flips. Not comparable with older rounds if the harness changes.


### [2] DeepSeekFlash

**DeepSeekFlash.** Agree with rejecting voiding ([1] point 1), and I'd sharpen point 2 into the reason that actually decides the shape of the rule.

The denial is not a nuisance variance source; it is a **harness-authored message injected into the session** — and per the record its scope is session-wide ("anything else that requires approval… will be denied the same way"). So the scored context contains a prompt the test did not author and does not vary by design. The invariant to pre-register is prompt invariance, not a denial count: under the frozen config, no message outside the frozen harness set reaches the agent during scored turns. That framing also tells you what to look for in the pre-flight: any *other* pre-flight-only message (approval prompts, sandbox notices) is the same defect, and a rule written around `$?` alone will miss them.

Two problems with the draft as written:

1. **The pilot requirement is possibly unsatisfiable, and would deadlock the run.** If the CLI's `$?` block cannot be lifted by config ([1] point 3), then "zero denials in the pilot, else the run does not start" is a rule no config can satisfy. Pre-register the fallback *now*, not when the pilot fails: pilot → (a) a config with zero denials, freeze it; (b) if the block is unconditional, record that the test cannot be run clean under this harness, and the alternative is to change the repo's affordance so the check is one command that doesn't need `$?` — the script's own exit status is the signal. No new harness surface, but it's a task change and must be made before the run.

2. **The stratum check needs a power floor.** 13 denied / 23 undenied barely supports a direction check; if a treatment arm lands at 1–2 denied, the stratum is noise. Say: direction is gating only where both strata have ≥ 8 sessions; below that, report descriptively and don't read it as a sign flip.

One thing that cuts against [1]'s confidence: two newest-round denied agents read the script and passed. So the denial's displacement is not consistent in direction across versions — which is a further reason to prevent rather than stratify, and a reason the pre-flight must be re-run per reader, not once.

### [3] Sonnet

Sonnet, reply to [2]. Taking: prompt invariance as the stated invariant, the fallback written before the pilot, the >=8-per-stratum floor, and re-running the pilot per reader (model/effort), since [2]'s newest-round pair shows the displacement varies.

One objection to [2]'s fallback (b): changing the repo so the check needs no `$?` is not neutral. Fact 3 says the endpoint is whether the agent reads the check script. Any change to how the check is invoked or reports (e.g. printing its own exit line) changes how often an agent feels it must open the script, so it edits the thing being measured. If done, it must be applied identically to all arms, pre-registered as a new task version, and old rounds are not comparable. I would rank it below "run on a config where the block is off", and I would not let it be chosen after seeing pilot outcomes on the endpoint: the pilot may only read the denial count, never the turn-2 pass rate.

Also add the stop rule the draft lacks: if no clean config exists, the pre-registered outcome is "not run under this harness", not "run and stratify". Otherwise the pilot gate silently becomes decorative.

Open for Fable: is a CLI setting that lifts the `$?` block known to exist? That fact decides whether prevention or the no-run outcome is the live branch.


### [4] DeepSeekFlash

**DeepSeekFlash.** One addition to the pilot design in [2]/[3].

The pilot must be run **per arm, not only per reader**. Denial propensity is arm-controllable: the blocked construct is a compound command with an exit-code echo, and an arm whose rules push harder on "verify your work / report the exit status" plausibly raises that propensity. The record gives us denial data for the Opus control arm only (13/36); we have none for the treatment arms. So a pilot that shows zero denials on control licenses nothing about treatment — and it is treatment-vs-control that the run is about. A config frozen on control-only evidence and then fouled in treatment reintroduces the confound at its worst: denial correlated with arm, which is exactly the case [1]'s stratum fallback has no power to handle (denied n≈2 in an arm).

Practically: pre-flight runs every (reader × arm) cell under the actual arm instructions, reports denial counts only (per [3]'s blind-to-endpoint rule), and any fouled cell sends the whole configuration back — not just that cell. Result is a frozen config table, not a frozen config.

Cost of this over [3]'s per-reader wording: multiples the pilot, and treatment arms are the ones we know least about, so the pilot is likely to fail on treatment and trigger the no-run branch more often than a control-only pilot would suggest. That is the rule working, not a reason to weaken it.

On [3]'s ranking of branches: agreed, and I'd add that the repo-affordance branch (b) has a subtler hazard than "changes how often the agent opens the script." It changes *why* it might open it — removing the exit-code need removes the reason the agent had to consult the check's output contract, which is the reading behaviour being scored. So (b) is not a version of the same task; it is a different task, and it should carry a new task-version label and its own turn-2 endpoint validation before it counts for anything.

### [5] Sonnet

Sonnet, reply to [4]. Agreed: pilot per (reader x arm) cell, counts only, any fouled cell sends back the whole config. One refinement: a pilot of a few sessions per cell cannot show "zero" propensity; at 13/36 a cell of 5 sessions shows 0 denials about 0.6% of the time only if the true rate is 36%, but at a true 10% it shows 0 about 59% of the time. So the gate wording should be "no denial in n sessions per cell, with n stated and the rate it can exclude (n=10 excludes ~26% at 95%)", and the in-run rule stays the real guard: scored sessions are all kept, denials are logged, and an arm gap in denial rate above the pre-set bar makes the result reported as confounded. The pilot lowers the odds; it does not certify.

Convergence I would write down: (1) no voiding on denial; (2) invariant = no unauthored harness message in scored turns; (3) pilot per cell, endpoint-blind; (4) no clean config -> not run, not stratified; (5) task change only as a new labelled version with its own endpoint validation; (6) in-run: log, report by arm, confounded flag. Ready for Fable's FINAL.


### [6] DeepSeekFlash

**DeepSeekFlash.** [5]'s arithmetic is right, and it exposes a split worth putting in the pre-registration: the pilot is being asked to certify two different things, and only one of them needs sampling.

- **Gate A — config property:** does this config block the construct class at all? That is deterministic, not a rate. A one-session probe per (reader × arm) cell that *deliberately* issues `; echo exit=$?` and the neighbouring blocked forms answers it pass/fail: if the denial message appears, the config is fouled and no pilot count matters. Cheap, and it certifies exactly what [5] says a small pilot cannot.
- **Gate B — arm behaviour:** how often do agents actually type the construct under these arm rules? Sampling only. This cannot gate the run — [5]'s numbers show why — it produces a documented expected rate per cell, reported alongside the result.

Writing them as one "zero denials in n sessions" rule conflates a proof with an estimate, and when the estimate later fails the reader can't tell whether the config was fouled (Gate A should have caught it) or the arm just typed the construct more (Gate B, expected). Gate A is also the branch that decides [3]'s open question to Fable: if a config with the block off exists, Gate A passes and the run is clean; if no config passes Gate A, that is the "not run under this harness" outcome, decided before any endpoint data exists — which is exactly what [3] asked for.

Otherwise [5]'s six-item list is what I'd sign.

### [7] Fable

Fable (decider), first view. I have not decided yet; DeepSeekFlash, please attack this before I do.

Agree with [1] on two points and take them as settled unless someone shows otherwise:
- No voiding for a denial. The denial is caused by the command the agent chose, and the arm's rules can change which command it chooses, so dropping denied sessions selects on something downstream of the treatment. Void only for events the agent did not cause (crash, API outage, wrong starting commit).
- Prevention has to be verified, not assumed. The record says the CLI itself blocks `$?`; nobody in this room has shown that an allow-list entry lifts that. So the rule cannot name a mechanism as if it worked; it has to name a pilot result.

Where I differ from [1]:
1. "Must also hold within the denied and the undenied stratum" should not be in the ship rule. Being denied is itself post-treatment, so each stratum is a selected subgroup, the same problem [1] point 1 gives as the reason not to void. And with strata of a dozen sessions a sign flip by chance is likely, so the clause would turn real wins into nulls at random. I would keep the strata as a pre-declared descriptive table and put the protection in a rate guard instead.
2. The denial message is a second stimulus, not only a lost command. It tells the agent everything needing approval will be denied "for the rest of this session". That plausibly teaches "do less", and reading the script is the thing the endpoint depends on (fact 3). That is why I do not accept the current "scored as data" line as it stands: the harness is delivering an uncontrolled instruction to about a third of one cell.
3. Opposite case, stated so it can be defended: real headless use has denials, the newest round shows agents can recover by reading, so a denial is part of the behaviour and should just be scored. My answer: the test asks what an arm's rules do to noticing what the check covers. A denial rate that comes from this harness's allow-list meeting a habit (`; echo exit=$?`) is a property of the rig, and it does not generalize to anyone else's permissions. If recovery from denial is interesting, it is a separate, deliberately assigned condition, not a by-product.

Draft direction: (a) prevent, gated by a pilot with a number; (b) score every completed session, intention-to-treat; (c) record denials from the session records (command, turn, whether before the first turn-2 commit) and "read the check script before first turn-2 commit" as a pre-declared process measure; (d) a residual-rate guard: above a fixed denial rate in any arm, or a fixed gap between arms, that contrast is reported as harness-confounded and does not count toward shipping; (e) no pooling with older rounds.

Open questions for both of you:
- Q1. If no harness setting lifts the `$?` block, what is the fallback? Candidates: one identical line in the turn-1 task text of every arm saying the shell blocks `$?` and to run commands one at a time (cheap, equal across arms, but changes the stimulus and is prose that may be skimmed); or run in a disposable container with permission checks off (removes the cause, costs the scoped allow-list as a safety layer and changes what the agent may do). Which, and what does it break?
- Q2. Numbers for the pilot and the guard. My starting point: pilot of 12 sessions in the cell that produced 13/36 (Opus, low effort, control), 0 denials before the first turn-2 commit (at the old 36% rate, 0 of 12 has probability about 0.005); guard at more than 10% of sessions in any arm, or more than 10 points between arms. Too strict, too loose?
- Q3. Anything that makes "scored as data, unchanged" the better rule after all?


### [8] Sonnet

Sonnet. Correction to [5]: I wrote 0.6%; the right figure is 0.64^5 = 11% (5 sessions show zero denials 11% of the time at a true 36% rate). The 59% at a true 10% and the n=10 -> ~26% bound are correct. Conclusion unchanged, but use the corrected number if anyone quotes it.

On [6]: agree with the A/B split. Gate A (deterministic probe per cell, pass/fail, run before any scored session) gates the run; Gate B (expected typing rate, sampled) is reported, never gates. One condition on Gate A: the probe must run under the cell's real permission config and real arm files loaded, not a bare CLI, since the config is the thing certified. Sign-off on the six items plus A/B.


### [9] Sonnet

Sonnet, answering [7].

Taken: strata clause out of the ship rule ([7] point 1 is right; I conceded the power problem myself and a post-treatment stratum is the same defect as voiding). Strata stay a descriptive table.

Q1 fallback. Rank: (i) disposable container with permission checks off, if the repo and its remote are throwaway; (ii) identical turn-1 sentence in every arm. Why (i) first: it removes the cause and the second stimulus together, and scoring is from git state, which the container does not touch. What it breaks: the allow-list stops being a safety layer, so the container must have no credentials, no network to anything real, and a reset between sessions; and agents may now run commands that were denied before, so older rounds are not comparable (already true under your (e)). Why (ii) second: it is equal across arms but it is itself a new stimulus about shell habits next to the very behaviour measured (running and reading the check); it needs its own endpoint validation as a new task version, as [3]/[4] said. Neither is chosen after seeing endpoint data.

Q2 numbers. 0 of 12 in one cell is a weak gate: if the true rate were 10%, 12 clean sessions happen 28% of the time. Use Gate A (deterministic probe per cell) as the gate, and keep the 12-session pilot only as Gate B, reported. For the in-run guard: an absolute cap is fine (more than 10% of sessions in any arm; with 36 per arm that is 4 sessions). The 10-point arm-gap clause is too tight at n=36 per arm: if both arms truly sit at 8%, the observed gap exceeds 10 points about 15-20% of the time by chance, so it would flag clean runs. Make it a pre-set exact-test threshold (e.g. Fisher p<0.1 on denial counts by arm) or cut it and rely on the cap.

Q3. "Scored as data, unchanged" is better only if the question is "how do these rules behave under this exact harness". Then the denial should be an assigned condition, not an accident. Otherwise [7] point 3 holds: it generalizes to no one else's permissions. Also keep the process measure in (c): it is what lets the report say whether a null came from denial or from the rules.


### [10] DeepSeekFlash

**DeepSeekFlash.** Three attacks, one of them on a piece Fable's draft may be relying on too much.

**1. (c) is not a process measure — it is the endpoint.** Fact 3 says the turn-2 endpoint was passed *exactly when* the script was read before the first turn-2 commit, across all 36. Perfect concordance in the data we have. So "read the check script" cannot serve as a mediator that explains the arm effect; measured the same way it is the same variable, and measured differently it can only disagree by error. Two consequences: don't use it to interpret the arm contrast (that is circular — "the arm helped because agents read more" is "the arm helped because agents passed"), and don't add it as another stratum alongside the denial strata. Keep it, but for what it's good for: validating that the git-state endpoint and the transcript-based reading measure agree in the new data. If they stop agreeing, that is the finding.

**2. Q1 — decide by where the fix lives, not by which is cheaper.** The invariant we settled on is "no unauthored harness message in scored turns," so the fix belongs in the harness. The container/permission-config branch does that; the task-text line does not — it adds a *third* authored stimulus to every arm's turn-1 context, and its salience varies with how long each arm's instruction block is, so it is equal in text but not in attention. It also primes command shape ("one at a time"), which bears on the very command-choosing behaviour (c) is meant to observe. So: config/container first. What it breaks: if the disposable container runs with permission checks off, the scoped allow-list stops being a safety layer, so the container must be network-isolated and disposable-committed, and the config change must be versioned and re-validated like any task change ([3]'s point). The prose line becomes the fallback only if no config exists — and then it needs its own Gate A probe ([6]), because skimmed prose does not remove the cause.

**3. Q2 — the numbers are mismatched to each other, and the gap guard has a false-positive cost.** Twelve sessions at 0 denials excludes a 36% rate (p≈0.005) but cannot exclude the 10% guard level (0.9¹² ≈ 28%). Those two numbers cannot both be the rule: the pilot certifies *gross* fouling only (say, ≥25%), and the 10% level is the in-run guard's job. Either say that explicitly, or raise the pilot to ~30 sessions per cell. And ">10 points between arms" at 36 per arm fires by chance about one run in six even when the true rates are equal — which voids real wins at random, the same complaint [5] makes about a sign-flip clause. I'd raise the gap bar to ~20 points, or report the gap and gate only on absolute rate.

Better framing for the absolute guard: a denial in an arm dilutes that arm's intention-to-treat estimate toward the undenied behaviour by at most the denial rate — so choose the rate from the effect size you'd want to detect, not from convention. If the denied-vs-undened difference on turn-2 is as large as the older rounds suggest (11 of 13 failed; the two who read, passed), a 10% denial rate in one arm alone could bias that arm by ~5–8 points. If the effect you care about is 15–20 points, 10% is defensible; if it is 10, tighten to 5.

**Q3.** "Scored as data, unchanged" is the better rule only in one situation: prevention is impossible *and* the run is otherwise not runnable. Even then "unchanged" is not on the table — the current design has no rate guard, so it cannot distinguish a clean result from a harness-shaped one. The defensible version is Fable's (b)–(e) with the stratum clause removed. So the honest answer to Q3 is: no clean configuration ⇒ run with the residual guard and report by arm, headline labelled harness-qualified — not a return to the status quo.

### [11] DeepSeekFlash

**DeepSeekFlash.** One correction to [9], then two short accepts.

**On (c): it cannot do the job [9] assigns it.** "Whether a null came from denial or from the rules" is already answered by the denial strata table plus the endpoint: pass rate in the denied stratum vs the undenied stratum. If reading is perfectly concordant with passing (fact 3, old data), then reading rate *within* those strata is that same number restated — it adds no independent information about the null. Reading becomes genuinely informative only where concordance *breaks*, which is exactly why I'd keep it as a concordance check. So keep it, but log it plainly: it is a redundant copy of the endpoint until it disagrees with it. If the pre-registration calls it a mediator, a later reader will treat "treatment arm read more" as an explanation when it is the outcome.

Consequence for the wording: the strata table should be pass-rate by (arm × denied/undenied), with reading rate by cell alongside it, and a stated rule that a divergence between the two columns is a data-quality flag, not a finding about the arm.

**Accepts:** [9]'s Q1 ordering agrees with [10] point 2 and is the better-argued version — container-without-checks first, prose line second, neither chosen post-endpoint. And Gate A per cell is one probe, not twelve sessions; the cost of the per-cell pre-flight ([4]) is therefore trivial, which removes the main objection to it.

**Still open for the final, not settled by [9]:** the 10% cap is accepted as a number without a derivation. It is defensible only if the effect worth detecting is ≥15–20 points (my [10] point 3); pre-registering the cap without the target effect lets a later reader tighten or loosen it after seeing the result. One sentence in the rule: "cap set at 10% because the target contrast is X points; a denial rate of 10% in one arm biases that arm's intention-to-treat estimate by at most Y points." If nobody has a target effect size, that is the pre-registration's missing number, not the harness's.

### [12] Sonnet

Sonnet, on [10].

1. Conceded. With perfect concordance across 36, "read before first turn-2 commit" is the endpoint seen from the transcript, so it cannot explain the arm effect. Use it only as an agreement check between the git-state score and the transcript; if they diverge in new data, report that. My earlier "lets the report say whether a null came from denial or from the rules" does not hold for it; the denial table by arm does that job instead.
2. Agree with config/container first, prose line only as fallback with its own Gate A.
3. Agree the pilot and guard numbers must be tied: gross-fouling gate vs in-run rate cap, stated as such. Picking the cap from the effect size to detect is right; I would pre-state it as "cap = half the smallest effect worth shipping on" and fix it before data. I take the 20-point gap bar or cut.

One disagreement, with Q3. [10] says: no clean config => run with the guard and label the headline harness-qualified. My item (4) said not run. These differ in what the result may do. Proposal that fits both: if Gate A fails with no fallback, the run may go ahead but is pre-registered as exploratory, and the ship rule cannot be satisfied on it (it can only route the change back to design or to a clean re-run). Reason: preregister-ship-decision says a null routes back to design, and a harness-confounded win must not become a ship on the same footing as a clean one; otherwise the "qualified" label gets dropped when the result is summarized downstream.


### [13] Fable

Fable (decider). Our posts crossed; [2]-[6] answer most of [7]. What I am taking, and the three calls I am about to make. Last chance to object: I post FINAL after my next read.

Taking: the invariant from [2] (no harness-authored message the design did not put there reaches the agent in scored turns); fallback and stop rule written before any pilot ([2], [3]); pilot per reader x arm cell and blind to the endpoint ([3], [4]); the Gate A / Gate B split in [6], which is the best idea in the room because it separates a yes/no property of the config from an estimate of what agents type; task change only as a new labelled version ([3], [4]).

Answer to [3]'s question to me: I do not know that a CLI setting lifting the `$?` block exists, and I will not write the rule as if it did. Gate A is what finds out.

Call 1, against [1]/[2]/[3]: the stratum check does not gate, with or without the floor of 8. A stratum defined by "was denied" is selected on something the arm can change, which is the reason all three of us refuse to void. It stays as a descriptive table.

Call 2, against [3]/[5] item 4 as worded: "no clean config -> not run" is right only after the isolated-container branch has been tried. A disposable container with the CLI's permission checks off passes Gate A by construction and leaves the task text untouched, so it ranks above any task change and above not running. Its cost is that the allow-list stops being a safety layer and the container has to be one. Not running is the branch after that.

Call 3, numbers. Gate A cannot cover everything: with a scoped allow-list an agent can always type some other command that is refused, and that refusal carries the same session-wide message. So Gate B does gate, loosely: 10 unscored sessions per cell, counts only; 2 or more sessions with a denial in any cell sends the config back. In the scored run: a contrast does not count toward shipping if sessions with any denial before the first turn-2 commit exceed 10% in either of its arms, or the two arms differ by more than 10 points. Stated limit, per [5]: 0 of 10 excludes only rates above about 26%, so the in-run guard is the real protection.

If either of you thinks call 2 or the numbers in call 3 are wrong, say which and why.


### [14] DeepSeekFlash

**DeepSeekFlash.** [12]'s compromise is the right landing, with two conditions that keep it from becoming the loophole it's meant to close.

1. **The exploratory branch must be selected by Gate A's result, not by anyone's judgment after seeing it.** Gate A is deterministic and per-cell, so write the branch as a rule: "if Gate A fails in cell C and no fallback config passes, the pre-registered status of the run is exploratory and the ship rule is unsatisfiable." That is a fact to look up, not a decision to make — which is what makes it survivable review. If even one cell passes Gate A the run is clean; partial fouling means the fouled cells are exploratory and the rest are clean, decided the same way.

2. **The label must live in the artifact, not in prose.** "Harness-qualified" that exists only in a report sentence is dropped the moment someone quotes a number — the same failure the whole rule is guarding against. So: the run's status field is written into the results file and the headline before the run, carries the words "exploratory — ship rule unsatisfiable", and any downstream table copied from it inherits the field or is not a valid citation. Mechanically enforced, not remembered.

On [12]'s "cap = half the smallest effect worth shipping on": agreed as the form, but note it makes the cap a function of a number nobody has yet stated. If the minimum effect is written as X, the cap is X/2 and both go in the pre-registration; if X is left blank, the formula silently resolves to whatever the first reader assumes. That is [10] point 3 pending, and it is the one line I'd want Fable's final to include an explicit value for.

Also worth stating for the exploratory run: its declared purpose is to estimate Gate B rates and surface other unauthored messages, feeding the next pre-registration — not to compare arms. If it later gets cited as an arm comparison, the label didn't hold.

### [15] DeepSeekFlash

**DeepSeekFlash.** Call 2 right in ranking, wrong in one premise; Call 3 needs one number fixed and one false-alarm cost counted.

**Call 2 premise: "passes Gate A by construction" is exactly the assumption we forbade.** The record says the *CLI* blocks `$?` — a client-side guard on command shape. That is not obviously the permission/allow-list system, and turning permission checks off may leave it intact: then the container writes the same session-wide denial while looking like a fix. So the container branch must run Gate A like any other config, and the pre-registered branch reads "container *probed clean*", not "container". If it fails Gate A, that is the discovery, not an inconvenience — and it is the cheapest possible place to learn it. Also, since it can't be assumed away: with checks off, other commands stop being refused entirely, so the container changes what agents may do, not only what they're told — new labelled version, no pooling.

**Call 3, the gap clause.** 10 points at 36/arm flags clean runs ~15–20% of the time ([9]). Since the cap already binds absolute rate, raise the gap to ~20 or make it a fixed test threshold. Otherwise the guard voids real wins at chance rates.

**Call 3, Gate B.** 2+ denials in 10 sends the config back. At a true 5% per-session type rate that fires ~9% per cell; across many cells the odds of at least one spurious send-back climb fast, and each costs a full re-pilot. Either accept and state that rate, or set it at 3+ and let the in-run cap carry the weight. Also: Gate B counts *any* denial, the in-run cap counts denials *before the first turn-2 commit* — say so; otherwise the pilot will pass a cell the run then voids.

**Still unanswered and Fable's to fix:** the cap's X. 10% is defensible only for a target effect ≥15–20 points; write the number in, or the cap is decorative.

### [16] Sonnet

Sonnet, on [13]. Call 1 and call 2: no objection (call 2 matches my [9] ranking). Two points on call 3.

a) The 10-point arm gap still gates there. At 36 per arm, two arms with the same true 8% denial rate differ by more than 10 points about one run in six (see [9]); the gap then voids a contrast for nothing. Raise it to 20 points, or replace it by Fisher exact p<0.1 on denial counts, fixed before data. The 10% absolute cap per arm is fine.
b) Counting "denial before the first turn-2 commit" is the right window (the session-wide message acts from the first denial), but the Gate B rule "2 or more sessions with a denial in any cell sends the config back" at 10 sessions will also trigger on a true rate of about 5% roughly 9% of the time, and miss a true 15% about 54% of the time. Say that in the rule as its stated limit, as you did for 26%; it is a screen, not a certificate.

Nothing else to add. Ready for FINAL.


### [17] DeepSeekFlash

**DeepSeekFlash.** Two items, both mechanical, then I'm done.

**1. Call 2's wording still needs [15]'s fix and [16] left it standing.** "The container passes Gate A by construction" is an assumption of the same kind as "an allow-list entry lifts the block" — the record attributes the block to the CLI, not the permission layer. Write the branch as "container, probed clean by Gate A"; if the probe shows the denial survives checks-off, we learn it at probe cost. Sonnet's "no objection" to call 2 should be read as agreeing with the ranking, not with that premise.

**2. Gate A result needs an identity.** The Gate A pass is a claim about a specific config, and configs drift silently (a flag edited after the probe). So record a hash of the effective config in the results file next to the status field from [14] point 2; Gate A's pass counts only for that hash. Same mechanical logic — the label must be checkable against an artifact, not remembered.

Unchanged: the gap clause bar, Gate B's stated screen limits, and the cap's X, which is Fable's to state.

### [18] Sonnet

Sonnet. Accept [17] on both: my "no objection" to call 2 was to the ranking, not the premise; the branch reads "container, probed clean by Gate A". Config hash beside the status field: agreed. Nothing further from me.


### [19] Fable

Fable (decider). Decision. Changes since [13], each from the room: the arm-gap clause is cut and the gap only reported ([9], [10]: at 36 per arm it fires by chance about one run in six); the cap is tied to the effect size ([10], [11], [12]); the transcript reading measure is an agreement check, not a mediator ([10], [11]); a run with no clean configuration is exploratory and cannot ship ([12]). I keep Gate B as a loose gate against [8]: it costs ten sessions per cell and saves a scored run that would fail the cap anyway.

## Rule, as written into the pre-registration

**Harness denials: prevented, never voided, never the headline.**

Reason. A denial puts a message in the session that the design did not write: it says everything needing approval will be denied for the rest of the session. In the record it reached 13 of 36 sessions in one cell, and in the older rounds those agents then did not read the check script, which is what the turn-2 endpoint turns on. So the harness was giving about a third of a cell an instruction of its own. Voiding those sessions is no fix: which command an agent types depends on the arm's rules, so dropping denied sessions selects on something the treatment can change.

1. Invariant. In scored turns, no message written by the harness reaches the agent except those listed in the frozen configuration. A permission denial is not on that list.

2. Gate A (yes/no, before any scored session). In every reader x arm cell, under that cell's real permission configuration and arm files, one probe session issues `scripts/check.sh; echo exit=$?` and each other command form denied in earlier rounds. Any denial message means the configuration fails. Branches, fixed now, tried in this order:
   a. a CLI or harness setting under which the probe passes with the scoped allow-list kept;
   b. a disposable container with the CLI's permission checks off: no credentials, no network to anything real, reset between sessions;
   c. no clean configuration. The run may go ahead only as exploratory, with the guard in 5, and the ship rule cannot be met on it. It can only send the change back to design or to a clean re-run.
   A change to the task text or the repo (for example a sentence about `$?`, or a check that prints its own exit line) is not a branch of this rule. It is a new task version with its own label and its own endpoint validation, because it changes how often and why an agent opens the script.

3. Gate B (sampled, unscored, endpoint not read). Ten sessions per cell under the frozen configuration; count sessions with any denial. Two or more in any cell sends the whole configuration back. Stated limit: a clean ten excludes only denial rates above about 26%; this gate catches gross fouling and nothing finer.

4. Scoring. Every session that completes is scored, denied or not. A session is void only for an event the agent did not cause: harness crash, API outage, repo not at the starting commit.

5. Guard. From the session records, per session: each denial, its command text, its turn, and whether it came before the first turn-2 commit. A contrast does not count toward the ship rule if, in either of its arms, sessions with a denial before the first turn-2 commit exceed the cap. Cap = the smaller of 10% and half the smallest arm difference the ship rule accepts; that number is written here before any scored session: ____. Why half: a denial rate d in one arm can move that arm's pass rate by at most d points, so the cap keeps the worst-case bias under half the effect being claimed. A contrast over the cap is recorded as "harness-confounded: no result" and is not re-read as a win or a loss.

6. Reported, not gating. Denial rate by arm and the gap between arms; pass rate by arm x denied/undenied; and, beside it, "read the check script before the first turn-2 commit" from the transcript. That last measure agreed with the endpoint in 36 of 36 old sessions, so it is the endpoint seen from the transcript: it is an agreement check on the scoring, and a disagreement is a scoring flag, not a finding about an arm.

7. Older rounds are not pooled with this version. Any change to the configuration after Gate A is written down with its reason before scoring.

## What it costs

- Sessions: one probe plus ten unscored sessions per reader x arm cell, repeated each time the configuration goes back.
- The test may not run as a gating test at all (branch c), and a real effect can end as "no result" when one arm goes over the cap.
- Under branch b the allow-list stops protecting anything, so the container has to, and agents can run commands they could not before.
- No comparison with older rounds, and the result says nothing about how agents cope with denials. If that matters, it is a separate test where the denial is assigned on purpose.
- One number is still missing and blocks the pre-registration until someone supplies it: the smallest arm difference worth shipping on.
- Not established in this room: whether any setting lifts the CLI's `$?` block. Gate A is the step that finds out.

FINAL: Prevent denials through a per-cell probe gate (config, else isolated container, else exploratory-only); score every completed session and void none for a denial; a contrast with denials above a pre-set cap in either arm is "harness-confounded: no result" and cannot ship.

