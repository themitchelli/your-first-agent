*Part 9 of [Your First Agent](README.md).*
*Code for this post: [`lessons/09-register`](../lessons/09-register).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Keep a register: what your agent is, written down and checked

Your agent now has two records. The run log from the production post says what it did. The harness from the swap-the-model post says whether a change helped. Neither says what the agent *is*.

You know, because you built it. But try answering these without opening the code: which tools can it use, and which of them change files? Does anything approve those changes when it runs at 7am? Which model does it call? And the harness score you got last time: which version of the instructions was that for? It scrolled off the screen the day you ran it.

That's the pain. Everything about your agent lives in your head and in 400 lines of Python. The fix is a **register**: one short file, next to the code, that says what the agent is. Organisations that run agents keep exactly this. It's the first thing a security team asks for, and usually the thing nobody has.

A register nobody checks is out of date the first time someone adds a tool in a hurry. So half of this post is the file, and half is four new tests that fail when the file stops telling the truth. After this post the three records fit together:

| Record | Answers | Kept up to date by |
|---|---|---|
| `register.json` | What is this agent? | you, and four tests that fail when it's wrong |
| `runs.jsonl` | What did it do? | the agent, every run, stamped with the register's id |
| harness score | Did a change help? | you, recorded in the register |

**Start of session:** VS Code open on `my-first-agent`, a new terminal, `(.venv)` showing, key set. If anything fails, the setup post's "When it goes wrong" section has the fixes. Coming back after a break? `my-first-agent` is in your home folder (Finder: Go > Home). A new terminal forgets both the virtual environment and the key, so switch the environment on again (`source .venv/bin/activate` on Mac, `.venv\Scripts\Activate.ps1` on Windows) and set the key again. Both are in the setup post, steps 4 and 7. Start from your four files from the last post, or copy everything in `lessons/08-structure` from the course files into `my-first-agent`. There should be no `harness` folder any more: `harness.py` sits next to `main.py`. Run every command in this post from `my-first-agent`. Your finished files match `lessons/09-register`.

**Checkpoint before you start:** from `my-first-agent`, run `python test_agent.py`. You should see "All 3 tests passed." If you did the last post's Try this, you'll see 4. Either is fine.

## Step 1: write the register

### 1a. Give the agent an id

Your agent has a name, `file-organiser`, but a name is a label, not an identity. Copy the project to build a second agent and you have two called `file-organiser`. Rename it and anything that pointed at the old name points at nothing. So the register gives the agent an **id**: a code that belongs to this agent and nothing else, and never changes, even when the name does.

From `my-first-agent`, make one:

```bash
python -c "import uuid; print(uuid.uuid4())"
```

```
57328a1c-9706-410f-8ba9-b46a2c42b4b8
```

`uuid` comes with Python. `uuid4()` makes a random id so long that nobody else, anywhere, will ever make the same one. Yours will be different from mine. Leave it in the terminal: you'll paste it in a moment.

### 1b. Create the file

In the sidebar, create a file called `register.json` in `my-first-agent`, next to `main.py`. JSON is the format you met in `answer_key.json`: labels in double quotes, a colon, then a value. Type this, with your own id pasted in place of mine and your own name as owner:

```json
{
  "id": "57328a1c-9706-410f-8ba9-b46a2c42b4b8",
  "name": "file-organiser",
  "purpose": "Tidies one folder: groups files into named subfolders and keeps notes in memory.md.",
  "owner": "Your Name",
  "runs_on": "My laptop, every morning at 7, started by cron through run.sh.",
  "monthly_limit_usd": 2.00,

  "model": "claude-haiku-4-5",
  "instructions": "SYSTEM in agent.py",
  "tools": {
    "list_files": "read",
    "read_file": "read",
    "write_file": "write",
    "move_file": "write"
  },
  "approval": "A person approves every write when run by hand. On the schedule, run.sh auto-approves them.",
  "memory": "memory.md inside the workspace. The agent reads it at the start and rewrites it at the end.",
  "trigger": "Schedule (run.sh), or by hand with main.py.",

  "scores": []
}
```

Two JSON rules catch everyone. Every line in a block ends with a comma **except the last one** before a closing `}` or `]`. And JSON has no comments, so you can't leave yourself a `#` note in here. That's why each value is a full sentence: the register has to explain itself.

