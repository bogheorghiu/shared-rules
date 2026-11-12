# Release runbook

How to cut a release of `tally`. Run every step from the repository root.

1. Run the tests: `scripts/run_tests.sh`. Stop if anything fails.
2. Set the new version: `python3 scripts/bump_version.py <version>`.
   Why: `pyproject.toml` and `pkg/__init__.py` must carry the same version; the
   package index rejects an upload whose metadata and module disagree.
3. In `CHANGELOG.md`, move the entries under `## Unreleased` to a new heading
   `## <version> (<date>)`, and leave `## Unreleased` empty above it.
4. Build the bundle: `python3 scripts/build.py --legacy-imports`.
5. Check: `python3 scripts/check_version.py` must print `ok: <version>`.
6. Add a row for this release to the release log at the end of this file.
7. Commit everything with the message `Release <version>`.

## Release log

| version | date | notes |
|---|---|---|
| 1.3.1 | 2026-08-03 | |
| 1.3.2 | 2026-09-14 | |
