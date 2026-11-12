# #ledger-ci: flaky CI on main (thread export)

Exported from the team chat on 2026-11-11, oldest first. Times are local. Reactions and edits are not included.

### #1 · Priya · Tue 2026-11-03 09:12

Opening a thread for the CI flakiness, since it's eaten most of my Monday. Three runs on main failed yesterday and passed on rerun without a code change. What I've seen fail so far:

- `test_sync.SyncTest.test_display_order`
- `test_export.ExportTest.test_matches_golden`
- `test_report.ReportTest.test_summary_totals`

The export one is the most annoying because the diff is enormous and it's hard to see what moved. I'll keep a list here. Please post failures in this thread rather than in #ci so they're in one place.

### #2 · Tomás · Tue 2026-11-03 09:40

The runner image rolled to 20261101.1 over the weekend (Python patch bump, new tzdata, a newer git). Timing fits uncomfortably well. I can pin the old image for a day if someone wants a controlled comparison.

### #3 · Rafael · Tue 2026-11-03 09:55

Thanks for corralling this, Priya. I'll second the request to keep it here — I spent twenty minutes yesterday scrolling #ci trying to figure out whether the export failure was new or the same one from last week, and gave up.

Worth adding to your list: I saw `test_report.ReportTest.test_summary_totals` go red on a branch build last Thursday too, before the weekend, though I can't swear the failure looked the same. It was on a branch that only touched the report templates, no logic, so I assumed I'd broken something and closed the laptop. It passed on rerun.

One thing I'd find useful, if whoever hits it next has the patience: the full failure output, not just the test name. The three you listed are all in different modules but they're all the kind of test that compares a whole rendered thing against an expected thing, and the diffs we get are mostly noise — ordering, whitespace, that sort of thing. If it's actually the same underlying wobble showing up in three places, one clean failure output might tell us more than three summaries.

Also, Tomás — re: pinning the old image, I'd take that comparison if it's cheap. Not asking anyone to burn a day on it, but if it's a one-line change to the workflow and we get a day of main builds on the old image next to a day on the new one, that seems like information we'd want before we start spelunking through the tests themselves. My only worry is that if the flake rate is as low as it looks from three failures, a single day might not be enough signal either way.

### #4 · Tomás · Tue 2026-11-03 10:08

Here's the rundown on 20261101.1, since a few people have asked. It's a bigger roll than usual because we skipped the October one while the base image was being rebuilt.

- Python: 3.12.6 → 3.12.7. Patch release, so mostly bugfixes, but it does pick up the newer SQLite and OpenSSL that ship with the patch. Nothing in our requirements pins around those, I checked.
- tzdata: 2026a → 2026b. This is the one I'd flag just because our test fixtures have a handful of hardcoded dates around month boundaries, and the ledger's monthly export does date bucketing. Whether the new tzdata changes anything for us I genuinely don't know, but it's the kind of thing that moves dates by an hour in a corner.
- git: bumped from 2.46.x to 2.51.x. Mostly matters for the checkout step; the new one is faster on shallow clones. No config change needed on our side.
- Locale: the image now defaults to `C.UTF-8` where it used to be plain `C`. That changes how anything that sorts or compares strings in a locale-aware way behaves, and it changes default encoding assumptions in a couple of places.
- New cache action: the image ships with the updated `actions/cache` shim, and the restore step now uses a different key prefix by default. Old caches won't be restored unless a workflow opts in explicitly. Ours doesn't, so first runs after the roll were cold.

Nothing there screams 'this is it' to me, and I want to be clear I'm not saying the image is the cause. But the tzdata and locale lines are the two I'd keep in mind while looking at failures. I can pin the old image for a day starting whenever someone says go — it's a one-line change in the workflow and I'll add a comment so nobody wonders why it's pinned.

### #5 · Wen · Tue 2026-11-03 10:31

Quick question from someone who's only been here a few weeks, so apologies if this is obvious: do these failures cluster on one runner pool? I've been watching the build results page out of curiosity and it seems like the reds I've seen were all on the larger pool, but I haven't actually checked, so that might be me pattern-matching on nothing.

Asking because if the image roll only landed on one pool so far, or landed on them at different times, that might be a cheaper way to get the comparison Tomás offered than pinning and unpinning. I don't know how the rollout works though — whether it's all at once or staged, or whether the pools even take different images. Tomás would know.

The other thing I noticed, and again, small sample: the failures seem to come in bursts rather than spread out evenly. Two or three within an hour, then nothing for most of a day. That could just be how many builds we run in an hour, honestly. I don't have enough of a picture to say. Happy to go pull the build history and put actual numbers on it if that's useful to anyone — I have the afternoon free and it beats reading the schema docs.

### #6 · Priya · Tue 2026-11-03 10:52

Here's the display_order failure from yesterday, trimmed to the assertion. Not going to editorialize, just putting it here so we're all looking at the same thing:

```
FAIL: test_display_order (test_sync.SyncTest.test_display_order)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "tests/test_sync.py", line 214, in test_display_order
    self.assertEqual(names, expected_names)
AssertionError: Lists differ: ['household', 'travel', 'savings', 'business', 'gifts'] != ['household', 'savings', 'travel', 'business', 'gifts']

First differing element 1:
'travel' != 'savings'

- ['household', 'travel', 'savings', 'business', 'gifts']
+ ['household', 'savings', 'travel', 'business', 'gifts']
```

Two notes on the data, in case they matter to someone reading it later: the balances on `travel` and `savings` are tied in the fixture — both come out to the same number of cents — and the other three are clearly separated. The test builds the expected list by hand in the order it wants. I have not looked at why the order came out the way it did, and I'm not going to guess in this thread.

I'll paste the export diff next time it fires; yesterday's was too big to be useful and I'd rather grab a smaller one. If anyone hits test_display_order before I do, drop the output here and I'll add it to the pile.

### #7 · Tomás · Tue 2026-11-03 11:14

Wen — good question, and no, not obvious at all, the pool layout is genuinely confusing. Short version: there are two pools, `general` and `heavy`, and they don't take image updates at the same time. `general` gets the new image first because it's most of our build volume and we want the roll to shake out there; `heavy` follows a day or two later once nothing has exploded. The roll to 20261101.1 went to `general` on Saturday night and to `heavy` this morning, so right now they're on different images.

That does mean there's a natural comparison window, but it's messier than it sounds. `heavy` only runs the long jobs — the integration ones and the packaging builds — and most of our unit test runs are on `general`. So a failure in `test_sync` or `test_report` is almost certainly going to show up on `general` regardless, and the fact that we haven't seen it on `heavy` tells us less than it looks like it does. The export test does run on both, so that one's a slightly fairer comparison.

On the bursts: I'd bet on build volume, honestly. We run most of our builds between 9 and 11 and again around 3, because that's when people push, so failures were always going to cluster in those windows even if the underlying rate is flat. Doesn't rule anything in or out, just means the burst shape isn't by itself interesting.

Wen, if you want to pull the build history and count failures per pool per day since the roll, that would genuinely help and it's the kind of tedious thing I keep not getting to. The API endpoint is in the runner docs under 'build history'. Pin offer still stands.

### #8 · Dana · Tue 2026-11-03 11:30

Catching up on this thread — good discussion, and I like that nobody's jumped to a cause yet. A few things from my side, mostly about how we spend time on this.

First, Priya, keep the failure list going in this thread, and if you can, note the pool and the time alongside each one. Tomás's point about the two pools being on different images right now means we have a window that won't last, and I'd rather we had the data written down than reconstructed from memory next week.

Second, Tomás, go ahead and pin the old image on `general` for a day, starting whenever's convenient this afternoon. I'm not expecting it to tell us much on its own given the rate, but it's cheap and it means if the failures keep coming on the old image we can stop thinking about the image roll entirely. Keep `heavy` on the new one so we don't lose the comparison there. Add a comment in the workflow with today's date and a link to this thread so it's not a mystery in three weeks.

Third, Wen, yes please to the build history numbers. Per pool, per day, since Saturday. If it's a slog, do the last four days and we'll take it from there. Don't let it eat your whole afternoon — the schema docs aren't going anywhere, but neither is this.

And Rafael, agreed on getting one clean failure output rather than three summaries. Priya's paste is a good start. If the export test fires again, whoever's nearest, grab the diff before the rerun and paste it here, even if it's ugly. We can trim it after.

I don't have a theory yet and I'm not going to invent one. Let's get the pin and the numbers in place and look again tomorrow morning. If the failure rate is unchanged by then we'll know to look elsewhere, and if it drops we'll know where to dig.

### #9 · Wen · Tue 2026-11-03 11:48

Possibly dumb idea: clocks went back on Sunday (Nov 1, US). Anything in ledger that buckets by day or compares dates could get an hour wrong for a week. The statement code groups by date, the export groups by month, sync sorts things. Not sure how sync would care about time though.

### #10 · Tomás · Tue 2026-11-03 12:19

Quick one on Wen's clock idea before it takes over the thread: the runners themselves are all UTC, and I don't see us setting TZ anywhere in the job config. So the runner's wall clock didn't move on Sunday. That said, the image bump did pull a newer tzdata, so anything that touches zoneinfo or localtime conversions is running against different zone data than it was last week. Whether that matters here is a different question than the runner clock, and I don't want us to conflate the two.

For the controlled comparison, I can pin 20261018.1 on a branch for a day. It's a one-line change in the job matrix, no shared state. If the failure rate drops to zero on the pinned image and stays nonzero on 20261101.1, that's a strong signal from the image. If it's noisy on both, it's probably not the image and we can stop chasing it. Cost is we don't get the Python patch bump on that branch for a day, which I'm fine with.

One caveat: pinned runs won't reproduce whatever tzdata difference exists, so if the DST angle is real, pinning could make it look cleaner than it is. If someone wants the comparison I'd rather run it alongside an unpinned branch than instead of one. Say the word and I'll set it up.

Also, if anyone has a failing run ID from yesterday, drop it here. I want to check whether the failures cluster on particular runners or follow the job around. If they follow the code rather than the machine, that changes what I'd look at next.

### #11 · Rafael · Tue 2026-11-03 12:58

On the DST angle specifically: the transaction feed dates are plain YYYY-MM-DD strings, no time component anywhere. The parser does a strptime on that format and stores a date, not a datetime. So an hour going backwards on a Sunday shouldn't touch them. Same for the statement grouping I looked at a while back, it's keyed on the date string. So my instinct is Wen's idea doesn't reach the sync test.

But in fairness I should say I haven't checked every code path. The export code builds a month key from a date, which is fine, but I don't know off the top of my head whether anything downstream of that does a conversion to local time before formatting. And the report summary does some arithmetic on totals that I'd have to actually read. I've been in the parser and the feed mapping this week, not the reporting side.

What I'd want before we spend time on DST is a failure that shows a date or time actually moving by an hour. The diffs Priya posted are big and ugly but I didn't see timestamps in them. If someone has a failing run with the actual diff pasted, I can look at whether the moved values are dates, amounts, or row ordering. That would tell us pretty fast which of the three failures are even the same bug.

Also worth saying: if it is tzdata, it should be reproducible outside CI on a box with the same data. That's a cheaper test than pinning runners.

### #12 · Priya · Tue 2026-11-03 13:31

To be clear about what I actually saw, since I don't want to send people down a hole: the three failures don't obviously involve dates at all. The sync display-order one is a list of display names coming back in a different order, no dates in the assertion output. The summary totals one is a number mismatch, and the numbers differ by small amounts that look like row counts or rounding, not a day boundary. The export golden diff is the only one I'd call date-adjacent, and even there it's a big block diff and I couldn't tell you what moved without diffing it properly.

So I can't rule DST in or out, but nothing I've looked at points at it. If someone wants to test it cheaply, run the export test with the system clock faked to before the changeover and see if the diff goes away. If it doesn't, that's one thread closed without touching the runners.

What I can do today is gather the failing run IDs and the assertion text verbatim for each of the three, so we're all looking at the same output instead of my paraphrasing. I'll post that this afternoon. If the export diff is genuinely huge I'll attach the first fifty lines rather than the whole thing so it doesn't flood the thread. And I'll note which ones passed on rerun and which didn't, because if one of them is actually failing consistently we've been treating a real bug as flakiness. That's the outcome I'm least looking forward to but most want to rule out.

### #13 · Ines · Tue 2026-11-03 14:07

Unhappy memory on the DST angle, for what it's worth. About two years ago the finance import blew up on the DST weekend. Not the spring one, the autumn one, when the clocks went back. What happened was the import script walked a directory of monthly statement files and matched them to months by parsing the file's modification time rather than its name. Normally that's fine because the file lands at the start of the month and the mtime is unambiguous. But one of our exports got copied into the drop folder at something like 01:30 on the Sunday morning, the hour that happens twice, and the mtime came back as the second 01:30, which the script's date arithmetic resolved to the following day, which rolled it into the next month. So a November file got imported as December, and December already existed, and the import aborted halfway through with a duplicate-month error.

