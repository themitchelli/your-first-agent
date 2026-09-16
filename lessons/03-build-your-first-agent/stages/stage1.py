"""Stage 1: tools, with no AI at all.

Run:  python stage1.py demo
Expected: your demo files listed with sizes. No API call, costs nothing.
"""

import pathlib
import sys

# ---- tools ----

def list_files(workspace):
    if not workspace.is_dir():
        return f"There is no folder called '{workspace}' here."
    lines = []
    for path in sorted(workspace.rglob("*")):
        if path.is_file():
            rel = path.relative_to(workspace)
            lines.append(f"{rel}  ({path.stat().st_size} bytes)")
    return "\n".join(lines) or "(the folder is empty)"

# Temporary test line - we delete this in stage 2
print(list_files(pathlib.Path(sys.argv[1])))
