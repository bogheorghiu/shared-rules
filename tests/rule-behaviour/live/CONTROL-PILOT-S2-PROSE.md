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