Took us most of a Monday to work out, because the error message said duplicate month and everyone went looking at the file contents. The fix at the time was to match on the filename instead of the mtime, which we should have done from the start. I'm not saying this is that, but the shape is similar enough that I'd rather mention it once than have it bite us and think 'someone should have said'. The thing that made it hard was that it only happened for one file, and only if it landed in that one-hour window.

If the ledger monthly export is read anywhere by mtime rather than by the date in the filename, that's worth a look. I don't think it is, but I haven't looked at that code recently and I don't want to vouch for it.

### #14 · Wen · Tue 2026-11-03 14:44

Thanks Ines, that's exactly the kind of thing I was worried about, and it's more concrete than my hunch. For the record my original thought was narrower than that: the statement code groups by date and the export groups by month, and if anything in there is doing a conversion through local time, then for the week after the changeover a timestamp near midnight could land on the wrong side of a day boundary. That's a one-hour-wide window per day for a week, so it would look random and pass on rerun, which matches what Priya's seeing. It doesn't explain the display-order one at all, I'll admit that.

I'm not attached to the theory. If Rafael's right that the feed dates never become datetimes, then most of it goes away. But I'd still like to know whether the reporting side converts anything before it formats, since that's the part nobody's said they've read. If it doesn't, I'll drop it and go back to the tzdata question with Tomás.

Happy to do the faked-clock run Priya suggested, it's a small thing and I have the afternoon. If it comes back clean that's useful either way.

### #15 · Rafael · Tue 2026-11-03 15:22

Wen, I'll save you the run on the reporting side, at least partially. I went and read the summary path just now instead of guessing. The totals are summed from the stored rows and the month labels are taken from the date field directly, no conversion step that I can see. So the summary failure is very unlikely to be a DST thing. The display-order one I still can't explain, and I'm not going to pretend I can.

On the export, I traced it as far as the month key and stopped, because the golden file comparison is downstream of that and I didn't want to guess at what it does. So: two of the three look unrelated to dates based on a reading of the code, one is unresolved. That's not the same as ruling DST out for the whole codebase, and I want to be honest that I've now looked at maybe half of what I claimed earlier.

What would help me most is Priya's verbatim assertion text. If the export diff shows a label shifting by a day or a month boundary moving, that's the DST shape. If it shows rows reordered or amounts recalculated, it isn't. I can look at that in ten minutes once it's posted. Until then I'd rather not have anyone spend a day pinning runners on my say-so.

### #16 · Tomás · Tue 2026-11-03 16:11

Summary of where I'm at, so nobody has to scroll. The runner clock is UTC and didn't shift; that part of the DST idea doesn't apply to the machines. The tzdata in the new image is different from the old one, which is a real difference and separate from the clock question. I can't tell yet whether either one is connected to the failures. I'm holding off on the pinned-image comparison until Priya posts the run IDs, because if one of these is a consistent failure rather than flaky, pinning tells us nothing.

If we do run the comparison I'd want it on a branch, side by side with an unpinned run of the same commit, and I'd want at least a few runs each before reading anything into it. One green run on a pinned image proves nothing.

One thing I'd ask: if anyone gets a failure, grab the run ID and the image tag from the job log before rerunning. Once it's rerun the environment info is harder to line up. That's the single most useful thing for me right now. I'll keep watching the thread and set up the branch if we get to that point.

### #17 · Priya · Tue 2026-11-03 17:02

Update on the list: `test_report.ReportTest.test_summary_totals` is NOT flaky. It failed on run #1041 because of the --since commit (4e1c9a2), which had an off-by-one on the boundary day, and that commit was reverted the same afternoon. Every failure of it is on 4e1c9a2 and none since the revert. Striking it. So for now the flaky ones are display_order and matches_golden.

### #18 · Wen · Wed 2026-11-04 08:34

On the --since thing since Priya cleared it off the flaky list: that one's on me, sorry for the churn. The bug was a boundary-day comparison. The CLI help text I wrote said "since, inclusive" and then the code did the natural-looking thing of `if tx.date > since: keep` — strict greater-than. So anything dated exactly on the --since day fell off. My local testing used ranges where the since day happened to have no transactions, which is exactly why I never saw it.

The reverted commit is 4e1c9a2. What I want to do for the redo is normalise both sides to plain `date` objects before comparing, which removes the datetime-vs-date ambiguity that made the off-by-one easy to write in the first place, and then make the comparison `>=`. I'm also going to add a comment right at the comparison saying the boundary day is included, because I clearly can't be trusted to remember that six months from now.

One thing I'm not sure about: do we want --since to be inclusive because the help text says so (my instinct), or exclusive because most tools do that? I don't think the docs anywhere else commit to either, so if we actually want exclusive we should change the help text and reject the redo as written. I'll hold off pushing the branch until someone weighs in — it's a two-line change either way, I just don't want to flip it twice.

### #19 · Rafael · Wed 2026-11-04 08:58

Wen, no worries, boundary bugs are a rite of passage. I read through the reverted diff and here's my take on the redo.

The normalise-to-date approach is right. The original was mixing a `datetime` from the import path with a `date` from somewhere else, and once you're comparing those you get whatever the comparison happens to do, which is nobody's idea of a spec. If both sides are `date`, the operator is the only thing left that can be wrong, and it's visible in one line.

Two things I'd add. First, put the normalisation in one small function rather than at each call site — I saw the same pattern in the CLI entry point and in the filter used by the export path, and if we fix one and not the other we'll be back here in a month. Second, when you write the test, don't just test the day exactly on the boundary — also test the day before and the day after, and one transaction with a timestamp late in the day (23:59-ish) on the boundary date, because that's the input that would have gone through datetime comparison in the wild.

Otherwise the shape of the redo looks fine to me. Ping me when the branch is up and I'll review properly, it's small enough that I can do it same day.

### #20 · Dana · Wed 2026-11-04 09:21

Quick one on the redo since I'm the one who'd have to bless the behaviour change: the test Rafael described is the minimum, please actually add it in the redo branch rather than as a follow-up. Specifically I want a test named for the boundary day that fails on the old code and passes on the new, so if someone later "simplifies" the comparison back to `>` they get a red build and not a mysterious report from a user. If it's annoying to write because the fixture has to have a transaction dated exactly on the since day, that's a sign the fixture is too coarse, not a reason to skip it.

On inclusive vs exclusive: I don't have a strong opinion and I'm not going to pretend the docs settle it. What I care about is that the help text and the code say the same thing, and that there's a test pinning whichever it is. Wen, you wrote the help text, so if you still think inclusive is right, go with inclusive and make the test say so loudly. If someone else has a real reason to prefer exclusive, say it now-ish, because after the redo lands the behaviour is what it is and users will build on it.

Also, unrelated but while I'm looking at this: this branch and the flaky stuff are separate, right? I don't want the --since redo to end up in the same PR as whatever's going on with the export test, because I'd like to be able to reason about one at a time.

### #21 · Wen · Wed 2026-11-04 09:39

Separate, yes — the redo branch is cut from main and touches the date filtering and the CLI help only, nothing in export or sync. I'll keep it that way.

I'll go with inclusive since that's what the help text already promises, and I'll write the test to assert the boundary day is included, plus the day-before and day-after cases Rafael suggested, plus one transaction at 23:59 on the boundary date to make sure the time component gets stripped rather than compared. Naming it something like `test_since_includes_boundary_day` so it's greppable. If I put it in and it passes on the old code I'll know I've written the wrong test and I'll come back here rather than quietly deleting it.

Will have the branch up this morning and ping Rafael.

Switching topics slightly: I noticed while running things locally that the full-feed sync test takes a while and the log output is mostly DEBUG lines about every record it touches. Is that normal for this suite or is it something that crept in? It's not the flaky test, I'm just curious because it made my terminal scroll for ages.

### #22 · Tomás · Wed 2026-11-04 09:57

On suite runtime, some numbers from the last few main builds, because I've been staring at the timings anyway:

```
build #1047  total 6m41s
  test_sync (full-feed)     2m18s
  test_export               1m02s
  test_report               0m47s
  everything else           ~2m30s
```

The full-feed sync test is the single biggest item and it's been that way for a while, it's not new. The log volume is real though — that test drives a feed with a few thousand records through the sync path and the sync code logs DEBUG per record, so you get thousands of lines that nobody reads on a green run. On a red run it's worse because the whole block gets dumped into the failure output and the actual assertion is buried somewhere near the top.

I don't want to just crank the global log level down because that would also hide the DEBUG lines on the tests where they're genuinely useful when something breaks. But scoping it down for that one test seems reasonable if someone wants to do it. I can also look at whether the runner is under-provisioned, but my gut says the 2m18s is mostly the test doing real work rather than the machine being slow — I can confirm that if it'd help.

### #23 · Rafael · Wed 2026-11-04 10:12

Re suite runtime: +1 to what Tomás said, the full-feed test is doing genuine work. I profiled it once out of curiosity and most of the time is in the sync loop itself, not setup. So I don't think there's a quick win there short of making the feed smaller, and I'd rather not — it's the only test that exercises the path with a realistic number of records, and the bugs we've had in that area were all at the edges of volume rather than with two records.

On the logging: I'm in favour of turning down the per-record DEBUG lines for that test specifically, as long as the lines that say what the sync is doing at a coarse level (start, batch boundaries, finish) stay. Those are the ones I actually read when it fails. The per-record ones I've never once found useful. The thing I'd be careful about is doing it by setting a global level in the test, because that tends to leak into other tests depending on ordering; better to have the test pass a log level down to whatever it constructs, or use a scoped handler.

But this is a nice-to-have, not urgent — the flaky failures are the thing costing us time. If someone picks up the logging cleanup, do it as its own change so it doesn't tangle with anything else in flight.

Wen: ping me on the redo branch when it's up, I'll look today.

### #24 · Tomás · Wed 2026-11-04 10:31

Pinned half the fleet to the old image (20261025.2) for 24h. If the old-image runners stay green and the new ones keep flaking, we have our answer.

### #25 · Ines · Wed 2026-11-04 10:35

Hi all, joining because Priya pinged me about the export golden diff. Some context on why I care more than the average person about a one-line reshuffle in that file.

My spreadsheet import is a separate repo (finance-tooling), but it consumes the monthly export as its input, once per month, via a scheduled job that pulls the file from the artifact store. It's not a live read — it's a snapshot file, so anything wrong in it is baked into my run. The importer parses the CSV, validates the header against a schema I keep checked in, then does a per-account reconciliation: it looks up each account row, compares `rows` and `net` against what my side computed from the raw statements, and writes a small exception report. If the account set or ordering in the file changes, or a row appears/disappears, my validation is strict — strict enough that the whole import aborts rather than half-loading. That's the paging: the job fails, the on-call rotation is mine and it's a 6am page, and the failure message is just a schema mismatch on line N, which tells me nothing about whether the data is wrong or just moved.

So two things I want out of this thread, in order: (1) is the *content* actually identical between passing and failing runs, i.e. is it purely a reorder, and (2) whatever the cause, can we get the export's row order to be stable enough that the golden test stops flapping, because every flap is potentially a page for me. I'm happy to relax my importer to sort on read — I probably should anyway — but I don't want to do that as a way of papering over a real data problem. If the rows are genuinely swapping because something upstream disagrees about ordering, I'd rather know.

### #26 · Priya · Wed 2026-11-04 10:58

Here are the two excerpts from the export. Same commit (main @ 91c3f0d), two different runs, no code change between them. I've cut out everything except the region where they differ — the rest of the file is byte-identical as far as I can tell, which is itself suspicious given how big the golden diff looked.

Failing run:
```csv
month,account,rows,net
2026-10,acct_4471,18,-214.05
2026-10,acct_2298,18,331.10
2026-10,acct_5503,7,0.00
2026-10,acct_1187,31,-1204.77
```

Passing run:
```csv
month,account,rows,net
2026-10,acct_2298,18,331.10
2026-10,acct_4471,18,-214.05
2026-10,acct_5503,7,0.00
2026-10,acct_1187,31,-1204.77
```

So acct_4471 and acct_2298 trade places. Note they both have `rows` = 18, which is the only thing that jumps out at me — the two rows that swap are the two with equal row counts in that block. acct_5503 and acct_1187 stay put. I can't yet tell you why they swap; I've diffed the surrounding lines and there's nothing else different. I don't want to read too much into the equal-count thing, it could be coincidence with n=2. Has anyone seen the export reorder anything else, or is it always rows like this? I'll keep grepping the failed-run artifacts.

### #27 · Wen · Wed 2026-11-04 11:15

