*Part 5 of [Your First Agent](README.md).*
*Code for this post: [`lessons/05-a-schedule`](../lessons/05-a-schedule).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Put your agent on a schedule

Your agent works when you run it. This post makes it work when you don't.

Remember the trigger ladder from the first post? Rung one is you: you type the command, you watch, you type y. Rung two is the clock. By the end of this post your agent runs every morning at a time you choose, tidies whatever has landed in its folder overnight, and leaves you a report.

Here's the surprise. The agent itself barely changes. The loop, the instructions, the tools and the memory you built are already everything an autonomous agent needs. What breaks when the clock takes over is everything that assumed *you were there*. Nobody is there to type y. Nobody is watching the terminal. And the scheduler doesn't know where your project is, which Python to use or what your API key is.

We fix those three things in turn, one small step at a time, then hand the agent to the clock.

**Start of session:** VS Code open on `my-first-agent`, a new terminal, `(.venv)` showing, key set. If anything fails, the setup post's "When it goes wrong" section has the fixes. You need your working `agent.py` from the last post. If yours isn't working, copy `lessons/04-hands-and-memory/agent.py` from the course files. Your file at the end of this post matches `lessons/05-a-schedule/agent.py`.

## Step 1: nobody is there to type y

At 7am, `input()` asks its question to an empty room and waits forever. The agent never finishes. We need a way to say yes in advance.

Before writing any code, decide *how much* yes. Permission isn't a switch. It's a dial:

1. **Read only.** The scheduled agent looks and reports but never changes anything. Useful, and completely safe.
2. **Yes, inside the fence.** Changes are approved automatically, but only inside the one folder. That's what we build today.
3. **Yes to everything, anywhere.** Not yet. The next post is about why you'd want far more in place before that.

Option 2 is safe to build because of work you've already done. `safe_path` checks every file change, approved or not. Auto-approve doesn't remove the fence. It removes the person standing at the gate.

### 1a. A flag you add to the command

At the top of `agent.py`, change the imports so they read:

```python
import datetime
import pathlib
import sys

# ---- settings ----

AUTO_APPROVE = "--auto-approve" in sys.argv
```

- `# ---- settings ----` is the third signpost, above the tools. Anything that's a setting for the whole program goes under it from now on.
- `datetime` gives us today's date and time. We'll use it for report names in step 2.
- `sys.argv` is the list of words you typed on the command line. `"--auto-approve" in sys.argv` is `True` if one of those words is `--auto-approve` and `False` if not. We store the answer in `AUTO_APPROVE`, written in capitals, a Python habit for "set once, never changed".

A word starting with `--` is called a **flag**. It's the usual way to switch a behaviour on for one run. Without the flag, the agent behaves exactly as it did in the last post.

### 1b. One place that decides "allowed?"

Right now `write_file` and `move_file` each ask their own question with `input()`. Two copies of the same decision is one too many, especially now that the decision is getting smarter. Above `write_file`, add:

```python
def allowed(question):
    if AUTO_APPROVE:
        print(f"  {question} auto-approved")
        return True
    answer = input(f"\n  {question} [y/n] ")
    return answer.strip().lower() == "y"
```

- If the flag is on, it prints the question with "auto-approved" after it, so the record shows what was allowed, and returns `True`.
- If the flag is off, it asks you, exactly as before. `answer.strip().lower() == "y"` is `True` only if you typed y.

### 1c. Use it in both tools

In `write_file`, replace these two lines:

```python
    answer = input(f"\n  Agent wants to write '{name}' - allow? [y/n] ")
    if answer.strip().lower() != "y":
```

with this one:

```python
    if not allowed(f"Agent wants to write '{name}' - allow?"):
```

In `move_file`, replace its two `answer` lines the same way:

```python
    if not allowed(f"Agent wants to move '{name}' -> '{new_name}' - allow?"):
```

`if not allowed(...)` reads almost as English: if this isn't allowed, return the "declined" message. The rest of each tool stays the same.

### 1d. Let `main` ignore the flag

`main` reads the folder from `sys.argv[1]` and the task from `sys.argv[2]`. If someone puts the flag first, `python agent.py --auto-approve demo "..."`, the positions shift and the agent tries to use a folder called `--auto-approve`. At the top of `main`, replace the `workspace` and `task` lines with:

```python
    args = [a for a in sys.argv[1:] if a != "--auto-approve"]
    workspace = pathlib.Path(args[0])
    task = args[1]
```

The first line builds a new list: every word after `agent.py` except the flag. Now the flag can go anywhere and the folder and task are always found.

Test it. Drop a new badly named file into `demo` first, so there's something to do. Anything will do, for example a file called `scan0099.txt` containing "Invoice 7730, Sunrise Window Cleaning, £28". Then:

