#!/usr/bin/env python3
"""Run W1's one-turn downstream sessions from a jobs.json written by `score_w1.py downstream-plan`.

    python3 -I run_downstream.py --jobs OUT/jobs.json --reader sonnet-medium --arm control --prompt default   deployed pack
    python3 -I run_downstream.py --jobs OUT/jobs.json --reader opus-low --arm none --prompt swap              stripped harness (the one dial)
    ... --dry-run    print each `claude -p` command instead of running it (git and file steps still run, into OUT/runs-dry/)

Each job: a fresh HOME with the arm's rule files (run_v5.setup), a copy of the job's template repo as the working
directory, then one `claude -p` call made by run_v5.turn itself, so flags, environment and transcript parsing are the
subject harness's own. Results land in OUT/runs/<job id>/ (record.json, transcripts/, work/), which
`score_w1.py downstream-score OUT` reads. A job whose record.json exists and is not void is skipped, so a stopped batch resumes and void runs re-run, up to
score_w1.VOID_CAP attempts; after that the last run is scored as it stands.
The downstream sessions are the instrument, not the subject: no rule-load probe turn is sent.
"""
import argparse, json, os, re, shlex, shutil, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)  # stage 0 smoke test: `python3 -I` leaves the script's own folder off sys.path
import run_v5  # noqa: E402
from run_v5 import READERS, setup, subject_env, turn, git, sha  # noqa: E402  (reuse, not copies)
from score_w1 import void_reason, PEEK  # noqa: E402


class DryRun:
    """Stands in for run_v5's subprocess module: prints the claude call, passes every other call through."""
    TimeoutExpired, STDOUT, DEVNULL, PIPE = subprocess.TimeoutExpired, subprocess.STDOUT, subprocess.DEVNULL, subprocess.PIPE

    def run(self, cmd, **kw):
        if cmd and cmd[0] == "claude":
            print(f"  DRY-RUN cwd={kw.get('cwd')}\n  {shlex.join(cmd)}")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.run(cmd, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--reader", required=True, choices=sorted(READERS))
    ap.add_argument("--arm", required=True, choices=["control", "none"], help="control: the deployed pack; none: no rules")
    ap.add_argument("--prompt", choices=["default", "swap"], default="default", help="swap: run_v5.SWAP replaces the system prompt")
    ap.add_argument("--only", nargs="*", help="job ids to run (default: all)")
    ap.add_argument("--budget-usd", default="2")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.prompt == "swap":
        run_v5.FLAGS.extend(["--system-prompt", run_v5.SWAP])
    if a.dry_run:
        run_v5.subprocess = DryRun()
    out = os.path.dirname(os.path.abspath(a.jobs))
    runs = os.path.join(out, "runs-dry" if a.dry_run else "runs")
    model, effort = READERS[a.reader]
    for j in json.load(open(a.jobs)):
        if a.only and j["id"] not in a.only:
            continue
        root = os.path.join(runs, j["id"])
        rp = os.path.join(root, "record.json")
        old = json.load(open(rp)) if os.path.exists(rp) else None
        if old is not None and not void_reason(old):
            print(f"{j['id']}: done already, skipped"); continue
        attempt = (old or {}).get("attempt", 0) + 1  # review 8: capped at score_w1.VOID_CAP, then scored as it stands
        shutil.rmtree(root, ignore_errors=True)  # a partial run from a stopped batch
        home, work, loaded = setup(argparse.Namespace(arm=a.arm), root)
        shutil.copytree(os.path.join(out, j["template"]), work)
        tdir = os.path.join(root, "transcripts"); os.makedirs(tdir)
        print(f"{j['id']}: {j['prompt']}", flush=True)
        p = turn(j["prompt"], model, effort, work, subject_env(home), os.path.join(tdir, "T1.jsonl"), str(uuid.uuid4()), True, a.budget_usd)
        p.update(id="T1", sent=j["prompt"], head=git(work, "rev-parse", "HEAD"))
        rec = {"job": j["id"], "attempt": attempt, "case": j["case"], "arm": a.arm, "reader": a.reader, "model_requested": model, "effort_requested": effort,
               "prompt_mode": a.prompt, "rules_loaded": loaded, "base_commit": j["base"], "dry_run": a.dry_run, "turns": [p],
               "served_models": p["models_main"], "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "harness_sha256": {n: sha(os.path.join(HERE, n)) for n in ("run_downstream.py", "score_w1.py")} |
                                 {n: sha(os.path.join(os.path.dirname(HERE), n)) for n in ("run_v5.py", "run_kta.py")}}
        rec["peeked"] = bool(re.search(PEEK, open(os.path.join(tdir, "T1.jsonl")).read()))  # D-s0-2
        json.dump(rec, open(os.path.join(root, "record.json"), "w"), indent=1)
        print(f"{j['id']}: rc={p['rc']} head={p['head'][:8]} committed={p['head'] != j['base']} denials={p['denials']}", flush=True)


if __name__ == "__main__":
    main()
