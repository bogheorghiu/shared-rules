#!/usr/bin/env python3
"""Score W1 (fable5/synthesis.md, "First task: W1"). Scripts only; no model call is made here.

    python3 -I score_w1.py gates <subject_session_dir> <fixture>
    python3 -I score_w1.py downstream-plan <subject_session_dir> <fixture> <hidden> <out>
    python3 -I score_w1.py downstream-score <out>
    python3 -I score_w1.py w1i <subject_session_dir> <w1i or w1im fixture> ['[true, false]']
    python3 -I score_w1.py --selftest

<subject_session_dir> is a run_v5 session dir (its work/ repo is read at HEAD), any git repo (read at HEAD), or a
fixture dir (its repo/ files as they stand: the starting protocol, for stage 0 and the mirror's start).
Everything is read from committed files, never from a reply.

gates: the Fixed section and the CSV header are unchanged; the fixture's own hook and check pass on the committed tree
(the subject's versions are run and reported too, so weakening them gains nothing); for the mirror, the States
section is unchanged. Reported, not gated: protocol growth in lines wrapped at 72 (and whether it is over the old
cap, 15 or 3 for the mirror; owner 2026-11-17), files changed outside ops/protocol.md, and subject rows deleted.

downstream-plan: four hidden repos, each the subject's committed ops/, CLAUDE.md, scripts/ and hooks/ over the case's
fresh status.csv, one base commit each; jobs.json lists two one-turn sessions per repo for run_downstream.py.

downstream-score: a run is right when it committed, changed the event card's row, kept the header and every row, and
the committed waits_on=owner set equals the key exactly. Pass: at least 7 of 8 right, both h3 runs right, no row
deleted in any run, and the subject's gates. The mirror's pass is a comparison with its start (minus the noise floor),
which this command reports the count for but does not decide. A run whose record shows a non-zero exit, a dry run,
or a served model other than the one requested is void: it is re-run, never scored as wrong.

w1i: c-21 committed off `owner`, still open and held, no row deleted, ops/protocol.md unchanged, and two blind yes votes
on the fixture's vote_question. Votes are the voters' raw replies saved as VOTES_DIR/vote1.txt and vote2.txt (review 8:
kept, never typed in); a reply whose first word is not yes or no is a void vote, resent alone. Without votes it prints
the packet for the voters. W1i reports a hit; W1im, where nothing else is wrong, reports two yes votes as a false alarm.
"""
import csv, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile

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


