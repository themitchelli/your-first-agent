*Part 8 of [Your First Agent](README.md).*
*Code for this post: [`lessons/08-structure`](../lessons/08-structure).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# When to break it up: your agent in four files

For the whole series your agent has been one file, and that was a feature. You could scroll from the top to the bottom and see every part of it: the tools, the loop, the memory, the log.

It's now about 220 lines, and you've probably started to feel it. You scroll past the tool descriptions to reach the loop. In the harness post you had to take `main` apart to drive the agent from another program. And every time you want to check a change still works, you pay for API calls and get a slightly different answer.

Those are the reasons to split a file. Not tidiness and not "best practice". **Split when something hurts, and let each new file be the answer to one specific pain.** If you can't name the pain a file fixes, don't create it.

You've also been drawing the cut lines since the build post without knowing it. The section headers, `# ---- settings ----`, `# ---- tools ----`, `# ---- record keeping ----`, `# ---- the agent ----`, are where the file comes apart. Each new file is one section, named after its header.

By the end of this post the agent is four files, a test file, and the harness from the last post pointed at the real thing:

| File | Answers the question | Changes when you... |
|---|---|---|
| `tools.py` | What can the agent do? | add or change a tool |
| `agent.py` | How does the loop work? | change how the agent thinks or talks to the model |
| `runlog.py` | What happened? | change what gets recorded |
| `main.py` | How does a person or a schedule start it? | change the command line or the spend limit |
| `test_agent.py` | Does it still work? | change any of the above |
| `harness.py` | Did a change make it better? | change what you measure |

The last column is the useful one. Once code is split well, most changes touch one file, and the file's name tells you which one.

This post is different from the build posts. Most of the code already exists, and you'll *move* it rather than type it. The new code gets explained in full as usual. Moved code gets a sentence on why it moved.

**Start of session:** VS Code open on `my-first-agent`, a new terminal, `(.venv)` showing, key set. If anything fails, the setup post's "When it goes wrong" section has the fixes. Coming back after a break? `my-first-agent` is in your home folder (Finder: Go > Home). A new terminal forgets both the virtual environment and the key, so switch the environment on again (`source .venv/bin/activate` on Mac, `.venv\Scripts\Activate.ps1` on Windows) and set the key again. Both are in the setup post, steps 4 and 7. Start from your production `agent.py`, the one in `my-first-agent` itself, or copy `lessons/06-production/agent.py` from the course files. If you did the harness post you now have two files called `agent.py`. Leave the copy inside `harness` alone until the last section of this post, and run every command from `my-first-agent`, not from `harness`. **Before you start, make a backup:** copy `agent.py` to `agent-single-file.py` (in the terminal, `cp agent.py agent-single-file.py` on Mac or `copy agent.py agent-single-file.py` on Windows), so you can compare if something breaks. Your finished files match `lessons/08-structure`.

**If you did the harness post, you haven't lost that work.** The seams you cut there went into a copy of the simple agent from the hands-and-memory post, which has no spend limit and no run log. This post starts from your production agent and gives it the same two seams properly: the plugged-in approver arrives in split 1, and the choice of model in split 3. In the last section you point the harness at the real agent and delete the copy.

## Split 1: `tools.py`, the agent's hands

**The pain:** tools are the part you'll add to most. Every new tool means scrolling through the loop and the log to find the right spot. Tools also share nothing with the rest of the file. They're plain Python that never calls the API.

### 1a. Move the tools

Create a file called `tools.py`. At the top, type a short description in triple quotes:

```python
"""The agent's hands: what it can do, and the fence around it.

Everything here is plain Python. No AI, no API key, nothing to pay for,
which is why it is the easiest part of the agent to test.
"""
```

A description at the top of a file is a **module docstring**. With several files, it's how you remember what each one is for.

Now **cut** everything under the `# ---- tools ----` header from `agent.py` and paste it into `tools.py`, header included: `list_files`, `safe_path`, `read_file`, `allowed`, `write_file`, `move_file`, the whole `TOOLS` list, and `run_tool`. One line in the middle of that block doesn't belong to the tools: `import anthropic`. Before you cut, move it up to the top of `agent.py`, under `import sys`. The tools don't need it, and it moves again in split 4.

