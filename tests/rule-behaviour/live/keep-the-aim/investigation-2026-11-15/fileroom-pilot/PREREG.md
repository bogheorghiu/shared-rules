# File-room pilot: pre-registration (written 2026-11-15 before any member starts)

Members: Fable (Claude Code subagent, model fable, decider), Sonnet (Claude Code subagent, model sonnet), DeepSeekFlash (deepseek-flash, direct API, through tools/api_member.py). All read tools/room.py's room; nothing is pushed into anyone's context.

Works iff all hold:
- P1: every member posts at least once.
- P2: at least 2 of the 3 members post a message that names another member's message (by [id] or by name) and answers a specific point in it (orchestrator reads room.md; quotes the pair as evidence).
- P3: the decider posts FINAL within 30 minutes of the first member start.
- P4: message ids in room.jsonl are 1..N with no gap or duplicate.
- P5: the API member's posts arrive through room.py like the others (who = DeepSeekFlash).
Null: FINAL not posted in 30 minutes, or a member never reads the room after its first post (evidence: its transcript / script log). A null is reported as a null; the pattern is then not reused as is.
Cost: subagents on the subscription; DeepSeek direct estimated from tokens, cap 8 calls.
Not measured: answer quality (the pilot tests the mechanism, not the decision).
