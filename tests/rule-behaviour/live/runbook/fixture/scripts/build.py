#!/usr/bin/env python3
"""Build a source bundle in dist/tally-<version>/.

    python3 scripts/build.py [--legacy-imports]

--legacy-imports also writes pkg/_legacy.py into the bundle, which re-exports
group_totals and parse_amount under their pre-1.0 names (sum_by, to_decimal).
"""
import pathlib, re, shutil, sys

root = pathlib.Path(__file__).resolve().parent.parent
version = re.search(r'^version = "([^"]+)"', (root / "pyproject.toml").read_text(), re.M).group(1)
out = root / "dist" / f"tally-{version}"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(root / "pkg", out / "pkg", ignore=shutil.ignore_patterns("__pycache__"))
shutil.copy(root / "pyproject.toml", out)
if "--legacy-imports" in sys.argv[1:]:
    (out / "pkg" / "_legacy.py").write_text(
        "from .core import group_totals as sum_by, parse_amount as to_decimal  # noqa: F401\n")
print(f"built {out.relative_to(root)}" + (" (with legacy imports)" if "--legacy-imports" in sys.argv[1:] else ""))
