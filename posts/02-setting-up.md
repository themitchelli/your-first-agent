*Part 2 of [Your First Agent](README.md).*
*Code for this post: [`lessons/02-setting-up`](../lessons/02-setting-up).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Setting up: everything you need before you build

This post installs everything the course needs and checks each piece before moving on. There are four things to get: an editor, Python, one Python package and an API key. None of it is hard. It is, though, exactly where tutorials lose people, so we go slowly. If something fails, that's normal. Fix it here and the next post will be smooth.

Every step ends with a checkpoint. Don't move on until you've seen it.

## 1. Install VS Code

VS Code is a free code editor from Microsoft. It's where you'll write the agent and also where you'll run it, because it has a terminal built in. One window for everything.

Download it from code.visualstudio.com and install it like any other app. On Mac, drag it into Applications. On Windows, run the installer and accept the defaults.

Why not Notepad or TextEdit? Python cares about spaces at the start of lines, and a plain text app won't show you when one is wrong. TextEdit is worse: it saves "rich text" by default, which quietly breaks Python files. Use VS Code.

**Checkpoint: VS Code opens and shows a Welcome tab.**

### Switch off the AI helpers

VS Code comes with AI features that offer to write code for you. For this course, turn them off. You're here to understand how an agent works, and you only get that by typing the code yourself and watching it run. Once you've finished the course, switch them back on with a much better idea of what they're doing.

Open Settings (Cmd+, on Mac, Ctrl+, on Windows), type **AI features** in the search box, and tick the setting that disables them. If VS Code asks you to sign in to Copilot at any point, say no.

### Add the Python extension

Click the Extensions icon in the left sidebar (four small squares), search for **Python**, and install the one published by Microsoft. It lets VS Code understand Python files and find the right Python for your project.

**Checkpoint: the Python extension shows as installed.**

## 2. Install Python

Python is the language the agent is written in. You may already have it. Open VS Code's terminal with **Terminal > New Terminal** from the top menu. A panel opens at the bottom of the window. That panel is the terminal: you type a command, press Enter, and read what comes back.

Type this and press Enter:

```bash
python3 --version        # Mac
python --version         # Windows
```

Anything that starts with 3.10 or higher is fine. If you get "command not found", or a number below 3.10, install it:

- **Mac:** download the installer from python.org and run it.
- **Windows:** download from python.org and run the installer. On the first screen, **tick the box that says "Add python.exe to PATH"** before clicking Install. Forgetting that box is the most common setup failure on Windows. If you missed it, run the installer again and tick it.

After installing, close VS Code completely and reopen it, then open a new terminal and run the version check again. A terminal only notices new software when it starts.

**Checkpoint: the terminal prints a version number of 3.10 or higher.**

## 3. Make the project folder