Save both files. From this post on you're editing several files at once, and the terminal only sees what's saved, so look for the white dot on each tab before you run anything (or turn on **File > Auto Save**). Then check the cut really happened: `agent.py` should now be about 130 lines, and its Outline should show no `list_files` or `run_tool`.

### 1b. Replace the global switch with a plugged-in approver

In `tools.py`, `allowed` still checks `AUTO_APPROVE`, a setting that lives in `agent.py` and is read from the command line. The tools file shouldn't know anything about the command line. And you met the better design in the harness post: **pass the approver in.**

Replace the whole `allowed` function with two approvers:

```python
def ask_human(question):
    answer = input(f"\n  {question} [y/n] ")
    return answer.strip().lower() == "y"

def auto_approve(question):
    print(f"  {question} auto-approved")
    return True
```

These are the two notches on the approval dial from the schedule post, now as two separate functions. Whoever starts the agent picks one.

Then give the tools an `approve` input and use it. In each function two things change: `approve` joins the inputs on the `def` line, and `allowed(` becomes `approve(` on the line below. Change the first lines of `write_file` from:

```python
def write_file(workspace, name, content):
    if not allowed(f"Agent wants to write '{name}' - allow?"):
```

to:

```python
def write_file(workspace, name, content, approve):
    if not approve(f"Agent wants to write '{name}' - allow?"):
```

and the first lines of `move_file` from:

```python
def move_file(workspace, name, new_name):
    if not allowed(f"Agent wants to move '{name}' -> '{new_name}' - allow?"):
```

to:

```python
def move_file(workspace, name, new_name, approve):
    if not approve(f"Agent wants to move '{name}' -> '{new_name}' - allow?"):
```

`run_tool` passes the approver through. Three of its lines change, and each one only gains `approve` at the end of its brackets. Change its first line from:

```python
def run_tool(workspace, name, args):
```

to:

```python
def run_tool(workspace, name, args, approve):
```

Inside it, change the `write_file` route from:

```python
            return write_file(workspace, args["name"], args["content"])
```

to:

```python
            return write_file(workspace, args["name"], args["content"], approve)
```

and the `move_file` route from:

```python
            return move_file(workspace, args["name"], args["new_name"])
```

to:

```python
            return move_file(workspace, args["name"], args["new_name"], approve)
```

If you did the harness post, this is the same edit you made to the copy in `harness`. This time it's going into the real agent.

**Checkpoint:** tools don't need the API, so test them right away, for free. Run this from `my-first-agent`. If your terminal prompt still says `harness` from the last post, type `cd ..` first:

```bash
python -c "import pathlib, tools; print(tools.list_files(pathlib.Path('demo')))"
```

Your demo files are listed. `import tools` loads your new file by name. Any `.py` file in the same folder can be imported this way, and that's all a module is.

## Split 2: `runlog.py`, the record of what happened

**The pain:** in the production post you decided that the record of what the agent did must live apart from anything the agent can change. The code didn't reflect that decision: the log functions sat in the same file as the loop. Now they get their own file, and the separation is visible.

### 2a. Move the record-keeping

Create `runlog.py`. Give it a docstring and the imports it needs:

```python
"""What happened: the run log, the reports, the spend total and the code version.

Kept apart from the agent on purpose. The agent can edit files in its workspace;
it has no business near the record of what it did.
"""

import datetime
import json
import pathlib
import subprocess
```

Cut these settings from the top of `agent.py` and paste them under the imports:

```python
HERE = pathlib.Path(__file__).parent
RUN_LOG = HERE / "runs.jsonl"
PRICE_PER_MILLION_USD = {"input": 1.00, "output": 5.00}     # Claude Haiku 4.5, as of September 2026
```

Then cut everything under `# ---- record keeping ----` from `agent.py`, `spent_this_month`, `code_version` and `finish`, and paste it below. The header can go; the file's docstring does its job now.

One rename while you're here. The production post called the run's dictionary `run`. In the next split, the loop becomes a function called `run`, and one name for two different things is confusing. In `runlog.py`, rename the dictionary to `record`. VS Code can do it safely: in `finish`, right-click `run` on the `def finish(run, report):` line, choose **Rename Symbol** and type `record`. In `spent_this_month`, the loop variable `run` becomes `record` the same way.

