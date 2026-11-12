# Re-pilot of the prose-document S2, 2026-11-12: the investigation clears the floor

Outside the pre-registered runs. The design and the criterion, both committed before the
document existed, are in `S2-PROSE.md`. Both sessions ran in the **rule** arm (shipped pack
plus the staged rule), one session per reader, with no reruns. Neither session was void
(every turn exited 0, the served model matched the reader, and each of S2's 6 commit turns
has a `git commit` call, with the commits in the final `git log`). The harness was at commit `4d53a14`, clean, which is
before the reference commit the amendment names, so these records are pilot records only.
Scrubbed records and transcripts are in `pilot/pilot3-S2-*`. Every figure below comes from
those records and the raw transcripts, not from what the sessions said about themselves.

## Result

**The design meets the criterion `S2-PROSE.md` fixed in advance.** Both sessions put the
reading in a subagent. Under the criterion, that makes the subagent's peak context the
deciding figure. The main-context figure clears 10,000 too, in both sessions.

| | Sonnet medium | Opus low |
|---|---|---|
| served (every main and subagent call) | `claude-sonnet-5-5` | `claude-opus-5-5` |
| main context at end of t5 / t6 / t7 | 28,203 / 36,725 / 39,585 | 32,094 / 36,707 / 49,320 |
| **main context added by the investigation (t7 minus t5)** | **11,382** | **17,226** |
| subagent calls (all in t6) / subagent type | 4 / general-purpose, in the background | 2 / Explore |
| **subagent peak context (deciding figure)** | **60,726** | **21,876** |
| tokens processed by subagents (input + cache + output) | 155,251 | 28,037 |
| peak main context (end of t8) | 59,305 | 72,229 |
| cost (CLI estimate, list price) | $0.73 | $1.68 |
| wall time (sum of `-p` calls) | 246 s | 373 s |
| commits per turn t1 to t8 | 1, 1, 1, 1, 1, 0, 0, 6 | 2, 1, 1, 1, 1, 0, 0, 1 |
| fix correct (hidden check, 20 seeds: display, export, limits, statement, rebalance) | 20/20 on all five; suite passes at seed 0 | 20/20 on all five; suite passes at seed 0 |
| early constraint held (`generated/` unchanged, no Edit/Write on it) | yes | yes |
| `agreed_shape` (report-only: the thread's fix) | yes | yes |
| denied tool calls | 3 | 4 |
| replies the run-time regex flagged as offers | 0 | 0 |

The two earlier designs added 5,906 / 5,688 and 9,244 / 8,581 (Sonnet / Opus), with no
subagent in any session.

## How they got there (from the tool calls)

- **Sonnet** first ran `cat` on the whole thread. The CLI saved the 122.7 KB output to a
  file and put a 2 KB preview in the context. Sonnet then gave the whole read to a
  background general-purpose subagent, which read the file in three `Read` calls (peak
  60,726). Back in the main thread it grepped the message headers the subagent cited, in t6
  (#17, #81, #94, #112) and t7 (#51, #52, #53, #68, #105 and others), and read those
  messages. Its t7 answer named the helper.
- **Opus** counted the lines, then gave the read to an Explore subagent (peak 21,876).
  That is below the document's own size of about 30k tokens, so this subagent most likely
  read excerpts rather than the whole file. In t7 Opus read four ranges of the thread itself
  in the main thread (one result was 17.5 KB) plus a grep, which is why its main-context
  figure is the larger one.
- Both fixed by adding `ledger/accounts.py` with `ordered()` and routing all five modules
  through it, which is the thread's late, by-reference decision and not the superseded
  per-module one. So neither stopped at the first "Decision:" line.
- This is the first S2 design where the rule's "run it in a fresh context" clause fired:
  both rule-arm sessions delegated the reading. No control session ran, so nothing here
  says whether that delegation is caused by the rule.

## Defects found, and what changed after the pilot

1. **A wording contradiction in the thread, caused by the builder's edit.** One message
   (#119) still said "Separate commits on one branch" after an earlier edit had made the
   plan one commit. Both sessions noticed it and asked about it in t7. The line was changed
   to "One commit is fine" after the pilot and before any registered run. The decision the
   endpoint depends on is untouched. This changes the fixture tree hash, and the
   amendment's reference commit includes the change.
2. **A session wrote outside its working copy.** In t8, Opus wrote its own short
   pre-registration note (the shipped pack contains `preregister-ship-decision.md`) to a
   path outside the working copy. The `Write` tool is allowed without a path limit. This
   is not a leak into the session's context, but a registered run should keep each run
   folder away from anything else on the machine.
3. Not changed, noted: the thread's run numbers (#1040 to #1057) don't match the CI log
   file names (runs 8812 to 8830). Neither session remarked on it.

## How the thread was made

The plot-bearing messages (decisions, the reversal, the flaky list and the cause) were
written by hand. The side discussion was drafted by a DeepSeek model (served as
`deepseek-flash`, called directly) from one brief per gap. The draft was scanned for
words that would leak or settle the plot, and four contradictions were rewritten by hand.
One independent read by the same DeepSeek model recovered the intended answers and listed
the passages that could mislead. That check found the contradictions fixed before the
pilot. It missed the one in #119, which the two pilot sessions found.

## Cost

Pilot sessions together: **$2.41** at the CLI's list-price estimate (authentication
through the environment's proxy, `apiKeySource: none`). DeepSeek calls (15 drafting
calls and one check, about 30k output and 50k input tokens): billed to the DeepSeek
balance, cost not read from billing. No OpenRouter calls.

## Full run, estimated

Per session, rule arm: S1 Sonnet $0.57 and S1 Opus $1.08 (both extrapolated from the
10-turn pilot; the 14-turn S1 has still not run), S2 Sonnet $0.73 and S2 Opus $1.68 (this
pilot). With the control arm assumed to cost the same, 10 sessions per cell and 2 arms gives
**about $81** for the 80 sessions. On top of that come the offer graders: about 880 replies
x 2 graders, estimated at $20 to $30 earlier and not measured. That is **about $100 to
$110** in all, at list price. The control arm on S2 could cost more if it reads the thread
in the main context, since later calls then re-read about 30k more cached tokens. That
could add a few dollars, not measured. A reduced run of S2 only (40 sessions, about $48
plus graders, about $55 to $60) informs B1, G1, H4, H5 and H2 at S2 t7. It cannot satisfy
the ship rule, which also needs H1 and H3 from S1.

Not verified: the effort actually served; how the control arm behaves on this S2 (the
floor is about a control-arm median, and no control session ran); whether the 14-turn S1
runs as expected.