Everything we build lives in one folder. Create an empty folder called `my-first-agent` directly inside your **home folder**, using Finder or File Explorer as you normally would. On Mac, that's the folder with the house icon (in Finder, choose Go > Home). On Windows, it's `C:\Users\` followed by your name.

Why not Documents? Later in the course the agent runs on a schedule, and on a Mac the scheduler isn't allowed into Documents, Desktop or Downloads. It fails with "Operation not permitted". The home folder avoids that trap from the start.

In VS Code, choose **File > Open Folder** and pick `my-first-agent`. If VS Code asks whether you trust the authors of the files in this folder, say yes. You are the author.

Now open a new terminal (**Terminal > New Terminal**). Because you opened the folder first, the terminal starts inside it. Check:

```bash
pwd                      # Mac
Get-Location             # Windows
```

**Checkpoint: the path printed ends in `my-first-agent`.** When a later post says "in your project folder", this is what it means: VS Code open on this folder, with a terminal at the bottom.

## 4. Give the project its own Python

We're going to create a virtual environment. It sounds grand, but it's just a private copy of Python that lives inside your project folder, in a subfolder called `.venv`. Anything you install goes into that copy and nowhere else, so this project can't break other software on your machine.

In the terminal:

```bash
python3 -m venv .venv    # Mac
python -m venv .venv     # Windows
```

A `.venv` folder appears in the sidebar on the left. VS Code may pop up a message asking whether to use this environment for the workspace. Say yes.

Now switch it on. Close the terminal (the bin icon on the terminal panel) and open a new one. The Python extension notices `.venv` and switches it on for you. You'll see `(.venv)` at the start of the terminal line.

If `(.venv)` doesn't appear, switch it on by hand:

```bash
source .venv/bin/activate          # Mac
.venv\Scripts\Activate.ps1         # Windows
```

On Windows you may get a red error saying running scripts is disabled. That's a Windows safety setting. Run this once, then try the activate line again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Checkpoint: the terminal line starts with `(.venv)`.** Whenever you work on the course, look for that prefix before running anything. If it's missing, open a new terminal or run the activate line.

## 5. Install the Anthropic package

With `(.venv)` showing, install the one package the agent needs. It's the official library for talking to Claude from Python:

```bash
pip install anthropic
```

Lines scroll past for a few seconds and it finishes with "Successfully installed".

**Checkpoint: this prints a version number instead of an error.**

```bash
pip show anthropic
```

## 6. Get an API key

This is the step that confuses almost everyone, including people who have paid for AI subscriptions for years. **A Claude or ChatGPT subscription is not an API key.** A subscription pays for the chat app. Programs talk to the model through a separate door, called the API, which has its own account and its own credit. Subscribers need to do this step too.

1. Go to console.anthropic.com and sign up.
2. Find Billing and add credit. £5 is plenty. A run of the agent in this course costs a few pence at most, so £5 covers far more practice than you'll need (as of September 2026).
3. Find API Keys and create a key. Copy it straight away, because it's shown once. It starts with `sk-ant-` followed by a long string.

Treat the key like a bank card number. Don't paste it into a file you might share, a chat, an email or a screenshot. For this course it goes in one place only: an environment variable. That's a value the terminal holds and hands to any program you run from it.

In the terminal:

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here          # Mac
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"          # Windows
```

This value disappears when the terminal closes. That's annoying, but it's also safe. Set it again in each new terminal you open for the course.

**Checkpoint: this prints `sk-ant` and nothing more.** It shows only the first six characters, so the rest of the key doesn't end up on screen.

```bash
python3 -c "import os; print(os.environ['ANTHROPIC_API_KEY'][:6])"     # Mac
python -c "import os; print(os.environ['ANTHROPIC_API_KEY'][:6])"      # Windows
```

## 7. The end-to-end test

Now prove the whole chain works together: editor, terminal, Python, package, key and credit.

In VS Code, click the new file icon at the top of the sidebar, name the file `check.py` and press Enter. Type this in, rather than pasting it. It's short, and typing it is good practice for the next post:

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'setup complete' and one encouraging sentence."}],
)
print(response.content[0].text)
```

Save it (Cmd+S or Ctrl+S). Here's what those lines do. `import anthropic` loads the package you installed. `anthropic.Anthropic()` creates a client, which finds your key in the environment variable on its own. `messages.create` sends one message to Claude Haiku, a fast and cheap model, and waits for the reply. The last line prints the reply's text. You'll meet each of these again in the next post, where we build on them.

Run it in the terminal:

```bash
python check.py
```

**Checkpoint: Claude replies with "setup complete" and a sentence of encouragement.** You just made your first API call. Everything the agent in the next post needs, your machine has now proven it can do.

If you got an error instead, the message usually tells you which step to revisit:

- `No module named 'anthropic'`: the `(.venv)` prefix is missing. Go back to step 4.
- An error mentioning `api_key` or `authentication`: the key isn't set in this terminal. Go back to step 6.
- An error mentioning `credit` or `billing`: add credit in the console.
- `python: command not found` on Mac: use `python3 check.py`, or check that `(.venv)` is showing, because inside the environment `python` works too.

Keep `check.py`. It's your smoke test. Months from now, if the agent misbehaves, run this first to prove the setup still works before you go looking for bugs in your code.

## Try this

Quit VS Code completely. Reopen it, open the `my-first-agent` folder, open a new terminal, check for `(.venv)`, set your key, and run `check.py`. Do it without this post open. That's the exact routine at the start of the next post, and doing it once from memory is worth more than reading this post three times.

---

← [Part 1](01-what-an-agent-actually-is.md) · [Series page](README.md) · [Part 3](03-build-your-first-agent.md) →
