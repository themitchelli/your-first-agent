*Part 4 of [Your First Agent](README.md).*
*Code for this post: [`lessons/04-hands-and-memory`](../lessons/04-hands-and-memory).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Give your agent hands and a memory

Last post you built an agent. The loop that makes it one is about 30 lines, and the whole file about 65. It asks the model what to do, runs the tool the model asks for, and hands back the result. But it can only look. It lists files and talks about them.

Today it gets hands: tools that read, write and move files. Hands on your disk need protection, so it also gets a fence that keeps it inside one folder and a rule that nothing changes without your yes. Then we give it a memory, so each run starts from what the last one learned.

Same approach as last time: small steps, each one explained, most ending with something you can run. Type the code yourself, with VS Code's AI helpers off. Your file at the end matches `lessons/04-hands-and-memory/agent.py` in the course files.

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

You need your `agent.py` from the last post, working. If it isn't, copy `lessons/03-build-your-first-agent/stages/stage2.py` from the course files into your folder as `agent.py` and carry on from here.

## Stage 3: hands that change things, with permission

In this stage it gets tools that read, write and move files. Tools that change your disk need two protections first: the agent must stay inside the demo folder, and you must approve every change.

### 3a. The fence: `safe_path`

Below `list_files`, add:

```python
def safe_path(workspace, name):
    path = (workspace / name).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ValueError(f"'{name}' is outside the workspace - refused")
    return path
```

This is the most important function in the file. The model will choose filenames, and a filename can point anywhere. `../../Documents/taxes.xlsx` means "go up two folders and into Documents".

- `(workspace / name).resolve()` works out where the name really points, with every `..` followed to its end.
- `is_relative_to` checks whether that real location is still inside the workspace.
- If it isn't, `raise ValueError` stops everything with an error. The file is never touched.

Every tool that touches a file goes through `safe_path`. That's why we can let an AI call these tools at all: it can only reach the one folder you point it at.

### 3b. Read a file

Below `safe_path`, add:

```python
def read_file(workspace, name):
    return safe_path(workspace, name).read_text(encoding="utf-8")
```

One line: check the path is inside the fence, then return the file's text. The `encoding="utf-8"` part says how the bytes in the file turn into text. UTF-8 is the way text is stored almost everywhere now, and Python on Mac assumes it. Python on Windows still guesses an older encoding unless told, and the guess can't handle a tick mark or an emoji, both of which models love to write. So every time this course reads or writes a text file, it says `encoding="utf-8"`, and the same file works on both machines. Now test the fence. Run this in the terminal:

```bash
python -c "import pathlib, agent; agent.read_file(pathlib.Path('demo'), '../agent.py')"
```

That command loads your `agent.py` without starting the agent (this is what the `if __name__` line from the last post was for) and tries to read `../agent.py`, a file one folder up, outside `demo`.

**Checkpoint: it fails, on purpose.** You get a block of red text ending in:

```
ValueError: '../agent.py' is outside the workspace - refused
```

That block is a **traceback**, and this is a good moment to learn to read one, because you'll see plenty. Read it from the bottom. The last line is the error and the message. The lines above it are the trail: which function called which, ending at the line that raised. Here the trail runs from your command into `read_file`, into `safe_path`, to the `raise`. A security test that passes by failing. Enjoy that feeling.

It's ugly on purpose. In 3f we wrap every tool so that an error like this becomes one line of text the model reads and recovers from, and the agent never shows you the raw version.

### 3c. Write a file, with your permission

Below `read_file`, add:

```python
def write_file(workspace, name, content):
    answer = input(f"\n  Agent wants to write '{name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this write."
    path = safe_path(workspace, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Wrote {name}."
```

- `input(...)` shows a question in the terminal and waits for you to type an answer. It's one line of code and a whole way of working: the agent proposes, you approve.
- `.strip().lower()` tidies your answer, so `Y` and `y ` both count as yes.
- Anything other than `y` returns a message saying you declined. Notice that it's *returned*, not raised as an error. The model reads it, learns you said no, and can choose something else.
- If you said yes, the path goes through the fence, `mkdir` creates any folders the path needs, and the file is written, as UTF-8, for the reason in 3b.

### 3d. Move or rename a file, with your permission

Below `write_file`, add:

```python
def move_file(workspace, name, new_name):
    answer = input(f"\n  Agent wants to move '{name}' -> '{new_name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
        return "The user declined this move."
    src = safe_path(workspace, name)
    dst = safe_path(workspace, new_name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    return f"Moved {name} to {new_name}."
```

