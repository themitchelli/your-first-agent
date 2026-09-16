*Part 3 of [Your First Agent](README.md).*
*Code for this post: [`lessons/03-build-your-first-agent`](../lessons/03-build-your-first-agent).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Build your first agent

Here's the whole secret, before we start: **an agent is about 25 lines of code.** A loop that asks the model what to do next, runs the tool it asks for, and hands back the result. That's it. Everything else in this post makes those 25 lines safe and useful.

Last time you proved your setup works: `check.py` talked to Claude and Claude answered. Today we build the agent itself, a small program that will tidy a messy folder. By the end of this post it can look at the folder and talk about it. The next post gives it hands and a memory. We build it in small steps. Each step adds a few lines, explains what they do and why they're there, and most steps end with something you can run. If a step fails, the fix is in that step, not somewhere behind you.

Type the code rather than pasting it. Typing makes you read every line, and reading every line is the point. Keep VS Code's AI helpers switched off, as in the setup post.

Your file at the end of this post matches `stages/stage2.py` in the [your-first-agent repo](https://github.com/themitchelli/your-first-agent), under `lessons/03-build-your-first-agent`. Use it to compare when something goes wrong, not as a shortcut.

**Start of every session:** open VS Code on your `my-first-agent` folder, open a new terminal, check the line starts with `(.venv)`, and set your key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...             # Mac
$env:ANTHROPIC_API_KEY="sk-ant-..."             # Windows
```

## Stage 0: something to practise on

The agent needs a messy folder to work on. Download the `demo` folder from the repo (it's inside `lessons/03-build-your-first-agent`) and put it inside your `my-first-agent` folder. It holds seven small text files with terrible names: `Untitled document.txt`, `IMG_scan_001 (1).txt`, `doc_final_FINAL.txt` and so on. Each has a few lines of real-looking content, such as a note, an invoice or a recipe.

You can make your own instead. Create a folder called `demo` and put five or so text files in it, with bad names and a few lines of content each. The mess is the point. The agent's job is to make sense of it.

**Checkpoint: the VS Code sidebar shows a `demo` folder with your messy files inside.**

## Stage 1: a tool, with no AI at all

An agent does things through **tools**. A tool is just a normal Python function that the model is allowed to ask for. We'll write the first one and test it on its own, before any AI is involved. This stage costs nothing, because it never calls the API.

### 1a. Two imports

Create a new file called `agent.py` and type:

```python
import pathlib
import sys
```

`import` loads code that comes with Python. `pathlib` handles files and folders. `sys` lets the program read the words you type after `python agent.py` on the command line. That's how you'll tell the agent which folder to work on.

### 1b. The first tool: list the files

Below the imports, leave a blank line and add:

```python
def list_files(workspace):
    lines = []
    for path in sorted(workspace.rglob("*")):
        if path.is_file():
            rel = path.relative_to(workspace)
            lines.append(f"{rel}  ({path.stat().st_size} bytes)")
    return "\n".join(lines) or "(the folder is empty)"
```

Line by line:

- `def list_files(workspace):` defines a function called `list_files`. `workspace` is the folder it will look in.
- `lines = []` starts an empty list. We'll add one line of text per file.
- `workspace.rglob("*")` finds everything inside the folder, including inside subfolders. `sorted` puts it in alphabetical order, so the output is the same every time.
- `if path.is_file():` skips folders. We only want files.
- `path.relative_to(workspace)` shortens a long path like `/Users/you/my-first-agent/demo/notes2.txt` to `notes2.txt`. The model doesn't need to see your whole disk layout.
- `lines.append(...)` adds a line with the file's name and size.
- The last line joins everything into one block of text, one file per line. If the folder is empty, it says so.

Notice what the function returns: **text**. The model reads text, so every tool we write will hand back text.

### 1c. A temporary test line

At the very bottom of the file, add:

```python
# Temporary test line - we delete this in stage 2
print(list_files(pathlib.Path(sys.argv[1])))
```

`sys.argv[1]` is the first word you type after the file name. `pathlib.Path` turns it into a folder path, and `print` shows what `list_files` returns. Save the file and run it:

```bash
python agent.py demo
```

**Checkpoint: your messy files are listed with their sizes.** If you see an error with a line number, the typo is on that line. Compare it against the code above, character by character. Spaces at the start of a line matter in Python.

You've written the agent's first hand. It's plain Python, and all it can do is look.

## Stage 2: the model meets the tool

Until now, *you* called `list_files`. In this stage the model decides to call it. This is the stage where the program becomes an agent, so we'll take it in small steps.

First, delete the two temporary lines at the bottom of `agent.py`.

### 2a. Describe the tool to the model

The model can't see your Python code. It only knows about a tool if you describe it. Below `list_files`, add:

```python
import anthropic

TOOLS = [
    {
        "name": "list_files",
        "description": "List every file in the workspace folder, with sizes.",
        "input_schema": {"type": "object", "properties": {}},
    },
]
```

`import anthropic` loads the package you installed in the setup post. It sits here rather than at the top so that stage 1 could run without it. Python doesn't mind where imports go, as long as they come before the code that uses them.

`TOOLS` is a list of tool descriptions, each with three parts:

- `name`: what the model says when it wants this tool.
- `description`: plain English the model reads to decide *when* the tool is useful. It matters more than it looks. A vague description gets a tool used badly or not at all.
- `input_schema`: what information the tool needs. `list_files` needs nothing (the empty `properties`), because we decide the folder, not the model. That's deliberate, and it comes up again in the next post.

### 2b. Connect the name to the function

When the model asks for a tool, it sends back a name as text. Something has to turn that name into a real function call. Add:

```python
def run_tool(workspace, name, args):
    if name == "list_files":
        return list_files(workspace)
    return f"Unknown tool: {name}"
```

`run_tool` is a switchboard. If the model asks for `list_files`, run `list_files`. If it asks for anything else, send back a message saying no such tool exists. Models occasionally ask for tools that don't exist, and a clear reply lets them recover.

`args` holds any information the model sent with its request. This tool ignores it. The tools in the next post will use it.

### 2c. One call to the model, to see what it asks for

Before the loop, let's watch the model ask for a tool once. Add:

```python
def main():
    workspace = pathlib.Path(sys.argv[1])
    task = sys.argv[2]
    client = anthropic.Anthropic()
    system = "You are a careful file assistant working inside one folder. Use your tools to complete the task."
    messages = [{"role": "user", "content": task}]

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        system=system,
        tools=TOOLS,
        messages=messages,
    )
    print(response.stop_reason)
    print(response.content)

