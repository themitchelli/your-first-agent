*Part 3 of [Your First Agent](README.md).*
*Code for this post: [`lessons/03-build-your-first-agent`](../lessons/03-build-your-first-agent).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Build your first agent

Here's the whole secret, before we start: **the part that makes it an agent is about 30 lines of code.** A loop that asks the model what to do next, runs the tool it asks for, and hands back the result. That's it. The whole file ends up about 65 lines, and everything outside the loop is there to make those 30 lines safe and useful.

Last time you proved your setup works: `check.py` talked to Claude and Claude answered. Today we build the agent itself, a small program that will tidy a messy folder. By the end of this post it can look at the folder and talk about it. The next post gives it hands and a memory. We build it in small steps. Each step adds a few lines, explains what they do and why they're there, and most steps end with something you can run. If a step fails, the fix is in that step, not somewhere behind you.

Type the code rather than pasting it. Typing makes you read every line, and reading every line is the point. Keep VS Code's AI helpers switched off, as in the setup post.

Your file at the end of this post matches `lessons/03-build-your-first-agent/stages/stage2.py` in the course files you cloned in the setup post. Every checkpoint below names the file to compare against. Use the compare trick from the setup post (Select for Compare, then Compare with Selected) when something goes wrong, not as a shortcut.

**Start of every session:** open VS Code on your `my-first-agent` folder, open a new terminal, check the line starts with `(.venv)`, and set your key:

**Mac**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Windows**

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

If anything fails, the setup post's "When it goes wrong" section has the errors and their fixes. Forgetting the key after a restart is the usual one.

## Stage 0: something to practise on

The agent needs a messy folder to work on. There's one in the course files. Copy it into your project with one command in the terminal (you're inside `my-first-agent`, and the course files are next door):

**Mac**

```bash
cp -r ../your-first-agent/lessons/03-build-your-first-agent/demo demo
```

**Windows**

```powershell
Copy-Item -Recurse ..\your-first-agent\lessons\03-build-your-first-agent\demo demo
```

`..` means "the folder above this one", your home folder, and the rest is the path down into the course files. The last word is the name of the copy. It holds seven small text files with terrible names: `Untitled document.txt`, `IMG_scan_001 (1).txt`, `doc_final_FINAL.txt` and so on. Each has a few lines of real-looking content, such as a note, an invoice or a recipe.

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
```

Line by line:

- `# ---- tools ----` is a comment. Python ignores anything after `#`. This one is a signpost for you: the file will grow, and section headers like this are how you'll find your way around it. There'll be a few more.
- `def list_files(workspace):` defines a function called `list_files`. `workspace` is the folder it will look in.
- `if not workspace.is_dir():` checks the folder exists before doing anything. Without it, a missing folder looks exactly like an empty one, and the model would report "empty" with total confidence. A tool has to hand back what's true, and "no such folder" and "no files" are different truths.
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

**Checkpoint: your messy files are listed with their sizes.** If it says there is no folder called demo, go back to stage 0. If you see an error with a line number, the typo is on that line. Compare it against the code above, character by character.

Your file should be about 17 lines. Not what you expected? Compare it with `lessons/03-build-your-first-agent/stages/stage1.py` in the course files.

You've written the agent's first hand. It's plain Python, and all it can do is look.

## How Python reads your spaces

Before the next stage, one thing about Python that every other language lets you ignore, and that will bite you in about five minutes if it isn't said.

Python builds its structure out of the spaces at the start of lines. A line that ends in a colon, like `def list_files(workspace):` or `for path in ...:`, opens a block. Every line inside that block is indented one step further than the line that opened it. One step is four spaces. The block ends when a line steps back out. That's the whole rule. There are no brackets or `end` words. The spaces *are* the structure.

Two things follow. First, the code boxes in this post show the leading spaces on purpose. When a box starts eight spaces in, your line starts eight spaces in. Match them exactly, not roughly. Second, VS Code helps more than you'd think: press Enter after a colon and it indents the next line for you, Tab inserts one step, Shift+Tab removes one, and the faint vertical lines down the editor show which block each line belongs to.