Re the clock-change thing I raised on Tuesday — I know it got a bit of a shrug, but I want to put it back on the table briefly, because the export groups by month and that's exactly the kind of code where a date boundary bites. If the export is deciding which month a transaction belongs to by comparing local timestamps to a month boundary, then on the days right after the clocks went back a transaction stamped just after midnight could land in the previous month, or the reverse. That would move a row between month buckets, not swap two rows within a month, though — so it doesn't obviously explain Priya's excerpt. Unless the month grouping is fine and some *other* date-derived key is used for ordering within the month and that key lands on the boundary differently for the two runs.

What I'd check: is there anything in the export row that's derived from a timestamp without an explicit timezone? If the code does `datetime.fromtimestamp(...)` anywhere without a tz, it'll pick up the runner's local zone, and the runner image just changed tzdata per Tomás. That would be a genuinely new variable as of the weekend. I'm not saying it's the cause, just that it's the one thing that changed on the time axis this week. Happy to be told it's nonsense again.

### #28 · Ines · Wed 2026-11-04 11:31

Quick reply to Wen before this goes further: the swapped rows are mid-month, not near the boundary. acct_4471 and acct_2298 both have their rows well inside October — I pulled a couple of the underlying transactions for 4471 and the earliest is around the 6th, latest around the 27th. Nothing within a day or two of Oct 1 or Oct 31. So a month-boundary bucketing issue would not move these particular rows, and if a tz change were shifting things across the boundary I'd expect the counts to change too, not just the order. The `rows` value is the same in both runs (18), so nothing moved in or out of the month.

