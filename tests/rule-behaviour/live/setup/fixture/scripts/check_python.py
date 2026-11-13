"""Print ok if this interpreter meets pyproject.toml's requires-python."""
import re, sys
need = re.search(r'requires-python = ">=(\d+)\.(\d+)"', open("pyproject.toml").read())
want = (int(need.group(1)), int(need.group(2)))
if sys.version_info[:2] >= want:
    print("ok")
else:
    sys.exit(f"need Python {want[0]}.{want[1]}+, have {sys.version.split()[0]}")