if __name__ == "__main__":        # run only when started directly, not when imported by a test
    main()
```

What's new:

- `task = sys.argv[2]` is the second thing you type on the command line: what you want done this run.
- `client = anthropic.Anthropic()` is the same line as in `check.py`. It finds your key in the environment variable.
- `system` is the agent's standing instructions, the instructions box from the first post. It says who the agent is and how to work, and it's sent with every call, whatever the task. Two sentences is plenty for now. The one about tools matters: without it, some models answer from guesswork instead of looking.
- `messages` is the conversation so far. It starts with one message from you, the user, carrying today's task.
- `messages.create` is the call you made in `check.py`, with two additions: `system=system` sends the standing instructions, and `tools=TOOLS` tells the model that `list_files` exists.
- `max_tokens=4096` caps how long each reply can be.
- The last two lines of `main` print *why* the model stopped and what it sent back.
- `if __name__ == "__main__":` means "run `main()` only when this file is started directly". It matters in the next post, when we test one function without starting the whole agent.

Run it:

```bash
python agent.py demo "What kinds of files are in this folder?"
```

**Checkpoint: the first line printed is `tool_use`.** Below it is a jumble that includes `ToolUseBlock` and `name='list_files'`.

Stop and look at that, because it's the heart of the whole course. The model didn't answer your question. It can't: it has no idea what's in your folder. Instead it stopped and said "I want to use `list_files`". That's what `tool_use` means. **The model can't run anything. It can only ask.** Your code does the running.

Notice where the instructions ended up. The first post said they live in three places, and all three are now in your file. The standing instructions are in `system`. The task came in with the trigger, which for now is you typing a command. And the tool description in `TOOLS` told the model when `list_files` is worth asking for. None of those three can *make* anything happen. Only your code can.

Right now nothing happens next, because we haven't written that part. That's the loop.

### 2d. The loop

Delete the two `print` lines and the `response = client.messages.create(...)` call inside `main`. In their place, type the loop below. It lines up under `messages = [...]`, indented four spaces:

```python
    for _ in range(20):                     # safety cap: a confused agent can't loop forever
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
```

`for _ in range(20):` repeats everything indented beneath it, up to 20 times. Why a limit? An agent that gets confused could keep asking for tools forever, and every call costs money. Twenty rounds is plenty for tidying a folder, and the cap means a bug can never become a big bill.

Inside the loop, the first thing we do is the same call as before: ask the model what to do next.

### 2e. Show what the model says, and stop when it's done

Still inside the loop, add:

```python
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n{block.text}")
        if response.stop_reason != "tool_use":
            break                           # no more tool requests: the agent is done
