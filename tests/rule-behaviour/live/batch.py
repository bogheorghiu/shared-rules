#!/usr/bin/env python3
"""Batch driver for the registered run (PREREG-live-2026-11-12.md, Running).

    python3 -I batch.py --out <dir outside the repository> [--only <list.json>] [--stop-usd 95] [--jobs 8]

Builds the 80 sessions (2 scenarios x 2 readers x 2 arms x 10) as one list, interleaved:
each block of 8 holds every cell once, in an order rotated from block to block, and runs
them `--jobs` at a time with run.py. `--only` runs a given list instead (reruns of void
sessions: a JSON list of [scenario, arm, reader]).

What it prints is limited to what the person running may read before every record exists:
per session and turn, rc, the cumulative cost and the denials. run.py's full progress lines
(context size, offer flag) go to a log file per session under <out>/logs/, unread until the
end. Stop condition: when the CLI cost estimate summed over all sessions (finished and
running) passes --stop-usd, every running session is stopped, nothing more starts, and the
batch exits 3 with the partial state in <out>/batch-state.json.

Changes none of the hashed files, and refuses to start if --out is inside the repository.
"""
import argparse, itertools, json, os, re, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CELLS = list(itertools.product(("S1", "S2"), ("sonnet-medium", "opus-low"), ("control", "rule")))
LINE = re.compile(r"^(?P<name>\S+) (?P<turn>t\d+): rc=(?P<rc>-?\d+) .* cost=(?P<cost>\S+) offer=\S+ denials=(?P<den>\d+)")


def interleaved(reps=10):
    out = []
    for b in range(reps):
        k = (3 * b) % len(CELLS)  # rotate the cell order each block
        out += [(s, arm, r) for (s, r, arm) in CELLS[k:] + CELLS[:k]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only")
    ap.add_argument("--stop-usd", type=float, default=95.0)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--tag", default="reg")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == REPO or out.startswith(REPO + os.sep):
        sys.exit("--out must be outside the repository")
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    todo = [tuple(x) for x in json.load(open(a.only))] if a.only else interleaved()
    state = {"planned": [list(x) for x in todo], "sessions": {}, "stopped": None}
    lock, procs, cost = threading.Lock(), {}, {}
    queue = list(enumerate(todo))

    def save():
        state["total_cost_usd"] = round(sum(cost.values()), 4)
        json.dump(state, open(os.path.join(out, "batch-state.json"), "w"), indent=1)

    def worker():
        while True:
            with lock:
                if not queue or state["stopped"]:
                    return
                i, (sc, arm, reader) = queue.pop(0)
            key = f"{i:02d}-{sc}-{arm}-{reader}"
            log = open(os.path.join(out, "logs", key + ".log"), "w")
            p = subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "run.py"), "--scenario", sc, "--arm", arm,
                                  "--reader", reader, "--out", os.path.join(out, "runs"), "--tag", a.tag],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, stdin=subprocess.DEVNULL)
            with lock:
                procs[key] = p
                state["sessions"][key] = {"cell": [sc, arm, reader], "status": "running", "turns": []}
            for line in p.stdout:
                log.write(line); log.flush()
                m = LINE.match(line)
                if m:
                    c = float(m["cost"]) if m["cost"] not in ("None", "") else 0.0
                    with lock:
                        cost[key] = max(cost.get(key, 0.0), c)
                        state["sessions"][key]["turns"].append({"turn": m["turn"], "rc": int(m["rc"]), "cost": c,
                                                                "denials": int(m["den"])})
                        total = sum(cost.values())
                        print(f"{key} {m['turn']} rc={m['rc']} cost={c} denials={m['den']} | batch total ${total:.2f}",
                              flush=True)
                        if total > a.stop_usd and not state["stopped"]:
                            state["stopped"] = f"CLI cost estimate ${total:.2f} passed ${a.stop_usd} during {key} {m['turn']}"
                            for q in procs.values():
                                if q.poll() is None:
                                    q.terminate()
                        save()
                elif line.startswith("record: "):
                    with lock:
                        state["sessions"][key]["record"] = line.split("record: ", 1)[1].strip()
            rc = p.wait()
            with lock:
                state["sessions"][key].update(status="done" if rc == 0 else f"exit {rc}", exit=rc)
                save()
            print(f"{key} finished exit={rc}", flush=True)

    threads = [threading.Thread(target=worker) for _ in range(a.jobs)]
    for t in threads:
        t.start()
        time.sleep(2)  # stagger start-up so session folders and CLI start-up don't collide
    for t in threads:
        t.join()
    save()
    print("stopped:" if state["stopped"] else "all sessions finished;", state["stopped"] or "", f"total ${state['total_cost_usd']}")
    sys.exit(3 if state["stopped"] else 0)


if __name__ == "__main__":
    main()
