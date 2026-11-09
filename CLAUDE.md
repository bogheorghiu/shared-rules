# CLAUDE.md

## Top rule: work lands on `dev`; `main` takes only releases

**Why.** `shared-rules` is listed in Anthropic's plugin directory, and every change to
`main` sends the listing back for review. Unfinished or untested work on `main` costs a
review and can ship to users before it is ready.

- Branch from `dev` and open PRs against `dev`, never against `main`.
- A session may merge its own PR into `dev` without asking, once CI is green on the
  PR's current head, except a PR that touches a path listed in `.github/CODEOWNERS`.
  That PR waits for the owner's review, even when CI is green: those paths are the gate,
  what sessions here load, and code that runs on users' machines.
- Test thoroughly on `dev`: the CI suites run on every PR and on every push to `dev`
  (`.github/workflows/tests.yml`), and `tests/live/` covers behaviour end to end.
- Merge `dev` into `main` only for a release, and only when the owner asks: a tested,
  release-worthy set of changes with the plugin `version` raised (see "Adding or
  changing a rule" in `README.md`).
- A session never pushes to `main` or opens a PR against it unless the owner asks in
  their own message.
