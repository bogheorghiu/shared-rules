#!/usr/bin/env python3
"""Set the package version in pyproject.toml and pkg/__init__.py.

    python3 scripts/set_version.py 1.2.3
"""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
    sys.exit("usage: set_version.py X.Y.Z")
v = sys.argv[1]
for path, pat in ((root / "pyproject.toml", r'^version = "[^"]*"'), (root / "pkg" / "__init__.py", r'^__version__ = "[^"]*"')):
    text = path.read_text()
    new = re.sub(pat, pat.split(" = ")[0].lstrip("^") + f' = "{v}"', text, count=1, flags=re.M)
    path.write_text(new)
    print(f"{path.relative_to(root)}: {v}")