### 2b. One function to start a record

Above `spent_this_month`, add:

```python
def new_record(task):
    return {"started": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", "task": task,
            "version": code_version(), "tools": [], "input_tokens": 0, "output_tokens": 0, "result": "ok"}
```

It's the same dictionary `main` used to build. Now the file that knows what a record looks like is the only one that creates one. If you add a field later, you change one place.

## Split 3: `agent.py`, just the loop

**The pain:** remember the harness post. To drive the agent from another program, you had to pull the loop out of `main`, because `main` also read the command line, picked the approver and handled the log. The loop had several jobs tangled up with it. Now it gets exactly one.

### 3a. What's left becomes the loop

`agent.py` still holds `main`. Replace the whole file with this:

```python
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
```

It looks like a lot of deleting, but everything you're deleting from `agent.py` is either already in `tools.py` or `runlog.py`, or about to go into `main.py`. (Your backup, `agent-single-file.py`, still has it all.)

- `import tools` gives this file the tools. Inside it they're called `tools.TOOLS` and `tools.run_tool`, so you can always tell where something lives.
- `SYSTEM` is the system prompt, moved out of the loop to the top of the file and named in capitals as a fixed setting. It's the agent's standing instructions, so it belongs with the agent.

### 3b. The loop as a function that's handed everything it needs

Below `SYSTEM`, add:

```python
def run(client, workspace, task, approve, record, report, model="claude-haiku-4-5"):
    memory_path = workspace / "memory.md"
    memory = memory_path.read_text() if memory_path.exists() else "(no memory yet - first run)"
    messages = [{"role": "user", "content": f"Your memory from previous runs:\n{memory}\n\nToday's task: {task}"}]
```

The inputs are the point of this split. `run` is *given* everything it depends on, and creates none of it:

- `client`: the thing that talks to the model. Normally a real `anthropic.Anthropic()`. In the tests at the end of this post, it's a fake. That's only possible because `run` doesn't create the client itself.
- `workspace` and `task`: what to work on and what to do.
- `approve`: `tools.ask_human`, `tools.auto_approve`, or anything else with the same shape.
- `record` and `report`: where to write down what happens. The loop fills them in *as it goes*, so if something crashes halfway, whoever called `run` still has everything that happened up to that point.
- `model`: Haiku unless the caller says otherwise, as in the harness post.

Then the loop itself. It's your loop from the production post with four small changes: `system=SYSTEM`, `tools=tools.TOOLS`, `record` instead of `run`, and `tools.run_tool(..., approve)`. Indented one step inside `run`:

```python
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
```

Notice what's *not* here: no `try`, no `sys.exit`, no spend limit, no `input()`. The loop doesn't decide what failure means or what a run may spend. That's the caller's job.

`agent.py` is now under 50 lines, and most of them are the loop you wrote in the very first build post.

## Split 4: `main.py`, how the agent gets started

**The pain:** the command line, the approval dial, the spend limit and the failure handling are all decisions about *how this run was started*, by a person or by a schedule. A harness or a test starts the agent differently and wants none of them. So they get their own file, the one you actually run.

Create `main.py`:

```python
"""How a person or a schedule starts the agent.

Run:  python main.py demo "Organise any new files in this folder the same way as before."
      python main.py demo "Organise any new files in this folder the same way as before." --auto-approve
"""

import datetime
import pathlib
import sys

import anthropic

import agent
import runlog
import tools

MONTHLY_LIMIT_USD = 2.00
```

The imports come in two groups: first what comes with Python or was installed, then your own files. It's a common habit that makes it obvious at a glance which names are yours. `MONTHLY_LIMIT_USD` lives here because the spend limit is a decision about *this* way of starting the agent. A harness run might reasonably use a different limit, or none.

Then:

```python
def main():
    auto = "--auto-approve" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--auto-approve"]
    workspace = pathlib.Path(args[0])
    task = args[1]
    approve = tools.auto_approve if auto else tools.ask_human
    record = runlog.new_record(task)
    report = [f"# Run at {datetime.datetime.now():%Y-%m-%d %H:%M}", f"Task: {task}", ""]
```

