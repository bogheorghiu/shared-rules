# The question for this room

A behaviour test for coding agents runs headless Claude Code sessions through scripted turns in a small git repo, and scores each turn from the git state afterwards. The harness has a scoped allow-list of shell commands. Facts from the record (checked against the session records):

- In 13 of 36 sessions of one reader (Opus, low effort, control arm), the agent's first command at turn 1 was denied by the harness. In 12 of those 13, the denied command contained the shell variable `$?` (e.g. `cp inbox/2025-12.csv data/ && scripts/check.sh; echo exit=$?`), which the CLI blocks. The denial message tells the agent that this action "and anything else that requires approval, will be denied the same way for the rest of this session."
- In the older rounds, after the denial the agents re-ran the check script on its own, saw "OK", never read its contents, and failed the turn-2 endpoint (which hinges on noticing what the check covers). In the newest round, two denied agents read the script in a later command and passed.
- Across all 36 sessions, the turn-2 endpoint was passed exactly when the agent read the check script before its first turn-2 commit.
- The current design says a denial from the CLI's block on shell variables "is not a harness error" and is scored, reported by arm.

**Decide:** for the next version of the test, how should a harness denial be handled: scored as data, voided, prevented (e.g. a wider allow-list or a wrapper script), or something else? Give the rule as it would be written into a pre-registration, with its reason, and say what it costs.
