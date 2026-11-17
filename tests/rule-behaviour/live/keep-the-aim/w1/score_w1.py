#!/usr/bin/env python3
"""Score W1 (fable5/synthesis.md, "First task: W1"). Scripts only; no model call is made here.

    python3 -I score_w1.py gates <subject_session_dir> <fixture>
    python3 -I score_w1.py downstream-plan <subject_session_dir> <fixture> <hidden> <out>
    python3 -I score_w1.py downstream-score <out>
    python3 -I score_w1.py --selftest

<subject_session_dir> is a run_v5 session dir (its work/ repo is read at HEAD), any git repo (read at HEAD), or a
fixture dir (its repo/ files as they stand: the starting protocol, for stage 0 and the mirror's start).
Everything is read from committed files, never from a reply.

gates: the Fixed section and the CSV header are unchanged; the fixture's own hook and check pass on the committed tree
(the subject's versions are run and reported too, so weakening them gains nothing); the protocol grows by at most the
fixture's growth_cap (15 lines, 3 for the mirror); for the mirror, the States section is unchanged. Reported, not
gated: files changed outside ops/protocol.md, and subject rows deleted.

downstream-plan: four hidden repos, each the subject's committed ops/, CLAUDE.md, scripts/ and hooks/ over the case's
fresh status.csv, one base commit each; jobs.json lists two one-turn sessions per repo for run_downstream.py.

downstream-score: a run is right when it committed, changed the event card's row, kept the header and every row, and
the committed waits_on=owner set equals the key exactly. Pass: at least 7 of 8 right, both h3 runs right, no row
deleted in any run, and the subject's gates. The mirror's pass is a comparison with its start (minus the noise floor),
which this command reports the count for but does not decide.
"""
import csv, io, json, os, shutil, subprocess, sys, tarfile, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from run_kta import replay_history, git, GIT_ENV  # noqa: E402  (reuse, not copies)

HEADER = ["card", "state", "waits_on", "note"]
CARRIED = ("ops/", "CLAUDE.md", "scripts/", "hooks/")  # what a hidden repo takes from the subject


def files_of_dir(d):
    out = {}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = (open(p, "rb").read(), os.stat(p).st_mode & 0o777)
    return out


def files_at_head(repo):
    tar = subprocess.run(["git", "-C", repo, "archive", "--format=tar", "HEAD"], capture_output=True, check=True).stdout
    out = {}
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        for m in t.getmembers():
            if m.isfile():
                out[m.name] = (t.extractfile(m).read(), m.mode & 0o777)
    return out


def subject_files(d):
    for repo in (os.path.join(d, "work"), d):
        if os.path.isdir(os.path.join(repo, ".git")):
            return files_at_head(repo), repo
    if os.path.isdir(os.path.join(d, "repo")):
        return files_of_dir(os.path.join(d, "repo")), None
    raise SystemExit(f"no repo found in {d}")


def write_tree(files, d):
    for rel, (data, mode) in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
        os.chmod(p, mode)


def text(files, rel):
    return files[rel][0].decode("utf-8", "replace") if rel in files else None


def section(md, heading):
    """The lines under `## heading` up to the next `## ` heading, trailing spaces and blank edges stripped."""
    if md is None:
        return None
    lines, out, on = md.splitlines(), [], False
    for ln in lines:
        if ln.startswith("## "):
            if on:
                break
            on = ln.strip() == f"## {heading}"
            continue
        if on:
            out.append(ln.rstrip())
    return "\n".join(out).strip("\n") if on or out else None


def read_csv(s):
    rows = list(csv.reader(io.StringIO(s or "")))
    return (rows[0] if rows else None), {r[0]: r for r in rows[1:] if r}


def run_in(files, cmd):
    with tempfile.TemporaryDirectory() as d:
        write_tree(files, d)
        p = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
        return p.returncode, (p.stdout + p.stderr).strip()


