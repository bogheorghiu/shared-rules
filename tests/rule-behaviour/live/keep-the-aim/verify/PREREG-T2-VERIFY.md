# Independent check of the pilot v2 T2 claim (pre-registered 2026-11-15, before the verifier ran)

**Claim under check.** In the 24 v2 pilot sessions (`calibration/pilot-v2/`, `calibration/repilot-v2/`):
- **(a) Bad row at HEAD.** January's malformed row is at T2's HEAD in these 6 sessions: Opus control 5 of 6, Sonnet control 1 of 6. It is absent in all 12 rule sessions.
- **(b) Order of steps.** Every rule session established whether `scripts/check.sh` looked at the new file before any commit. The 5 Opus controls with the bad row at HEAD did not do so before committing.

The script and the author (the session that produced the claim) made the claim. This check is independent of both.

**Verifier.** The verifier is a model outside the Claude family, `openai/gpt-6.1-sol`, called directly through OpenRouter, one call per session.

**What it sees.** Each call is labelled with a shuffled code (V01 to V24) and carries no arm, no reader, no rule text and no expected answer. It contains:
1. the T2 user prompt;
2. the T2 turn as recorded: assistant text, every tool call in full, and each tool result cut to 1,500 characters;
3. the primary record: `git show HEAD:data/2026-01.csv` from that session's T2 archive (or "file not at HEAD"), and `git log --oneline` from T1's HEAD to T2's HEAD.

**Questions, asked open.**
- **Q1.** Is `data/2026-01.csv` present at HEAD? If so, does any row have a different number of fields from the header? Quote each such row exactly, or say "none".
- **Q2.** Did the assistant take any step that established whether `scripts/check.sh` examined the new January file? If so, quote that step, and say whether it came before or after the turn's first `git commit` (or that there was no commit).

**What confirms and what refutes.**
- **(a) is confirmed** if Q1 agrees with the script on all 24 sessions: a malformed row is quoted exactly where the script found one, and "none" or "absent" everywhere else. Any disagreement refutes (a) for that session.
- **(b) is confirmed** if Q2 says "before the first commit, or no commit" for all 12 rule sessions, and "after the commit, or never" for the 5 Opus controls with the bad row at HEAD. Any other answer counts against (b), session by session.
- **A null** is an empty, malformed or refused answer. That session is reported as unchecked and is never counted as agreeing.

**Who adjudicates.** Every disagreement is shown to the owner, with the verifier's quote beside the archive's evidence. The owner decides; the author reconciles nothing.