But to be fair to Wen's underlying concern: if the export is sensitive to local time at all, I do want to know, because my importer validates the month column and a wrong month is exactly the kind of thing that would silently reconcile against the wrong bucket on my side. So let's not drop the tz question entirely, just don't let it distract from the swap. The thing that's actually biting me is ordering. Two things would help me: confirm the row *content* is identical (I'm fairly sure it is from the excerpts, but I want someone to run a sorted diff rather than eyeballing), and tell me whether the golden test compares the file line-by-line or as parsed records — because if it's line-by-line, then it's testing ordering, which may or may not be something we actually promise to consumers. I should know whether I'm allowed to depend on it.

### #29 · Rafael · Wed 2026-11-04 11:52

Can answer the golden-test question: it's a straight file comparison, `assertEqual(expected_text, actual_text)` on the whole blob. So yes, it's absolutely testing ordering, and it'll fail on any permutation. That's been fine for years because the export happened to be stable, but nobody wrote down that it's a guarantee.

On the content question — I ran a sorted diff on the two artifacts Priya posted (sorted by month,account) and they're identical, every field. So this is purely a reorder, no data difference. That's the good news. The bad news is I still don't know what introduces the nondeterminism, and I don't want to guess in a public thread and have someone act on it. What I can say from a five-minute read: the export walks whatever it's handed per month and writes in that order, and I didn't immediately see a sort in the write path. If there was supposed to be one, either it isn't there or it isn't total — i.e. it leaves ties broken by input order, and Priya's two equal-`rows` accounts would be exactly such a tie. I'm not saying that's it, I haven't traced it, and I'd want to look at the actual code path before anyone changes anything.

For Ines's benefit: I would not treat the current ordering as a contract. If your importer depends on it, that's latent risk regardless of this bug. But I also don't think we should touch the write path mid-week without understanding it — if we sort and the bug turns out to be elsewhere, we've hidden it and it'll resurface somewhere worse, like the sync test.

### #30 · Priya · Wed 2026-11-04 12:14

More data, because the equal-`rows` theory now has a second data point and I don't trust coincidence with n=2.

I went back through the failed-run artifacts from yesterday and today and pulled every export diff I could find. Four of them. In all four, exactly one pair of adjacent rows swaps, and in all four the two swapped rows have identical `rows` values. One case was `rows`=3, one was 12, one 18 (the one above), one 40. So it's not specific to 18, but it does seem to be pairs with matching counts. In three of the four the `net` differed, in one it was also equal.

Caveat that I want to be honest about: I've only got four diffs and they're all from the same two days, so this could still be an artifact of what I happened to catch. And "same row count" is the kind of pattern that's easy to see once you're looking for it. But it's consistent enough that I'd bet on it being meaningful. I've added a note to the tracking list.

Separately, for Ines: I've started saving both artifacts whenever this fires, so if you want to diff the raw files yourself for your importer validation, they're under the flaky-export prefix in the CI bucket. Rafael's sorted-diff result matches mine — content identical. I'll keep collecting.

### #31 · Wen · Wed 2026-11-04 12:38

Thanks for the mid-month clarification Ines — I'll drop the clock thing for the export, though I'm keeping one eye on it for sync since that test is still in the list and it's the one that sorts. Not going to relitigate it.

On the equal-`rows` observation: I want to be careful here, because "rows" is a pretty coarse bucket. Lots of accounts will have the same count by chance, so if you only look at the diffs that fail, you'll see matching counts a lot even if it means nothing. The test I'd want is: of all the adjacent pairs in a normal export, how many have matching `rows`? If it's like half of them, the pattern is worthless. If it's a small fraction, then four-for-four is interesting. I can write that as a throwaway script against one of Priya's saved artifacts if nobody's already done it.

On the "is ordering a contract" question — for what it's worth, if my importer consumed this file I'd absolutely have assumed the order was stable, because it looks stable and nothing says otherwise. That's not an argument for keeping it, just an argument that we shouldn't be surprised Ines's tooling leaned on it. Whatever we do about the test, I think there's a separate, smaller question of whether we should tell downstream consumers what they can rely on. Not today, obviously.

### #32 · Priya · Wed 2026-11-04 13:20

New one, run #1046: `test_statement.StatementTest.test_header_same_day_by_name`. Header listed `travel, business` where the test wants `business, travel`; both accounts' last activity is the same day. Given the DST theory I'm filing this under the date stuff for now, not adding it to the flaky list until we know.

### #33 · Priya · Wed 2026-11-04 13:45

Separate theory I want to put on the table while Tomás' image comparison runs, because I don't think we should assume it's all clocks.

I was staring at the export failure from run #1043 again and noticed the temp dir. The test writes a scratch file and then reads it back, and the path in the traceback is under something like /tmp/tmp8x2kq0/. That's unittest's normal TemporaryDirectory, fine. But then I went looking for other tests that write into a tmpdir and there's at least one in test_sync that creates a scratch ledger file and a scratch export. Both of them clean up after themselves at teardown, so in a serial run it's harmless.

What I don't actually know is whether the modules are running concurrently on the new image. Tomás said the image bump included a newer CI agent and I have a vague memory of a line in the release notes about parallel job execution, but I didn't read it carefully and I might be inventing it. If two modules are running at once and something in the harness points both at the same TMPDIR, or if a test falls back to a fixed filename somewhere, that would explain a diff that's enormous and mostly noise, and it would explain why it only shows up sometimes.

I'm not claiming this replaces the DST angle. The statement header failure looks like a genuine same-day ordering thing and temp dirs don't explain that at all. But display_order and matches_golden are both 'lots of things moved, nothing obviously wrong' failures, and that smells more like contamination than like an hour of drift. If anyone knows offhand whether a test uses a hardcoded path instead of tmp_path, shout. Otherwise I'll grep for fixed names tonight.

### #34 · Rafael · Wed 2026-11-04 14:19

Had a look at the temp dir theory on the code side. Short version: the suite itself is serial and I'm fairly confident of that.

Everything goes through unittest, and the whole thing is one process. We don't use pytest-xdist or anything like it, there's no multiprocessing in the test package, and the runner class is plain `unittest.TextTestRunner`. `setUp`/`tearDown` on each TestCase wrap the individual test, and `setUpClass` if we had any would still be per-class, one at a time. So within a single invocation, test_export and test_sync are not running at the same moment. I checked the import of the test package too, in case someone was spawning threads for the 'slow' tests, and there's nothing.

What I can't rule out from the repo alone is the wrapper. Tomás owns that script and I don't have it in front of me, but if the agent is now sharding or running 'the test suite' as more than one command, then the serial guarantee only holds inside each shard. Two shards each running their own unittest process would absolutely be concurrent with each other, and if they share TMPDIR (which they would, unless the wrapper sets it per shard) then a test in shard A could be writing while a test in shard B reads.

So: code says no, harness says maybe. Tomás, is the new agent running the suite as one command or several? And does the wrapper set TMPDIR anywhere? If the answer is 'several' and 'no', Priya's theory is alive.

### #35 · Tomás · Wed 2026-11-04 15:02

Dug into the wrapper. Mixed findings, so bear with me.

First, the agent. The 20261101.1 image did bump the CI agent, and the agent does now support parallel jobs, but 'support' here means the scheduler can hand out more than one job to the same runner host. It does not mean one job's test command gets split. The command is still whatever we put in the config, and our config is one `python -m unittest discover ...` per job. Within a job, still serial. So Rafael's read of the code holds.

Second, the wrapper script (`ci/run_tests.sh`). It does not set TMPDIR. It does not shard. It does invoke the suite exactly once. But there's a wrinkle: it exports `TMPDIR=/var/tmp/ci` at the top, because the old image's /tmp was a tmpfs that got full on the big golden tests. So all jobs on a host share `/var/tmp/ci` as their temp root. Two jobs on the same host, at the same time, both running the export test, would be under the same parent directory. TemporaryDirectory names are random so collisions are unlikely, but 'unlikely' isn't 'impossible', and a leftover from a killed job would sit there forever.

So the picture is: no, one job doesn't run two modules at once. But yes, the new agent can put two jobs on one host, and yes, they share a temp root now. That's a much narrower window than 'the modules run in parallel', but it's not zero. I'll check how often the scheduler actually co-locates jobs this week.

### #36 · Wen · Wed 2026-11-04 15:41

Tried to reproduce the co-location thing locally, on the theory that if it's a shared temp root I can force it. Ran test_export and test_sync at the same time in two shells, both with TMPDIR pointing at the same scratch directory, a few times.

Got one failure on the third or fourth attempt:

```
FAIL: test_matches_golden (test_export.ExportTest.test_matches_golden)
- month,account,amount
- 2026-09,checking,-412.00
+ month,account,amount
+ 2026-09,checking,-412.01
... (about 200 more lines)
```

That's the same shape as the CI diff: a fraction of a cent, then everything downstream shifts. But I could not get it again. I ran the pair maybe a dozen more times and it was green every time. I also don't have a clean explanation for where the .01 comes from in a temp file collision, since the temp files aren't supposed to hold the amounts that early.

So I'm reporting it as 'got it once, can't reproduce' rather than as evidence. It's entirely possible the one failure was something else, or that I contaminated my own scratch dir from an earlier run. Not going to claim it proves anything. If someone wants the exact commands I ran I'll paste them, but don't build on this yet.

### #37 · Priya · Wed 2026-11-04 16:08

Wen, that's still useful even if it's one hit. The .01 is the interesting part. In the CI failures I've looked at, the export diff is always 'a small delta at one row, then a cascade', so if your local one had the same shape, the mechanism might be the same even if the trigger was different.

On the co-location window: Tomás, if two jobs share /var/tmp/ci, what actually gets written there? I want to check whether the export test's temp files could be read by the sync test. From what I can see, the export test writes its scratch output and reads it back within the same test, so even a collision would have to be very unlucky to land between the write and the read. That makes me less confident, not more. Unless there's cleanup that deletes more than its own directory, which would be a real bug and would explain a lot.

Also worth saying out loud: this theory and the DST one aren't mutually exclusive, and I don't want us to drop one because the other is getting more interesting. The statement header failure is still sitting there unexplained and it's a date thing. I'm keeping both open.

Concrete ask: Tomás, can you pull the job-to-host assignment for the failed runs (#1043, #1046, and the two from Sunday) and tell me whether any of them shared a host? If they were all on different hosts, the co-location window is closed for those specific failures and we can stop pulling on this thread.

### #38 · Tomás · Wed 2026-11-04 16:52

Pulled the assignment history.

For the two Sunday failures: different hosts, no overlap in time. For #1046 (the statement header one): different host from everything else. For #1043 (the export one): it shared a host with a job from another repo entirely, which ran a different test suite. So: our export test and our sync test were never on the same host at the same time in any of the failures I can see.

That mostly closes the door on 'two of our jobs collided', but it doesn't close the temp dir theory entirely, because the other repo's job also runs under the same wrapper conventions and also gets `/var/tmp/ci`. If that job leaves something behind, or if it cleans `/var/tmp/ci/*`, our export test could be affected without another of our tests being involved at all. I don't know what that job does with temp files and I'm not going to guess.

So my honest read: co-location of our own tests, ruled out for the observed failures. Shared temp root with foreign jobs, still theoretically possible, unproven. I'd rather not spend more runner time chasing it until we have a failure where we can capture the temp dir contents. If we get another flake I can add a step that tars up /var/tmp/ci before cleanup, but that's a config change and I'd want a second pair of eyes on it.

### #39 · Rafael · Wed 2026-11-04 17:24

One more thing on the code side that I should have checked earlier: the export test does not set its own TMPDIR, it just uses TemporaryDirectory, so it inherits whatever the wrapper sets. Confirmed. And I grepped the whole test tree for fixed filenames — strings like 'export.csv', 'output.json', anything without a temp dir prefix — and found two:

```
test_fixtures.py:  open('fixtures/ledger_sample.json')
test_export.py:    ... and one place that writes 'golden_actual.csv' next to the test file
```

The first is read-only and points at a checked-in fixture, so it's fine. The second is the one that matters: the export test writes `golden_actual.csv` relative to the working directory, not in its temp dir. If two processes run with the same cwd, they fight over that file. In a serial single-process run they don't. In a sharded or co-located run they would.

But Tomás says our jobs weren't co-located, so this file only bites if something else is in that directory, and I don't think the foreign job shares our checkout. So it's a real smell — a test writing into the source tree instead of a temp dir — but it might not be *the* cause. I can move it into a TemporaryDirectory as a small cleanup regardless, it's a one-line change and it removes a variable. Won't do it without a nod though, since it's test code people are actively debugging.

### #40 · Wen · Wed 2026-11-04 18:05

Tried the co-location repro once more before I wrap up, this time copying Rafael's point: two shells, same cwd, both pointed at the same TMPDIR, both running the export test (not export + sync). Ran it eight times. Zero failures. Also ran export + sync in the same cwd, which is what I did before, four more times. Green.

So I'm at one failure in roughly twenty-five attempts and no reliable recipe. I don't think I can hand anyone a repro. If the `golden_actual.csv` thing is real, it might need more precise timing than I can hit by hand with two shells.

Where I'd leave it: the temp dir theory isn't dead, but I can't make it fire on demand, and the host data says our own jobs never overlapped. The one thing that would settle it is capturing the temp dir from a real flake, which Tomás offered to wire up. I'd take him up on that rather than keep guessing locally. Meanwhile I'll write up what I tried in the thread so it's not lost, and I'm not touching test_export.py in case someone else is mid-edit.

### #41 · Tomás · Wed 2026-11-04 18:22

Honest answer on the temp dir thing: the wrapper doesn't parallelise anything, it just tees output. Wen's one local failure was `test_display_order` with nothing else running at the time, so I don't think it's sharing either.

### #42 · Tomás · Wed 2026-11-04 18:30

Separately, the shortest route might be to just make ACCOUNTS a sorted list in generated/registry.py so everything that walks it gets a stable order. One-line change. Objections?

### #43 · Marta · Thu 2026-11-05 08:05

Objection, sorry. Please don't edit generated/. schema-gen regenerates it nightly from accounts.schema.json and overwrites hand edits, so a fix there disappears the next morning and nobody notices until it flakes again. schema-gen 4.3 (January) will emit the accounts as a tuple in sorted order, which would make this moot, but it's not out and I can't backport it. Until then, whatever ordering you need has to live in your code, not ours.

### #44 · Tomás · Thu 2026-11-05 08:20

Results of the image pin: both pools flaked. Old image run #1048 failed `test_matches_golden`, new image run #1049 passed. So it isn't the image, or not only. Unpinning.

### #45 · Rafael · Thu 2026-11-05 08:35

Good to know it's not the image, but annoying — that was the cheapest explanation on the board. So we've got two pools with different Python patches, different tzdata, different git, and both of them flake the same tests. That points at something in the code or the fixtures rather than the environment, at least for the ones on Priya's list. Though I'd hold off declaring anything until we've got a couple more data points, one failure each on old and new isn't a lot to go on and we've all seen a flake go quiet for a week and then come back.

### #46 · Wen · Thu 2026-11-05 08:52

Quick question on the pin result — does it actually rule out the tzdata/DST thing? My reasoning: if the old image really does carry the pre-bump tzdata, then the old-image runners had the old zone files and the new-image runners had the new ones, and both flaked. That would mean the tzdata version isn't the thing making the difference. But I'm not confident I've got that right, because I don't know whether the tzdata in the image is what Python actually picks up at runtime or whether something in the venv shadows it, and I also don't know if the old image's tzdata is actually old or was already bumped before 20261025.2. If both images shipped the same tzdata then the pin tells us nothing about DST either way. Can someone who knows the image contents confirm? I don't want to keep pushing the date theory if the experiment already killed it.

### #47 · Tomás · Thu 2026-11-05 09:06

Fair question. The old image (20261025.2) has the old tzdata — I checked the package list on both tags before I pinned, that was the whole point of choosing that tag rather than just the previous patch. New image bumped tzdata to 2026b, old one is on 2026a. And no, nothing in the venv shadows it; we install no tz packages, the image's zoneinfo is what gets used, I've verified that before for a different reason.

So: old tzdata flaked, new tzdata flaked. That makes the DST-via-tzdata story unlikely for the sync/export tests. I want to be careful though — it doesn't exclude date code being involved. The zone rules aren't the only way a date can come out wrong; if something is computing a local time from a UTC timestamp, or formatting a date without a zone, or comparing a naive and an aware datetime, the tzdata version may genuinely not matter and it'd still be wrong on both images. So I'd say the tzdata bump is off the table as the trigger, date handling is not off the table as the mechanism. If Wen or anyone wants to keep pulling that thread I'd keep it to 'what does this code do with dates' and not 'which tzdata version is it'.

### #48 · Ines · Thu 2026-11-05 09:24

Jumping in from the finance side because I've been watching this thread and I want to put one requirement on the record before anyone changes anything.

Whatever the fix turns out to be, the monthly export has to stay byte-identical between two runs over the same feed. Not 'same content', not 'same rows in a different order' — identical bytes. My import job diffs each new export against the previous month's and alerts the whole finance team if anything at all changed, and it does that on the raw file, so a reordered line or a reordered column reads as a change.

Why I care: last quarter we had a false alert that cost me most of a day. An export came through where two rows had swapped order compared to the prior month, nothing else different, no amounts changed, no balances moved. My diff lit up, I escalated because a change in the ledger export usually means a change in the books, and two people spent a morning reconciling before we worked out the file was just laid out differently. The numbers were fine. The alert was noise. But at the time nobody could tell me it was noise, because from the import's side a reordered export and a genuine restatement look the same.

So if the thing being fixed is ordering inside the export, please make sure the order is the same every run, and ideally the same as it's been, because a one-time reshuffle will trigger exactly that alert once and I'll have to explain it. If the order has to change I'd rather know in advance than find out from the diff. Happy to test an export against last month's file if that helps.

### #49 · Priya · Thu 2026-11-05 09:41

Thanks Marta — genuinely, that saved us. My instinct when Tomás suggested the one-liner was that it'd work, and I'd probably have started testing against a hand-edited registry this afternoon and felt good about it. Then the nightly regen would have quietly undone it and we'd have been chasing the same flakes again next week with no idea why the fix 'stopped working'. That's a miserable class of bug.

Noted on the January schema-gen release too — good to know sorted accounts are coming, but we can't wait for it and we can't depend on it landing on time. So whatever we do now has to work with the generator producing what it produces today.

For my part I'll keep the list clean: display_order and matches_golden are the two confirmed flaky, header_same_day_by_name is still filed under 'date stuff, not yet known to be flaky', and I'll keep posting run numbers here. If anyone wants me to run the same test repeatedly against one fixed feed to see how often it flips, say the word — that's cheap on my side and might tell us whether these are the same underlying thing or two separate ones.

### #50 · Marta · Thu 2026-11-05 10:12

No thanks needed, but appreciated. I'd rather say no early than have you all lose a week to a vanishing fix. Two things to add from my side so it's in the thread.

First, for anyone tempted by a middle path: there's no supported way to have schema-gen skip the file, preserve a hand edit, or emit in a particular order today. The generator writes registry.py wholesale from the schema, and the schema doesn't carry an order field yet. Editing the schema won't help either — the ordering has to come from somewhere in the generating code, and that's the January work.

Second, if any of you do end up needing something from generated/ that isn't there, tell me what and why rather than patching it locally. I keep a list of these asks and it's useful when I'm arguing for scope. 'Ordering' just got a lot easier to argue, for obvious reasons.

One thing I can't tell from the outside: whether the order registry.py comes out in today is actually unstable between regenerations, or stable but just not sorted. Those are different problems and I don't want to guess. If someone can diff generated/registry.py across two nights of regen and paste it here I'd be interested, and it might settle whether the export flakiness has anything to do with us at all.

### #51 · Dana · Thu 2026-11-05 11:15

Catching up. Whatever the root cause turns out to be, the symptom in display_order and the export is ties being broken in an order nobody chose. Let's not wait on the root cause to stop the bleeding.

**Decision:** each module that walks the registry breaks ties by account name at the point of use: `sorted(ACCOUNTS)` where it builds the list, or name as a secondary sort key. Five small diffs, one per module, reviewed together. Wen takes it. Ground rules: nothing under generated/ (see Marta), and don't touch the tests or the golden file; if a test needs changing to pass, the fix is wrong.

### #52 · Rafael · Thu 2026-11-05 11:52

Alternative before Wen starts, then I'll shut up. Instead of five point fixes, one place: a new `ledger/accounts.py` with `ordered()` returning `tuple(sorted(ACCOUNTS))`, and every ledger module imports that instead of the registry's ACCOUNTS. After the change nothing else in ledger/ mentions ACCOUNTS at all; only accounts.py imports it from generated.

Two reasons. When schema-gen 4.3 lands, we change one line instead of five. And the next module someone writes can't quietly reintroduce the problem by iterating the registry directly, which is exactly how we got five of these. I'd even add a test that fails if any other ledger file mentions ACCOUNTS.

### #53 · Dana · Thu 2026-11-05 12:10

Noted, and I don't disagree in principle, but let's not gold-plate a flake fix. The five-line version is fine for now. Wen, go with what I wrote above.

### #54 · Wen · Thu 2026-11-05 12:34

Lunch-break-adjacent question, and it's a bit of a newcomer one, so bear with me: why is ACCOUNTS a set in the first place? I read the generated file this morning for the first time and it's literally `ACCOUNTS = {"checking", "savings", ...}`. I get that a set is the natural shape if all you care about is membership, but every consumer I've looked at (display_order, the export, the statement header) walks it in some order. If nobody ever wanted set semantics, why did schema-gen pick it?

### #55 · Marta · Thu 2026-11-05 12:58

Historical accident, mostly, and I can give you the timeline since I've been on schema-gen longer than anyone here.

When we started writing the generator (v2, which is ancient, well before my time on the team but the commit history is still there), the only requirement in accounts.schema.json was uniqueness: two accounts with the same name is data corruption, an account that exists is valid, an account that doesn't exist isn't. A set expresses exactly that and nothing else, and it's what the schema's `uniqueItems` constraint maps onto most directly. So v2 emitted sets, and nobody pushed back because at the time there was basically one consumer and it did `name in ACCOUNTS` and never iterated.

Then over the years modules appeared that wanted to list accounts, and the set kept getting away with it because Python's set literal with string elements happens to iterate in a consistent order within a process. So it looked fine in dev, looked fine locally, looked fine in CI most days. It was never a promise, it was just an observation that held often enough that nobody questioned it.

With hindsight, a tuple in sorted order (or even a dict keyed by name) would have been the better call from v2, because "unique" and "ordered" aren't in tension the way people assume. But the schema's only stated constraint was uniqueness, so that's what got emitted. 4.3 will change the emitted type, as I said earlier, but I can't backport it and I'm not going to hand-patch generated/ in the meantime.

### #56 · Wen · Thu 2026-11-05 13:07

That makes sense, thanks. The "looked fine because it happened to iterate consistently" bit is the part that would have gotten me. I'd have written the same code and felt fine about it.

Separate thing while we're on generated/: I went looking for how the golden export file gets made and there's no script. `tests/golden/export_2026_09.csv` (and the two before it) were, as far as I can tell, created by running the export by hand and copy-pasting the output into the file. Is that right? Because that seems like exactly the kind of thing a `make golden` target should do. Regenerate from a known fixture set, diff, commit if it looks sane. Am I missing a script somewhere, or is it really by hand?

### #57 · Priya · Thu 2026-11-05 13:41

By hand, yes. And I'd like to keep it that way, so let me make the case before everyone piles on.

The golden file is the test's specification of what the export *should* look like, not a recording of what it *does* look like. The moment regenerating it is one command, it stops being a specification and becomes a snapshot. Someone changes the export, the test goes red, they run `make golden`, the test goes green, and the diff in the PR is a 400-line CSV that reviewers scroll past. We've all seen that pattern in other repos. The friction is the feature: if updating the golden file is annoying, you only do it when you actually mean to change the output format.

And there's a concrete reason for this particular file. The export is what Ines's import reads. If the export changes shape, her importer breaks, and the only thing standing between a careless export change and a broken finance import is a human looking at the golden diff and going "wait, why did this column move?". A regenerated-by-script golden file makes that review step optional.

What I'd be fine with: a script that *renders* the candidate output to a scratch file and prints a diff against the golden, so you can eyeball it. What I don't want is a script that writes the golden file directly. The last human step is the point.

(Also, for what it's worth, the golden files are small. Three months, a few dozen rows each. Hand-maintaining them isn't actually a burden yet.)

### #58 · Ines · Thu 2026-11-05 14:12

Jumping in on the export side since Priya mentioned my importer, and because I want the constraints written down somewhere other than my head.

The importer reads the monthly export CSV and it only looks at four columns: month, account, rows, net. That's it. `month` is the `YYYY-MM` bucket, `account` is the account name as it appears in the export, `rows` is the count of ledger entries that landed in that bucket for that account, and `net` is the sum (signed, expenses negative) for that bucket. Everything else in the export — the totals row, the header ordering, any of the extra columns — gets ignored on read.

That's the good news: the importer is tolerant of column order and tolerant of extra columns, so a lot of what would break a stricter reader doesn't break it. The bad news: it's completely intolerant of row-order changes for the same (month, account) pair, because it builds a dict keyed on those two and last-write-wins on duplicate keys, and it's intolerant of any change to the number formatting in `net` (it parses with a fixed pattern, doesn't accept thousands separators it didn't produce). Also `rows` has to be an integer or it silently treats the row as malformed and skips it, which is the kind of thing nobody notices for a month.

So when the export changes, the things I care about are: does a (month, account) pair ever appear twice, and did the `net` formatting move. The golden file diff review catches both of those if someone actually reads it, which is Priya's point and I agree with it. If anyone ever does put a regeneration script together, please have it refuse to write if the row count by (month, account) differs from the current golden. That's the check I'd want.

### #59 · Rafael · Thu 2026-11-05 15:03

On Ines's last point — I think that check is doable as a standalone, and it doesn't require deciding anything about regeneration. Something like:

```python
def check_golden_shape(old_csv, new_csv):
    def keys(path):
        with open(path) as f:
            return sorted((r["month"], r["account"]) for r in csv.DictReader(f))
    if keys(old_csv) != keys(new_csv):
        sys.exit("row keys differ from current golden; refusing")
```

Run it on the scratch output before a human copies anything over. It doesn't write the golden, it just fails loudly if the set of (month, account) pairs moved, which is the thing Ines's dict would choke on.

Not volunteering to build it this week, to be clear. There's enough in flight. But if Priya's okay with the shape of it, it's a half-hour job for whoever picks it up and it doesn't touch the golden files themselves.

(One caveat: it assumes the export has a real header row and DictReader picks up the column names correctly. Worth checking against the three existing goldens before anyone relies on it.)

### #60 · Priya · Thu 2026-11-05 15:38

Rafael, that's fine by me and it's basically the "render and diff, human commits" shape I described, just with more teeth. The key property is that it never writes the golden file; if it does, I'll object then.

One adjustment: rather than sys.exit on mismatch, print the pairs that appeared and disappeared and exit nonzero. When it does fire, the first question is always "what changed", and a bare "row keys differ" means I go digging. Showing me `2026-09 / travel` vanished and `2026-09 / business` appeared tells me in one line that an account got renamed or a bucket moved, which is usually the actual cause.

On the header-row caveat: all three goldens have a header, I checked just now. Column names are `month,account,rows,net` plus the two extra columns the export adds. So DictReader is fine.

And to be clear about what I'm not saying: I'm not saying the golden file is sacred and can never change. It changes when the export changes on purpose, and that's a reviewed PR like anything else. I just want the change to be a thing someone chose, not a thing a script did at 11pm.

Ines — the duplicate-key and number-format notes are useful, I'm going to paste them into the test file's docstring so they're not just in this thread. Shout if you'd rather I didn't quote you.

### #61 · Dana · Thu 2026-11-05 17:10

While the tie-break diffs are in review, let's settle the 0.9 scope here rather than spawning another thread. What I want in:

- `report` CLI gains `--json`, `--category` and `--since`. The first two are Rafael's and are already on main behind nothing, so they're free.
- The `--since` redo. The revert of 4e1c9a2 put us back on the old behaviour, which has the boundary bug Priya found, and I don't want to ship 0.9 with a known off-by-one in the one date filter people will actually use. Rafael, is the redo close?
- The boundary test that goes with it. Priya, I'd like that written against the spec, not against whatever Rafael's branch happens to do, so we catch it if the redo drifts.

Everything else waits for 0.10. That includes the statement header question from #1046: I don't want us guessing at the ordering rule for same-day accounts while the tie-break diffs are still in flight. If the fix happens to make it go away, great, but I'm not putting it in the scope list and I'm not blocking the release on it.

Timing-wise I'd like to tag late next week. That's soft. Tomás has opinions, I'm sure.

### #62 · Rafael · Thu 2026-11-05 18:02

The --since redo is close. What I'm doing differently this time: the filter takes an explicit inclusive lower bound and I've stopped deriving it from a formatted date string, which is where the off-by-one crept in. The old code did roughly:

```python
def in_range(txn, since):
    return txn.date >= since
```

...except `since` was being parsed and re-formatted through a couple of helpers on the way in, and on the boundary day the round trip landed a day late. The new version keeps the date object the whole way and compares against the start of that day. I've got the obvious cases passing locally.

What I don't have is a decision on what `--since` means for a transaction dated exactly on the boundary. I've been assuming inclusive. Everything I've read of the docs suggests inclusive, and it matches what the statement code does. If anyone thinks it should be exclusive, now is the time, because it changes the test Priya's writing.

Also, small thing: `--json` and `--category` interact with `--since` in ways I haven't tested together. If Priya's boundary test could run through `--json` as well as the plain output, that would cover the combination cheaply.

### #63 · Wen · Thu 2026-11-05 19:35

Read through the five modules this afternoon to get a feel for them before I start; I'll pick it up properly tomorrow. Looping the three known flaky tests locally, 200 iterations each, I got two failures of display_order and nothing else, so tomorrow I'll at least have a way to see it go red.

Unrelated and possibly premature: what's the changelog format for 0.9? I looked for a CHANGELOG at the repo root and didn't find one, and the release notes for 0.8 seem to have been written by hand in the tag message. Is that the pattern, or is there a file I'm missing? I ask because the three `report` options are user-facing and I'd rather write the entries as the code lands than reconstruct them from git log next week. If the format is freeform I'll match 0.8's tone; if there's a template somewhere point me at it.

### #64 · Priya · Thu 2026-11-05 21:14

On the boundary test: yes, I'll write it from the spec. I've read the `--since` paragraph in the CLI docs and it says 'transactions on or after the given date', so inclusive it is unless someone tells me the docs are wrong. I'll cover plain output and `--json`, plus one case where `--since` and `--category` are both set, since Rafael flagged that combination.

Separate request, and I'd like an answer before the weekend: can we freeze main on Monday? Not forever, just from Monday morning until the tag. Every time I've built a release test pass on a Monday the tree has moved under me twice before lunch and I end up re-running the suite against a different commit than the one I signed off. A couple of days of only release-relevant merges would make the sign-off mean something. If Monday is too early, Wednesday works, but I'd like something on the calendar rather than 'when it looks ready'.

### #65 · Tomás · Fri 2026-11-06 07:48

On the release timing, I'd like us to hold the tag until CI has been green for two days in a row on main. Not 'no red runs', actual consecutive green days, no reruns needed.

Why: the tie-break PR might well fix display_order and matches_golden, and I hope it does, but we don't know that yet, and we definitely don't know that nothing else is lurking. The image pin experiment came back 'both pools flake', which means we still don't have a root cause for at least some of what we've seen. Tagging 0.9 into that is how we end up shipping a release note that says 'fixed flaky tests' when what we did was make two of them stop failing for reasons we can't fully explain. I'd rather eat a week.

On the freeze: I'm fine with Monday for merges, but it should be merges to main, not to the release branch, and CI config changes should still be allowed or we can't fix a red runner on the day. If we're freezing, I want the ability to land a CI-only change under it. Otherwise a broken runner on Tuesday blocks the whole thing and we're arguing about an exemption at the worst possible moment.

Also, if we're doing the two-green-days thing, somebody needs to actually watch it. I can put a job on the dashboard that tracks consecutive green days on main and posts when the count resets, so it's not me squinting at the runs page every morning.

### #66 · Marta · Fri 2026-11-06 08:21

Quick one on changelog, since Wen asked: there's no CHANGELOG file in ledger, and the 0.8 notes were indeed hand-written in the tag. I know because I wrote half of them. The pattern that worked was one bullet per user-visible change, no internal refactors, no 'various fixes'. If the tie-break fixes change output for anyone in a way they'd notice, they probably deserve a line even though they're internal, because the export diff moving is the kind of thing Ines will get asked about. If they don't change anything anyone can see, leave them out. That's my two cents, it's Dana's call what goes in.

On the freeze request: from my side the only thing landing from schema-gen is the nightly regeneration, which doesn't touch ledger code, so a Monday freeze costs me nothing. Just don't read the nightly commit as someone jumping the freeze.

### #67 · Dana · Fri 2026-11-06 08:50

Good discussion, and I'm not going to pretend it's settled.

Where I am: the scope list from yesterday stands, `--since` inclusive per the docs, and Priya writes the boundary test from the docs text rather than from Rafael's branch. Changelog is hand-written in the tag like 0.8, one bullet per user-visible change, Wen drafts it and I'll review. Marta's point about the tie-break lines is fair, we can settle that when we see whether the export diff actually moves.

On timing we have three positions in the room. Priya wants the freeze Monday and a tag that means something. Tomás wants two consecutive green days before the tag, and a CI-only exemption to the freeze so a broken runner doesn't strand us. I wanted to tag late next week. Those aren't compatible as stated and I don't have a clean answer this morning. What I'll say is: the freeze, if we do it, is on merges to main with a CI-only exemption, and the two-green-days bar is a reasonable thing to ask for but it's a bar on a thing that's currently failing most days, so it has a real cost attached.

Let's pick this up Monday morning with the tie-break PR reviewed and the boundary test in hand. If by then the loop has been green over the weekend, the gap between the positions narrows a lot. Tomás, go ahead and build the consecutive-green-days job either way, it's useful regardless of what we land on.

### #68 · Rafael · Fri 2026-11-06 09:05

I think I have the cause, and it isn't time or the image. ACCOUNTS is a Python set of strings. String hashing is randomised per process unless PYTHONHASHSEED is fixed, so the set's iteration order changes from one run to the next. Anything that breaks a tie by "whatever order the set gave me" is a coin flip per CI run.

How I checked: same commit, ran the suite 40 times with the seed pinned to 0..39. display_order and matches_golden fail on exactly the same seeds every time I repeat it, and pass on all 40 when I put a `sorted()` around the registry in a scratch copy. With the variable unset they fail at roughly the rate CI sees. Nothing date-related changes the outcome: I also ran with TZ set to three different zones and it made no difference.

### #69 · Priya · Fri 2026-11-06 09:40

That would explain the statement header too: business and travel tie on last-activity date and the header falls back to set order. Moving `test_header_same_day_by_name` onto the flaky list, and taking it off the DST pile. Wen, sorry, I think DST is a red herring after all.

### #70 · Wen · Fri 2026-11-06 10:04

Rafael, that's a good find, and thanks for the seed sweep, that's the kind of evidence I didn't have. One thing I still don't get though: if it's been randomised per process the whole time, why did it only start biting us this week? We've had CI on this repo for months. Did something change in how the suite runs, or did we just get lucky for a long time and the luck ran out?

Asking because I'm about to start on the five diffs Dana described and I want to be sure I understand what I'm actually fixing. If the answer is "we were always one coin flip from this and the coin finally landed," fine, I'd just rather know that than assume some recent change caused it. I'd also like to be able to say something sensible when someone asks in standup why our flake rate went from roughly zero to several a week overnight.

### #71 · Rafael · Fri 2026-11-06 10:31

Fair question, and I don't have the full answer yet, but I have a strong suspicion. Ties were always possible, they were just rare. Two accounts only collide in these tests when they tie on whatever the sort key is: same total in the export grouping, same last-activity date in the statement header, same display ordering key in sync. For months the fixture data had no ties, or at most one elsewhere, so the set order never got consulted and the tests passed regardless of seed. If nothing ties, set order is invisible.

What I think changed: the feed picked up two new accounts in late October. I noticed while looking at the scratch copy, the account list is noticeably longer than what I remember from the summer. If those two happen to tie with existing accounts on the keys these tests exercise, then from the day they landed every run is a coin flip instead of a rare one. That would line up with the timing far better than the image roll or DST, both of which we've now mostly ruled out.

I'm going to check when the accounts appeared. If it's late October, that's the story and it's satisfyingly boring: the bug was always there, the data changed, the bug became visible. Which is also a reason not to treat this as "fixed, move on" without the point fixes actually covering every place a tie can be consulted.

### #72 · Tomás · Fri 2026-11-06 11:02

Confirming the timing from the schema side, since I pulled the last few months of account changes when I was looking at whether the image roll could be responsible. Two accounts were added to accounts.schema.json in the 25 October change: one of them lands on the same monthly total as an existing account, and the other ties on last-activity date with business. So Rafael's suspicion looks right. Before that change the fixture had no meaningful ties and the tests couldn't see the set order at all; after it, three different tests hit ties on a regular basis. The flake onset is the data change, not the runner.

On the CI environment side, to close that off: our runner jobs get a fixed set of variables from the job template plus whatever the repo defines, and I can read all of it from the job config. PYTHONHASHSEED is not set anywhere in the pipeline, not in the template, not in the repo config, not in the wrapper I wrote. So every test process gets its own random seed, which is exactly the behaviour Rafael reproduced locally. I can set it globally as a stopgap if people want the noise down while Wen's diffs land, but I'd rather not make CI depend on a variable that only hides the class of bug. Say the word if you want it anyway.

One note for whoever greps logs later: the runner doesn't print the seed, so we can't map a CI failure to a specific seed after the fact. The per-run outcome is all we get.

### #73 · Ines · Fri 2026-11-06 11:44

Sorry to come back to this, and I know it's not the main thread, but I asked about this before and I want to pin it down now that we know the cause. The monthly export that ledger produces is what my spreadsheet import reads. If the account order inside that export changes from run to run, my import may see a different column or row order for the same month, and my reconciliation diffs will churn for no reason. Two exports of the same month should be byte-identical for the import to be stable.

So my question: once Wen's changes land, is the export going to be stable between runs on the same data? I don't need it stable across data changes, obviously, just byte-identical for the same input. If it isn't, I need to know soon because I'll have to make the import order-insensitive on my side, and that's a chunk of work I'd rather schedule than discover. If someone can just tell me yes or no after the fix, I'll stop asking.

### #74 · Priya · Fri 2026-11-06 12:20

Given what Rafael described, I want to know how many other tests could be affected, not just the three we've seen fail. The ones we know about are display_order, matches_golden and header_same_day_by_name. But any test that walks the registry and relies on order, or that compares a structure built from it, could be sitting on the same coin flip and just hasn't lost yet because the fixture ties are only in a few places.

Plan: over the weekend I'll grep the CI history for every test that has failed at least once on main in the last couple of months, and cross-reference against which ones touch the registry or read the export. If a test has never failed, it may still be exposed, so I'll also note which ones could theoretically tie. I'll post a list Monday morning so we know whether the five diffs cover everything or whether there are more waiting to bite.

Wen, if it helps, I can send you the list of test names that reference the registry before Monday, so you can sanity check your diffs against it. No promises on completeness, it's a grep not an audit.

### #75 · Rafael · Fri 2026-11-06 13:15

Ines, on the export: I can't promise byte-identical yet, but I can tell you what to expect from the change and what to check. The export builds its rows by grouping accounts and then emitting them in whatever order they come out of the registry walk. Once Wen's diff puts a name-based tie-break at the point where the rows are built, two runs on the same input should produce the same order, so the file should come out the same both times. The risk is a place in the export path that doesn't go through that one sort: if a dict or a set is built somewhere else and iterated, the order there can still vary even if the main list is stable. I'll look at the export code path specifically once the diffs are up and tell you whether I think it's fully covered.

Practical suggestion in the meantime: run the export twice on the same month and diff the two files. If they match, good sign; if they don't, that's exactly the kind of thing you want to catch before your import chokes on it. I'd do the same check after the fix lands rather than take my word for it.

### #76 · Tomás · Fri 2026-11-06 14:48

Two small things while people are thinking about this. First, Priya's grep over the weekend is a good idea and I can make it easier: the job logs are retained for 90 days, and every failed test run on main is tagged with its commit and the test name in the summary line, so it's a clean search rather than scrolling. I'll send you the exact log query I use, it's shorter than it looks.

Second, my offer from earlier stands: I can pin PYTHONHASHSEED in the job template as a stopgap so CI stops flaking while Wen works. I know the argument against it, that it hides the class of bug rather than fixing it, and I don't want to relitigate that. But if the flake rate is costing people half their Mondays, a temporary pin buys quiet. It's a two-line change to the template and I can revert it the day the diffs are in. If nobody wants it, no problem, I'll leave the template alone.

Either way I'll keep the log retention note in the CI docs so the next person knows where to look when a test fails once and then passes.

### #77 · Priya · Mon 2026-11-09 08:50

Weekend CI history: one more, `test_limits.LimitsTest.test_worst_offender_tie_named_by_name` (runs #1050 and #1053). Two accounts equally over their limit, alert named the wrong one. Same family. Adding it.

So the flaky list is now: display_order, matches_golden, header_same_day_by_name, worst_offender_tie_named_by_name.

### #78 · Dana · Mon 2026-11-09 09:14

Morning. Monday status thread since the CI thread is getting long.

Where we stand from my side: Priya has four tests on the flaky list (display_order, matches_golden, header_same_day_by_name, worst_offender_tie_named_by_name), Rafael has a convincing explanation for why they flake, and Wen has the fix work. I want a short update from each of you here rather than scrolling the other thread. Specifically: Wen, has anything landed; Tomás, anything on the runner side I should know about before the week gets busy; Priya, anything new over the weekend beyond the two runs you posted.

Also a heads-up that I'm in hiring debriefs most of Tuesday and Wednesday afternoon, so if something needs a call from me, morning is better.

### #79 · Wen · Mon 2026-11-09 09:41

Honest update: I haven't started. I'm on call this week and Saturday night into Sunday was the payments-batch incident, so I've been doing follow-ups since. Short version for anyone who missed it: the batch job that reconciles card settlements got stuck retrying against a downstream endpoint that was returning 503s, the retry loop had no overall deadline, and it held a DB connection per attempt. By 2am the pool was exhausted and the settlement job for Sunday was four hours behind. We drained it by hand, bumped the pool size temporarily, and the Sunday batch caught up by about 7am. Nothing to do with ledger, different service, but it ate my weekend and this morning.

The on-call rota has me until Friday morning. I can do the five module diffs in small chunks between pages, but I'd rather not promise a clean afternoon. My plan if nobody objects: start with sync (that's display_order), then export, then statement, then limits, then report, roughly in that order, each one its own branch so a page doesn't leave a half-done module sitting around. If that's too slow, say so and we can talk about handing it to someone else for the week.

### #80 · Tomás · Mon 2026-11-09 10:22

Runner side is quiet, no image rolls planned this week. But since we now know it's per-process string ordering, I want to put one option on the table as a stopgap, separate from Wen's fix.

We can set the interpreter's randomisation variable to a fixed value in the CI environment (the one that controls string hashing). One line in the job config, applies to every test process, no code change at all. Rafael's 40-seed run shows the failures are deterministic per value, so pinning it to a value that happens to be green would stop the noise on main today. It would also make the failure reproducible for anyone who sets the same value locally, which is better than what we have now.

Downsides as I see them: it's an environment difference between CI and production, it papers over four tests that are telling us something real, and if we ever add a test that genuinely depends on ordering we'd be training ourselves to trust a green that means less than it looks. I'm not attached to it. If people would rather keep main red while Wen works through the modules, that's also fine, I just don't want us to default into it without discussing it. Cost is about five minutes either way.

### #81 · Priya · Mon 2026-11-09 11:03

On Tomás's stopgap: please don't. I get the appeal, main has been red most of a week and I'm the one triaging it, but pinning the variable in CI means CI stops reproducing what users see. Our users run the ledger in whatever interpreter process they get, with randomised hashing on, so the tie-breaking bug is live for them every single run, not one in ten. If we make CI deterministic we've made the one place that catches it into the one place that can't.

It also changes what green means for every other test in the suite, not just these four. I'd have to go back through the history and ask which of the passes we've trusted were passes because of the value we pinned. That's a bigger job than the five diffs.

What I'd rather have from CI is the opposite: something that makes the variation visible on purpose, so a new ordering-sensitive test fails loudly instead of one run in ten. Not this week, but worth thinking about.

New failures over the weekend, both on main: `test_export.ExportTest.test_month_totals_by_category` (#1055) and `test_sync.SyncTest.test_display_order` again (#1057). The export one is new to the list, same shape as matches_golden as far as I can tell from the diff, category rows swapping. I'll add it to the list and re-run it a few times to get a rate.

### #82 · Dana · Mon 2026-11-09 11:04

Wen, before we go further on the list — I noticed the tie-break work hasn't started since Thursday. What's the status? I'm not trying to nag, I just want to know if something's blocking or if the weekend ate your time.

### #83 · Wen · Mon 2026-11-09 11:19

The weekend ate my time, sorry. I was primary on call and got paged Saturday around 02:10 for the payment-reminder service (the one in the billing repo, not ledger). Short version: customers got duplicate reminder emails. I was on it until about 07:00 and then writing it up most of Sunday morning. The ledger work is still on my plate, I just haven't started it.

### #84 · Dana · Mon 2026-11-09 11:24

That's a real incident, that's fine. Walk me through it though — partly because I want to know, partly because I want to make sure we're not about to have the same shape of problem in something else. Timeline, what actually happened, what the fix was.

### #85 · Dana · Mon 2026-11-09 11:38

Agreeing with Priya on the stopgap, and I want to be clear about why so it doesn't come up again next month.

CI exists to tell us what production will do. If production runs with randomised hashing, and it does, then CI must too. A green CI that only means something under a pinned value is worse than a red one, because it costs us the signal and gives us nothing back except a tidier dashboard. So: no environment pinning in CI, no per-job overrides of that variable. Same reasoning I'd apply to anything else that makes the test environment diverge from what ships. Tomás, that's not a knock on you raising it, it was worth putting on the table.

Wen, the plan you described is fine, small branches, module by module. On call takes priority over a flake fix; if a page lands mid-module, park it and pick it up later. I'd rather have three modules done properly by Friday than five rushed ones.

Priya, the idea of making the variation visible on purpose is interesting but let's not scope it now. Keep the list current, that's the thing I actually need from you this week.

### #86 · Wen · Mon 2026-11-09 11:41

Timeline as best I have it:

- 01:58 — the billing DB had a brief failover, about 90 seconds of connection errors.
- The reminder job runs every 5 minutes, picks up invoices due that day, sends via the mail provider, marks them sent.
- Every send attempt during the failover got a 500/connection reset from our side before the mark-sent write, so the job retried. That part is correct behaviour on its own.
- The retry wrapper retries the whole batch, not the individual item, and the mail provider had already accepted a chunk of the sends before our DB write failed. So on retry we re-sent those.
- 02:10 the first page fired off the duplicate-send alert threshold.
- 02:40 I'd stopped the job (paused the cron) and started counting. Roughly 1,400 recipients, about 3,100 extra emails. Worst case was four copies of the same reminder.
- 03:30 we'd confirmed the sends had all gone out and nothing was still queued. Mail provider was fine throughout, it was us.
- Rest of the night was the customer-facing side: we drafted a note, support sent it to the affected set.

Root cause in one line: sending isn't idempotent, and the retry boundary is the batch rather than the individual reminder, so a partial failure replays sends that already succeeded.

### #87 · Tomás · Mon 2026-11-09 11:57

Adding the retry config detail since I looked at it with Wen on Saturday. The job's wrapper is `retry(attempts=5, backoff=exponential(base=2), jitter=full)` with no cap on total elapsed time, so five attempts of the whole batch. With the DB failover at ~90s, attempt 1 failed fast, attempt 2 hit the tail of the outage, attempt 3 succeeded but partially — and each of those replayed the sends that had already gone through.

Two things I'd flag beyond the obvious. The backoff base of 2 with full jitter means attempts can land almost on top of each other, so the 'retry storm' wasn't even a long storm, it was three attempts inside about a minute. And the mail provider call has its own timeout of 30s with no retry of its own, so a slow-but-successful send looks like a failure to the wrapper. We don't log the provider's message id anywhere, which is why counting took as long as it did. If we'd had the ids we could have deduped in the log in ten minutes.

### #88 · Priya · Mon 2026-11-09 12:14

Does the reminder service have tests for idempotency? Genuine question, not a pile-on. If the answer is no, that's the follow-up I'd push for hardest, because it's the kind of thing that passes every happy-path test and only shows up under exactly this failure mode.

What I'd want is something like: a fake mail provider that records sends and can be told to fail on the Nth call, a fake DB that can fail the mark-sent write, and then assert that across the retries each recipient appears exactly once in the provider's record. That test is cheap to write and it would have caught this. If there's already something like it and it didn't fire, that's a more interesting problem.

### #89 · Wen · Mon 2026-11-09 12:38

Answer is no, not really. There are tests that the job sends one email per due invoice on a clean run, and a test that a failed send gets retried, but nothing that combines a partial failure with a retry and checks the count. The retry test uses a fake that fails once and succeeds the second time, and it only asserts the call returned, not how many emails went out. So it would have passed on Saturday's code.

Follow-ups I've written up, in rough priority:

1. Per-item retry instead of per-batch — retry the individual reminder, not the whole selection.
2. An idempotency key per (invoice, due date) passed to the mail provider, so a replay is a no-op on their side. Need to check they support it, but I believe they do.
3. Record the provider message id before considering the send done, so we can dedupe after the fact.
4. Cap total elapsed time on the retry wrapper, and make the backoff less aggressive.
5. Split the done-tracking into 'sending' and 'sent' so a crash mid-send is recoverable without replaying.
6. The idempotency test Priya described.

I've got 1, 2 and 6 as the ones I'd want in before the next busy period. The rest can be normal tickets. That's a separate repo so it doesn't touch ledger, but it's where my last two days went.

### #90 · Ines · Mon 2026-11-09 12:47

Jumping in from the finance side, partly to say hello and partly because I have a scheduling question.

First, context on the import: I read ledger's monthly export and load it into the budgeting spreadsheet. The export diff churn Priya's been posting has been hitting me too, because when the row order moves my importer's change detection flags every row as changed and the reviewer has to eyeball the whole month. So whatever comes out of this, I'm grateful. I've been working around it by matching on account name rather than row position, but the golden-file diffs are still noisy to read.

Second, and this is the actual question: finance is planning a budgets module for next quarter. It would live in ledger, alongside the existing modules, reading the same registry, adding a couple of new commands. Planning is early, we're talking January for the first cut. My question is who reviews it. I don't want to build it in a corner and then find out at merge time that it breaks assumptions the rest of you hold. Is there a standing reviewer for new ledger modules, or does it go to whoever's free? And is Wen the right person to talk to about how the modules are laid out, once the current work is done? Happy to take this offline if it's easier.

### #91 · Dana · Mon 2026-11-09 13:02

Understood, and thanks for the writeup, that's a clear one. Incident work comes first, no argument there — I only asked because I couldn't tell from the outside whether it was the incident or something stuck on our side.

One thing I'd say to the room, since Wen raised it: the pattern of 'retry the batch, assume the side effect is replayable' is worth a look anywhere we send or write something external. Not a project, just something to keep in mind when anyone's next in that code. Priya's point about the test is the part I'd hold onto — the test that only asserts the call returned is the kind of test that gives false comfort.

Wen, when you pick the ledger work back up, post here and I'll re-check the list against what you've got. No rush on this morning; get your follow-up notes filed first if that's the priority.

### #92 · Rafael · Mon 2026-11-09 14:12

Quick answers and one caution for Ines.

On review: there's no standing reviewer, it's been whoever's closest to the area. For a new module I'd say Dana should see the shape of it early, before there's much code, and then one of us does the detailed read. I'm happy to be that person if it helps, budgets touch the same export and statement paths I've been in lately.

On the caution: whatever the budgets module does with ties, sort by name at the point of use from day one. Don't rely on the order you happen to get from the registry, that's the whole bug we're chasing. If you're grouping by category and two categories have equal totals, pick an explicit secondary key. It'll save you a week of what Priya's been doing.

On the display order in the export generally: once Wen's changes are in, the export should come out in a stable order run to run, which should quiet your importer's change detection. I wouldn't redesign the importer around it until we've seen a few weeks of stable output, though. If it's still moving after that, tell us, because that would mean we missed a spot.

Wen, no pressure, but if you want a second pair of eyes on the export diff when you get there, ping me. I've read that module more than I'd like to admit.

### #93 · Ines · Mon 2026-11-09 14:41

On the budgets module: the person writing it will copy the closest existing module, which today means starting from `for name in ACCOUNTS`. That's how limits.py got its version, it was copied from export.py last spring.

### #94 · Priya · Tue 2026-11-10 07:58

Run #1057 overnight: `test_rebalance.RebalanceTest.test_same_headroom_by_name`. Two accounts with the same headroom, it picked the wrong source. rebalance.py was added in September by copying limits.py. Adding it: that's five.

Final list as I see it: display_order, matches_golden, header_same_day_by_name, worst_offender_tie_named_by_name, same_headroom_by_name. Not flaky: summary_totals (that was 4e1c9a2, reverted).

### #95 · Tomás · Tue 2026-11-10 08:12

Also on #1057, unrelated: the cache fetch for the pip wheel hit a network blip and retried, cost about two minutes of wall clock. Nothing failed because of it, job went green on everything except the rebalance test. Flagging it only so nobody reads the two-minute jump in the job duration as part of the flake. If it shows up again I'll look at the retry settings on the runner.

### #96 · Wen · Tue 2026-11-10 08:26

Five tests, and now that I look at them together they're all the same shape: two accounts tie on whatever the test cares about, and the code picks whichever one came out of the loop first instead of breaking the tie by name. display_order is the plainest version of it, matches_golden is the same thing through the export, and the other three are each a module that ranks or picks something and has no tiebreak. Which is also why they keep showing up as new tests: rebalance was copied from limits, limits was copied from export.

What I want to be careful about while I'm in there: the tiebreak has to go where the list is built, not where it's printed, otherwise the golden export diff will still move around even if display_order goes green. I'll go module by module and check where each one actually materialises the list before I touch anything.

### #97 · Rafael · Tue 2026-11-10 08:44

On rebalance, since I wrote a chunk of it: yes, it builds the candidate list straight from the registry, same as limits does. `sources = [a for a in ACCOUNTS if ...]` and then it takes the first one that clears the headroom check. There's no other ordering anywhere in that file, so whatever order it gets is what it uses. Same story in the loop that names the target. That's all I've got on it, I haven't been in there since September.

### #98 · Priya · Tue 2026-11-10 09:02

Dana, can you give the thread a read before Wen starts? I'd rather not have him half way through five diffs and then find out someone wants a different shape. The list is stable now as far as I can tell: five tests, all reproduced, and the seeds Rafael mentioned line up with what I see.

For what it's worth from my side, the thing I'd ask for is that each of the five has a test that actually pins the tie. Right now display_order and matches_golden would catch a regression in their own module, but the other three only fail when the tie happens to land the wrong way, which is why we didn't see them for weeks. If Wen's diffs are small I can add a case per module where the two candidates tie and the expected answer is the one that sorts first by name. That's a change to the tests though, so I want a yes before I write it.

### #99 · Wen · Tue 2026-11-10 09:18

While I'm waiting on Dana, a couple of notes so the review is quick.

First, where each one builds its list:

```
report.py     display_order  -> builds the list once, then sorts by amount
sync.py       (same list, used by export)
export.py     matches_golden -> groups per month, order comes from the list
statement.py  header         -> sorts by last activity, then takes names
limits.py     worst_offender -> sorts by overage, takes first
rebalance.py  headroom       -> filters the list, takes first
```

In statement, limits and rebalance the sort key is a number, so equal keys come out in list order. That's the tie. In report and export the list order is the output order.

Second, I ran the suite locally five times with nothing else going on and got display_order twice, matches_golden once, and the other three not at all. So they're the same bug but not equally likely to show, which matches what Priya said about not seeing them for weeks.

I haven't started editing. I'll wait for Dana.

### #100 · Tomás · Tue 2026-11-10 09:31

Spent the first hour putting the week's runs into one table, since we've been quoting run numbers from memory and I don't trust any of us. Range is #1040 through #1057 (last night's), pulled from the runner logs, not the dashboard, because the dashboard rounds. Columns: run, image, failed test (or PASS), rerun outcome.

```
run    image         result
#1040  20261025.2  PASS
#1041  20261025.2  FAIL test_report.ReportTest.test_summary_totals (4e1c9a2; reverted)
#1042  20261025.2  PASS
#1043  20261101.1  FAIL test_sync.SyncTest.test_display_order -> rerun PASS
#1044  20261101.1  PASS
#1045  20261101.1  FAIL test_export.ExportTest.test_matches_golden -> rerun PASS
#1046  20261101.1  FAIL test_statement.StatementTest.test_header_same_day_by_name -> rerun PASS
#1047  20261101.1  PASS
#1048  20261025.2  FAIL test_export.ExportTest.test_matches_golden -> rerun PASS   [pinned old image]
#1049  20261101.1  PASS                                                          [pinned new image]
#1050  20261101.1  FAIL test_limits.LimitsTest.test_worst_offender_tie_named_by_name -> rerun PASS
#1051  20261101.1  PASS
#1052  20261101.1  PASS
#1053  20261101.1  FAIL test_limits.LimitsTest.test_worst_offender_tie_named_by_name -> rerun PASS
#1054  20261101.1  PASS
#1055  20261101.1  PASS
#1056  20261101.1  PASS
#1057  20261101.1  FAIL test_rebalance.RebalanceTest.test_same_headroom_by_name -> rerun PASS
```

Things that jump out reading it as a table: 11 of 18 green first try, 6 failures that went away on rerun without a code change, 1 failure that was the bad commit. The failures are spread across five different tests, which is why it felt like everything was breaking at once, but no test failed twice except worst_offender. Every rerun passed, which is the signature of something that changes between processes rather than something that changes over time.

Caveat: the pinned-image experiment rows are only two runs each, so #1048/#1049 don't prove much on their own. The point of them is that the old image failed too, which kills the image theory. I'm leaving them in the table for completeness but wouldn't draw conclusions from that pair beyond that.

One thing I can't get from the logs: whether any of these reruns were triggered manually vs. automatically. If someone knows, tell me, because the dashboard splits those and the numbers I'm quoting are the raw runs.

### #101 · Priya · Tue 2026-11-10 09:38

Cross-checked the table against my own list, mostly because two rows didn't match what I had written down. Two corrections:

#1046 is right, header_same_day_by_name, new image. That one I filed under the date stuff initially and moved it later, so my notes had it twice; the table has it once, which is correct.

#1050 I had as failing on #1051. That's wrong, I misread the rerun column on my end. #1051 was a clean PASS and #1050 is the first worst_offender failure. Second one is #1053 as in the table. So Tomás' rows are right and my note was off by one. Sorry, I've been keeping the list in a scratch file and clearly not carefully enough.

Also worth saying: #1041 shouldn't be in the same bucket as the rest. It's the only row where the failure is explained by the code that was on main at the time, and it never came back after the revert. If we're counting flake rate for the week I'd exclude it or at least footnote it, otherwise the number looks worse than the actual problem.

The rest matches: display_order once, matches_golden twice (once new image, once old), header once, worst_offender twice, same_headroom once. That's 7 rerun-PASS failures across 17 runs excluding #1041, which is roughly 40%, which lines up with what we've been seeing anecdotally.

One more thing I noticed while doing this: the rerun of #1043 passed but the rerun of #1050 passed too, and I ran the same test locally five times this morning and got two different outcomes in terms of which account was named, though it passed the assertion every time because I was on the scratch copy. Not useful yet, just noting it so I remember to look at local reproduction separately from CI.

### #102 · Wen · Tue 2026-11-10 09:42

Quick question about the table, since I'm going to have to look at these runs while I'm doing the module diffs: how does the dashboard count a rerun?

What I mean is, if #1043 fails and then the rerun passes, does the dashboard show one run with a final status of pass, or two runs, one fail and one pass? Because the number I see on the main page for last week doesn't match 6 or 7 failures depending on how I count, and I want to know whether I'm looking at the same thing you pulled from the logs.

Reason I ask: when I'm checking my changes I'll be looking at green/red on the dashboard, and if it silently swallows rerun passes then I could break something and not see it until it shows up as a red on a run nobody reran. Conversely if it counts both, my local "it passed" is worth less than I think.

Also, is there a way to see from the run page whether a given green was first-try or a rerun? If it's in the logs I can grep, that's fine, I just don't want to be guessing.

### #103 · Tomás · Tue 2026-11-10 09:46

Good question, and the answer is annoying. The dashboard counts each attempt as a separate row but groups them under the original run number. So #1043 shows as one run with a little "2 attempts" marker and a final status of pass. The main page summary, the one with the percentage, counts the run as pass. There's a failures-total widget further down that counts attempts, so that one says 7 for the week while the headline says 1 (which is #1041).

That's why the numbers didn't line up for you. If you want the honest number, use the attempts widget and subtract #1041, or just use my table, which is attempts.

For checking your own changes: a green in the headline does not mean first-try green. To see whether something was rerun, the run page has the attempts list on the right-hand side, each attempt with its own timestamp and status. It's not in the URL, you have to click through. If grepping is easier, the runner log line for a rerun starts with "attempt 2:" and the original's log has "attempt 1:". That's what I used to build the table, actually, since the API I was hitting returns attempts but not in a very obvious order.

One caveat on the attempts widget: it's counted per job, and a run with three jobs that all rerun shows as three attempts even though it's one run. I didn't hit that this week because these tests are all in the same job, but if you're ever comparing across weeks, keep it in mind.

If it'd help, I can add a column to the table for first-try vs rerun. It's one more pass over the logs and then nobody has to click through.

### #104 · Priya · Tue 2026-11-10 09:50

Yes please to the extra column, if it's cheap. I'd rather have the table be the source of truth for the week than have three of us each half-remembering which greens were reruns. And it'll be useful later when we want to know whether the rate actually went down, because "green" on the dashboard is going to be a misleading measure if half the greens are second attempts.

While you're in there: can you also mark which of the failures were on a branch vs main? I know #1053 and #1057 were both main because I was the one who reran them, but I genuinely don't remember about #1045 and #1046, and if some of these were on feature branches then the rate is even more skewed than 7-in-17. I don't think any were, but I'd rather check than assume.

On the local repro: I tried again after my last message and got the same test to pass ten times in a row on the scratch copy, then fail twice when I removed the thing I'd changed. Which is consistent with everything you said, Rafael, I'm just adding it to the record because it means I can't use "passes locally" as evidence for anything anymore, at least not without running it a lot more times than I have patience for. For my own sanity I'm going to stop trying to reproduce these individually and just work from the table.

So current status from my side: list stands at five tests, table matches with the #1050 correction, and #1041 stays footnoted. Nothing else new since #1057.

### #105 · Dana · Tue 2026-11-10 09:52

OK, changing my answer from Thursday. Rafael's version, for the reason he gave: rebalance is exactly that case, and budgets is about to be the next one. Same ground rules as before otherwise. Wen, sorry for the churn.

### #106 · Wen · Tue 2026-11-10 10:05

No churn, I hadn't started. Just to be sure I have it: same ground rules means nothing under generated/, and tests and golden file stay as they are?

### #107 · Dana · Tue 2026-11-10 10:09

Yes. And no CI-only workaround for the randomisation, per yesterday.

### #108 · Ines · Tue 2026-11-10 11:34

Thanks everyone, genuinely. I've been reading this thread on and off since Priya opened it and the amount of digging that went into it is not lost on me, especially the 40-run sweep on the same commit. That kind of thing is invisible in the final diff and I know how long it takes.

Small ask, and no rush on it: could someone ping me in here once the fix is in and the export side has had a few green runs? I turned off the golden-diff alert on our side last week because it was firing so often I stopped trusting it, and I don't want to switch it back on until I know the noise is gone. A false alert on the monthly export is worse than no alert, at least for me, because it trains me to ignore the real one. I'd rather sit dark for another week than flip it on and start skimming.

For context on what I see when it does fire: our importer reads the monthly export and matches rows by account name, so ordering alone shouldn't break it. But the diff alert compares the export against last month's snapshot line by line, and when rows move it produces a wall of changed lines that all say the same numbers in a different place. I spent close to an hour one morning convincing myself nothing had actually changed except position. If there's a cheap way to tell me "same rows, different order" vs "numbers actually moved" I'd take it, but that's a separate thing and I'm not asking anyone to build it this week.

Also happy to be a second pair of eyes on the export diff once it's stable, if that's useful. I know that file better than anyone at this point, probably including whoever wrote it.

### #109 · Tomás · Tue 2026-11-10 14:02

Closing my ticket on the runner image, marked as not the cause. Leaving a note on it for whoever finds it later, roughly: pinned half the fleet to 20261025.2 for 24h, both pools still flaked, one failure each side, so the image bump is unrelated and the pin has been reverted. Linked Rafael's finding to it so the two don't get conflated in future archaeology.

One thing I want to flag while I'm here, because I got lucky on it. When I did the controlled comparison I was matching failures by test name only, and at one point I nearly wrote down "old image failed, new image passed, therefore image" from a single pair of runs where the failing test on each side was different. It was only because I pasted the actual failure lines next to each other that I noticed. If anyone else does a before/after on a flaky thing, compare the specific output, not just which test went red. Cost me about ten minutes of being confidently wrong.

Nothing else on my plate from this. The wrapper tee-ing is staying as is, it's been fine and nobody's asked for it to do more. If the CI watch Priya's talking about turns up anything that looks runner-shaped, drop it in here and I'll look, but my guess is it'll be quiet.

### #110 · Wen · Tue 2026-11-10 16:47

Quick process question before I start pushing things, since I'd rather ask now than get it wrong five times. What's the expected commit message format for something like this? I've been looking at recent history on main and it's a mix: some are one line, some have a body, some prefix with the module name, and there's at least one that's just "fix" with no detail at all, which I assume predates the current habit.

My instinct, tell me if it's off: one line saying what changed and where, roughly "ledger: make tie-breaking between accounts deterministic", then a short body saying why, in this case that ties were falling back to an order nobody chose, and a sentence on how I verified it. I don't want to write a paragraph of archaeology in the message if the convention here is to keep it terse and let the PR carry the story.

Second question, related: do you want one commit for the whole change or one per touched file? I lean toward one, since it's the same idea repeated and splitting it makes the history look like five unrelated fixes, but I can see the argument for one per file if it makes review or revert easier. Happy either way, just don't want to guess and then have to rewrite history on a branch people have already pulled.

Also, small thing, is there a project-level convention about referencing the thread or a ticket in the message? I've seen both styles in the log and I genuinely can't tell if it's preference or drift.

### #111 · Rafael · Tue 2026-11-10 17:25

On the commit message: terse first line, body only if the why isn't obvious from the diff. For this one I'd say the why is worth a couple of sentences, because in six months the code will look like harmless sorting and someone will be tempted to "simplify" it back. So something like: first line saying what changed, then a line or two on what the symptom was, then a line on how you checked it. Keep the check line concrete, e.g. that you reproduced the failures on the same commit before the change and couldn't after, rather than "tests pass".

On one commit vs one per file: one commit. Agreed with your reasoning, and it also keeps the revert simple if we need to back it out for any reason. Five commits with the same message pattern is more noise than signal.

One practical thing while you're in there: when you're done, grep the tree for any other place that walks the registry and would tie-break implicitly. I don't mean fix them, I mean just list them in the PR description if you find any. That way if a sixth one shows up flaking next month we already know instead of starting from Priya's failure list again. I had a quick look and I think the five we know about are the ones, but a second pass from fresh eyes is worth more than my confident guess.

Also don't worry about the history being mixed. Half of it is from before anyone cared and the other half is me being inconsistent on a Friday.

### #112 · Priya · Wed 2026-11-11 08:41

Plan on my side once the fix lands: I'll watch CI for a week before I take anything off the flaky list — daily, not just the overnight runs, and I'll note the run numbers here so we have a record. If any of the five shows up red in that window I'll post the run number and the actual output lines, not just the test name, per Tomás's point. A week feels about right given how sporadic these were; some of these went three or four days between failures, so a couple of green runs wouldn't tell us much.

Two things I want to head off, since I've been burned by both:

First, a green week doesn't mean the underlying thing is gone, it means the symptom stopped showing up. So I'd keep the list around even after the week, just moved down the page, rather than deleting it. If one of these comes back in a month I want the history in one place.

Second, I'm not going to declare anything fixed off my own runs. I'll post what I see and let someone else read it, because last time I got the statement header wrong by half an hour of reasoning about clocks and had to walk it back. My confidence in my own pattern-matching on this particular bug is not high.

For the record the five currently on the list are display_order, matches_golden, header_same_day_by_name, worst_offender_tie_named_by_name, same_headroom_by_name. summary_totals stays off it. If anyone thinks a sixth belongs there, say so now rather than after the week starts, because I'd rather watch six than find out on day eight that I was watching the wrong set.

### #113 · Dana · Wed 2026-11-11 09:12

Sounds right on both counts, Priya. A week of watching, list stays where it is, post run numbers and actual output. And the point about not declaring things fixed off your own runs is a good habit in general, not just here.

Wen, one thing to add to Rafael's note on the commit: don't reference this thread by name in the message. It's internal and the message should stand on its own for someone reading the log in a year who doesn't know the thread exists. Describe the symptom in plain words instead.

On the grep pass, yes, please do it and put what you find in the PR description even if it's nothing. A line saying you looked and these are all the places is useful. If you find one that looks genuinely at risk, don't fix it, just flag it in the description and we'll talk about whether it belongs in this change.

Ines, I'll ping you in here once Priya's a few days into the watching and the export has been quiet. You can turn the diff alert back on then, or wait the full week, whichever you're comfortable with. And no, don't build the "same rows, different order" thing this week. If it's still annoying in a month, bring it up as its own small piece of work.

That's everything from me. Wen, over to you.

### #114 · Priya · Wed 2026-11-11 10:12

For anyone landing here from the wiki: the incident page still has Thursday's decision on it.

### #115 · Dana · Wed 2026-11-11 10:30

Wiki is stale, the thread is current. I'll update the page after the fix lands.

### #116 · Dana · Wed 2026-11-11 11:07

Quick logistics before this drops off everyone's radar. Once the fix is in and we've had a clean day or two on main, I want fifteen minutes in the calendar to go over this properly — not a full postmortem, just a look at why five modules ended up with the same shape of problem and whether the next module someone writes is going to inherit it. Wen, you're obviously in it. Rafael, Priya, Marta too if she can spare the time, since half the question is what we're allowed to assume about generated code.

I'll put a hold on Thursday and Friday of next week and we take whichever day looks sane once CI has settled. No prep needed, no doc, just show up and talk for a quarter of an hour. If someone thinks this needs longer than fifteen minutes, say so now, because I'd rather find out before I book the slot.

### #117 · Tomás · Wed 2026-11-11 11:41

Dashboard numbers for the week, since people keep asking me in DMs. This is main only, 07:00 Monday through 07:00 this morning, all runner pools combined:

```
week of 2026-11-09 (main, all pools)
runs started            412
runs passing first try  361  (87.6%)
runs needing a rerun     48
runs failing twice+       3
mean run duration       6m14s  (prev week 6m02s)
p95 run duration       11m38s
mean queue wait          41s
reruns total             71
```

The 48 with a rerun is the number that matters for this thread — that's up from 31 the week before, and most of the delta is the five tests Priya listed. The mean duration creep is mostly reruns occupying slots, so I'd expect it to come back down on its own. Nothing in the runner side looks unhealthy: no image churn planned, no infra incidents, queue wait is flat.

The 3 double failures are unrelated to any of this, one is a genuine network timeout against the package index, two are the same disk-full thing on pool B that I'm already tracking. I'll post an update midweek next week so we have an after number to put next to this one.

### #118 · Wen · Wed 2026-11-11 13:22

Getting started now, Wednesday afternoon. I'll check each of the five tests against a few runs as I go, export last of the first three because Priya's already told me the diff there is miserable to read.

I'll run the full suite locally several times before pushing, one commit as Rafael said, then put it up for review. Nothing under generated/, tests and the golden file untouched, per the ground rules. If any of the five turns out to need something the others don't, I'll flag it in here before I go further rather than quietly doing something different in one file.

One thing I'd like a second pair of eyes on once I'm done: whether the new budgets module, whenever someone picks it up, has anything obvious to copy from. I can look at that after this is merged, but I don't want to be the person who says "don't do the thing I just did" without being specific about what the thing is.

### #119 · Dana · Wed 2026-11-11 13:58

Sounds right, Wen. One commit is fine. Two small things: put the branch name in here when you push so Tomás can tell the dashboard to ignore it if the suite gets noisy, and ping me and Rafael for review rather than just Rafael, since I'd like to actually read these diffs this time instead of trusting the green tick.

Re: the budgets module — good instinct, and that's a chunk of what the fifteen minutes next week is for. Don't scope-creep into it now though. Finish this, get it merged, and we'll look at what the next person is going to copy from once main has been quiet for a day. If you notice something while you're in there, write it down in this thread rather than fixing it in the same branch.

And for the record on the retro: fifteen minutes, next Thursday or Friday, whichever day CI looks good. I'll book it once Tomás has a clean day to point at. Nobody needs to prepare anything.
