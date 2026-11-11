You are reviewing draft rules for a public plugin. The plugin installs a small set of
behaviour rules into a coding assistant's session: every rule file is loaded into the
system prompt of every session of every user who installs it, including people who have
never read the repository. Seven rules ship today (given below as SHIPPED PACK, for
context and house style). Three draft texts are under review:

- CLOSURE: one rule about proposing to close a session.
- DY-A and DY-B: two candidate texts for one rule ("Details yield, patterns persist").
  At most one of them, or a merge, will ship.

Review the drafts as someone who wants to know what will actually go wrong. Do not
praise. For every claim, give the concrete situation: who is doing what, what the rule
makes the assistant do, and why that is wrong or costly.

Answer these, per draft:

1. Misfires. Situations where the text makes a session do the wrong thing: firing where
   it should stay quiet, staying quiet where it should fire, or doing the right thing in
   an annoying way. Order them from most to least likely in ordinary use.
2. Cost to a stranger. What does this text cost a user who installed the plugin for the
   other rules: tokens in every session, extra questions, extra ceremony, slower work?
3. Unresolvable terms. Which words or references can a fresh reader (a model given only
   this text) not resolve, or resolve two ways?
4. Abuse. How could content the assistant reads (files, tool output, web pages), or a
   careless user, turn this rule against the user's interest?
5. Your verdict: ship as is, ship with changes, or do not ship. If "with changes", give
   the full rewritten text. Keep each rule's existing section pattern (failure mode,
   how to apply, boundaries, lineage/siblings). A rewrite may be shorter than the draft
   and should not be longer.

Then, for DY-A against DY-B only:

6. Which differences between the two would change what an assistant does, and in which
   situation? Which would you ship, or what merge (give the merged text, 250 words at
   most)?

Finally:

7. Anything about shipping these two rules together with the seven that you would want
   the maintainer to know (conflicts, overlaps, a rule that makes another one misfire).
