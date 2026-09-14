"""The agent itself: the loop that asks the model, runs tools and hands back results.

It doesn't know how it was started, who approves changes, or where records go.
Whoever calls run() decides all of that. That is what lets a person, a schedule,
a harness or a test all drive the same loop.
"""

import tools

SYSTEM = (
    "You are a careful file assistant working inside one folder. "
    "Use your tools to complete the task. When finished, use write_file to update "
    "'memory.md' with a short note on what you did and learned, then summarise for the user."
)

def run(client, workspace, task, approve, record, report, model="claude-haiku-4-5"):
    memory_path = workspace / "memory.md"
    memory = memory_path.read_text() if memory_path.exists() else "(no memory yet - first run)"
    messages = [{"role": "user", "content": f"Your memory from previous runs:\n{memory}\n\nToday's task: {task}"}]

    for _ in range(20):                     # safety cap: a confused agent can't loop forever
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM,
            tools=tools.TOOLS,
            messages=messages,
        )
        record["input_tokens"] += response.usage.input_tokens
        record["output_tokens"] += response.usage.output_tokens
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n{block.text}")
                report.append(block.text)
        if response.stop_reason != "tool_use":
            break                           # no more tool requests: the agent is done
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}")
                report.append(f"- tool: {block.name} {block.input}")
                record["tools"].append({"name": block.name, "input": block.input})
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tools.run_tool(workspace, block.name, block.input, approve),
                })
        messages.append({"role": "user", "content": results})
