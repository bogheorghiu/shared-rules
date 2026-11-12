# What the headless harness does, as verified (2026-11-12)

Step 1 of the job: how the CLI drives a multi-turn headless session, sets effort, offers
subagents, and reports tokens. Each line says how it was checked. "Verified" means seen in
this environment with Claude Code `2.1.322`; "docs" means the `--help` text or the CLI
reference page (code.claude.com/docs/en/cli-reference, read 2026-11-12); "not verified"
means neither settles it.

## Multi-turn sessions

- **First turn** `claude -p "<text>" --session-id <uuid> --output-format stream-json --verbose`;
  **later turns** `claude -p "<text>" --resume <uuid>` with the same flags. Docs (`-r`,
  `--session-id`) and verified: a second call resumed with `--resume` answered a question
  about a codeword given only in the first call, and both calls' `init` and `result` events
  carry the same `session_id`.
- `--continue` is not used: the CLI reference says it skips sessions created with `claude -p`.
- Pass `stdin` as `/dev/null`. Verified: without it the CLI waits 3 s and prints a warning
  into the output stream.

## Isolation

- A child inherits the parent cloud session's environment. Verified: with the environment
  passed through, the child's `init` event listed the account's synced skills and remote
  tools (artifacts, messaging). `run.py` therefore starts each session from an empty
  environment holding only `PATH`, the proxy and CA variables, a fresh `HOME` and
  `CLAUDE_CONFIG_DIR`. Verified: the `init` event then lists only built-in skills and
  plugins, and `apiKeySource` is `none` (authentication is supplied by the environment's
  proxy, outside the session).
- Rule files copied to `$HOME/.claude/rules/shared-rules/` load natively in `-p` mode.
  Verified: a session with no tools listed all 8 headings of the rule arm verbatim.

## Effort

- `--effort low|medium|high|xhigh|max` (docs: "Available levels depend on the model").
- **Not verified: the effort a session actually ran at.** Neither the stream-json events
  nor a `--debug api` log of a probe contains the effort level. The only related field is
  `per_turn_effort_active: true` in `init`. Records therefore store the requested effort,
  labelled as requested. The model served is read from each assistant event's
  `message.model`.
- **Not verified: the effort of subagents.** The docs page read does not say whether a
  subagent inherits `--effort`.

## Subagents

- Available headless. Verified: with `--tools Read,Grep,Glob,Agent`, an Opus session
  spawned a general-purpose subagent through the tool named `Agent` (not `Task`; the model
  remarked on the name). Subagent events arrive in the same stream with
  `parent_tool_use_id` set; their usage is per call, separate from the main thread's.
- Without `--forward-subagent-text`, a foreground subagent's text and thinking blocks are
  left out of the stream (docs); its tool calls and usage are present (verified).

## Tokens and cost in the transcript

- Each `assistant` event carries `message.usage`: `input_tokens` (uncached),
  `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`. One API
  response can arrive as several events with the same `message.id`; `run.py` counts each id
  once. The main thread's context at a point is input + cache reads + cache writes of its
  last call there (plus that call's output).
- The `result` event's `usage` covers that one `-p` call. Its `total_cost_usd` and
  `modelUsage` are **cumulative over a resumed session**. Verified: 0.0725 after the first
  call, 0.0751 after the resumed one, whose own usage was a few hundred tokens.
- `total_cost_usd` is the CLI's client-side estimate at list price (`costBasis: "list"`);
  the docs say it can differ from the bill. Nothing in the transcript shows plan usage or
  rate-limit consumption beyond a `rate_limit_event` with no figures in it.

## Permissions

- This session's own permission check refused launching headless sessions with
  `--permission-mode bypassPermissions` and with an unscoped `--allowedTools Bash`
  ("Create Unsafe Agents"). It allowed read-only tools, and Bash scoped to named commands
  (`Bash(python3 -m unittest:*)`, `Bash(git commit:*)`, ...). `run.py` uses the scoped list,
  with `--permission-prompts none` so anything outside it is denied instead of hanging.
  A session can therefore not run arbitrary shell loops; denials are counted per turn.