If you're on Windows, `runs_on` should say Task Scheduler and `run.bat` instead. If you added `delete_file` in the last post's Try this, add a line for it under `move_file`: `"delete_file": "write"`, and put a comma after `"move_file": "write"`.

Save it.

### 1c. What you just wrote down

The file has three parts, separated by the blank lines.

**About the agent:** its id, what it's called, what it's for, who owns it, where it runs, and the most it may spend. The limit is the same number as `MONTHLY_LIMIT_USD` in `main.py`.

**The five boxes:** model, instructions, tools, memory and trigger, the framework from the first post. Each tool has a permission word: `read` if it only looks, `write` if it changes files. `approval` says who approves the writes.

Read the `approval` line again. It's the most important sentence in the file. Your agent has written files without asking anyone every morning since the schedule post. That was always true. Now it's written down where someone else can see it. Writing a register usually turns up one sentence like this, and finding it is the point.

**Scores:** empty for now. Step 4 fills it.

**Checkpoint:** from `my-first-agent`, check the file loads:

```bash
python -c "import json; print(json.load(open('register.json', encoding='utf-8'))['tools'])"
```

You should see `{'list_files': 'read', 'read_file': 'read', 'write_file': 'write', 'move_file': 'write'}`. If you see `JSONDecodeError` instead, it's almost always a comma: one missing between lines, or one extra before a `}`. The error gives the line number. "When it goes wrong" at the end of this post has the exact messages.

## Step 2: make the register checkable

Some of the register can be checked by code and some can't. No test can tell whether you really own this agent. A test can tell whether the tools listed are the tools that exist.

| Field | Checked by |
|---|---|
| `tools` | test 4: the names match `tools.TOOLS` |
| `model`, `monthly_limit_usd` | test 5: the agent asks for that model, `main.py` has that limit |
| `id` | test 6: every new line in the run log carries it |
| `scores` | test 7: the latest score was measured on the code that runs now |
| everything else | you, when you read it |

It's the same rule as the tools in the build post: instructions ask, tools enforce. Here the prose asks and the tests enforce. The tests go in `test_agent.py`, where they run with the other three for free.

### 2a. Two more imports

At the top of `test_agent.py`, change:

```python
import pathlib
import tempfile
from types import SimpleNamespace

import agent
import tools
```

to:

```python
import json
import pathlib
import tempfile
from types import SimpleNamespace

import agent
import harness
import main
import runlog
import tools

HERE = pathlib.Path(__file__).parent
```

`json` reads the register. `main` is there so the test can see `MONTHLY_LIMIT_USD`, and `runlog` is for step 3. Importing `main.py` doesn't run the agent, because its last lines only call `main()` when you run the file directly. `harness` is for step 4. `HERE` is the folder the test file is in, the same trick `runlog.py` and `harness.py` use, so the tests find `register.json` wherever you run them from.

### 2b. Test 4: the register lists exactly the agent's tools

Find the last test, `def test_loop_runs_the_requested_tool_and_hands_back_the_result`. Below the end of that function and above `if __name__ == "__main__":`, at the left margin, add:

```python
def read_register():
    return json.loads((HERE / "register.json").read_text(encoding="utf-8"))

def test_register_lists_exactly_the_agents_tools():
    in_code = {tool["name"] for tool in tools.TOOLS}
    in_register = set(read_register()["tools"])
    assert in_code == in_register, (f"tools in the code but not the register: {in_code - in_register or 'none'}. "
                                    f"In the register but not the code: {in_register - in_code or 'none'}.")
```

- `read_register` opens the file fresh for each test, so a mistake in the JSON shows up as a failing test, not a crash before any test runs.
- The curly brackets make a **set**: a bag of names with no order and no repeats. `in_code` is every tool name in `tools.TOOLS`. `set(...)` around the register's `tools` gives just its labels.
- Two sets are equal when they hold the same names, whatever the order. That's the whole check.
- `in_code - in_register` means "names in the first set that aren't in the second". The message uses it to tell you exactly which tool is missing and from where. `or 'none'` prints "none" instead of an empty `set()`.

The text after the comma in an `assert` is the message Python shows when the check fails. Up to now the tests had short messages or none. The register tests need good ones, because the person reading them is you in three months, mid-change, wanting to know what to fix.

**Checkpoint:** from `my-first-agent`:

```bash
python test_agent.py
```