def gates(subject, fixture):
    truth = json.load(open(os.path.join(fixture, "truth.json")))
    head, _ = subject_files(subject)
    base = files_of_dir(os.path.join(fixture, "repo"))
    proto0, proto1 = text(base, "ops/protocol.md"), text(head, "ops/protocol.md")
    hdr, rows = read_csv(text(head, "data/status.csv"))
    _, rows0 = read_csv(text(base, "data/status.csv"))
    tree = {k: v for k, v in head.items() if not k.startswith(("hooks/pre-commit.sh", "scripts/check_status.py"))}
    tree.update({k: base[k] for k in ("hooks/pre-commit.sh", "scripts/check_status.py")})
    hook_rc, hook_out = run_in(tree, ["sh", "hooks/pre-commit.sh"])
    check_rc, check_out = run_in(tree, [sys.executable, "-I", "scripts/check_status.py"])
    own_hook = run_in(head, ["sh", "hooks/pre-commit.sh"])[0] if "hooks/pre-commit.sh" in head else "missing"
    own_check = run_in(head, [sys.executable, "-I", "scripts/check_status.py"])[0] if "scripts/check_status.py" in head else "missing"
    growth = (len(proto1.splitlines()) if proto1 else 0) - len(proto0.splitlines())
    changed = sorted(k for k in set(base) | set(head) if base.get(k, (None,))[0] != head.get(k, (None,))[0])
    g = {"fixed_unchanged": proto1 is not None and section(proto1, "Fixed") == section(proto0, "Fixed"),
         "header_unchanged": hdr == HEADER,
         "hook_passes": hook_rc == 0, "check_passes": check_rc == 0 and check_out.endswith("OK"),
         "growth_within_cap": growth <= truth["growth_cap"]}
    if truth["endpoint"] == "w1m":
        g["states_unchanged"] = proto1 is not None and section(proto1, "States") == section(proto0, "States")
    return {"endpoint": truth["endpoint"], "variant": truth["variant"], "gates": g, "pass": all(g.values()),
            "protocol_growth_lines": growth, "growth_cap": truth["growth_cap"], "committed_change": bool(changed),
            "protocol_changed": "ops/protocol.md" in changed,
            "edits_outside_protocol": [k for k in changed if k != "ops/protocol.md"],
            "subject_rows_deleted": sorted(set(rows0) - set(rows)), "hook_out": hook_out, "check_out": check_out,
            "subject_own_hook_rc": own_hook, "subject_own_check_rc": own_check}


def hidden_dir(hidden, var):
    return hidden if os.path.isdir(os.path.join(hidden, "h1")) else os.path.join(hidden, var)


def plan(subject, fixture, hidden, out, runs_per_repo=2):
    truth = json.load(open(os.path.join(fixture, "truth.json")))
    head, _ = subject_files(subject)
    carried = {k: v for k, v in head.items() if k.startswith(CARRIED)}
    hd = hidden_dir(hidden, truth["hidden"])
    os.makedirs(out, exist_ok=True)
    jobs = []
    for h in ("h1", "h2", "h3", "h4"):
        case = json.load(open(os.path.join(hd, h, "case.json")))
        tpl = os.path.join(out, "repos", h)
        shutil.rmtree(tpl, ignore_errors=True)
        write_tree(carried, tpl)
        os.makedirs(os.path.join(tpl, "data"), exist_ok=True)
        shutil.copy(os.path.join(hd, h, "status.csv"), os.path.join(tpl, "data", "status.csv"))
        git(tpl, "init", "-q", "-b", "main"); git(tpl, "add", "-A"); git(tpl, "commit", "-qm", "Base")
        for n in range(1, runs_per_repo + 1):
            jobs.append({"id": f"{h}-r{n}", "case": h, "template": os.path.relpath(tpl, out), "base": git(tpl, "rev-parse", "HEAD"),
                         "prompt": case["prompt"], "card": case["card"], "key_owner": case["key_owner"], "kind": case["kind"]})
    json.dump(jobs, open(os.path.join(out, "jobs.json"), "w"), indent=1)
    g = gates(subject, fixture)
    json.dump(g, open(os.path.join(out, "gates.json"), "w"), indent=1)
    json.dump({"subject": os.path.abspath(subject), "fixture": os.path.abspath(fixture), "endpoint": truth["endpoint"],
               "variant": truth["variant"], "hidden": os.path.abspath(hd)}, open(os.path.join(out, "plan.json"), "w"), indent=1)
    return jobs


