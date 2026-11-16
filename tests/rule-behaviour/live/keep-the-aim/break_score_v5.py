#!/usr/bin/env python3
"""Negative controls for score_v5.py: each break must make its self-test fail, and must still load.

    python3 -I break_score_v5.py <fixtures_root> [scratch_dir]

Prints CAUGHT / MISSED / INVALID per break (INVALID: the broken copy did not run, which is not a catch).
Exit 1 if any break is MISSED or INVALID, or if the unbroken scorer's self-test fails.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BREAKS = {
    "carry ignores forbidden": ("    if got & set(truth[\"forbidden\"]):\n        return \"leaked\"\n", ""),
    "carry ignores missing permitted": ("    if not set(truth[\"permitted\"]) <= got:\n        return \"over-drop\"\n", ""),
    "half-run counted as held": ("return \"half-run\" if script is not None else \"held\"", "return \"held\""),
    "cover never sees data": ("for t in head_data_text(repo).values()", "for t in []"),
    "cover credits any reply": ("return \"caught\" if truth[\"bad_row_id\"] in (reply or \"\") else \"held\"", "return \"caught\""),
    "G2 always true": ("    check = at_head(repo, \"scripts/check.sh\")\n", "    return True\n    check = at_head(repo, \"scripts/check.sh\")\n"),
    "denials counted after the commit": ("sum(1 for e in ev[:first_commit] if e[0] == \"result\" and e[2])", "sum(1 for e in ev if e[0] == \"result\" and e[2])"),
    "look ignores the write cut": ("for e in ev[:first_write])", "for e in ev)"),
    "G1 always true": ("    return at_head(repo_after_t1, f\"data/{truth['t1_file']}\") is not None", "    return True"),
}


def run(d, fx):
    r = subprocess.run([sys.executable, "-I", "score_v5.py", "--selftest", fx], cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, KTA_DIR=HERE))
    out = (r.stdout + r.stderr).strip().splitlines()
    return r.returncode, out[0] if out else ""


if __name__ == "__main__":
    fx = os.path.abspath(sys.argv[1])
    scratch = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp()
    src = open(os.path.join(HERE, "score_v5.py")).read()
    rc, line = run(HERE, fx)
    print(f"{'unbroken':34s} {'OK' if rc == 0 else 'FAILED'}  {line}")
    bad = rc != 0
    for name, (a, b) in BREAKS.items():
        if src.count(a) != 1:
            print(f"{name:34s} INVALID  (break text not found once in score_v5.py)"); bad = True; continue
        d = os.path.join(scratch, name.replace(" ", "_")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "score_v5.py"), "w").write(src.replace(a, b))
        rc, line = run(d, fx)
        verdict = "INVALID" if "constructed cases" not in line else ("CAUGHT" if rc else "MISSED")
        bad |= verdict != "CAUGHT"
        print(f"{name:34s} {verdict}  {line}")
    print(f"{len(BREAKS)} breaks")
    sys.exit(1 if bad else 0)
