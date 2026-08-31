"""Stage 1: tools, with no AI at all.

Run:  python stage1.py demo
Expected: your demo files listed with sizes. No API call, costs nothing.

Also try the security test (it should FAIL, on purpose):
  python -c "import pathlib, stage1; stage1.read_file(pathlib.Path('demo'), '../stage1.py')"
"""

import pathlib
import sys

def list_files(workspace):
    lines = []
    for path in sorted(workspace.rglob("*")):
        if path.is_file():
            rel = path.relative_to(workspace)
            lines.append(f"{rel}  ({path.stat().st_size} bytes)")
    return "\n".join(lines) or "(the folder is empty)"

def safe_path(workspace, name):
    path = (workspace / name).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ValueError(f"'{name}' is outside the workspace - refused")
    return path

def read_file(workspace, name):
    return safe_path(workspace, name).read_text()

# Temporary test line - we delete this in stage 2
print(list_files(pathlib.Path(sys.argv[1])))