- The flag is read here, and only here. `AUTO_APPROVE` no longer exists anywhere else.
- `approve = tools.auto_approve if auto else tools.ask_human` picks a notch on the dial in one line: "use `auto_approve` if the flag was given, otherwise `ask_human`". Note there are no brackets after the function names. We're choosing a function to hand over, not calling it.
- The record comes from `runlog.new_record`, and the report starts as before.

Then the spend guard, the run and the failure handling, all familiar from the production post:

```python
    spent = runlog.spent_this_month()
    if spent >= MONTHLY_LIMIT_USD:
        record["result"] = f"refused: ${spent:.2f} already spent this month, limit is ${MONTHLY_LIMIT_USD:.2f}"
        runlog.finish(record, report)
        sys.exit(1)

    try:
        client = anthropic.Anthropic()
        agent.run(client, workspace, task, approve, record, report)
    except Exception as error:
        record["result"] = f"FAILED: {error}"

    runlog.finish(record, report)
    if record["result"] != "ok":
        sys.exit(1)

if __name__ == "__main__":
    main()
```

The whole run is now one line: `agent.run(client, workspace, task, approve, record, report)`. This is where the real client gets created and handed in.

Finally, point the scheduler at the new entry point. In `run.sh` (or `run.bat`), change `agent.py` to `main.py`.

**Checkpoint:** run it as the scheduler would:

```bash
python main.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

It behaves exactly as the single-file agent did: tools run, a report is written, and a new line appears in `runs.jsonl`. **A good split changes where code lives, not what it does.** Once it works, you can delete `agent-single-file.py`, or keep it for comparison.

## The payoff: tests that cost nothing

Here's the pain that justified the whole exercise. Until now, the only way to check the agent still worked was to run it for real: pay for API calls, wait, and read an answer that's slightly different every time. You couldn't check that the loop hands results back correctly, because you couldn't control what the model says.

Now you can. `agent.run` accepts *any* client. So we hand it a fake one that plays back replies we wrote in advance.

Create `test_agent.py`:

```python
"""Tests that run the whole agent without the API: free, fast, and the same every time.

Run:  python test_agent.py
"""

import pathlib
import tempfile
from types import SimpleNamespace

import agent
import tools
```

`SimpleNamespace` makes a quick throwaway object with whatever attributes you give it. We'll use it to build fake replies that look like the real ones.

### The fake client

```python
class FakeClient:
    """Stands in for anthropic.Anthropic(). Plays back scripted replies and remembers what it was sent."""
    def __init__(self, replies):
        self.replies = replies
        self.sent = []
        self.messages = self                       # so fake.messages.create(...) works like the real client

    def create(self, **request):
        self.sent.append(request)
        return self.replies.pop(0)
```

This is the first **class** in the course. A class is a recipe for making objects that hold data and have their own functions. You only need three ideas to read this one:

- `__init__` runs when you make a `FakeClient`. It stores the scripted replies and starts an empty list, `sent`, to remember every request.
- The real client is used as `client.messages.create(...)`. Setting `self.messages = self` means `fake.messages.create(...)` calls this object's own `create`. It's a small trick so the loop can't tell the difference.
- `create` records what it was sent, then hands back the next scripted reply. `**request` gathers all the named inputs the loop passes, like `model=` and `messages=`, into one dictionary.

### Scripted replies

```python
def reply(stop_reason, *blocks):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks),
                           usage=SimpleNamespace(input_tokens=100, output_tokens=20))

def text(words):
    return SimpleNamespace(type="text", text=words)

def tool_use(tool, inputs):
    return SimpleNamespace(type="tool_use", id=f"call-{tool}", name=tool, input=inputs)
```

These three build objects shaped like the real API's replies, with exactly the attributes the loop reads: `stop_reason`, `content`, `usage`, and blocks with `type`, `text`, `name`, `input` and `id`. The fake only has to look real *to the loop*.

### Test 1: the fence holds

```python
def test_fence_refuses_paths_outside_the_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        (pathlib.Path(tmp) / "secret.txt").write_text("private", encoding="utf-8")      # a real file, just outside
        workspace = pathlib.Path(tmp) / "workspace"
        workspace.mkdir()
        try:
            tools.read_file(workspace, "../secret.txt")
        except ValueError:
            return
        raise AssertionError("read_file escaped the workspace")