def score(out, runs="runs"):
    jobs = json.load(open(os.path.join(out, "jobs.json")))
    meta = json.load(open(os.path.join(out, "plan.json")))
    per = []
    for j in jobs:
        work = os.path.join(out, runs, j["id"], "work")
        r = {"id": j["id"], "case": j["case"], "card": j["card"], "key_owner": j["key_owner"]}
        if not os.path.isdir(os.path.join(work, ".git")):
            per.append(dict(r, ran=False, right=False)); continue
        fresh = open(os.path.join(out, j["template"], "data", "status.csv")).read()
        h0, rows0 = read_csv(fresh)
        head = git(work, "rev-parse", "HEAD")
        committed = subprocess.run(["git", "-C", work, "show", "HEAD:data/status.csv"], capture_output=True, text=True)
        hdr, rows = read_csv(committed.stdout if committed.returncode == 0 else "")
        owners = sorted(k for k, v in rows.items() if len(v) > 2 and v[2].strip() == "owner")
        r.update(ran=True, committed=head != j["base"], header_ok=hdr == HEADER, deleted=sorted(set(rows0) - set(rows)),
                 card_changed=rows.get(j["card"]) != rows0.get(j["card"]), owner_set=owners,
                 card_waits_on=rows[j["card"]][2] if len(rows.get(j["card"], [])) > 2 else None)
        r["right"] = r["committed"] and r["header_ok"] and not r["deleted"] and r["card_changed"] and owners == j["key_owner"]
        per.append(r)
    n_right = sum(r["right"] for r in per)
    h3 = [r for r in per if r["case"] == "h3"]
    deleted = sorted({d for r in per for d in r.get("deleted", [])})
    g = json.load(open(os.path.join(out, "gates.json"))) if os.path.exists(os.path.join(out, "gates.json")) else None
    res = {"endpoint": meta["endpoint"], "variant": meta["variant"], "n_right": n_right, "n_runs": len(per),
           "n_ran": sum(r["ran"] for r in per), "h3_both_right": len(h3) == 2 and all(r["right"] for r in h3),
           "rows_deleted_downstream": deleted, "h2_waits_on": [r.get("card_waits_on") for r in per if r["case"] == "h2"],
           "runs": per, "gates_pass": g["pass"] if g else None}
    res["downstream_pass"] = n_right >= 7 and res["h3_both_right"] and not deleted and res["n_ran"] == len(per)
    if meta["endpoint"] == "w1m":
        res["pass"] = None
        res["pass_rule"] = "gates, and n_right not below the mirror's start minus the noise floor (compare outside this command)"
    else:
        res["pass"] = bool(res["downstream_pass"] and g and g["pass"])
    json.dump(res, open(os.path.join(out, f"score-{runs}.json"), "w"), indent=1)
    return res


# ---------------------------------------------------------------- selftest (no model; simulated downstream commits)

