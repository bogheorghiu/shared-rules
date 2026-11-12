#!/usr/bin/env python3
"""Check that pyproject.toml, pkg/__init__.py and the dist/ bundle agree on the version."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
a = re.search(r'^version = "([^"]+)"', (root / "pyproject.toml").read_text(), re.M).group(1)
b = re.search(r'^__version__ = "([^"]+)"', (root / "pkg" / "__init__.py").read_text(), re.M).group(1)
problems = []
if a != b:
    problems.append(f"pyproject.toml says {a}, pkg/__init__.py says {b}")
if not (root / "dist" / f"tally-{a}").is_dir():
    problems.append(f"no bundle at dist/tally-{a}")
print("\n".join(problems) or f"ok: {a}")
sys.exit(1 if problems else 0)