It follows the same pattern as `write_file`: ask, then fence, then act. Both the old and the new path go through `safe_path`, so the agent can't move a file out of the folder, or bring one in from outside. Moving a file into a subfolder that doesn't exist yet creates the subfolder, which is how the agent will sort files into groups.

### 3e. Describe the new tools to the model

The model doesn't know these functions exist until they're in `TOOLS`. Inside the `TOOLS` list, after the `list_files` entry (the `},` line), add:

```python
    {
        "name": "read_file",
        "description": "Read one file from the workspace folder.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Path relative to the workspace"}},
            "required": ["name"],
        },
    },
```

This tool needs information from the model: *which* file to read. `properties` names that piece of information, `name`, and says it's text (`string`). `required` says the model must always send it. The description, "Path relative to the workspace", tells the model to send `notes2.txt`, not a full path.

Then add the other two after it:

```python
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
```

`write_file` needs two pieces of information: the file name and what to put in it. `move_file` needs the current name and the new one. Both descriptions mention that you'll be asked to approve. That's honest, and it means the model won't be surprised by a "declined" reply.

### 3f. Route the new tools, and survive errors

Replace the whole `run_tool` function with this version:

```python
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
```

There are two changes:

- Three new routes. Each takes what the model sent in `args` and passes it to the right function. `args["name"]` is the `name` property you described in 3e. This is where the description and the function meet.
- `try` and `except` wrap the whole thing. Before, an error inside a tool, like `safe_path` refusing a path or a file that doesn't exist, would crash the agent. Now the error becomes text, `Error: ...`, and goes back to the model like any other result. The model reads what went wrong and tries something else. An agent that crashes on its first mistake isn't much use.

Save and run:

```bash
python agent.py demo "Rename the worst-named file in this folder to something sensible"
```

**Checkpoint: the agent reads some files, picks the worst name, and asks your permission to rename it.** Type `y` and check the sidebar. Then run it again, type `n`, and confirm it accepts the refusal.

Your file should be about 135 lines. Not what you expected? Compare it with `lessons/04-hands-and-memory/stages/stage3.py` in the course files.

That's the hands. An AI just changed something on your disk, and it asked first. If you want to stop for the day, this is the place to stop. What's left is a different idea, and it's short.

## Stage 4: memory

Right now the agent forgets everything the moment it finishes. Each run starts from nothing. Memory is the new idea in this post, and it's smaller than it sounds: a file the agent reads when it starts and writes when it finishes. One step.

### 4a. Read a memory file and extend the instructions

Inside `main`, find the two lines starting `system = "You are a careful file assistant...` and `messages = [{"role": "user", "content": task}]`, and replace them with:

```python
    memory_path = workspace / "memory.md"
    memory = memory_path.read_text(encoding="utf-8") if memory_path.exists() else "(no memory yet - first run)"
    system = (
        "You are a careful file assistant working inside one folder. "
        "Use your tools to complete the task. When finished, use write_file to update "
        "'memory.md' with a short note on what you did and learned, then summarise for the user."
    )
    messages = [{"role": "user", "content": f"Your memory from previous runs:\n{memory}\n\nToday's task: {task}"}]
```

- The first two lines read `memory.md` from the workspace if it exists. On the first run it doesn't, so the agent is told this is its first run.
- `system` is the same standing instructions as before, with one sentence added: update `memory.md` when finished, using the `write_file` tool it already has. The brackets let one string run over several lines. Nothing else about the instructions changed, and they're already sent with every call.
- The first message now carries the memory *and* today's task, so the agent starts every run knowing what it did last time.

That's the entire memory system. It's a file, read at the start and updated at the end by the agent itself, using a tool it already had. No database, and nothing new to install.

Run the full job:

```bash
python agent.py demo "Organise this folder: rename the files sensibly, group them into subfolders, and tell me what's in it"
```

**Checkpoint: the agent sorts your mess, asking permission for every change, then asks to write `memory.md`.** Say yes, then open `memory.md` and read what your agent wrote about its own work. Run it again with a different task and watch it start from what it already knows.

Your file should be about 145 lines. Not what you expected? Compare it with `lessons/04-hands-and-memory/agent.py` in the course files.

## Try this

Point the agent at a real messy folder of your own. Copy the folder first if you're nervous, although the y/n prompts protect you either way. Then try the task you wrote down for the exercise in the first post.

If that task needs a tool the agent doesn't have, you now know the recipe. Write a function. Describe it in `TOOLS`. Route it in `run_tool`. That isn't a beginner exercise. It's the actual job, and you can do it.

Next post: the same agent on a schedule, doing its work while you sleep.

---

← [Part 3](03-build-your-first-agent.md) · [Series page](README.md) · [Part 5](05-put-your-agent-on-a-schedule.md) →
