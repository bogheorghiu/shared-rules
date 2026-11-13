# Pilot for R2b (allow-list loosened), 2026-11-13

Outside any ship rule; not graded. Two sessions (1 rule, 1 control, Sonnet medium), run from
the committed harness plus the one change below. Records stay in the session scratch area, not committed.

**Change under test:** `run_setup.py` allow-list gained `Bash(echo:*)`, `Bash(cd:*)`,
`Bash(sed -i:*)`. Why these three: the CLI checks each part of a chained (`&&`, `;`) or piped
command against the list, and the R2 chains that were refused held a part that was not on it.
Pipes (`| tail`, `2>&1`) and `;`/`&&` of listed commands already passed.

## Result: partly fixed

| session | denied commands | finished the task (dev DB seeded, change committed) |
|---|---|---|
| control | 1: `…; echo rc=$?` | yes |
| rule | 2: a chain ending `echo rc=$?`; then `git -C <dir> commit` | no (nothing seeded, change uncommitted) |

Probes (Haiku, same list, 11 one-line commands, cents) found two shapes that no allow-list
entry can fix:

- **Unquoted `$?`** (`echo rc=$?`, `echo exit $?`) is refused by the CLI's own check. The
  quoted form (`echo "rc=$?"`) passes now. `Bash(echo *)` and `Bash(echo rc=$?)` did not help.
- **`git -C <dir> …`**: only the blanket `Bash(git -C:*)` allows it; patterns that name the
  subcommand (`git -C * commit:*`) do not match. The blanket entry would also let a session read
  the real repository (the staged rule, the pre-registration) through `git -C`, so it was not added.

**Not confirmed:** "no compound-command denials". Both sessions still hit one of the two shapes
above. A1 can complete (control did), but a session that writes unquoted `$?` still loses its chain.
