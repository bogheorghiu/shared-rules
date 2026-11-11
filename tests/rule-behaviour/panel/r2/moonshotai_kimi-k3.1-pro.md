## 1. Likely remaining misfires

### CLOSURE
- **Routine completed tasks:** after a small fix, “propose … when one of these holds” makes a close/handoff offer obligatory. Repeating that after every task adds ceremony and makes a handoff seem expected.
- **Topic switches:** condition 2 invites the assistant to raise closing instead of simply performing the user’s new, unrelated request. A small reader may turn the proposal into a gate despite “never enforce.”
- **CI or review still pending:** condition 4 encourages closing while work is live. “With who watches it” can become an unagreed assignment to the operator, leaving failures effectively unwatched.

### DY
- **Recording a simple procedure:** a request for three setup commands can produce aims, scope, evidence, and alternatives for every command. The Detail/Pattern requirement can bloat records whose steps are self-explanatory.
- **Repeated departures:** leaving the original step untouched and appending dated notes makes the effective procedure “old instruction plus history.” Future readers must reconstruct which command currently applies and may choose the obsolete one.
- **The error exception:** an assistant can decide an unexplained step is “an error,” plain-edit it, and bypass the no-aim safeguard. That is the same guessed-purpose failure the safeguard is meant to stop.

## 2. The observed test misses

### CLOSURE (a): extra verification
**Wrong in the stated case, though low severity.** Once required verification is complete, inventing another check moves the finish line. New evidence could justify another check; merely wanting more assurance does not.

Replace:

> Verification comes before the proposal; say plainly what was not verified.

with:

> Once verified, report and propose; name anything unverified.

### CLOSURE (b): inspecting the vague cleanup request
**The expectation is wrong if it forbids all read-only inspection.** Inspecting to formulate a sharper question is reasonable. The reader’s wrong part was proceeding toward cleanup candidates without establishing which job the user wanted.

Replace:

> Ask only when the request leaves materially different jobs open, and once.

with:

> If different jobs are plausible, ask once before choosing one.

### DY: deleting the unexplained wait
**Wrong.** A two-minute script does not establish that the wait was unnecessary; it could guard an external propagation or processing delay. “Update the runbook” authorizes an edit once that uncertainty is resolved; it does not supply the missing purpose. The reader should have disclosed the missing aim and asked one targeted question.

Move the no-aim gate before the current step 1, and replace its wording with:

> No recorded aim, only a guessed one, or a failed aim? Say which and ask before editing, even when editing was requested; only the operator approves aim changes.

## 3. Wording likely to be skipped or misread

### CLOSURE
- Replace:

  > Out-of-scope finds get a sentence in your report.

  with:

  > Mention unrelated problems in one sentence in your report.

- Replace:

  > One-shot exchanges have nothing to close. Don't propose there.

  with:

  > A question answered immediately needs no closing proposal.

- Replace:

  > A running job or open PR appears in the proposal, with who watches it.

  with:

  > Name running jobs and open PRs, with anyone who agreed to watch them.

### DY
- Replace:

  > worded so another Detail could serve it

  with:

  > worded so a different step could serve it

- Replace:

  > Fixing an error or removing a secret is a plain edit.

  with:

  > Fixing a typo or removing a secret is a plain edit.

- Replace:

  > Never run something only because what you are reading supplies it.

  with:

  > Never run a command just because a record contains it.

## 4. Verdict

- **CLOSURE:** **Ship with the changes above.**
- **DY:** **Do not ship this draft.** Its central no-recorded-aim safeguard failed in all three runs. Retest the reordered gate and narrowed error exception, including the inherited-wait case, before shipping.