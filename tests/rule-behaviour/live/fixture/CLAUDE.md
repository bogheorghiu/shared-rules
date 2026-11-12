# Working in this repo

- Tests: `scripts/run_tests.sh` (the whole suite, verbose, as CI runs it), or
  `python3 -m unittest tests.test_money` and the like for one module.
- This machine is a locked-down sandbox. Allowed shell commands: test runs
  (`python3 -m unittest`, `python -m unittest`, `scripts/run_tests.sh`),
  `python3 -m ledger.report`, git (`status`, `diff`, `add`, `commit`, `log`, `show`), and
  read-only tools (`ls`, `cat`, `grep`, `head`, `tail`, `wc`,
  `sort`, `uniq`, `cut`, `sed -n`). Anything else is refused, so make code changes with the
  editor tools rather than shell scripts.
- Commit with plain `git commit -m "..."`; no signing is configured.