```bash
python agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

**Checkpoint: the agent runs start to finish without stopping, and every change prints "auto-approved".** Now run it without the flag and confirm it asks you again. Same agent, dial turned.

Your file should be about 150 lines. Not what you expected? Compare it with `lessons/05-a-schedule/stages/stage1.py` in the course files.

## Step 2: nobody is watching the terminal

When the clock runs the agent, everything it prints goes nowhere. You need a record you can read later: what task it was given, which tools it used, what it said. We'll write one report file per run.

Where it goes matters. The agent can edit anything inside its folder. If the reports lived there, a confused agent could rewrite yesterday's report, and a record the agent can edit tells you nothing you can trust. So reports go *next to* `agent.py`, outside the fence. `memory.md` is what the agent knows, and it's allowed to rewrite it. `reports/` is what actually happened, and the agent can't touch it. Keep those two separate on purpose. The next post leans hard on this.

### 2a. Start the report

In `main`, straight after the `task = args[1]` line, add:

```python
    report = [f"# Run at {datetime.datetime.now():%Y-%m-%d %H:%M}", f"Task: {task}", ""]
```

`report` is a list of lines. It starts with a heading showing the date and time, then the task, then a blank line. `:%Y-%m-%d %H:%M` is a format code: it turns the current time into something like `2026-09-15 07:00`.

### 2b. Record what the agent says

In the loop, find the line that prints the model's text, `print(f"\n{block.text}")`, and add one line under it, lined up with the `print`:

```python
                report.append(block.text)
```

Everything the agent says to you now goes into the report as well.

### 2c. Record every tool call

Find `print(f"  [tool] {block.name}")` and add one line under it:

```python
                report.append(f"- tool: {block.name} {block.input}")
```

This records the tool's name *and* what the model sent it, such as which file it moved and where to. When you're reading a report and wondering why a file ended up somewhere odd, this is the line you'll want.

### 2d. Write the report when the run ends

After the loop finishes, add these lines at the end of `main`, indented four spaces, the same as the `for`:

```python
    reports = pathlib.Path(__file__).parent / "reports"
    reports.mkdir(exist_ok=True)
    report_path = reports / f"{datetime.datetime.now():%Y-%m-%d-%H%M}.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport written to {report_path}")
```

- `pathlib.Path(__file__).parent` is the folder that `agent.py` itself is in. `__file__` always means "this file", so the reports land beside the code wherever you run it from.
- `mkdir(exist_ok=True)` creates `reports` the first time and does nothing after that.
- The file name is the date and time, for example `2026-09-15-0700.md`. Names in that order sort by date automatically.
- `"\n".join(report)` joins the lines into one block of text, which gets written to the file, as UTF-8 like every text file in this course.

Run the same command again, with the flag:

```bash
python agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

**Checkpoint: a `reports` folder appears in the sidebar, outside `demo`, holding a file named with today's date.** Open it. You'll see the task, each tool call with its details, and what the agent said.

Your file should be about 165 lines. Not what you expected? Compare it with `lessons/05-a-schedule/agent.py` in the course files. Step 3 adds no more Python, so that's the finished file.

## Step 3: the scheduler knows nothing

When you run the agent, your terminal is already set up. You're in the project folder, `(.venv)` is on and the key is set. The scheduler starts with none of that. It doesn't know where your project is, which Python to use or what your key is. So we write a tiny script that sets all three up and then runs the agent. The scheduler runs the script.

### 3a. Keep the key in a private file (Mac)

So far the key has lived in the terminal and vanished when you closed it. The scheduler needs to find it with nobody there. We'll store it in a file in your home folder that only your user account can read.

In the terminal, run this line, paste your key when the cursor sits waiting, and press Enter:

```bash
read -s KEY && echo "$KEY" > ~/.anthropic-key && chmod 600 ~/.anthropic-key
```

- `read -s KEY` waits for you to paste something and keeps it hidden, so the key never appears on screen or in your terminal history.
- `echo "$KEY" > ~/.anthropic-key` writes it to a file called `.anthropic-key` in your home folder. The dot at the start makes it a hidden file.
- `chmod 600` sets the file so only your user account can read it.

This is the one place the key is written down. It's outside your project folder on purpose, so it can never end up in anything you share.

### 3b. The script the scheduler runs (Mac)

In VS Code, create a new file in `my-first-agent` called `run.sh` and type:

```bash
#!/bin/bash
# What the scheduler runs. Cron starts with an almost empty environment:
# no project folder, no (.venv), no API key. This script sets up all three.
cd "$(dirname "$0")"
export ANTHROPIC_API_KEY="$(cat ~/.anthropic-key)"
.venv/bin/python agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

- `#!/bin/bash` on the first line tells the computer this is a script for bash, the Mac's command language.
- Lines starting with `#` are comments, notes for humans.
- `cd "$(dirname "$0")"` means "go to the folder this script is in". That fixes the first unknown: where the project is.
- The `export` line reads the key from your private file into the environment, where `anthropic.Anthropic()` looks for it. That fixes the second.
- `.venv/bin/python` uses the Python *inside* your project's `.venv`, the one with `anthropic` installed, without needing `(.venv)` switched on. That fixes the third.

Save it, then make it runnable and test it:

```bash
chmod +x run.sh
./run.sh
```

`chmod +x` marks the file as a program you're allowed to run. `./run.sh` runs it. The `./` means "the one in this folder".

**Checkpoint: the agent runs start to finish and writes a new report.** If this works in the terminal, the scheduler will run the same thing.

