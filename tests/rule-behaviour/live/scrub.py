#!/usr/bin/env python3
"""Copy a run folder's record and transcripts into the repository with identifying text removed.

    python3 -I scrub.py <run-folder> <dest-folder>

The repository is public. Replaced: the run's absolute paths (they contain host and session
paths) with <RUN>, every UUID with <uuid-N> (consistent within the run), any e-mail
address with <email>. Afterwards the copy is scanned for words that must never appear; a hit
stops with an error and nothing is left half-copied.
"""
import os, re, shutil, sys

UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
FORBIDDEN = re.compile(r"claude\.ai/code|session_0|cse_0|/tmp/claude-0|scratchpad|oauth|sk-ant", re.I)


def scrub(text, run, ids):
    text = text.replace(os.path.abspath(run), "<RUN>")
    text = re.sub(r"/tmp/claude-0/[^\s\"']*", "<TMP>", text)
    text = re.sub(r"[-\w.]*scratchpad[-\w.]*", "<TMP>", text)  # the path again, flattened into a folder name
    text = UUID.sub(lambda m: ids.setdefault(m.group(0).lower(), f"<uuid-{len(ids) + 1}>"), text)
    return EMAIL.sub(lambda m: m.group(0) if m.group(0).endswith("example.invalid") else "<email>", text)


def main(run, dest):
    ids, tmp = {}, dest + ".partial"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, "transcripts"))
    files = ["record.json"] + [os.path.join("transcripts", f) for f in sorted(os.listdir(os.path.join(run, "transcripts")))]
    for rel in files:
        text = scrub(open(os.path.join(run, rel)).read(), run, ids)
        hit = FORBIDDEN.search(text)
        if hit:
            shutil.rmtree(tmp)
            sys.exit(f"forbidden text {hit.group(0)!r} left in {rel}")
        open(os.path.join(tmp, rel), "w").write(text)
    shutil.rmtree(dest, ignore_errors=True)
    os.rename(tmp, dest)
    print(f"{dest}: {len(files)} files, {len(ids)} ids replaced")


if __name__ == "__main__":
    main(*sys.argv[1:3])
