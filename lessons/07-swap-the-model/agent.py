"""Your first agent, with two seams so a harness can plug in.

Identical to post 4's agent.py (lessons/04-hands-and-memory) except for two changes, marked SEAM:

  1. The model is a parameter, not hardcoded.
  2. Approval is a function you pass in. People get ask_human (type y);
     the harness passes one that always says yes and counts the approvals.

Run it yourself exactly as before:
  python agent.py demo "Organise this folder into subfolders"
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

def ask_human(question):
    return input(f"\n  {question} [y/n] ").strip().lower() == "y"

def write_file(workspace, name, content, approve):          # SEAM 2: approve is passed in
    if not approve(f"Agent wants to write '{name}' - allow?"):
        return "The user declined this write."
    path = safe_path(workspace, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"Wrote {name}."

def move_file(workspace, name, new_name, approve):
    if not approve(f"Agent wants to move '{name}' -> '{new_name}' - allow?"):
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

def run_tool(workspace, name, args, approve):
    try:
        if name == "list_files":
            return list_files(workspace)
        if name == "read_file":
            return read_file(workspace, args["name"])
        if name == "write_file":
            return write_file(workspace, args["name"], args["content"], approve)
        if name == "move_file":
            return move_file(workspace, args["name"], args["new_name"], approve)
        return f"Unknown tool: {name}"
    except Exception as error:
        return f"Error: {error}"

def run(workspace, task, model="claude-haiku-4-5", approve=ask_human, quiet=False):
    """Run the agent once. Returns what a harness needs to know about the run."""
    client = anthropic.Anthropic()
    stats = {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0}

    memory_path = workspace / "memory.md"
    memory = memory_path.read_text() if memory_path.exists() else "(no memory yet - first run)"
    system = (
        "You are a careful file assistant working inside one folder. "
        "Use your tools to complete the task. When finished, use write_file to update "
        "'memory.md' with a short note on what you did and learned, then summarise for the user."
    )
    messages = [{"role": "user", "content": f"Your memory from previous runs:\n{memory}\n\nToday's task: {task}"}]

    for _ in range(20):                     # safety cap: a confused agent can't loop forever
        response = client.messages.create(
            model=model,                    # SEAM 1: the model is a parameter
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        stats["input_tokens"] += response.usage.input_tokens
        stats["output_tokens"] += response.usage.output_tokens
        for block in response.content:
            if block.type == "text" and block.text.strip() and not quiet:
                print(f"\n{block.text}")
        if response.stop_reason != "tool_use":
            break                           # no more tool requests: the agent is done
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                stats["tool_calls"] += 1
                if not quiet:
                    print(f"  [tool] {block.name}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(workspace, block.name, block.input, approve),
                })
        messages.append({"role": "user", "content": results})
    return stats

def main():
    run(pathlib.Path(sys.argv[1]), sys.argv[2])

if __name__ == "__main__":        # run only when started directly, not when imported by a test
    main()
