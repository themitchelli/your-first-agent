"""Your first agent.

An agent is four things: a model, tools, memory, and a trigger.

  Model   - the LLM we call over the API (here: Claude Haiku, cheap and fast)
  Tools   - three functions that let it see and touch ONE folder on your machine
  Memory  - a markdown file it reads at the start and updates at the end
  Trigger - you, for now: `python agent.py <folder> "<task>"`

Everything else in this file is the "inner loop": ask the model what to do,
run the tool it asks for, show it the result, repeat until it says it's done.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py demo "Organise this folder and tell me what's in it"
"""

import json
import pathlib
import sys

import anthropic

MODEL = "claude-haiku-4-5"
MAX_TURNS = 20  # safety net: a confused agent can't spend money forever
MEMORY_FILE = "memory.md"


# ---------------------------------------------------------------- the tools
# Each tool is a plain Python function, scoped to one folder (the workspace).
# The agent cannot see or touch anything outside it.

def list_files(workspace: pathlib.Path) -> str:
    lines = []
    for path in sorted(workspace.rglob("*")):
        if path.is_file():
            rel = path.relative_to(workspace)
            lines.append(f"{rel}  ({path.stat().st_size} bytes)")
    return "\n".join(lines) or "(the folder is empty)"


def safe_path(workspace: pathlib.Path, name: str) -> pathlib.Path:
    """Refuse any path that escapes the workspace."""
    path = (workspace / name).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ValueError(f"'{name}' is outside the workspace - refused")
    return path


def read_file(workspace: pathlib.Path, name: str) -> str:
    return safe_path(workspace, name).read_text()


def write_file(workspace: pathlib.Path, name: str, content: str) -> str:
    # The safety rail: the agent must ask you before it changes anything.
    answer = input(f"\n  Agent wants to write '{name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this write."
    path = safe_path(workspace, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"Wrote {name} ({len(content)} characters)."


def move_file(workspace: pathlib.Path, name: str, new_name: str) -> str:
    answer = input(f"\n  Agent wants to move '{name}' -> '{new_name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this move."
    src = safe_path(workspace, name)
    dst = safe_path(workspace, new_name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    return f"Moved {name} to {new_name}."


# The schemas tell the model what tools exist and what arguments they take.
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


def run_tool(workspace: pathlib.Path, name: str, args: dict) -> str:
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


# ---------------------------------------------------------------- the agent

def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: python agent.py <folder> "<task>"')
        sys.exit(1)

    workspace = pathlib.Path(sys.argv[1])
    task = sys.argv[2]
    if not workspace.is_dir():
        print(f"'{workspace}' is not a folder.")
        sys.exit(1)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    # MEMORY: whatever the agent wrote last time, it sees this time.
    memory_path = workspace / MEMORY_FILE
    memory = memory_path.read_text() if memory_path.exists() else "(no memory yet - this is my first run)"

    system = (
        "You are a careful file assistant working inside one folder (the workspace). "
        "Use your tools to complete the user's task. "
        f"When the task is finished, use write_file to update '{MEMORY_FILE}' with a short note on "
        "what you did and anything useful you learned, then give the user a plain-language summary."
    )

    messages = [{
        "role": "user",
        "content": f"Your memory from previous runs:\n{memory}\n\nToday's task: {task}",
    }]

    # THE INNER LOOP. This is the whole mystery of agents:
    # ask the model -> run the tool it asks for -> show it the result -> repeat.
    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        # Print anything the model says out loud.
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n{block.text}")

        if response.stop_reason != "tool_use":
            break  # no more tool calls: the agent is done

        # Run every tool the model asked for and collect the results.
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name} {json.dumps(block.input)[:80]}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(workspace, block.name, block.input),
                })
        messages.append({"role": "user", "content": results})
    else:
        print(f"\nStopped after {MAX_TURNS} turns (safety limit).")


if __name__ == "__main__":
    main()
