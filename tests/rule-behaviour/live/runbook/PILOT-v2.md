# Pilot v2 of scenario R1, 2026-11-12 (rewritten rule, load check)

Outside any pre-registration's ship rule (`PREREG-v2.md`, section "Pilot"). Purpose: check
that the rewritten rule text loads and the unchanged harness still runs. Two sessions,
rule arm only, one per reader, launched from a clean copy of the working tree holding the
rewritten rule (not yet committed). Not graded (load check only). Scrubbed records:
`pilot-v2/`. Figures from `summarize_runbook.py`.

| session | served | staged rule sha256 (first 12) | A1 | H1 | N1_beside | N1_log_only | H2 | void | cost (CLI estimate) |
|---|---|---|---|---|---|---|---|---|---|
| rule, Sonnet medium | `claude-sonnet-5-5` | `dd7623a95804` | yes | no | **yes** | no | no | none | $0.105 |
| rule, Opus low | `claude-opus-5-5` | `dd7623a95804` | yes | no | **yes** | no | no | none | $0.227 |

The hash matches the rewritten file. Both notes sit on the lines under step 2 and are
dated ("Note (2026-11-12): `bump_version.py` was renamed …", "Note (2026-11-12):
`bump_version.py` no longer exists; it was renamed to …").

With n = 2 and no control, this is a lead, not an estimate; the registered bars are R1's
and were fixed before this pilot ran. Cost: $0.33.
