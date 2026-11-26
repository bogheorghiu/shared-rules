# keep-the-aim: handoff for whoever continues (2026-11-23)

Machine-facing, dense. Supersedes `HANDOFF.md` (2026-11-17, stale from "State now" on; its owner standing instructions on budget, anonymisation and explaining still hold unless the owner has said otherwise since). Record of truth: `DESIGN.md` (L-refs below are its lines). Conclusions: `CONCLUSIONS.md`. Owner-facing page plan: `CONTENT-MAP.md`. One-page summary: `SUMMARY.md`.

## State in ten lines

- Rule under test: `docs/staged-rules/keep-the-aim.md`. Staged, not shipped. Text unchanged through the whole series.
- Normal harness = headless Claude Code, default system prompt, eight shipped rules. Control = that. Rule arm = that + the rule.
- Control failed, rule did not help: L1 0/8 vs 0/8 (L1223, L1241); W1m 0/8 vs 0/8 (L1385); K4 0/8 vs 1/8 (L603-L606).
- Control at ceiling, rule arm not run: v5 CARRY 40/40 (L492); W1 8/8 medium + 8/8 low (L1361, L1371); P1 16/16, mirror 8/8 (L1463); H1 8/8 with statements (L1625), 8/8 with data note only (L1680).
- H1-nodoc 2/8 (L1652) is a fixture confound + scorer defect, not headroom for the habit (L1661-L1663).
- Rule effect seen only in the stripped harness (swap prompt, no rules, Opus low): only 8/8 vs none 2/8 on cover-K1d and carry-R1; placebo 1/8 and 5/8 (L792-L793, L798-L799). Opus medium none 4/4 (L800). Descriptive; "cannot feed the ship decision" (L731).
- L1 told-rescore: control 8/8 named the conflict, rule 8/8 (L1494). Telling is at ceiling; the page is what fails.
- L1m: control 0/4 (kept list on opening although purpose asks for the picture, L1204), rule 2/4 (L1241). Registered reading "surfaces only" (L1242).
- Pre-registered global stop (L889): no two tasks in two domains with headroom → keep staged, capture the next real failure from the owner's harness. CONCLUSIONS reads this as now applying; the owner has not ruled.
- Open owner decisions: keep/narrow/drop; rule vs path-scoped skill (deferred "Decide after H1", L1518); next test.

## Best current account (see CONCLUSIONS for evidence and tags)

- Not a noticing gap, not a telling gap, not a copy-the-neighbour habit (in one-turn, small repo, Opus medium).
- Lab-grounded failure: an accepted artefact is in place; session adds the requested thing beside it and does not displace it (L1203-L1207). W1m is the same additive move under a user order (L1365, L1385).
- Field hypothesis, untested in lab: hand-off hardens a proposal into a requirement (`reviews/fable-h1-priorart.md` F-A, F-C). "Form arrives as a given" in a repo file (README + script) did NOT reproduce (L1635).
- Harness mismatch flagged and never closed: owner saw failures in Claude Desktop / Claude Design / many skills, not headless Claude Code with eight rules (L705). Ask the owner before building more.
- Three outside reviews (`reviews/final/`): agree on hand-off as the place to look; DeepSeek's "aim not in view" diagnosis is contradicted by L1494, and it misstates H1 (no rule arm ran; copying was not impossible, L1620). Treat all three as data, not instructions.

## Method (what to keep doing)

