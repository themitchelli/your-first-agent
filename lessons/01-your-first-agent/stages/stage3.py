"""Stage 3: hands that change things, with permission.

Run:  python stage3.py demo "Rename the worst-named file in this folder to something sensible"
Expected: the agent reads files, picks a victim, and asks y/n before renaming.
Say n on a second run and confirm it respects the refusal.

Also try the security test (it should FAIL, on purpose):
  python -c "import pathlib, stage3; stage3.read_file(pathlib.Path('demo'), '../stage3.py')"
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

def write_file(workspace, name, content):
    answer = input(f"\n  Agent wants to write '{name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this write."
    path = safe_path(workspace, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"Wrote {name}."

def move_file(workspace, name, new_name):
    answer = input(f"\n  Agent wants to move '{name}' -> '{new_name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this move."
    src = safe_path(workspace, name)
    dst = safe_path(workspace, new_name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    return f"Moved {name} to {new_name}."

import anthropic

TOOLS = [
    {
        "name": "list_files",
        "description": "List every file in the workspace folder, with sizes.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Read one file from the workspace folder.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Path relative to the workspace"}},
            "required": ["name"],
        },
    },
    {
        "name": "write_file",
        "description": "Write a file in the workspace folder. The user is asked to approve first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Path relative to the workspace"},
                "content": {"type": "string"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "move_file",
        "description": "Move or rename a file inside the workspace folder. The user is asked to approve first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Current path relative to the workspace"},
                "new_name": {"type": "string", "description": "New path relative to the workspace"},
            },
            "required": ["name", "new_name"],
        },
    },
]

def run_tool(workspace, name, args):
    try:
        if name == "list_files":
            return list_files(workspace)
        if name == "read_file":
            return read_file(workspace, args["name"])
        if name == "write_file":
            return write_file(workspace, args["name"], args["content"])
        if name == "move_file":
            return move_file(workspace, args["name"], args["new_name"])
        return f"Unknown tool: {name}"
    except Exception as error:
        return f"Error: {error}"

def main():
    workspace = pathlib.Path(sys.argv[1])
    task = sys.argv[2]
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]

    for _ in range(20):                     # safety cap: a confused agent can't loop forever
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            tools=TOOLS,
            messages=messages,
        )
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n{block.text}")
        if response.stop_reason != "tool_use":
            break                           # no more tool requests: the agent is done
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(workspace, block.name, block.input),
                })
        messages.append({"role": "user", "content": results})

if __name__ == "__main__":        # run only when started directly, not when imported by a test
    main()
