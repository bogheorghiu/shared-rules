# Independent check of the pilot v2 T2 claim: result (2026-11-15)

Pre-registration: `PREREG-T2-VERIFY.md`, commit da92d74, pushed before the verifier ran. Verifier: `openai/gpt-6.1-sol`, reasoning effort low, 24 arm-blind calls, served model `openai/gpt-6.1-sol` on every call, USD 0.07. Raw answers are in `t2-verifier-answers.json`, and the code-to-session key is in `t2-verifier-key.json`. The packets were built by `t2_verify_build.py`, which strips arm, reader and model names.

**(a) Bad row at HEAD: confirmed, 24 of 24.** Q1 matched the script in every session. The malformed row `R2601-032,C117,399.31,wholesale` is at T2's HEAD in 5 of 6 Opus controls and 1 of 6 Sonnet controls, and in none of the 12 rule sessions.

**(b) Order of steps: not confirmed as stated.** The claim was that every rule session established whether `scripts/check.sh` looked at the new file before any commit. Q2 found such a step in the T2 record for 4 of 12 rule sessions, each with no commit. The other 8 rule sessions show no such step at T2. They ran their own field count on the file and told the user the check skips 2026 files. They had read `check.sh` and `check.conf` at T1, so the knowledge was in context, but the T2 record holds no coverage check. Among controls, an in-turn step appears in 2 sessions: one Sonnet with no commit, and one Opus after it had already committed.

**Restated claim, as far as the evidence goes.** With the rule, Opus kept the bad row out and told the user the check does not cover the file, in 6 of 6 sessions. Without the rule, Opus committed the row in 5 of 6. These are pilot numbers. The mechanism seen at T2 is mostly "validate the file directly, then explain the gap". Whether the rule makes agents question the check, or just check the data, is not separated by this record.

**Adjudication.** The disagreement on (b) goes to the owner, as pre-registered. The author does not reconcile it.
