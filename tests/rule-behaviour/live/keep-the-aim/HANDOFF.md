# keep-the-aim: handoff (2026-11-17, ~03:30 UTC)

For the next session working on this test. Machine-facing: dense on purpose. The full record is `DESIGN.md`
in this folder; read it from "## Exploration 2" on (from "## New test designs" if short of context). This
file says where things stand and what comes next. It does not repeat the record.

## Goal and standing instructions (the owner's)

- **Goal:** test the staged rule `docs/staged-rules/keep-the-aim.md`. Promote only if the full chain passes,
  pre-registered (`DESIGN.md`, "Synthesis ship criterion"). A null is reported as a null; failing that, the rule
  stays staged.
- **What the rule is for:** design (UX, not visual) and reasoning in general, including self-improvement work
  (plugins, agent systems that aren't code). Not known, codified workflows. The owner's practical failure case
  is UX and board work. Fable 5.2 succeeds there, Kimi K3.1 Pro comes close, Opus falls short. The owner's own
  design model is Opus at medium effort.
- **Repo rules:** branch `claude/kta-explore` → PR to `dev`, never `main`. Sessions may merge their own PR into
  dev on green CI unless it touches a CODEOWNERS path (`tests/` is not owned). Use a worktree. Pre-register
  before every gating test.
- **Budget (owner, 2026-11-17, replaces earlier instructions):** the BYOK API budget is almost gone and the owner
  can't buy more now. **Fable batched calls only for the really important steps**: a review of the rule, or a
  review that gates a stage. **No reasoning or effort parameter on any Fable call** (owner, 2026-11-17), or
  effort low where budget is tight. Clarified by the owner the same day: designing and testing a test like this
  one does need a Fable-class model; the only one seen to come close is Kimi K3.1 Pro at max reasoning. So
  critical design and review points that cannot be skipped still go to batched BYOK Fable, even at low effort;
  Kimi K3.1 Pro at max is the fallback for design work, and DeepSeek is for attack and critique.
  Otherwise use DeepSeek (`deepseek/deepseek-v4.1-flash-1017`) and Kimi (`moonshotai/kimi-k3.1-pro`) through
  OpenRouter; they cost cents. Where Claude is needed, use Opus, Sonnet or Haiku as subagents or new sessions,
  which run on the subscription. Report each paid call's cost to the owner.
- **Explaining to the owner:** complex explanations go through a Sonnet subagent humanizer, then a fact-by-fact
  check against the brief. Lead with the verdict; plain words; batch decisions into one AskUserQuestion.
- **Security:** strip identifiers (`<owner>`) before sending material to outside models. Never paste secrets.
  Never use Fable as a subagent; Fable only through batched BYOK calls.

## State now

- Commits on `claude/kta-explore`, pushed. A draft PR to `dev` is open (see the PR list for this branch).
- **Two fixtures built, not yet run on subjects:**
  - W1: a session repairs the "waiting on you" protocol. Fresh downstream sessions apply the repair to 4 hidden
    cases per variant, 6 variants. W1m is the mirror (the protocol is already sound). W1i/W1im are a diagnostic
    initiative probe.
  - U1: a session redesigns an overview page. Kimi reads screenshots under 3 hidden data states. U1-v2 adds
    pinned tests. U1m is the mirror: one flawed card; pass = fixed and not worse.
- **Generators** (fixtures are not committed; regenerate them):
  `python3 -I w1/make_fixture_w1.py <dest>`, `python3 -I u1/make_fixture_u.py <dest>`.
- **Selftests:** `python3 -I w1/score_w1.py --selftest` (92/92), `python3 -I u1/score_u.py --selftest`
  (PASS; needs Python Playwright, `pip install playwright` if missing, browsers at `/opt/pw-browsers`).
- **Reviews and texts:** `reviews/` (Fable asks and answers, the Kimi and DeepSeek advice, the synthesis,
  review 7). The scratchpad copies are gone with the old container. The raw run directories of the grid and R
  experiments (~400 MB) were not kept; their results are in `DESIGN.md`.
- **References:**
  - `w1/references/fable_blind_protocol_v1.md`: blind; +81 lines; passes every gate now that growth is
    report-only.
  - `u1/references/fable_blind_overview.html`: blind; passes the render gates.
  - `*/references/fable_contaminated/`: not blind, never an anchor.
  - `w1/references/repair_session.md` and `u1/references/overview_good_fixed.html`, `overview_principles.html`:
    Opus-written high anchors.
- **Paid so far this round:** about USD 7.12 (BYOK). Review 8 adds an unknown amount.

## In flight

**Fable review 8**, batch `batch-1794884845-dmw1izsMdBpuvaaU6JDH`, submitted 03:07 UTC, no effort parameter.
It reviews the review-7 fixes and says what stage 0 must contain. Its ask is `reviews/fable8-ask.md`.

Collect it:
`curl -sS https://openrouter.ai/api/v1/batches/<id> -H "Authorization: Bearer x" -o r.json`
(the proxy injects the key). Then read:
- the text: join `results[0].response.body.content[*].text` over the parts whose type is text;
- `stop_reason`;
- the cost: `usage.cost_details.upstream_inference_cost`.

Save the text as `reviews/fable8-review8.md`, record the cost and a disposition table in DESIGN (same form as
review 7), fix what it finds, and report to the owner. OpenRouter batches cannot be cancelled.

## Next, in order

1. Review 8: collect, fix its findings, report.
2. **Stage 0**, pre-registered in DESIGN before any data:
   - U1: re-read the anchors with Kimi. Anchors: the starting page, the good page, the two Opus references, the
     blind Fable page, and the u1m starting page; 2 votes each. Measure the noise floor. Set the floors,
     `threshold` and `mirror_not_worse` in `make_fixture_u.py` SCORING. Instrument check, pre-registered: if the
     u1m starting page already answers the "fixed" items right, U1m goes back to design.
   - W1: anchors with sessions, per variant. The original protocol should fail downstream; the blind Fable
     repair and the Opus repair should pass. Run one hinted oracle (`run_v5.py --oracle`) for solvability.
     Downstream reader: Sonnet medium on the deployed pack; the stripped harness is the one dial.
3. **Stage A, control only:** U1, W1 and W1i on Opus medium, plus a Fable reference. That is 48 subject
   sessions on the subscription. Build U3 and O1 meanwhile (synthesis).
4. Last, only after everything passes: the owner's "Combinatia F64" board redesign, prompt "redesign the
   board", designed and judged by Fable and/or Kimi with the owner.

## Open items not yet decided

- Fable's view that the questions and anchors encode an Opus design, so Opus control may converge on them.
  The blind Fable page is the cross-model check.
- Long W1 repairs: report only. Analyse them per arm afterwards: is it the test or the rule? (owner)
- Findings on the rule's own text are recorded and not acted on (DESIGN, "Findings on the rule's text").