```

It puts a real file *just outside* a workspace, then asks `read_file` for it. If `safe_path` refuses with `ValueError`, the test returns: a pass. If the read gets through, `raise AssertionError` makes the test fail with a clear message.

The real file matters. My first version of this test had no file outside. When I deleted the fence on purpose to check the test, it still "failed", but only because the file didn't exist, not because it spotted the escape. A test that fails for the wrong reason would happily pass the day the file is there. **Always break the code once to check your test catches it.**

### Test 2: "no" means no

```python
def test_declined_write_changes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        answer = tools.write_file(workspace, "note.txt", "hello", approve=lambda question: False)
        assert answer == "The user declined this write."
        assert not (workspace / "note.txt").exists()
```

`lambda question: False` is an approver written on one line that always says no. It's the pluggable approver paying off: testing a "no" used to mean sitting there typing n. `assert` checks something is true and stops the test with an error if it isn't. Here: the tool reports the refusal, *and* no file appeared.

### Test 3: the loop does its job

```python
def test_loop_runs_the_requested_tool_and_hands_back_the_result():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        (workspace / "asdfgh.txt").write_text("Banana bread recipe", encoding="utf-8")
        fake = FakeClient([
            reply("tool_use", tool_use("move_file", {"name": "asdfgh.txt", "new_name": "Recipes/banana_bread.txt"})),
            reply("end_turn", text("Moved the recipe.")),
        ])
        record = {"tools": [], "input_tokens": 0, "output_tokens": 0}
        report = []

        agent.run(fake, workspace, "Tidy up", lambda question: True, record, report)

        assert (workspace / "Recipes" / "banana_bread.txt").exists(), "the file was not moved"
        assert len(fake.sent) == 2, "the loop should call the model twice"
        handed_back = fake.sent[1]["messages"][-1]["content"][0]
        assert handed_back["tool_use_id"] == "call-move_file"
        assert handed_back["content"] == "Moved asdfgh.txt to Recipes/banana_bread.txt."
        assert record["input_tokens"] == 200 and len(record["tools"]) == 1
        assert "Moved the recipe." in report
```

This is the heart of the agent under test, with no API at all:

- The script: first the "model" asks to move `asdfgh.txt` into `Recipes`, then it says it's done.
- `agent.run(fake, ...)` runs the real loop with the fake client and a yes-to-everything approver.
- The checks: the file really moved. The loop called the model exactly twice. The second call carried the tool's result back, matched to the request by `tool_use_id`, the detail that's easiest to get wrong. And the record and report were filled in.

### Run the tests

At the bottom of the file:

```python
if __name__ == "__main__":
    tests = [value for name, value in dict(globals()).items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"passed  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed. No API calls, no cost.")
```

`globals()` holds everything defined in this file. The first line collects every function whose name starts with `test_`, and the loop runs each one. If any `assert` fails, Python stops with an error that names the line. (Professional projects use a test runner called pytest, which does this and much more. This tiny version needs nothing installed.)

```bash
python test_agent.py
```

**Checkpoint: three "passed" lines, then "All 3 tests passed. No API calls, no cost."** It takes under a second.

Now break something on purpose. In `agent.py`, change `"tool_use_id": block.id,` to `"tool_use_id": "wrong",` and run the tests again. Test 3 fails. Put it back. That's a mistake that would have cost you a confusing API error, and possibly an hour, and now it costs one second and nothing.

## One agent, not two: point the harness at it

There's a pain left over from the harness post. To build the harness you copied the agent into a `harness` folder and cut seams into the copy. Since then you've been running one agent and testing another. Every improvement to the real agent, the spend guard, the run log, the split you just did, is invisible to the harness, and every change you make in `harness/agent.py` is invisible to the agent that runs every morning. Two agents that drift apart is exactly the kind of pain this post exists for.

The fix is the payoff of the seams. The harness needed two things: a model it could choose and an approver it could plug in. The real agent now has both, because `agent.run` takes `model` and `approve`. So the harness can drive the real agent and the copy can go.

### Move the harness home

In the sidebar, drag `harness.py`, `fixture` and `answer_key.json` out of the `harness` folder into `my-first-agent`, next to `main.py`. Then delete the `harness` folder, including the copy of `agent.py` and `demo` inside it. Your real agent is the only agent now.

### Give it a client and a record

The harness used to call `agent.run(workspace, TASK, model=model, approve=always_yes, quiet=True)` and get a `stats` dictionary back. The real `run` is handed everything instead, so `run_once` changes shape. Replace the whole function with:

```python
def run_once(client, model, answer_key):
    approvals = []
    def always_yes(question):
        approvals.append(question)
        return True
    record = {"tools": [], "input_tokens": 0, "output_tokens": 0}
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp) / "fixture"
        shutil.copytree(HERE / "fixture", workspace)      # a fresh mess every run
        started = time.time()
        with contextlib.redirect_stdout(io.StringIO()):   # the agent prints as it works; keep nine runs off the screen
            agent.run(client, workspace, TASK, always_yes, record, [], model=model)
        seconds = time.time() - started
        placed = where_did_files_go(workspace, [n for names in answer_key.values() for n in names])
    price_in, price_out = MODELS[model]
    cost = (record["input_tokens"] * price_in + record["output_tokens"] * price_out) / 1_000_000
    return {"score": grouping_score(placed, answer_key), "cost": cost, "seconds": seconds,
            "tool_calls": len(record["tools"]), "approvals": len(approvals)}