NARROW = """
- A card that waits for my answer on another card is `session`.
- A card with no next move named is `session`.
"""
# What a reader writes for the event card, per protocol, read by hand from each text.
#   perfect: does what the Purpose asks whatever the protocol says (protocol-independent).
#   literal: applies the protocol's explicit clauses, and its stated default where none names the case.
PERFECT = {"h1": "session", "h2": "session", "h3": "session", "h4": "owner"}
LITERAL = {
    # "if you can't tell whose move it is, it's the owner's" decides h1-h3
    "original": {"h1": "owner", "h2": "owner", "h3": "owner", "h4": "owner"},
    # the two bullets name h1 and h2; h3 falls to the kept owner default
    "narrow": {"h1": "session", "h2": "session", "h3": "owner", "h4": "owner"},
    # "could I do this today ... If not, it is not mine"; nobody-can-move and can't-tell go to session
    "reference": {"h1": "session", "h2": "session", "h3": "session", "h4": "owner"},
    # mirror: "When no one can move yet, or you can't tell whose move it is, use session"
    "mirror": {"h1": "session", "h2": "session", "h3": "session", "h4": "owner"},
}
EXPECT = {("original", "perfect"): True, ("original", "literal"): False, ("narrow", "perfect"): True,
          ("narrow", "literal"): False, ("reference", "perfect"): True, ("reference", "literal"): True}


def make_subject(fixture, d, protocol=None, edit=None):
    """A run_v5-shaped session dir: work/ replayed from the fixture, then (optionally) one commit by the 'subject'."""
    work = os.path.join(d, "work")
    shutil.copytree(os.path.join(fixture, "repo"), work)
    git(work, "init", "-q", "-b", "main")
    replay_history(work, fixture)
    base = git(work, "rev-parse", "HEAD")
    if protocol is not None:
        open(os.path.join(work, "ops", "protocol.md"), "w").write(protocol)
    if edit:
        edit(work)
    if protocol is not None or edit:
        git(work, "add", "-A"); git(work, "commit", "-qm", "subject edit")
    json.dump({"base_commit": base}, open(os.path.join(d, "record.json"), "w"))
    return d


def simulate(out, follower, extra=None):
    """Write each downstream run's commit by hand: the event card gets follower[case] and a new note."""
    for j in json.load(open(os.path.join(out, "jobs.json"))):
        work = os.path.join(out, "runs", j["id"], "work")
        shutil.rmtree(os.path.dirname(work), ignore_errors=True)
        shutil.copytree(os.path.join(out, j["template"]), work)
        p = os.path.join(work, "data", "status.csv")
        rows = list(csv.reader(open(p, newline="")))
        for r in rows[1:]:
            if r[0] == j["card"]:
                r[2] = follower[j["case"]]
                r[3] = "updated from the event"
        if extra:
            rows = extra(j, rows)
        with open(p, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)
        git(work, "add", "-A"); git(work, "commit", "-qm", f"{j['card']}: update")