The trap isn't the error you'll get when spaces are wrong, though you'll get one and the setup post lists it. The trap is spaces that are *valid and wrong*: a line that's one step too shallow is still legal Python, it's just outside the block you meant it to be in, and the program runs and does something else. Stage 2 ends with a shape check for exactly that.

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
# ---- the agent ----

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

- `# ---- the agent ----` is the second signpost. Tools above it, the agent below it.
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

Save and run the same command as before. Tip: press the up arrow in the terminal and the last command comes back, so you don't retype it.

```bash
python agent.py demo "What kinds of files are in this folder?"
```

**Checkpoint: `[tool] list_files` flashes past once, then a sensible description of your mess.**

If instead `[tool] list_files` prints many times, or the run takes a long time and then answers as if it never looked, a block is at the wrong depth. The most likely one is the code from 2f sitting one step too shallow, outside the loop. The loop then goes round without ever handing a result back, asks the same question again, and does that twenty times before the safety cap from 2d stops it. That's the cap doing its job, and it just saved you a much bigger bill. Check the shape below.

**The shape of `main`.** Here's its outline, with only the lines that open blocks, each at its real depth:

```python
def main():                                  # column 1
    workspace = ...                          # 4 spaces: inside main
    ...
    for _ in range(20):                      # 4 spaces: inside main
        response = client.messages.create(   # 8 spaces: inside the loop
        ...
        for block in response.content:       # 8 spaces: inside the loop
            if block.type == "text" ...      # 12 spaces: inside that for
        if response.stop_reason != "tool_use":   # 8 spaces: inside the loop
            break
        messages.append(...)                 # 8 spaces: still inside the loop
        results = []                         # 8 spaces
        for block in response.content:       # 8 spaces
            if block.type == "tool_use":     # 12 spaces
        messages.append(...)                 # 8 spaces: the loop's last line

if __name__ == "__main__":                   # column 1
```

Everything from `response =` to the last `messages.append` sits at eight spaces or deeper. If any of those lines sits at four, it's outside the loop.

Your file should be about 65 lines. Not what you expected? Compare it with `lessons/03-build-your-first-agent/stages/stage2.py` in the course files.

Here's what just happened. The model read your question and asked for `list_files`. Your code ran it and sent back the result. The model read the list and answered you. That's the whole loop, and it's worth having a phrase for it: **ask, run, hand back, repeat.** Every agent you'll ever meet is that phrase with more tools.

Two things you built without being told what they were. The twenty-round cap is a **termination guard**: the standard answer to "what if the agent never decides it's done?" And the `Unknown tool` reply in `run_tool` is the standard answer to a model asking for a tool that doesn't exist, which models do. Frameworks sell both as features. You typed them.

One more thing to know about the loop. The model has no memory between calls, so every call sends the whole conversation again, including every tool result so far. That's why a long run costs more than a short one, and why the cap is a ceiling on purpose, not just a safety net. Count the lines inside `main` and you'll find about 30 of them. That's the agent. The other 35 are one tool, its description and two imports. Everything from here on is more tools and better manners.

Look at who did what. `list_files` is ordinary Python: it gives the same answer every time and costs nothing. The model did the one part that needs judgement, which was deciding that it needed the file list and then making sense of it. That split is the right-tool check from the first post in action. Keep it as you add tools: anything with a rule you can write down belongs in code, and the model gets only the decisions.

## Try this

Ask the agent different questions about the folder and watch the `[tool]` lines. Try "Which file is the biggest?" and "Is there anything here that looks like a bill?". Notice when it can answer from the file list alone and when it can't. It can see names and sizes, but not what's inside the files. That gap is exactly what the next post fills.

Then compare your file with `lessons/03-build-your-first-agent/stages/stage2.py` in the course files. If they match, you've built an agent.

Next post: we give the agent hands that read, write and move files, a fence that keeps it inside one folder, your permission before every change, and a memory.

---

← [Part 2](02-setting-up.md) · [Series page](README.md) · [Part 4](04-give-your-agent-hands-and-a-memory.md) →