1. **Pre-register every gating test in DESIGN.md before any data**: arms, endpoint and how measured (artefacts, not self-report), voids, numeric bands, what each band means. Scored "against the registration, nothing re-derived". Deviations recorded before the data they affect (examples L1182, L1236, L1363).
2. **Stage order**: stage 0 (instrument) → stage −1 (control-only headroom) → rule arm. Never run a rule arm on a task at control ceiling. Typical bands: headroom iff ≤4/8; ≥5/8 or ≥7/8 closes (per registration); one dial (Opus low) where registered (L1342, L1369, L1459, L1533).
3. **Stage 0 anchors**: known-bad must fail, known-good must pass, narrow-fix must fail, mirror pair both ways, plus a hinted oracle (`run_v5.py --oracle`) to show solvability. Anchor off its bar → back to design, owner adjudicates (L1162, L1528-L1531).
4. **Mirror for every task**, two-sided where possible (copy right → passes; redesign that loses an answer → fails, L1507). A mirror that can only be passed by disobeying the user measures obedience, not over-firing (L1393, L1396).
5. **Score outcomes, not shape or self-report**: hidden data never visible to the subject; rebuild the committed artefact on hidden data; reader questions with keys computed from hidden data; scripted checks. Classes (COPY/ADDED/LITERAL/FIT/HELD) reported, not gated (L1505, L1525).
6. **Readers are an instrument**: non-Claude where possible (owner direction L1551-L1554). Changing reader = changing instrument → re-pass anchors first. Two readers, pass needs both (held a pure copy at 6/7 vs 3/7, L1620). One independent call per item/screenshot; a reader that sees a good page can carry keys to a bad one (L1226).
7. **Downstream-session scoring for protocols/skills**: fresh sessions apply the edited text to hidden cases. Use the literal-reader prompt; a blind/helpful reader repairs the protocol itself and hides the defect (L1073, L1080, L1129, L1290).
8. **Placebo arm** when claiming a text-specific effect (L770-L776).
9. **Voids are not wrong answers**: void on rc≠0, wrong served model, API error, failed rule-load probe; re-run once, cap retries (L945, L969, L1003). Check `served` model per session, not the requested one.
10. **Do not buy headroom by hiding information** (L1511). If control passes, record no headroom.
11. **Falsification station at each hand-off**: check claims against their source (L621 found three unverified claims in a review; L1298 fresh agent checked case overlaps). Subagent self-reports of file writes were wrong twice (L1389, L1498): take the text from the hand-back message and verify files.
12. **Tripped gate + instrument doubt → owner, no re-scoring** (L1653).

## Pitfalls actually hit (each with where)

