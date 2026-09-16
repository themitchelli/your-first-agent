"""Stage 2: the model meets one tool.

Run:  python stage2.py demo "What kinds of files are in this folder?"
Expected: "[tool] list_files" flashes past, then a description of your mess.
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

import anthropic

TOOLS = [
    {
        "name": "list_files",
        "description": "List every file in the workspace folder, with sizes.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

def run_tool(workspace, name, args):
    if name == "list_files":
        return list_files(workspace)
    return f"Unknown tool: {name}"

# ---- the agent ----

def main():
    workspace = pathlib.Path(sys.argv[1])
    task = sys.argv[2]
    client = anthropic.Anthropic()
    system = "You are a careful file assistant working inside one folder. Use your tools to complete the task."
    messages = [{"role": "user", "content": task}]

    for _ in range(20):                     # safety cap: a confused agent can't loop forever
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            system=system,
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
