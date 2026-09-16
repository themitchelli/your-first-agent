*Part 6 of [Your First Agent](README.md).*
*Code for this post: [`lessons/06-production`](../lessons/06-production).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# What production means for an agent

Your agent runs every morning without you. Congratulations: you now have a small production system.

"Production" sounds like a place, somewhere serious with servers and on-call rotas. It isn't a place. It's a set of questions you have to be able to answer once nobody is watching. When you ran the agent by hand, you answered all of them without noticing, just by sitting there. What was it allowed to do? You typed y. What did it do? You watched. Each step up the trigger ladder takes away some of your attention, and something written down has to take its place.

Here are the five questions. For each one we'll write a few lines of code, not a platform.

**Start of session:** VS Code open on `my-first-agent`, a new terminal, `(.venv)` showing, key set. You need your scheduled `agent.py` from the last post. If yours isn't working, copy it from `lessons/05-a-schedule` in the [repo](https://github.com/themitchelli/your-first-agent). Your file at the end of this post matches `lessons/06-production`.

## Question 1: what is it allowed to do?

You've already answered this one, twice. `safe_path` fences the agent into one folder. The approval dial from the last post decides whether a person or a flag says yes. No new code.

The principle is worth naming, though: **an agent that runs unattended should have the narrowest permissions that still let it do its job.** Picture the opposite: the same agent pointed at your whole home folder, with auto-approve on. In a demo, nothing bad happens. That's the problem. Nothing would tell you if it did, which brings us to the next question.

## Question 2: what did it do?

Last post gave you a report per run, written for a human to read. Now we add a **run log**: one line per run, in a format a program can read, added to the end of one file and never edited. It lets you answer questions across many runs. How much did last week cost? When did it last fail? Which run moved that file?

### 2a. Two new imports and the log's location

Change the imports at the top of `agent.py` to:

```python
import datetime
import json
import pathlib
import subprocess
import sys
```

`json` writes data in JSON, a text format that almost every program can read. `subprocess` lets Python run another program. We need it for question 5.

Under the `AUTO_APPROVE` line, add:

```python
HERE = pathlib.Path(__file__).parent
RUN_LOG = HERE / "runs.jsonl"
MONTHLY_LIMIT_USD = 2.00
PRICE_PER_MILLION_USD = {"input": 1.00, "output": 5.00}     # Claude Haiku 4.5, as of September 2026
```

- `HERE` is the folder `agent.py` lives in. Like the reports, the log sits here, outside the fence, where the agent can't edit it.
- `RUN_LOG` is the log file. The `.jsonl` ending means "JSON lines": one complete JSON record per line.
- `MONTHLY_LIMIT_USD` is for question 3. Set it now so all the settings sit together.
- `PRICE_PER_MILLION_USD` is what the model charges per million **tokens**, the chunks of text models read and write, measured in and out. Check the current prices on Anthropic's pricing page and update this line when they change.

### 2b. A record for this run

In `main`, straight after the `report = [...]` line, add:

```python
    run = {"started": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", "task": task,
           "version": "unknown", "tools": [], "input_tokens": 0, "output_tokens": 0, "result": "ok"}
```

`run` is a **dictionary**: a set of labelled values, like a form with named boxes. It starts with the time, the task, an empty list of tools, zero tokens and a result of `"ok"`. The boxes get filled in as the run goes. `"version"` stays `"unknown"` until question 5.

### 2c. Count tokens and record tools

In the loop, straight after the closing `)` of `client.messages.create(...)`, add:

```python
            run["input_tokens"] += response.usage.input_tokens
            run["output_tokens"] += response.usage.output_tokens
```

Every reply from the API says how many tokens it used, in `response.usage`. `+=` adds this call's count to the running total. That's the raw material for question 3.

Then, under the `report.append(f"- tool: ...")` line, add:

```python
                    run["tools"].append({"name": block.name, "input": block.input})
```

The same information as the report line, stored so a program can read it.