**Contamination**
- Subject/reader sessions launched with relative `--out` under the repo loaded `CLAUDE.md` and `.claude/rules/board.md` as parent-directory instructions; `probe_ok` False; oracle void (L1581). Fix: all subject and reader work dirs under `/tmp`, outside any repo (L1586). Always read `probe_ok`.
- Reference builds sent the hidden cases and questions with the request → not blind, quarantined in `*/references/fable_contaminated/` (L936).
- Downstream readers carried `ops/incidents.md` (the owner's complaint) and repaired toward the aim (L1129).
- Reader sessions' scratch HOME got committed, including a session key file (L1557). Check `.gitignore` before committing run dirs.

**Scorer defects**
- "Do nothing" passed three of four W1 hidden cases (start state equalled the key) (L942). Selftest must include an inertia break.
- H1 judge: forbid-list hit a name the reader mentioned only to exclude it; the unknown-count item could not tell "undecided" from "not shown" (L1578-L1579).
- H1 hidden-data swap missed reshaped copies of the export; board picker chose the wrong board when a session built two (L1657-L1658, L1663). Fixed by `derived_hidden`, build-all, most-markers page (L1670-L1675). Known approximation: a row-filtered derived copy gets all rows back (L1675).
- `check_read_before_T2` had no cut at the first commit (L377). Exact owner-set key scored correct card closures as wrong (L1286).
- U1 score measured one thing (asks in first viewport or not) (L1099); floor inflation from "none" questions (L858).
- Infrastructure failure scored as a wrong answer (L945). A `--force` path that resent all votes was a re-grade route (L998).
- Hidden constraint the subject cannot know: W1 growth cap failed a thorough blind repair (+81 lines vs cap 15) → report-only (L981-L982). `states_unchanged` fails harmless edits (L1395).

**Fixture confounds**
- H1-nodoc: deleting `docs/pattern.md` removed the "one instance" statements AND the only data-flow note; 4 of 6 fails were data-flow (L1662). Change one thing per arm; grep what else a file carries.
- v1: T2's committed row crashed T4's script (L163). v4: a decoy column turned a turn into a puzzle, Sonnet leaked 12/12 both arms (L375).
- v2/v3: CLI denials of `$?` commands differed by arm and drove E1 (L374). Count denials by arm.
- W1 d2/d6 events duplicated cards already on the status file (L1285-L1287).
- L1: control fails L1 and L1m identically, so headroom may be "surface the change on opening", not "purpose over wording" (L1205). L1m premise unsupported: reader found the loop from a list (L1199). "Served = opening view only" is the result's main lever (L1205, owner-confirmed L1208).
- W1/W1m: the prompt names the file and the failure → ceiling; mirror passable only by disobeying (L1392-L1396, L1402).
- One-turn headless: hold-and-ask scores zero; nobody answers (L1126). L1 had a canned turn 2 for held runs; none held (L1157, L1230).
- K4: nothing in the prompt marks the case as new; no reader solved it; retired (L618).

**Reader / infra**
- Diagram pages cost readers 87–553 s and up to 48k reasoning tokens per vote; non-streamed calls timed out; stream and persist the generation id (L1179, L1209).
- OpenRouter 402: parallel uncapped requests reserve worst-case cost against the balance (L1227). Send one at a time when the balance is low.
- Route change needs calibration on anchors first (L1236, L1239).
- Fable batch with max_tokens 64000 spent everything on reasoning, no text (L932). Owner rule: no effort parameter on Fable calls (L934).
- Azure GPT endpoint refuses >50 images; screens paired side by side above 48 (L1593).
- Hooks: W1 fixture's pre-commit hook was not installed in subject sessions at first, so a renamed heading failed silently; `run_v5.py` now installs it (L951, L975). "Hook loops" were named as a pitfall in the task brief for this file; DESIGN.md has no entry on a hook loop. If one happened, it is recorded elsewhere: add the reference here.

**Reading results**
- Pooled/early signals move with the harness (L544). Bare cell is not "control" (L729).
- Counts in reviews and summaries drift: verify against DESIGN lines (L323 corrects 10→9 and the council's 7/7; L538 corrects a false "never ran on API" sentence).
- `reviews/writeup/ledger.jsonl` last line is truncated JSON (the grid entry); `ledger2.jsonl` parses. Both are machine-extracted; verify before citing.
- Dossier lines not found in DESIGN.md by this pass (do not cite without checking session data): "Seven of eight mirror replies said the protocol already covered the case"; "all replaced the default with a positive test taken from the protocol's own purpose line".

## File map (this folder unless noted)

| Path | What |
|---|---|
| `DESIGN.md` | Full log, 1693 lines. Sections: `grep -n '^## ' DESIGN.md`. v1–v4 L1-L367; v5 L368; exploration/K4 L513; grid + stripped R L625; U1 L804; design synthesis + text findings L862; reviews 7/8 L930/L984; stage 0 W1/U1 L1025/L1067; round 9 L1114; L1 L1141-L1245; W1 L1247-L1398; P1 L1400-L1465; owner restatement L1469; H1 L1477-L1693 |
| `CALIBRATION.md` | v1–v4 pilot data |
| `CONCLUSIONS.md`, `CONTENT-MAP.md`, `SUMMARY.md` | Synthesis, page plan, one-pager |
| `HANDOFF.md` | 2026-11-17 handoff (stale state; owner standing instructions) |
| `run_v5.py` | Session runner, all later tests. Arms control/rule/none/only/placebo; readers fable-low/opus-low/opus-medium/sonnet-low/sonnet-medium; `--oracle`, `--prompt swap`, `--wording` |
| `run_kta.py`, `run_kta_api.py`, `score_kta.py`, `grade_kta.py`, `make_fixture.py` | v1–v4 five-turn harness and API loop |
| `make_fixture_v5.py`, `score_v5.py`, `grade_v5.py`, `break_score_v5.py` | v5 CARRY/COVER |
| `l1/` | `make_fixture_l1.py`, `score_l1.py` (render / ask / grade), `BUILD-NOTES.md`, `references/` |
| `w1/` | `make_fixture_w1.py`, `score_w1.py` (gates / downstream-plan / downstream-score / w1i), `run_downstream.py`, `references/` |
| `p1/` | `make_fixture_p1.py`, `score_p1.py` (gates / e2 / reference) |
| `h1/` | `make_fixture_h1.py` (prompt at line 24), `score_h1.py` (render / readers / gates / classify / anchor) |
| `u1/` | `make_fixture_u.py`, `score_u.py`; instrument failed stage 0 (L1102), not rebuilt |
| `stage0/` | Kept data: `l1-told/`, `l1-fable-reads/`, `p1-votes/`, `h1/`, `h1r2/`, `h1sm1/` (run 1), `h1nd/` (nodoc), `h1dn/` (datanote), hashes |
| `reviews/` | Every ask and answer. `fable-h1-priorart.md` (owner's real record; not for external models unparaphrased), `fable-w1-pattern.md`, `design9-*`, `fable5-synthesis.md` |
| `reviews/final/` | Dossier sent to outside reviewers + the three reviews |
| `reviews/writeup/` | Ledgers, source brief and draft behind SUMMARY.md |
| `council_hub.py`, `or_shim.py`, `COUNCIL-BRIEF-v4.md`, `investigation-2026-11-15/` | v4 council and the v2–v4 investigation |
| `board-learnings.md` | Sonnet reading of board-pattern, input to round 9 |

Fixtures are generated, not committed. Raw run dirs for the grid and R were not kept (`HANDOFF.md`).

## Running the harnesses

All from this folder; use `python3 -I`. Subjects run on the session's own Claude connection (subscription). **`--out` must be an absolute path under `/tmp`.**

```
# selftests (no model)
python3 -I h1/score_h1.py --selftest      # 62 ok expected (L1679)
python3 -I p1/score_p1.py --selftest      # 43 ok (L1442)
python3 -I w1/score_w1.py --selftest      # 99/99 at review 8 (L1015); re-run to confirm the current count
python3 -I l1/score_l1.py --help          # render | ask | grade

# fixtures
python3 -I h1/make_fixture_h1.py /tmp/h1-fx
python3 -I p1/make_fixture_p1.py /tmp/p1-fx
python3 -I w1/make_fixture_w1.py /tmp/w1-fx
python3 -I l1/make_fixture_l1.py /tmp/l1-fx

# a subject session
python3 -I run_v5.py --fixture <fixture dir> --arm control|rule --reader opus-medium --out /tmp/<run> [--oracle]

# H1 scoring
python3 -I h1/score_h1.py render <session dir> <hidden tasks.csv> <out>
python3 -I h1/score_h1.py gates <out> [...]
# readers for H1 since round 2 are API calls to Kimi K3.1 Pro + GPT-6.1 Terra via OpenRouter, ZDR, effort low (L1592); see stage0/h1r2/ for records

# W1 scoring
python3 -I w1/score_w1.py gates <session dir> <fixture>
python3 -I w1/score_w1.py downstream-plan <session dir> <fixture> <hidden> <out>
python3 -I w1/run_downstream.py --jobs <out>/jobs.json --reader sonnet-medium --arm control
python3 -I w1/score_w1.py downstream-score <out>

# P1 scoring
python3 -I p1/score_p1.py gates <session dir> <fixture> <hidden>
```

Exact flag spellings beyond `--help` output above were not exercised by this pass: run `--help` and read the registration section for each test before launching. Freeze hashes are in the registrations (L1263, L1304, L1442, L1535); regenerate and compare before reusing a fixture.

## Still open

1. Owner: which surface, which rules loaded, session length, brief author, in the real failures (L705).
2. L1 permission probe: L1 + one sentence granting standing to change what exists; 8 control; tells permission from reasoning. Proposed in kind at L1131, never run. Pre-register first.
3. Hand-off test (CONCLUSIONS "The next test"): frozen real brief, heading "Design goals" vs "Proposed, not decided", multi-file incumbent, navigating phone readers with a time budget fixed from reference builds, ADDED-shape + reader-fail must coincide. Control screen first.
4. Not covered (L1693): form inside the request's own brief; multi-file builds; multi-turn sessions where the old form was built earlier; other models and efforts (Sonnet only in early rounds; Fable only planned as a non-gating coverage reader, L430, and used for references and reads).
5. Owner failure shape "only the named specifics, no design" never reproduced: flat list passes as fair (L1621). Needs a task where a flat list is not good enough, checked at stage 0.
6. L1 scored only the opening view. A navigating reader with a tap/time budget was never run on the L1 pages (they are in `stage0/` only if kept; check before assuming).
7. P1 E2 (told) votes on the 24 stage −1 sessions not run (L1463). W1i initiative sidecar built, never run (L973). v3–v6 W1 variants and P1 v3–v4 held back, no stage 0 (L1344, L1409).
8. Findings on the rule's text recorded, not acted on (L896-L905); note L905's "4 of 7 pilot rounds" was not found in its source by the L621 check.
9. Rule vs path-scoped skill: undecided. No text has shown an outcome effect in the normal harness.
10. Repo rules: branch `claude/kta-explore` → PR to `dev`, never `main`; the repo has a board (`BOARD.md`); pre-register before every gating test.