Four "passed" lines, then "All 4 tests passed. No API calls, no cost." (One more if you kept last post's `delete_file` test.)

Now break it on purpose. In `register.json`, delete the line `"move_file": "write"` and the comma on the line above it. Save and run the tests again. The last line reads:

```
AssertionError: tools in the code but not the register: {'move_file'}. In the register but not the code: none.
```

Put the line back, with the comma after `"write_file": "write"`, and save.

### 2c. Test 5: the model and the spend limit

The register says `claude-haiku-4-5`. How does a test find out which model the agent really uses? Ask it. You already have a fake client that remembers everything the agent sends. Run the loop once with a fake reply, then look at the model in the request.

Below `test_register_lists_exactly_the_agents_tools`, add:

```python
def test_register_matches_the_model_and_the_spend_limit():
    register = read_register()
    fake = FakeClient([reply("end_turn", text("Nothing to do."))])
    with tempfile.TemporaryDirectory() as tmp:
        agent.run(fake, pathlib.Path(tmp), "Check", lambda question: True,
                  {"tools": [], "input_tokens": 0, "output_tokens": 0}, [])
    assert fake.sent[0]["model"] == register["model"], (
        f"the agent asks for {fake.sent[0]['model']}, the register says {register['model']}")
    assert main.MONTHLY_LIMIT_USD == register["monthly_limit_usd"], (
        f"main.py's limit is {main.MONTHLY_LIMIT_USD}, the register says {register['monthly_limit_usd']}")
```

- The fake's one reply is `end_turn`, so the loop asks the model once and stops.
- `agent.run` gets no `model`, exactly as `main.py` calls it. So the model it sends is the one your agent really uses when it runs at 7am.
- `fake.sent[0]["model"]` is the `model=` from that first request. This is why the fake keeps everything it's sent.
- The second check reads the limit straight out of `main.py`.

**Checkpoint:** run `python test_agent.py` from `my-first-agent`. Five "passed" lines. There's also a line saying `Nothing to do.` above the fifth one. That's the fake model's reply, printed by the loop, the same way test 3 prints `Moved the recipe.`

Break it: in `register.json`, change `"claude-haiku-4-5"` to `"claude-sonnet-5"`, save, and run again:

```
AssertionError: the agent asks for claude-haiku-4-5, the register says claude-sonnet-5
```

Change it back and save.

## Step 3: one id, on every record

The id is only worth having if something uses it. Right now each line in `runs.jsonl` says when a run started, what it cost and which code ran, but not *which agent* it was. With one agent that's obvious. With two, their records look the same. So every new record gets stamped with the register's id, and "what did this agent do?" becomes a search for one string.

### 3a. Stamp the id on every record

In `runlog.py`, find `def code_version():`. Above it, at the left margin, add:

```python
def agent_id():
    try:
        return json.loads((HERE / "register.json").read_text(encoding="utf-8"))["id"]
    except Exception:
        return "unregistered"
```

It reads the id from the register. If there's no register, or no id in it, the record says `"unregistered"` instead of crashing the run. That's the same choice `code_version` makes when there's no git: the run still happens, and the record says honestly what's missing.

Then change the first two lines of `new_record` from:

```python
def new_record(task):
    return {"started": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", "task": task,
```

to:

```python
def new_record(task):
    return {"agent": agent_id(), "started": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", "task": task,
```

The third line, starting `"version": code_version()`, stays as it is. Save.

**Checkpoint (free):** from `my-first-agent`:

```bash
python -c "import runlog; print(runlog.new_record('test')['agent'])"
```

You should see your id, the same one as in `register.json`. If you see `unregistered`, the register didn't load: run the step 1 checkpoint again. Your next real run will write the id into `runs.jsonl`. Older lines won't have it, and that's fine.

### 3b. Test 6: every run record carries the register's id

Below `test_register_matches_the_model_and_the_spend_limit` in `test_agent.py`, add:

```python
def test_every_run_record_carries_the_register_id():
    register_id = read_register()["id"]
    assert register_id, "the register's id is empty. Make one with: python -c \"import uuid; print(uuid.uuid4())\""
    stamped = runlog.new_record("Check")["agent"]
    assert stamped == register_id, f"new run records say agent {stamped}, the register's id is {register_id}"
```

- The first check catches an id left empty.
- The second makes a record the way `main.py` does and checks it carries the same id. If someone removes the stamp from `new_record` later, this is the test that notices. The `\"` inside the message is a double quote inside a string that's already in double quotes. The backslash tells Python it's part of the text.

**Checkpoint:** run `python test_agent.py` from `my-first-agent`. Six "passed" lines, then "All 6 tests passed. No API calls, no cost."

## Step 4: a score belongs to a version

In the harness post you measured your agent, and the numbers went nowhere. Here's why that matters. Next month you reword the instructions and the harness says 0.94. Is that worse than before? You can't know unless you wrote down the last score and *which code it was for*. A score with no version attached tells you nothing.

So each score in the register carries a fingerprint of the two files the harness measures: `tools.py` and `agent.py`. You met fingerprints in the harness post. It's a short code worked out from a file's contents, and any change to the file, even one character, gives a completely different code. See for yourself, from `my-first-agent`:

```bash
python -c "import hashlib; print(hashlib.sha256(b'hello').hexdigest()[:8]); print(hashlib.sha256(b'hello!').hexdigest()[:8])"
```

```
2cf24dba
ce06092f
```

One exclamation mark, and nothing in common. That's what lets a test tell whether the code changed since the last score.

### 4a. Teach the harness to print its fingerprints

In `harness.py`, find `def fingerprint(path):`. Below that function and above `def where_did_files_go`, at the left margin, add:

```python
def code_fingerprint(path):
    """A short fingerprint of a code file, for the register. Line endings are evened out so Windows and Mac agree."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:8]
```

- `[:8]` keeps the first eight characters. Plenty to tell your versions apart, and short enough to read.
- Windows ends each line of a text file with two invisible characters, `\r\n`. Mac uses one, `\n`. The same code copied between the two would get two different fingerprints. `.replace(b"\r\n", b"\n")` evens them out first.

Then, at the bottom of `main` in `harness.py`, change:

```python
    print(f"\nscore: lowest-highest over {runs} runs (1.00 = perfect grouping). Other columns: average per run.")
```

to:

```python
    print(f"\nscore: lowest-highest over {runs} runs (1.00 = perfect grouping). Other columns: average per run.")
    print(f"measured on: tools.py {code_fingerprint(HERE / 'tools.py')}  agent.py {code_fingerprint(HERE / 'agent.py')}")
```

The new line sits level with the one above, four spaces in. Now every harness run tells you which code it measured.

**Checkpoint (free):** from `my-first-agent`:

```bash
python -c "import pathlib, harness; print(harness.code_fingerprint(pathlib.Path('tools.py')))"
```

Eight letters and numbers. Yours won't match anyone else's, because you typed your own `tools.py`. `harness.py` should be about 109 lines. Compare with `lessons/09-register/harness.py`.

### 4b. Test 7: the latest score is for the code that runs now

Below `test_every_run_record_carries_the_register_id` in `test_agent.py`, add:

```python
def test_register_score_was_measured_on_the_code_that_runs():
    scores = read_register()["scores"]
    assert scores, "the register has no scores yet. Run the harness and add one to 'scores'."
    latest = scores[0]
    for name in ["tools.py", "agent.py"]:
        now = harness.code_fingerprint(HERE / name)
        assert latest[name] == now, (f"{name} has changed since the latest score was measured "
                                     f"(the register says {latest[name]}, the file is now {now}). "
                                     f"Run the harness and add a new score at the top of 'scores'.")
```

- `assert scores` fails when the list is empty. An empty list counts as false in Python.
- The newest score goes first in the list, so `scores[0]` is the latest.
- For each of the two files, the fingerprint recorded with the score has to match the file as it is now.

**Checkpoint: this one is supposed to fail.** Run `python test_agent.py` from `my-first-agent`. Six tests pass, then the last line reads:

```
AssertionError: the register has no scores yet. Run the harness and add one to 'scores'.
```

That's the test doing its job. There's no score in the register yet, so it can't say the score is current. `test_agent.py` should be about 120 lines. Compare with `lessons/09-register/test_agent.py`.

### 4c. Record a score

From `my-first-agent`, run the harness with its default three runs per model:

```bash
python harness.py
```

It takes a few minutes and costs about $1.20 as of September 2026. `python harness.py 1` costs about a third of that, but one run proves little, and this is the number you'll compare against later.

**Checkpoint:** the same table as the harness post, with one new line at the end starting `measured on:`.

Now copy two things into the register: the Haiku row's score, because Haiku is the model the register names, and the two fingerprints from the `measured on:` line. In `register.json`, change:

```json
  "scores": []
```

to:

```json
  "scores": [
    {"date": "2026-09-26", "model": "claude-haiku-4-5", "score": "0.33-0.67", "runs": 3,
     "tools.py": "2303edd6", "agent.py": "8e6366d4"}
  ]
```

using today's date, your Haiku score and your two fingerprints. Mine are shown. Yes, my Haiku scored between 0.33 and 0.67 that day, even though a single run on my own copy earlier had scored 1.00. That's why the harness runs three times, and why the register records the range, not the best run. Save.

**Checkpoint: "All 7 tests passed. No API calls, no cost."** (8 with last post's `delete_file` test.)

## Step 5: the loop from now on

Now try the loop once, for real. In `agent.py`, find the first line of `SYSTEM` and change:

```python
    "You are a careful file assistant working inside one folder. "
```

to:

```python
    "You are a careful, tidy file assistant working inside one folder. "
```

Save, and run `python test_agent.py` from `my-first-agent`. Test 7 fails:

```
AssertionError: agent.py has changed since the latest score was measured (the register says 8e6366d4, the file is now c9abdfed). Run the harness and add a new score at the top of 'scores'.
```

Your fingerprints will differ. The message is the loop you'll follow from now on:

1. Change the agent.
2. The tests tell you the register's score is out of date.
3. Run the harness.
4. Add the new score **at the top** of `scores`, with a comma after its closing `}`. Leave the old one below it.

Then "is this version better than the last?" has an answer: compare the top two entries. They sit next to each other in the file, each tied to the code it measured.

Try it, or put the line back the way it was and save. The tests pass again, because the fingerprint only depends on what's in the file. Undo the change and you're back on the version that was measured.

If you use git (the version control side post), commit `register.json` with the code. Git then keeps every earlier version of the register too.

## Where this stops

A register in a JSON file works for one person with a few agents. At work, the same idea becomes an inventory kept by a security or risk team, and the tests become a gate that stops an agent going live when its register is wrong. There are whole products for this. Every agent gets an id there too, and the id is what the inventory, the logs and the bill all use to mean the same agent. The fields in those products are the same questions you just answered: what is it, who owns it, what can it touch, who approves, what does it cost, which version is live and how good is it. If someone at work asks for "an agent register", you know what goes in one, and why it has to be checked.

## Try this

Add the `delete_file` tool from the last post's Try this, if you haven't yet. Before you touch `register.json`, run the tests and read which ones fail and what they say. Then update the register until they pass. Test 4 will want a new line under `tools`. Test 7 will want a new score, because `tools.py` changed. No test will ask you to reread `approval`, `purpose` or `runs_on`, but a delete tool changes what your agent is allowed to do, so read them anyway. That's the part of a register only a person can keep true.

## When it goes wrong

The last line of the error is the one that matters.

**`json.decoder.JSONDecodeError: Illegal trailing comma before end of object: line 15 column 25`** (Python 3.13 and later) or **`json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 16 column 3`** (Python 3.12 and earlier). There's a comma after the last item in a block. Go to the line it names, or the one above, and delete the comma before the `}`.

**`FileNotFoundError: [Errno 2] No such file or directory: '.../register.json'`**. The file isn't next to `test_agent.py`, or it's called something else. Check the sidebar: it should say `register.json` exactly, in `my-first-agent`, not inside `demo`.

**`KeyError: 'id'`**. The register has no `"id"` line. Step 1a makes one.

**`KeyError: 'agent'`**. `new_record` in `runlog.py` doesn't stamp the id yet. Step 3a.

**`KeyError: 'tools.py'`**. The score entry is missing one of the fingerprint labels, or has a typo in it. The labels are `"tools.py"` and `"agent.py"`, with the `.py`.

**`AttributeError: module 'harness' has no attribute 'code_fingerprint'`**. Either step 4a isn't saved yet, or `harness.py` is still inside a `harness` folder and Python found the folder instead of the file. If there's a folder, do the last section of the previous post, "One agent, not two", first.

**`ModuleNotFoundError: No module named 'harness'`**. There's no `harness.py` in `my-first-agent` at all. Copy it from `lessons/08-structure` in the course files, with `fixture` and `answer_key.json`.

---

← [Part 8](08-when-to-break-it-up.md) · [Series page](README.md) · [Part 10](10-what-you-built.md) →