(If your indentation in these boxes looks one step deeper than your file, don't worry. It matches the file after question 4. For now, line each new line up with its neighbours.)

### 2d. Finish the run: log it, then report it

Above `def main():`, add this function:

```python
def finish(run, report):
    run["cost_usd"] = round((run["input_tokens"] * PRICE_PER_MILLION_USD["input"]
                             + run["output_tokens"] * PRICE_PER_MILLION_USD["output"]) / 1_000_000, 5)
    with RUN_LOG.open("a") as log:
        log.write(json.dumps(run) + "\n")
    reports = HERE / "reports"
    reports.mkdir(exist_ok=True)
    failed = "" if run["result"] == "ok" else "-FAILED"
    report_path = reports / f"{datetime.datetime.now():%Y-%m-%d-%H%M}{failed}.md"
    report.append(f"\nResult: {run['result']}  |  cost ${run['cost_usd']}  |  version {run['version']}")
    report_path.write_text("\n".join(report) + "\n")
    print(f"\nReport written to {report_path}")
```

- The first line works out the cost: tokens times price per million, divided by a million. `1_000_000` is just a million; Python lets you use underscores so you can read it. `round(..., 5)` keeps five decimal places.
- `RUN_LOG.open("a")` opens the log in **append** mode. `"a"` can only add to the end of the file, never change what's already there. That's what makes the log trustworthy. `with` makes sure the file is closed properly afterwards.
- `json.dumps(run)` turns the dictionary into one line of JSON text.
- The rest is last post's report code, moved in here, with two additions. A run that didn't end `"ok"` gets `-FAILED` in its file name, so failures stand out in the folder. And the report ends with a result line showing the outcome, cost and version.

Now delete the old report-writing lines at the end of `main` (the five lines starting `reports = pathlib.Path(__file__).parent / "reports"`) and put this in their place:

```python
    finish(run, report)
```

Run the agent as the scheduler would:

```bash
python agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

**Checkpoint: a `runs.jsonl` file appears next to `agent.py`.** Open it. There's one long line with the time, task, every tool call, the token counts, `"result": "ok"` and `"cost_usd"`. When I ran this on the demo folder it cost under 2 cents. Run it again and a second line appears underneath. The first is never touched.

## Question 3: what can it spend?

The 20-round cap stops one run from spinning forever. Nothing stops a month of runs from adding up, or a bug from firing the agent a thousand times.

Here's why I care. In August 2026 one of my own API keys burned through $103 of credit in eighty minutes on a Friday evening, while I was doing something else entirely. I found out nine days later, when I went to use the account and the money was gone. The console's logs told me which key and which night. Nothing told me while it was happening, because I'd never set a limit.

Two fixes, both cheap.

**Fix 1 costs no code.** In the Anthropic console, find the spend limits under your billing settings and set a monthly limit for your account. It would have saved me $100. Do it before you read on.

While you're in the console: **one API key per agent, named after the agent.** My burned key was named after the service it belonged to, and that's the only reason "which key was it?" took seconds instead of days. A key called `my-key-2` tells you nothing.

**Fix 2 is a guard inside the agent**, so it refuses to start once the month's spending passes a number you chose.

### 3a. Add up this month's spending

Above `def finish`, add:

```python
def spent_this_month():
    if not RUN_LOG.exists():
        return 0.0
    this_month = f"{datetime.datetime.now():%Y-%m}"
    total = 0.0
    for line in RUN_LOG.read_text().splitlines():
        run = json.loads(line)
        if run["started"].startswith(this_month):
            total += run["cost_usd"]
    return total
```

- No log yet means nothing spent yet.
- `this_month` is text like `2026-09`.
- The loop reads the log one line at a time. `json.loads` turns a line of JSON back into a dictionary, the reverse of `json.dumps`.
- If the run started this month, its cost is added to the total.

Notice that the guard is built on the log from question 2. The questions stack: you can't limit spending you never recorded.

### 3b. Refuse to start when the limit is reached

In `main`, straight after the `run = {...}` lines, add:

```python
    spent = spent_this_month()
    if spent >= MONTHLY_LIMIT_USD:
        run["result"] = f"refused: ${spent:.2f} already spent this month, limit is ${MONTHLY_LIMIT_USD:.2f}"
        finish(run, report)
        sys.exit(1)
```

If this month's total has reached the limit, the run is recorded as refused, written to the log and a FAILED report, and the program stops. `:.2f` shows a number to two decimal places. `sys.exit(1)` ends the program with **exit code** 1. Every program reports a number when it ends: 0 means success, anything else means something went wrong. Schedulers and other tools read that number.

The check happens *before* the agent calls the API, so a refused run costs nothing.

Test it without spending money. Temporarily change `MONTHLY_LIMIT_USD = 2.00` to `MONTHLY_LIMIT_USD = 0.00` and run the agent.

**Checkpoint: the run is refused straight away, and a report ending `-FAILED.md` appears.** Set the limit back to `2.00`. $2 a month is plenty for this agent. Choose your own number, but choose one.

## Question 4: what happens when it fails?

Cron doesn't care that the API was down this morning, or that your key expired. Right now an error inside the loop crashes the agent before `finish` runs, so the failure leaves no log line and no report. The one run you most need to know about is the one that leaves no trace.

### 4a. Catch the failure

In `main`, select everything from the `client = anthropic.Anthropic()` line down to the last line of the loop, `messages.append({"role": "user", "content": results})`, and press Tab once. VS Code indents the whole block one step. (If `client = ...` sits above the `memory_path` lines in your file, move it down so it's directly above the `for` line first.) Then type `try:` on a new line above it, and add these lines under it:

```python
    try:
        client = anthropic.Anthropic()
        for _ in range(20):                     # safety cap: a confused agent can't loop forever
```

and, under the loop, back at the same indentation as `try:`:

```python
    except Exception as error:
        run["result"] = f"FAILED: {error}"
```

- `try:` means "attempt everything indented below me".
- If anything in there raises an error, Python jumps straight to `except` instead of crashing. The error is saved in `error`, and we record it as the run's result.
- `client = anthropic.Anthropic()` goes *inside* the `try` on purpose. A missing or wrong key fails right there, and that's one of the most likely failures on a schedule. It happened to me while testing this course.

This is a different `try` from the one in `run_tool`. That one catches a single tool's error and hands it back to the model to deal with. This one catches anything that stops the whole run.

### 4b. Finish, then say so with the exit code

Replace the `finish(run, report)` line at the end of `main` with:

```python
    finish(run, report)
    if run["result"] != "ok":
        sys.exit(1)
```

The run is always logged and reported, success or failure, and a failure ends with exit code 1.

Test it by breaking the key on purpose. In the terminal, set a wrong one and run:

```bash
export ANTHROPIC_API_KEY=wrong                  # Mac
$env:ANTHROPIC_API_KEY="wrong"                  # Windows
python agent.py demo "Organise this folder." --auto-approve
```

**Checkpoint: the agent doesn't crash with a wall of red text. It writes a `-FAILED` report, and the last line in `runs.jsonl` has `"result": "FAILED: ..."` with the reason.** Set your real key again afterwards.

The real test for this question: **would you know by lunchtime that the 7am run failed?** A `-FAILED` file in a folder you never open doesn't count. Make checking the reports folder part of your morning, or, once you're comfortable, have the failure send you a notification. Most notification services take one extra line of code. If you wouldn't know, you don't have an agent. You have a hope.

## Question 5: which version is running?

The quiet question. One day the agent will start filing things differently. Was it the model? Its memory? Or did you change the code last Tuesday? If each run records exactly which version of the code it ran, you can answer "what changed?" instead of guessing.

The standard way to version code is **git**. If you're not using it yet, the side post on version control (not yet written) sets it up on this exact project in about fifteen minutes. The code below still works without git. It just records "unknown".

### 5a. Ask git which version this is

Above `def spent_this_month`, add:

```python
def code_version():
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                cwd=HERE, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return "unknown (not a git repo)"
```

- `subprocess.run` runs another program, here `git rev-parse --short HEAD`. That's git's way of saying "give me the short ID of the version I'm on", something like `b51f8a6`.
- `cwd=HERE` runs it in the agent's folder. `capture_output=True, text=True` hands git's answer back to Python as text instead of printing it. `check=True` treats a git error as an error.
- If git isn't installed, or the folder isn't a git project, the `except` returns "unknown" instead of crashing the run over something that isn't the agent's job.

### 5b. Record it with every run

In the `run = {...}` line, replace `"version": "unknown"` with:

```python
"version": code_version(),
```

Run the agent once more.

**Checkpoint: the newest line in `runs.jsonl` has a `"version"`, and so does the result line at the bottom of the newest report.** It's either a short git ID or "unknown (not a git repo)".

## Where this stops

Everything in this series runs on one machine and relies on one person's judgement. For a personal agent, that's enough.

The moment more people, more machines or other people's data get involved, each question gets harder. Permissions become identity systems. The run log becomes monitoring dashboards. The spend guard becomes a gateway every call passes through. "Which version?" becomes a deployment pipeline. The tools change, but the five questions don't. If you ever find yourself in a meeting about agent platforms, you already know the checklist that meeting is really about.

## Try this

Answer the five questions out loud for your own agent, one sentence each:

1. What is it allowed to do?
2. What did it do yesterday?
3. What's the most it can spend this month?
4. If this morning's run failed, how would you know?
5. Which version ran?

Any question you can't answer in one sentence is your next evening's work. When you can answer all five, you know more about your agent than many teams know about the AI agents they ship.

---

← [Part 5](05-put-your-agent-on-a-schedule.md) · [Series page](README.md) · [Part 7](07-swap-the-model.md) →