```

A reply from the model comes in **blocks**. Some are text meant for you. Some are tool requests meant for your code. The first three lines print any text blocks that aren't empty.

Then comes the most important decision in the file. If the model stopped for any reason other than wanting a tool, it has finished, so `break` leaves the loop. If it does want a tool, we carry on to the next step.

### 2f. Run the tool and hand back the result

Still inside the loop, add:

```python
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
```

This is the part that makes it an agent:

- The first line adds the model's reply to the conversation. The model has no memory between calls, so every call sends the whole conversation again. If we didn't add its reply, it would forget it had asked for a tool.
- The inner `for` goes through the blocks looking for tool requests. For each one, it prints `[tool]` and the tool's name so you can watch, then calls `run_tool` with the name and arguments the model sent.
- Each result is wrapped up with `tool_use_id`, the ID of the request it answers. The model can ask for several tools at once, and the ID tells it which result belongs to which request.
- The last line sends all the results back as the next message in the conversation. Then the loop goes round again, and the model sees the results and decides what to do next.

Save and run the same command as before:

```bash
python agent.py demo "What kinds of files are in this folder?"
```

**Checkpoint: `[tool] list_files` flashes past, then a sensible description of your mess.**

Here's what just happened. The model read your question and asked for `list_files`. Your code ran it and sent back the result. The model read the list and answered you. Count the lines inside `main` and you'll find about 25 of them. That's the agent. Everything from here on is more tools and better manners.

Look at who did what. `list_files` is ordinary Python: it gives the same answer every time and costs nothing. The model did the one part that needs judgement, which was deciding that it needed the file list and then making sense of it. That split is the right-tool check from the first post in action. Keep it as you add tools: anything with a rule you can write down belongs in code, and the model gets only the decisions.

## Try this

Ask the agent different questions about the folder and watch the `[tool]` lines. Try "Which file is the biggest?" and "Is there anything here that looks like a bill?". Notice when it can answer from the file list alone and when it can't. It can see names and sizes, but not what's inside the files. That gap is exactly what the next post fills.

Then open `stages/stage2.py` in the repo and compare it with your file. If they match, you've built an agent.

Next post: we give the agent hands that read, write and move files, a fence that keeps it inside one folder, your permission before every change, and a memory.

---

← [Part 2](02-setting-up.md) · [Series page](README.md) · [Part 4](04-give-your-agent-hands-and-a-memory.md) →