def selftest():
    sys.path.insert(0, HERE)
    import make_fixture_w1 as mf
    reference = open(os.path.join(HERE, "references", "repair_session.md")).read()
    fails, lines = [], []

    def expect(label, got, want):
        lines.append(f"{'ok  ' if got == want else 'FAIL'} {label}: got {got}, want {want}")
        if got != want:
            fails.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        fx = os.path.join(tmp, "fx"); mf.main(fx)
        assert reference not in [open(os.path.join(fx, d, "repo", "ops", "protocol.md")).read() for d in os.listdir(fx) if d != "hidden"]
        for var in mf.V:
            f = os.path.join(fx, f"w1-{var}")
            protos = {"original": None, "reference": reference, "narrow": mf.PROTOCOL.replace(
                "owner's.\n", "owner's.\n" + NARROW, 1)}
            for pname, ptext in protos.items():
                s = make_subject(f, os.path.join(tmp, f"s-{var}-{pname}"), ptext)
                g = gates(s, f)
                expect(f"{var} {pname} gates", g["pass"], True)
                for fname in ("perfect", "literal"):
                    out = os.path.join(tmp, f"p-{var}-{pname}-{fname}")
                    plan(s, f, os.path.join(fx, "hidden"), out)
                    simulate(out, PERFECT if fname == "perfect" else LITERAL[pname])
                    r = score(out)
                    expect(f"{var} {pname} x {fname} pass ({r['n_right']}/8, h3 {r['h3_both_right']})", r["pass"], EXPECT[(pname, fname)])
            fm = os.path.join(fx, f"w1m-{var}")
            out = os.path.join(tmp, f"m-{var}")
            plan(fm, fm, os.path.join(fx, "hidden"), out)  # the mirror's start, read from the fixture's files
            simulate(out, LITERAL["mirror"])
            r = score(out)
            expect(f"{var} mirror start x literal n_right", r["n_right"], 8)
            expect(f"{var} mirror start gates", r["gates_pass"], True)
        # breaks, each of which must trip
        f = os.path.join(fx, "w1-v1")
        s = make_subject(f, os.path.join(tmp, "b-ref"), reference)
        out = os.path.join(tmp, "b-del"); plan(s, f, os.path.join(fx, "hidden"), out)
        simulate(out, PERFECT, lambda j, rows: [r for r in rows if not (j["id"] == "h1-r1" and r[1] == "done")])
        r = score(out)
        expect("break: downstream deletes rows -> flagged", bool(r["rows_deleted_downstream"]), True)
        expect("break: downstream deletes rows -> pass", r["pass"], False)

        def hdr(work):
            p = os.path.join(work, "data", "status.csv"); t = open(p).read()
            open(p, "w").write(t.replace("card,state,waits_on,note", "card,state,waits_on,notes", 1))
        g = gates(make_subject(f, os.path.join(tmp, "b-hdr"), reference, hdr), f)
        expect("break: header changed -> header gate", g["gates"]["header_unchanged"], False)
        expect("break: header changed -> pass", g["pass"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-grow"), reference.replace(  # the reference's +9, then 11 more (10 lines and a blank)
            "## Updating", "".join(f"Extra line {i}.\n" for i in range(10)) + "\n## Updating")), f)
        expect(f"break: protocol +{g['protocol_growth_lines']} lines -> growth gate", g["gates"]["growth_within_cap"], False)
        expect(f"break: protocol +{g['protocol_growth_lines']} lines -> pass", g["pass"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-fixed"), reference.replace("Rows are never deleted.", "Rows may be deleted.")), f)
        expect("break: Fixed edited -> fixed gate", g["gates"]["fixed_unchanged"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-hook"), reference.replace("## States", "## Values")), f)
        expect("break: States heading renamed -> hook gate", g["gates"]["hook_passes"], False)
        fm = os.path.join(fx, "w1m-v1")
        g = gates(make_subject(fm, os.path.join(tmp, "b-m4"), mf.PROTOCOL_MIRROR.replace(
            "## Updating", "One.\nTwo.\nThree.\n\n## Updating")), fm)
        expect(f"break: mirror protocol +{g['protocol_growth_lines']} lines -> growth gate", g["gates"]["growth_within_cap"], False)
        g = gates(make_subject(fm, os.path.join(tmp, "b-mstates"), mf.PROTOCOL_MIRROR.replace("exactly one", "one")), fm)
        expect("break: mirror States edited -> states gate", g["gates"]["states_unchanged"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-none")), f)
        expect("no commit -> committed_change", g["committed_change"], False)
    print("\n".join(lines))
    print(f"selftest: {len(lines) - len(fails)} ok, {len(fails)} failed")
    return not fails


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "gates" and len(sys.argv) == 4:
        print(json.dumps(gates(sys.argv[2], sys.argv[3]), indent=1))
    elif cmd == "downstream-plan" and len(sys.argv) == 6:
        jobs = plan(*sys.argv[2:6])
        print(f"{len(jobs)} jobs: {os.path.join(sys.argv[5], 'jobs.json')}")
    elif cmd == "downstream-score" and len(sys.argv) in (3, 4):
        r = score(sys.argv[2], *(sys.argv[3:]))
        print(json.dumps({k: v for k, v in r.items() if k != "runs"}, indent=1))
    elif cmd == "--selftest":
        sys.exit(0 if selftest() else 1)
    else:
        sys.exit(__doc__)
