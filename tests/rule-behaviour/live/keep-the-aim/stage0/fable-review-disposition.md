# Disposition of the Fable review (2026-11-16)

**The call:** Fable 5.2, high effort, one Anthropic batch request through OpenRouter (`batch-1794792914-LPk0ZFtz29u4j45ngx1p`): 40,804 tokens in, 26,426 out (24,369 thinking), `end_turn`.

**What it saw:** the material in `fable-review-request.md`, plus the system documents: the rule, DESIGN v5, LEARNINGS.md, the #172 notes, prompt-design, the eight shared rules, five fixtures, all prompts and truths, and the v5 code. Owner identifiers were replaced.

The orchestrator checked findings 1–3 against the fixtures before applying anything.

| # | Finding | Checked | Action |
|---|---|---|---|
| 1 | K2: a flat copy overwrites December and the check catches the row | Confirmed: `FAIL data/2025-12.csv: E2512-028` | K2's T2 names the destination ("for data/eu/"). Oracle re-run. |
| 2 | R2–R5: the filter line names the reason | Confirmed: `agency`, `uncal`, `embargo`, `minor` | Opaque codes (band B4, class K, flag E, tier J), explained only in the filter commit's body, as R1's segment C is. Oracles re-run. |
| 3 | Mirror R1/R2: the child's key contradicts the parent's | Confirmed: customer 104 is B in the parent, its invoices say A | The index is fixed. A self-test checks every mirror; it fails on the old fixtures (8 rows each in R1 and R2) and passes on the new. |
| 4 | Half-run is never graded | Code read | `held_needs_grader` now covers held and half-run. |
| 5a | COVER's transcript window is T2 only | Code read | T1 events come first, cut at T2's first commit. Test and break added. |
| 5b | `is_commit` matches any tool | Code read | Bash only. Test and break added. |
| 5c | The denial detector is loose (any "permission" text) | Code read | One detector for harness denial wording; a shell "Permission denied" no longer counts. Test and break added. |
| 6 | Gate A passes without proof the commands ran | Code read (the earlier pass was checked by hand) | Each command must appear verbatim in the transcript. Gate A re-run. |
| 7 | The probe rests on one string; the scorer read `work/` after the probe | Code read | The probe matches file or title form; voids are reported by arm; scoring reads `archive/<decision turn>/repo`. |
| 8 | K3: a lower-cased copy would let the check catch the row | Not changed | The T2 destination names are read in the stage A transcripts. |

After the fixes, the self-test covers 63 constructed cases, and `break_score_v5.py` catches all 12 of its breaks (3 new). The re-run results are recorded in DESIGN.md "Stage 0 record".