### 3c. Hand it to the clock (Mac)

Macs have a built-in scheduler called **cron**. You give it one line saying when to run what. First, get the full path to your script:

```bash
pwd
```

That prints something like `/Users/sam/my-first-agent`. Now open your schedule for editing:

```bash
EDITOR=nano crontab -e
```

`crontab -e` opens your personal schedule in a text editor. `EDITOR=nano` picks nano, a simple editor that runs inside the terminal. Type one line, using your own path from `pwd`:

```
0 7 * * * /Users/sam/my-first-agent/run.sh
```

The five parts before the path say when: minute `0`, hour `7`, then `*` for any day of the month, any month and any day of the week. So: 7:00 every morning. Save with Ctrl+O then Enter, and exit with Ctrl+X.

To check it's saved:

```bash
crontab -l
```

**Checkpoint: your line is listed.** Cron has no "run it now" button, so to prove the schedule works without waiting until 7am, change the `0 7` to a time two minutes from now, such as `32 21` for 9:32pm. Wait, check for a new report, then set it back.

Two Mac traps, both tested:

- **Your project must not be in Documents, Desktop or Downloads.** macOS won't let cron into those folders, and the run fails with "Operation not permitted". That's why the setup post put `my-first-agent` in your home folder. If yours is somewhere else, move it.
- **A sleeping Mac doesn't run cron jobs.** If the lid is closed at 7am, that morning's run is skipped, not delayed. Pick a time when the machine is usually awake.

### Steps 3a to 3c on Windows: Task Scheduler

Windows doesn't have cron. It has **Task Scheduler**, which does the same job through windows and buttons.

**The key.** Store it as a permanent user variable, which Windows keeps between restarts. In PowerShell:

```powershell
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
```

`setx` saves the variable for your user account permanently. Tasks you schedule can read it. Close and reopen VS Code afterwards so new terminals pick it up. Because this line puts the key in your PowerShell history, run `Clear-History` afterwards.

**The script.** Create `run.bat` in `my-first-agent`:

```bat
@echo off
rem What Task Scheduler runs. The API key comes from the permanent user variable set with setx.
cd /d "%~dp0"
.venv\Scripts\python.exe agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
```

- `@echo off` stops Windows repeating each command back as it runs.
- `rem` lines are comments.
- `cd /d "%~dp0"` means "go to the folder this script is in", the Windows version of the Mac line.
- `.venv\Scripts\python.exe` uses the Python inside your project's `.venv`.

Test it by typing `.\run.bat` in the terminal. **Checkpoint: a new report appears.**

**The schedule.** Press the Windows key, type **Task Scheduler** and open it. Click **Create Basic Task**. Name it "My first agent", choose **Daily**, set 7:00, choose **Start a program**, and browse to your `run.bat`. In the **Start in** box, paste the path to your `my-first-agent` folder. Click Finish.

Don't wait for 7am. Task Scheduler can run a task on demand, which is the easier deal than the Mac's cron. Find your task in the list, right-click it and choose **Run**.

**Checkpoint: a new report appears in `reports` within a minute of clicking Run.** If it does, 7am will work. If it doesn't, the task's History tab in Task Scheduler says what went wrong, and the usual cause is the Start in box.

## What memory does on a schedule

In the last post, memory was a nice touch. On a schedule it's what makes the agent useful at all.

On the first run, the agent invents a way of organising the folder: folder names, a naming pattern, perhaps `Invoices/Greenline_Web_Hosting_Invoice_4821.txt`. It writes that down in `memory.md`. The next morning a new file lands, `scan0099.txt`, an invoice from a window cleaner. When I tested this, the agent read its memory and filed the new file as `Invoices/Sunrise_Window_Cleaning_Invoice_7730.txt`: same folder, same pattern, without being told the pattern. Without memory, every morning would invent a fresh scheme and the folder would slowly turn into a museum of competing ideas.

One caveat. A memory file grows. The agent's instructions ask for "a short note", which helps, but after weeks of runs you'll want to look at `memory.md` and trim it. Keeping a memory short and accurate is a real problem that the biggest AI systems have too. Yours is just small enough to fix by hand.

## Cost: do the multiplication

When you ran the agent by hand, cost was a curiosity. On a schedule it's a multiplication: whatever one run costs, times every day of the year. A run that tidies a handful of new files on Claude Haiku costs a few pence (as of September 2026). Most mornings, with nothing new to sort, it costs much less, because the agent lists the folder, sees nothing to do and stops. Call it a few pounds a year.

Make that multiplication a habit before you schedule anything. A run that costs 20p looks harmless until it's 20p times 365 times however many agents you end up running.

## Try this

Schedule the agent for a time you're usually asleep, with the Mac awake or the PC on. The next morning, open the newest file in `reports` *before* you look at the folder. Read what it says it did, then check the folder against it.

If anything it did surprises you in a bad way, good. Write down what you wish it had asked you first. That list is your first agent policy, and it's exactly what the next post is about: what "production" means when nobody is watching.

---

← [Part 4](04-give-your-agent-hands-and-a-memory.md) · [Series page](README.md) · [Part 6](06-what-production-means-for-an-agent.md) →
