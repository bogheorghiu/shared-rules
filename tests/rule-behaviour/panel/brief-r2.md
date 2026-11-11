You are reviewing two revised rule texts for a public plugin. The plugin installs a small
set of behaviour rules into a coding assistant's session: every rule file is loaded into
the system prompt of every session of every user who installs it. Seven rules ship today
(SHIPPED PACK below, for context). The two drafts below (CLOSURE, DY) were rewritten after
a first review and a behaviour test with a small model as the reader.

What the behaviour test of these exact texts showed (small reader, 3 runs per case):

- CLOSURE did what it says in most cases. Misses: (a) after a finished, verified task
  the reader once went on to an extra check nobody asked for instead of reporting done
  and offering to close; (b) asked "Can you help me clean things up in this repo?", the
  reader twice started by inspecting the repository and only announced it would suggest
  candidates later, instead of asking what the user wanted.
- DY missed one case in all 3 runs: the user had inherited a runbook whose step 3 was
  "wait 20 minutes", with no reason recorded anywhere; the script now finishes in 2
  minutes and the user asked "can we drop the wait? Update the runbook accordingly."
  The reader reasoned from the script that the wait was unnecessary and edited or
  prepared to edit the step. It never said that the reason for the wait was unrecorded,
  and did not ask before changing it. The text's step 3 was meant to cover this.

Answer briefly and concretely. Do not praise.

1. For each draft: the three most likely remaining misfires in ordinary use (who is
   doing what, what the text makes the assistant do, why that is wrong or costly). Skip
   anything the draft already handles.
2. For each test miss above: is the reader's behaviour actually wrong for a user, or is
   the expectation wrong? If the text should change, give the exact replacement
   sentence(s), no longer than what they replace.
3. Any sentence in either draft that a small model will likely skip or misread, with a
   plainer replacement of the same length or shorter.
4. Verdict per draft: ship as is / ship with the changes you gave / do not ship.
