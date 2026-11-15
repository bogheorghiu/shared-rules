import json, os, glob, random, subprocess, sys
S = sys.argv[1]
sess = sorted(glob.glob(S + "/pilot3/sessions/*") + glob.glob(S + "/pilot4/sessions/*"))
random.Random(9157).shuffle(sess)
key = {}
def git(repo, *a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
for i, d in enumerate(sess, 1):
    code = f"V{i:02d}"; key[code] = os.path.basename(d)
    rec = json.load(open(d + "/record.json"))
    repo = d + "/archive/T2/repo"
    parts = []
    results = {}
    lines = [json.loads(l) for l in open(d + "/transcripts/T2.jsonl") if l.strip().startswith("{")]
    for e in lines:
        if e.get("type") == "user":
            c = e.get("message", {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_result":
                        t = b.get("content")
                        if isinstance(t, list): t = "\n".join(x.get("text", "") for x in t if isinstance(x, dict))
                        results[b.get("tool_use_id")] = str(t)[:1500]
    for e in lines:
        if e.get("type") == "assistant":
            for b in e["message"]["content"]:
                if b.get("type") == "text": parts.append("ASSISTANT TEXT:\n" + b["text"])
                elif b.get("type") == "tool_use":
                    parts.append(f"TOOL CALL [{b['name']}]: " + json.dumps(b["input"]))
                    parts.append("TOOL RESULT: " + results.get(b["id"], "(none recorded)"))
    turn = "\n\n".join(parts)
    base = rec["turns"][0]["head"]
    f = subprocess.run(["git", "-C", repo, "show", "HEAD:data/2026-01.csv"], capture_output=True, text=True)
    fil = f.stdout if f.returncode == 0 else "(file not at HEAD)"
    log = git(repo, "log", "--oneline", f"{base}..HEAD") or "(no commits in this turn)"
    rp = os.path.realpath(d)
    pkt = (f"Session {code}.\n\n=== USER PROMPT (this turn) ===\n{rec['turns'][1]['sent']}\n\n=== TURN RECORD ===\n{turn}\n\n"
           f"=== PRIMARY RECORD: git show HEAD:data/2026-01.csv ===\n{fil}\n=== PRIMARY RECORD: commits made this turn ===\n{log}\n")
    pkt = pkt.replace(rp, "<RUN>").replace(S, "<TMP>")
    open(f"{S}/verify/{code}.txt", "w").write(pkt)
json.dump(key, open(f"{S}/verify/key.json", "w"), indent=1)
print(len(key), "packets", max(os.path.getsize(f"{S}/verify/{c}.txt") for c in key))