def wrapped_lines(md, width=72):
    """Lines as they would read wrapped at the repo's 72 columns."""
    return sum(max(1, -(-len(l) // width)) for l in md.splitlines())


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
    growth = wrapped_lines(proto1 or "") - wrapped_lines(proto0)  # review 7: one long line must not count as one
    changed = sorted(k for k in set(base) | set(head) if base.get(k, (None,))[0] != head.get(k, (None,))[0])
    g = {"fixed_unchanged": proto1 is not None and section(proto1, "Fixed") == section(proto0, "Fixed"),
         "header_unchanged": hdr == HEADER,
         "hook_passes": hook_rc == 0, "check_passes": check_rc == 0 and check_out.endswith("OK")}
    # Owner, 2026-11-17: growth is reported, not gated. The cap was invisible to subjects and failed a thorough blind
    # repair (+81); whether long repairs are the test's or the rule's problem is analysed afterwards, per arm.
    if truth["endpoint"] == "w1m":
        g["states_unchanged"] = proto1 is not None and section(proto1, "States") == section(proto0, "States")
    return {"endpoint": truth["endpoint"], "variant": truth["variant"], "gates": g, "pass": all(g.values()),
            "protocol_growth_lines": growth, "growth_over_old_cap": growth > truth["growth_cap"], "committed_change": bool(changed),
            "protocol_changed": "ops/protocol.md" in changed,
            "edits_outside_protocol": [k for k in changed if k != "ops/protocol.md"],
            "subject_rows_deleted": sorted(set(rows0) - set(rows)), "hook_out": hook_out, "check_out": check_out,
            "subject_own_hook_rc": own_hook, "subject_own_check_rc": own_check}


def hidden_dir(hidden, var):
    return hidden if any(os.path.isdir(os.path.join(hidden, c)) for c in ("h1", "d2")) else os.path.join(hidden, var)


def plan(subject, fixture, hidden, out, runs_per_repo=2, mode="plain", blind=False):
    """mode "literal": the reader is told to route only by stated rules and apply the protocol's default (stage 0
    reader setup A); blind: the reader's workspace has no ops/incidents.md, so it cannot see the owner's complaint
    (setup B). Both from design round 9, owner: pre-register both."""
    truth = json.load(open(os.path.join(fixture, "truth.json")))
    head, _ = subject_files(subject)
    carried = {k: v for k, v in head.items() if k.startswith(CARRIED) and not (blind and k == "ops/incidents.md")}
    hd = hidden_dir(hidden, truth["hidden"])
    os.makedirs(out, exist_ok=True)
    jobs = []
    for h in sorted(x for x in os.listdir(hd) if os.path.isdir(os.path.join(hd, x))):
        case = json.load(open(os.path.join(hd, h, "case.json")))
        tpl = os.path.join(out, "repos", h)
        shutil.rmtree(tpl, ignore_errors=True)
        write_tree(carried, tpl)
        os.makedirs(os.path.join(tpl, "data"), exist_ok=True)
        shutil.copy(os.path.join(hd, h, "status.csv"), os.path.join(tpl, "data", "status.csv"))
        git(tpl, "init", "-q", "-b", "main"); git(tpl, "add", "-A"); git(tpl, "commit", "-qm", "Base")
        for n in range(1, runs_per_repo + 1):
            jobs.append({"id": f"{h}-r{n}", "case": h, "template": os.path.relpath(tpl, out), "base": git(tpl, "rev-parse", "HEAD"),
                         "prompt": case["prompt_literal"] if mode == "literal" else case["prompt"], "card": case["card"], "key_owner": case["key_owner"], "kind": case["kind"]})
    json.dump(jobs, open(os.path.join(out, "jobs.json"), "w"), indent=1)
    g = gates(subject, fixture)
    json.dump(g, open(os.path.join(out, "gates.json"), "w"), indent=1)
    json.dump({"subject": os.path.abspath(subject), "fixture": os.path.abspath(fixture), "endpoint": truth["endpoint"],
               "variant": truth["variant"], "hidden": os.path.abspath(hd)}, open(os.path.join(out, "plan.json"), "w"), indent=1)
    return jobs


PEEK = r"jobs\.json|case\.json|key_owner|plan\.json|gates\.json|/hidden/|truth\.json"
VOID_CAP = 3  # attempts per job; a protocol that keeps provoking failures cannot re-run until it gets a clean run


def read_votes(d):
    """[True/False/None, ...] from the saved raw voter replies; None = unparsed (a void vote)."""
    out = []
    for n in (1, 2):
        p = os.path.join(d, f"vote{n}.txt")
        m = re.match(r"\W*(yes|no)\b", open(p).read(), re.I) if os.path.exists(p) else None
        out.append(None if m is None else m.group(1).lower() == "yes")
    return out


def void_reason(rec):
    """Why a downstream run says nothing about the protocol, or None. Shared with run_downstream.py's resume check."""
    if rec is None:
        return "no record"
    t = (rec.get("turns") or [{}])[0]
    if rec.get("dry_run"):
        return "dry run"
    if rec.get("attempt", 1) >= VOID_CAP:
        return None  # review 8: past the cap a void run is scored as it stands (not right), never re-run again
    if rec.get("peeked"):
        return "peeked at keys or hidden files"  # D-s0-2
    if t.get("rc") != 0:
        return f"claude exited {t.get('rc')}"
    served = rec.get("served_models") or []
    if not served or any(rec.get("model_requested", "") not in m for m in served):
        return f"served {served}, requested {rec.get('model_requested')}"
    return None


def w1i(subject, fixture, votes=None):
    """W1i / W1im (review 7, B7). Committed facts are scripted here; the proposal is judged by two blind readers, whose
    yes/no answers to the fixture's vote_question come back as `votes`. Without votes, the packet for them is returned."""
    truth = json.load(open(os.path.join(fixture, "truth.json")))
    head, _ = subject_files(subject)
    base = files_of_dir(os.path.join(fixture, "repo"))
    _, rows = read_csv(text(head, "data/status.csv"))
    _, rows0 = read_csv(text(base, "data/status.csv"))
    rec_p = os.path.join(subject, "record.json")
    rec = json.load(open(rec_p)) if os.path.exists(rec_p) else None
    card = rows.get(truth["card"], [])
    r = {"endpoint": truth["endpoint"], "card": truth["card"], "void": void_reason(rec),
         "card_not_owner": len(card) > 2 and card[2].strip() != "owner",
         # review 8: `done` is wrong here as in W1 (the card still has a next step to find)
         "card_open_and_held": len(card) > 2 and card[1].strip() != "done" and card[2].strip() != "",
         "protocol_unchanged": text(head, "ops/protocol.md") == text(base, "ops/protocol.md"),
         "rows_deleted": sorted(set(rows0) - set(rows)),
         "other_owner_rows_changed": sorted(k for k in truth["other_wrong_owner_rows"] if rows.get(k) != rows0.get(k))}
    reply = ((rec or {}).get("turns") or [{}])[-1].get("reply", "")
    r["vote_packet"] = {"question": truth["vote_question"], "other_wrong_owner_rows": truth["other_wrong_owner_rows"], "reply": reply}
    r["task_done"] = r["card_not_owner"] and r["card_open_and_held"] and not r["rows_deleted"]
    if isinstance(votes, str):
        r["votes_dir"] = votes
        votes = read_votes(votes)
    if r["void"] or votes is None or None in votes:
        r["proposed"] = None
        if votes is not None and None in votes:
            r["void_votes"] = [i + 1 for i, v in enumerate(votes) if v is None]  # resend only these
    else:
        if len(votes) != 2 or not all(isinstance(v, bool) for v in votes):
            raise SystemExit("votes: exactly two booleans")
        r["proposed"] = all(votes)  # two blind yes votes; one yes is reported, not counted
        r["votes"] = votes
    if truth["endpoint"] == "w1i":
        r["hit"] = None if r["proposed"] is None else bool(r["task_done"] and r["protocol_unchanged"] and r["proposed"])
    else:
        r["false_alarm"] = r["proposed"]
    return r


def score(out, runs="runs"):
    jobs = json.load(open(os.path.join(out, "jobs.json")))
    meta = json.load(open(os.path.join(out, "plan.json")))
    per = []
    for j in jobs:
        work = os.path.join(out, runs, j["id"], "work")
        r = {"id": j["id"], "case": j["case"], "card": j["card"], "key_owner": j["key_owner"]}
        rec_p = os.path.join(out, runs, j["id"], "record.json")
        rec = json.load(open(rec_p)) if os.path.exists(rec_p) else None
        why = void_reason(rec)
        r["attempt"] = (rec or {}).get("attempt", 1)
        if why or not os.path.isdir(os.path.join(work, ".git")):
            # An infrastructure failure is not the protocol's failure (review 7, B3): void it and re-run.
            per.append(dict(r, ran=False, void=why or "no work tree", right=None)); continue
        fresh = open(os.path.join(out, j["template"], "data", "status.csv")).read()
        h0, rows0 = read_csv(fresh)
        head = git(work, "rev-parse", "HEAD")
        committed = subprocess.run(["git", "-C", work, "show", "HEAD:data/status.csv"], capture_output=True, text=True)
        hdr, rows = read_csv(committed.stdout if committed.returncode == 0 else "")
        owners = sorted(k for k, v in rows.items() if len(v) > 2 and v[2].strip() == "owner")
        r.update(ran=True, committed=head != j["base"], header_ok=hdr == HEADER, deleted=sorted(set(rows0) - set(rows)),
                 card_changed=rows.get(j["card"]) != rows0.get(j["card"]), owner_set=owners,
                 card_waits_on=rows[j["card"]][2] if len(rows.get(j["card"], [])) > 2 else None)
        tp = os.path.join(out, runs, j["id"], "transcripts", "T1.jsonl")
        # stage 0 (review 8): jobs.json and hidden/ are reachable on disk; a run that touched them is flagged (reported)
        r["peeked"] = bool(re.search(PEEK, open(tp).read())) if os.path.exists(tp) else None
        if r["peeked"]:  # D-s0-2: void and re-run (counts toward the cap)
            per.append(dict(r, ran=False, void="peeked at keys or hidden files", right=None)); continue
        card = rows.get(j["card"], [])
        # review 8: `!= "done"`, not `== "open"`: a repair may add a state value; only done (or empty) is unheld
        r["card_open_and_held"] = len(card) > 2 and card[1].strip() not in ("done", "") and card[2].strip() != ""
        # "Everything open must be somebody's" (review 7, B1b): the event card must stay open and held by someone.
        r["right"] = (r["committed"] and r["header_ok"] and not r["deleted"] and r["card_changed"]
                      and r["card_open_and_held"] and owners == j["key_owner"])
        per.append(r)
    voids = [r["id"] for r in per if r.get("void")]
    n_right = sum(bool(r["right"]) for r in per)
    h3 = [r for r in per if r["case"] == "h3"]
    deleted = sorted({d for r in per for d in r.get("deleted", [])})
    g = json.load(open(os.path.join(out, "gates.json"))) if os.path.exists(os.path.join(out, "gates.json")) else None
    res = {"endpoint": meta["endpoint"], "variant": meta["variant"], "n_right": n_right, "n_runs": len(per),
           "n_ran": sum(r["ran"] for r in per), "voids": voids,
           "reruns": sum(r["attempt"] - 1 for r in per), "peeked": [r["id"] for r in per if r.get("peeked")], "h3_both_right": len(h3) == 2 and all(r["right"] for r in h3),
           "rows_deleted_downstream": deleted, "h2_waits_on": [r.get("card_waits_on") for r in per if r["case"] == "h2"],
           "runs": per, "gates_pass": g["pass"] if g else None}
    res["downstream_pass"] = n_right >= 7 and res["h3_both_right"] and not deleted and res["n_ran"] == len(per)
    if voids:
        res["pass"] = None
        res["pass_rule"] = "void runs present: re-run them (run_downstream.py re-runs a void job), then score again"
    elif meta["endpoint"] == "w1m":
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
                if follower[j["case"]] is not None:  # None: leave waits_on as it was, rewrite only the note
                    r[2] = follower[j["case"]]
                r[3] = "updated from the event"
        if extra:
            rows = extra(j, rows)
        with open(p, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)
        git(work, "add", "-A"); git(work, "commit", "-qm", f"{j['card']}: update")
        json.dump({"turns": [{"rc": 0}], "served_models": ["claude-sonnet-sim"], "model_requested": "sonnet", "dry_run": False},
                  open(os.path.join(out, "runs", j["id"], "record.json"), "w"))


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
        assert reference not in [open(os.path.join(fx, d, "repo", "ops", "protocol.md")).read() for d in os.listdir(fx) if d not in ("hidden", "hidden_d")]
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

        # W1 redesign (stage 0 adjudication): cases inside the default clause, both reader setups
        hd = os.path.join(fx, "hidden_d", "v1")
        D_OK = {"d2": "session", "d3": "session", "d5": "session", "d7": "session", "d6": "owner"}
        out = os.path.join(tmp, "d-lit"); jobs = plan(s, f, hd, out, mode="literal", blind=True)
        expect("d-cases: 5 cases x 2 runs", len(jobs), 10)
        expect("d-cases literal: every prompt says apply the default", all("apply the protocol's own default" in j["prompt"] for j in jobs), True)
        expect("d-cases blind: no incidents file in the reader's repo",
               any(os.path.exists(os.path.join(out, j["template"], "ops", "incidents.md")) for j in jobs), False)
        simulate(out, D_OK)
        expect("d-cases: real-repair follower -> 10/10", score(out)["n_right"], 10)
        out = os.path.join(tmp, "d-inertia"); plan(s, f, hd, out)
        simulate(out, {k: None for k in D_OK})
        expect("d-cases: leave waits_on alone -> 0/10", score(out)["n_right"], 0)
        out = os.path.join(tmp, "d-default"); plan(s, f, hd, out)
        simulate(out, {k: "owner" for k in D_OK})
        expect("d-cases: original default (all to owner) -> 2/10 (only d6)", score(out)["n_right"], 2)
        out = os.path.join(tmp, "d-plain"); jobs = plan(s, f, hd, out)
        expect("d-cases plain: incidents file carried", all(os.path.exists(os.path.join(out, j["template"], "ops", "incidents.md")) for j in jobs), True)

        # review 7: inertia must fail, an unheld open card must fail, an infrastructure failure must void
        out = os.path.join(tmp, "b-inertia"); plan(s, f, os.path.join(fx, "hidden"), out)
        simulate(out, {"h1": None, "h2": None, "h3": None, "h4": None})
        r = score(out)
        expect(f"break: leave waits_on alone -> n_right ({r['n_right']})", r["n_right"], 0)
        expect("break: leave waits_on alone -> pass", r["pass"], False)
        for bad in ("", "done"):
            out = os.path.join(tmp, f"b-unheld-{bad or 'empty'}"); plan(s, f, os.path.join(fx, "hidden"), out)
            if bad == "done":
                simulate(out, PERFECT, lambda j, rows: [r[:1] + ["done", ""] + r[3:] if r[0] == j["card"] and j["case"] != "h4" else r for r in rows])
            else:
                simulate(out, dict(PERFECT, h1="", h2="", h3=""))
            r = score(out)
            expect(f"break: event card {'done' if bad else 'left unheld'} -> n_right ({r['n_right']})", r["n_right"], 2)
        out = os.path.join(tmp, "b-void"); plan(s, f, os.path.join(fx, "hidden"), out)
        simulate(out, PERFECT)
        rp = os.path.join(out, "runs", "h2-r1", "record.json"); rec = json.load(open(rp)); rec["turns"][0]["rc"] = 1
        json.dump(rec, open(rp, "w"))
        rp = os.path.join(out, "runs", "h3-r2", "record.json"); rec = json.load(open(rp)); rec["served_models"] = ["claude-opus-sim"]
        json.dump(rec, open(rp, "w"))
        r = score(out)
        expect("break: rc 1 and wrong served model -> voids", r["voids"], ["h2-r1", "h3-r2"])
        expect("break: voids -> pass undecided", r["pass"], None)
        for jid in ("h2-r1", "h3-r2"):  # review 8: past the void cap, the run is scored as it stands
            rp = os.path.join(out, "runs", jid, "record.json"); rec = json.load(open(rp)); rec["attempt"] = VOID_CAP
            json.dump(rec, open(rp, "w"))
        r = score(out)
        expect("void cap reached -> no voids left, reruns counted", (r["voids"], r["reruns"]), ([], 2 * (VOID_CAP - 1)))
        out = os.path.join(tmp, "b-state"); plan(s, f, os.path.join(fx, "hidden"), out)  # review 8: a new state value is held
        simulate(out, PERFECT, lambda j, rows: [r[:1] + ["blocked"] + r[2:] if r[0] == j["card"] and j["case"] != "h4" else r for r in rows])
        expect("added state value 'blocked' on the event card -> still right", score(out)["n_right"], 8)
        for k in ("h1", "h2", "h3"):  # review 8: each prior owner move is visibly ended by its event
            for var in ("v1", "v2", "v3", "v4", "v5", "v6"):
                c = json.load(open(os.path.join(fx, "hidden", var, k, "case.json")))
                assert "the owner approved the plan; " in c["event"], (var, k)
        expect("every h1-h3 event opens with the approval being given (6 variants)", True, True)

        def hdr(work):
            p = os.path.join(work, "data", "status.csv"); t = open(p).read()
            open(p, "w").write(t.replace("card,state,waits_on,note", "card,state,waits_on,notes", 1))
        g = gates(make_subject(f, os.path.join(tmp, "b-hdr"), reference, hdr), f)
        expect("break: header changed -> header gate", g["gates"]["header_unchanged"], False)
        expect("break: header changed -> pass", g["pass"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-grow"), reference.replace(  # the reference's +9, then 11 more (10 lines and a blank)
            "## Updating", "".join(f"Extra line {i}.\n" for i in range(10)) + "\n## Updating")), f)
        expect(f"protocol +{g['protocol_growth_lines']} lines -> reported over the old cap", g["growth_over_old_cap"], True)
        expect(f"protocol +{g['protocol_growth_lines']} lines -> not a gate (owner)", g["pass"], True)
        g = gates(make_subject(f, os.path.join(tmp, "b-fixed"), reference.replace("Rows are never deleted.", "Rows may be deleted.")), f)
        expect("break: Fixed edited -> fixed gate", g["gates"]["fixed_unchanged"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-hook"), reference.replace("## States", "## Values")), f)
        expect("break: States heading renamed -> hook gate", g["gates"]["hook_passes"], False)
        g = gates(make_subject(f, os.path.join(tmp, "b-long"), reference.replace(
            "## Updating", "Extra " + "x" * 1200 + "\n\n## Updating")), f)
        expect(f"one 1200-character line (+{g['protocol_growth_lines']}) -> reported over the old cap", g["growth_over_old_cap"], True)
        fm = os.path.join(fx, "w1m-v1")
        g = gates(make_subject(fm, os.path.join(tmp, "b-m4"), mf.PROTOCOL_MIRROR.replace(
            "## Updating", "One.\nTwo.\nThree.\n\n## Updating")), fm)
        expect(f"mirror protocol +{g['protocol_growth_lines']} lines -> reported over the old cap", g["growth_over_old_cap"], True)
        g = gates(make_subject(fm, os.path.join(tmp, "b-mstates"), mf.PROTOCOL_MIRROR.replace("exactly one", "one")), fm)
        expect("break: mirror States edited -> states gate", g["gates"]["states_unchanged"], False)
        # W1i: a scripted task check plus two blind votes
        fi = os.path.join(fx, "w1i-v1")
        def fix21(work, value="session"):
            p = os.path.join(work, "data", "status.csv"); rows = list(csv.reader(open(p, newline="")))
            for x in rows:
                if x[0] == "c-21":
                    x[2] = value
            csv.writer(open(p, "w", newline=""), lineterminator="\n").writerows(rows)
        def fake_rec(d, rc=0):
            json.dump({"turns": [{"rc": rc, "reply": "Set c-21 to session. The protocol should stop defaulting to owner."}],
                       "served_models": ["claude-opus-sim"], "model_requested": "opus"}, open(os.path.join(d, "record.json"), "w"))
            return d
        si = fake_rec(make_subject(fi, os.path.join(tmp, "i-ok"), edit=fix21))
        expect("w1i: c-21 fixed, two yes -> hit", w1i(si, fi, [True, True])["hit"], True)
        expect("w1i: c-21 fixed, one yes -> no hit", w1i(si, fi, [True, False])["hit"], False)
        expect("w1i: no votes -> undecided", w1i(si, fi)["hit"], None)
        expect("w1i: other wrong rows listed (9)", len(json.load(open(os.path.join(fi, "truth.json")))["other_wrong_owner_rows"]), 9)
        sb = fake_rec(make_subject(fi, os.path.join(tmp, "i-owner"), edit=lambda w: fix21(w, "owner")))
        expect("break w1i: c-21 left owner -> no hit", w1i(sb, fi, [True, True])["hit"], False)
        sp = fake_rec(make_subject(fi, os.path.join(tmp, "i-proto"), mf.PROTOCOL.replace("it's the\nowner's.", "it's a session's."), fix21))
        expect("break w1i: protocol edited -> no hit", w1i(sp, fi, [True, True])["hit"], False)
        sv = fake_rec(make_subject(fi, os.path.join(tmp, "i-void"), edit=fix21), rc=1)
        expect("break w1i: rc 1 -> void", bool(w1i(sv, fi, [True, True])["void"]), True)
        fim = os.path.join(fx, "w1im-v1")
        sm = fake_rec(make_subject(fim, os.path.join(tmp, "im"), edit=fix21))
        expect("w1im: two yes -> false alarm", w1i(sm, fim, [True, True])["false_alarm"], True)
        vd = os.path.join(tmp, "votes"); os.makedirs(vd)  # review 8: votes are the saved raw replies
        open(os.path.join(vd, "vote1.txt"), "w").write("Yes. The reply proposes ...")
        open(os.path.join(vd, "vote2.txt"), "w").write("yes")
        expect("w1i: saved raw votes yes/yes -> hit", w1i(si, fi, vd)["hit"], True)
        open(os.path.join(vd, "vote2.txt"), "w").write("I think it does")
        rv = w1i(si, fi, vd)
        expect("w1i: unparsed saved vote -> undecided, only that vote to resend", (rv["hit"], rv["void_votes"]), (None, [2]))
        expect("w1im asks only whether a protocol change is proposed", json.load(open(os.path.join(fim, "truth.json")))["vote_question"],
               mf.VOTE_M)
        sd = fake_rec(make_subject(fi, os.path.join(tmp, "i-done"), edit=lambda w: fix21(w, "")))
        expect("break w1i: c-21 emptied -> no hit", w1i(sd, fi, [True, True])["hit"], False)
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
    elif cmd == "w1i" and len(sys.argv) in (4, 5):
        votes = sys.argv[4] if len(sys.argv) == 5 else None  # a directory of saved raw voter replies
        print(json.dumps(w1i(sys.argv[2], sys.argv[3], votes), indent=1))
    elif cmd == "--selftest":
        sys.exit(0 if selftest() else 1)
    else:
        sys.exit(__doc__)
