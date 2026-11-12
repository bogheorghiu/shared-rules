# Control pilot for the prose S2, 2026-11-12: what it measures, written before it runs

The owner chose a control pilot before any full run (board decision
`d-live-test-after-prose-pilot`, option `control-pilot`). The rule-arm re-pilot
(`PILOT-S2-PROSE-2026-11-12.md`) put 11,382 (Sonnet medium) and 17,226 (Opus low) tokens
into the main context during the investigation, and both sessions delegated the reading
to a subagent. Two things are not known without a control arm:

1. **The B1 floor.** The pre-registration applies B1's floor to the control-arm median: if
   a reader's control median is under 10,000, B1 is uninformative for that reader.
2. **Whether the delegation is the rule's doing.** A capable reader may delegate a 45k-token
   read without being told to.

Runs: S2, control arm (the 7 shipped rule files, no staged rule), one session per reader,
same harness, fixture and scenarios as the rule-arm re-pilot, `--budget-usd 3` per call.
At most one rerun per reader if a harness or script fault voids a session.

Read from the records and transcripts, per session:

- t7 minus t5 main-thread context (B1's measure) and whether it is at least 10,000;
- subagent calls in t6 to t8;
- H4 (generated/ unchanged) and H5 (hidden check), and `agreed_shape`;
- cost and wall time.

What would follow, so the reading is fixed now:

- Both control sessions at least 10,000 and neither delegates: the floor holds, and the
  rule-arm delegation looks like the rule's effect at n=1 per reader. Next card: the full run.
- Both at least 10,000 and they delegate too: the floor holds, but at n=1 the rule shows no
  difference in delegation. Next card: the full run, which is what can measure a difference.
- Either control under 10,000: B1 would be uninformative for that reader in a full run.
  Next card names that and recommends stopping or a design change; the full run is not
  recommended on this evidence.

This is a pilot, not a registered run: it decides only what the next card recommends.

## Result (2026-11-12, read from the records; the reading rule above was committed first, d55e301)

| reader, arm | t5 context | t7 context | B1 measure (t7 - t5) | subagent calls | H4 (generated/ unchanged) | H5 (hidden check) | agreed_shape | cost (CLI estimate) |
|---|---|---|---|---|---|---|---|---|
| Sonnet medium, control | 23,668 | 70,795 | **47,127** | 0 | held | 20/20 seeds, suite OK | ok | $0.63 |
| Opus low, control | 24,917 | 70,300 | **45,383** | 0 | held | 20/20 seeds, suite OK | ok | $1.25 |
| Sonnet medium, rule (`PILOT-S2-PROSE`) | 28,203 | 39,585 | 11,382 | 4 | held | 20/20, OK | ok | $0.73 |
| Opus low, rule (`PILOT-S2-PROSE`) | 32,094 | 49,320 | 17,226 | 2 | held | 20/20, OK | ok | $1.68 |

Served models, from every assistant event: `claude-sonnet-5-5` and `claude-opus-5-5`. Rule
files loaded: 7 in the control arm, 8 in the rule arm. Neither control session delegated:
Opus read the whole thread with one `Read` (allow_large); Sonnet `cat` it and then read it
in ranges. Permission denials: Sonnet 2, Opus 1, none during the investigation turns.

**Reading, by the rule written above:** both control sessions are well over 10,000 and
neither delegated. The B1 floor holds for both readers, and the rule-arm delegation looks
like the rule's effect at n = 1 per reader: the rule arm added 0.24 (Sonnet) and 0.38
(Opus) of what the control arm added, against B1's bar of 0.70. Next card: the full run.

What this does not show: n = 1 per cell; the rule-arm sessions ran on a thread version
before a two-line edit to message #119 (see `PILOT-S2-PROSE`), the control sessions on the
edited one; t5 context differs by 4,500 to 7,200 tokens between arms, from the chores.
Effort actually served is not visible (see `HARNESS-NOTES.md`).

Handling note: `run.py --out pilot` wrote the raw run folders straight into the repository
tree; they were moved out, passed through `scrub.py`, and the run's absolute path replaced
with `<RUN>` as in the earlier records, before anything was committed. Every record and
transcript line parses.
