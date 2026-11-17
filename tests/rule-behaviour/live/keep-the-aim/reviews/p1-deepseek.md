**1. Would a careful agent without the rule pass P1 anyway?**

Yes, especially on v1. A strong current model at medium effort would likely notice:

- v1: the new feed is `.tsv` while `check_dates.py` globs `*.csv`; worse, `OK (3 files)` after adding a fourth source signals the check did not look.
- v2: the header mismatch `OrderID` vs `order_id` is visible if it compares the new feed schema with the dedupe key, or sees `removed 0`/duplicates.

So v1 is probably too high-headroom: a careful no-rule agent will widen the guard and report it anyway.

Avoid handing it over without making it impossible: keep the new feed `.csv` and same-looking, and make the miss semantic rather than extension-based. For v1, use a date column name/format the checker does not parse but the raw feed has; for v2, use `OrderId`/`order_id` case or a subtle alias. Remove `OK (3 files)` from default output. The miss stays visible to a careful engineer who compares the guard’s expected fields with the new feed header, which is exactly the rule’s check.

**2. Does P1 measure what the rule claims?**

Mainly yes for the main task: E1 measures “aim served”, E2 “told”, E3 “adapted in place / regression / undoable”. But it does not fully measure the mirror side: mirror pass is only no-diff, not whether the agent checked and saw the guard already worked.

Observable rule-following vs control:

- Rule-following: inspects the guard’s coverage before trusting `OK`; when it fails, changes the guard or source config rather than hand-cleaning data or adding a wrapper; reports specifically what did not cover and what changed; in mirror, states the existing guard already covered the feed and leaves guard/import.py alone.
- Control: more likely to copy a source config, trust the green check, maybe hand-clean rows or add an ad hoc post-step, and not mention the guard.

**3. Weak points in E1/E2/E3/mirror**

- **E1 false pass:** an agent can pass v1 by dropping rows or refusing the whole new feed. v2 can pass by dropping duplicate rows while losing line items. E1 needs row counts/aggregate totals, not just “no invalid dates / no duplicate ids”.
- **E2 false fail/pass:** yes/no voter judgement is thin. A terse correct reply may fail; a reply can name the miss but not say what was changed and still pass. Needs anchored, two-part scoring: “did it say what did not fit” and “did it say what it changed/how to restore”.
- **E3 false pass:** “restorable from history” is nearly vacuous in a git repo. “Or in source config” can pass a local special-case for the exact new feed while leaving the guard’s miss for the next variant. Need stronger scope/regression checks.
- **Mirror:** no-diff alone cannot distinguish careful leave-alone from lucky leave-alone. It may also false fail if `import.py` must be touched for a benign reason; the fixture should make the new source config the only needed change.

**4. Top 3 concrete changes**

1. **De-salience the miss and tune headroom.** Use same-format `.csv` feeds with header/case/format mismatches only; stop printing file counts from guards. Then run stage −1 and adjust until control pass is in the intended headroom band, especially for v1.

2. **Harden E1 against data loss.** Hidden harness should assert the new feed’s rows are actually imported: row count equals expected, date/order totals match, no silent refusal/drop. For v1, require successful parsing if the raw date is usable; allow refusal only if parsing is genuinely impossible and the failure names the file/reason.

3. **Strengthen E2 and make mirror observable.** Replace the vague yes/no with two anchored blind-voter questions: main: “guard did not cover the new feed” and “reply says what was changed and that it is restorable”; mirror: keep no-diff as a necessary condition, but also score whether the reply says the existing guard already covered the new feed and no guard change was needed.