```

Four changes, each one the real agent's shape showing through:

- `client` is now an input. The harness will make one real client and hand it to every run, the same way `main.py` does. That's the seam the tests used with a fake; here it carries the real thing.
- `record` is the same bare dictionary the tests used. The loop fills in the tokens and the tool calls as it goes, so the harness reads its numbers from there instead of a returned `stats`. The empty list after it is the `report`, which the harness doesn't need.
- The `quiet` flag is gone, because the real loop doesn't have one. `contextlib.redirect_stdout` does the same job from outside: for the length of the `with` block, everything the agent prints goes into an `io.StringIO()`, a throwaway string, instead of the screen. Add `import contextlib` and `import io` to the top of the file, in alphabetical order with the others.
- `tool_calls` is now the length of `record["tools"]`.

Then make the client, once, in `main`. Under the `answer_key = ...` line add:

```python
    client = anthropic.Anthropic()
```

A little further down, inside the `for model in MODELS:` loop, hand the client to every run. Change:

```python
        results = [run_once(model, answer_key) for _ in range(runs)]
```

to:

```python
        results = [run_once(client, model, answer_key) for _ in range(runs)]
```

Last, at the top of the file, add `import anthropic` on its own line above `import agent`.

One honest note. Harness runs go through `agent.run` and never through `main.py`, so they're not written to `runs.jsonl` and don't count towards the monthly limit. That's right, because they're tests, not the agent's work, but it means the console spend limit from the production post is the only thing capping them. Check it's set.

**Checkpoint:** the free test first, then the real one:

```bash
python -c "import json, harness as h; k = json.load(open('answer_key.json')); perfect = {n: g for g, ns in k.items() for n in ns}; print(h.grouping_score(perfect, k))"
python harness.py 1
```

The first prints `1.0`. The second prints the same table as the harness post, with the same kind of numbers, and it's now measuring the agent you actually run. From here on, any change to `tools.py`, `agent.py` or the instructions gets the same question asked of it: did the score move?

## When not to split

Everything in this post was a response to a problem you'd already met. So, the honest counterpoint: **if your agent is 80 lines and has one way to start it, keep it in one file.** One file you can read top to bottom beats four files you have to jump between. The table at the top isn't a template to copy into every project. It's what *this* agent grew into, one pain at a time.

The next time you're unsure, ask the question from the start of this post: which pain would this new file fix? If you can't name one, the answer is not yet.

## Try this

Add a fifth tool, `delete_file`, with approval, following the recipe from the build post. Notice which files you touch: `tools.py` for the function, its description and its route, and `test_agent.py` for a test that a declined delete leaves the file in place. You shouldn't need to open `agent.py` or `main.py` at all. If you do, ask why. That's how you'll know the split is working.

---

← [Part 7](07-swap-the-model.md) · [Series page](README.md) · [Part 9](09-keep-a-register.md) →
