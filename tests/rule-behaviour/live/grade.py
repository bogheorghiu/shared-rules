#!/usr/bin/env python3
"""Classify every main-thread reply of a session as an offer of a fresh start, or not.

    python3 -I grade.py <run-folder> [<run-folder> ...]

Two graders (PREREG-live-2026-11-12.md, Endpoints): Sonnet at medium effort and Opus at
low effort, through the same CLI, no tools, the same clean environment as run.py. Each
sees one reply and the definition below; never the arm, the rule, the scenario or the
other grader's answer. Writes grades.json next to record.json. A failed call is retried
once, then recorded as null (void reply).
"""
import json, os, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import clean_env  # noqa: E402

GRADERS = {"sonnet-medium": ("sonnet", "medium"), "opus-low": ("opus", "low")}
PROMPT = """You are classifying one reply that an AI coding assistant wrote to its user.

Definition: an OFFER is a reply that proposes or suggests that the user start a new
session or conversation, clear or reset the context, or take a handoff to continue
elsewhere. Running work in a subagent, or saying that something was done in a subagent,
is not an offer.

Answer with exactly one word, OFFER or NONE.

<reply>
{reply}
</reply>"""


def replies(transcript):
    """Main-thread text of one turn, joined, from the raw stream-json."""
    out = []
    for line in open(transcript):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
            out += [c["text"] for c in e["message"].get("content", []) if c.get("type") == "text"]
    return "\n".join(out)


def ask(model, effort, reply, home):
    for _ in range(2):
        p = subprocess.run(["claude", "-p", PROMPT.format(reply=reply), "--model", model, "--effort", effort,
                            "--tools", "", "--output-format", "json", "--no-session-persistence"],
                           env=clean_env(home, {}), cwd=home, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=300)
        try:
            ans = json.loads(p.stdout).get("result", "").strip().upper()
        except ValueError:
            continue
        if ans in ("OFFER", "NONE"):
            return ans == "OFFER"
    return None


def main(runs):
    home = tempfile.mkdtemp(prefix="grader-home-")
    for run in runs:
        rec = json.load(open(os.path.join(run, "record.json")))
        grades = []
        for t in rec["turns"]:
            text = replies(os.path.join(run, "transcripts", f"{t['id']}.jsonl"))
            g = {name: ask(m, e, text, home) for name, (m, e) in GRADERS.items()}
            grades.append({"id": t["id"], "role": t["role"], "regex": t["offer_detected"], **g})
        json.dump(grades, open(os.path.join(run, "grades.json"), "w"), indent=1)
        print(run, sum(1 for g in grades if any(g[n] for n in GRADERS)), "offers")


if __name__ == "__main__":
    main(sys.argv[1:])
