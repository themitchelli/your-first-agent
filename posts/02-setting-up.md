*Part 2 of [Your First Agent](README.md).*
*Code for this post: [`lessons/02-setting-up`](../lessons/02-setting-up).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# Setting up: everything you need before you build

This post installs everything the course needs and checks each piece before moving on. There are five things to get: an editor, Python, one Python package, git with the course files, and an API key. None of it is hard. It is, though, exactly where tutorials lose people, so we go slowly. If something fails, that's normal. Fix it here and the next post will be smooth.

Every step ends with a checkpoint. Don't move on until you've seen it.

One rule about the code boxes. Terminal commands, the short lines you run, are fine to copy and paste. Where Mac and Windows differ there are two boxes, labelled, and you use the one for your machine. Python files, the code that becomes the agent, you type. That starts in the last step of this post, and the reason is in the next one.

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

It also checks your file as you type. If a line gets a red or yellow underline, hover over it and read the message. That's the Python extension, not the AI helper, and it's allowed. It catches typos and stray spaces before you run anything.

**Checkpoint: the Python extension shows as installed.**

### Getting around VS Code

Three parts of the window matter for this course, and later posts use these names.

![VS Code with the sidebar, the editor and the terminal panel labelled](images/02-vscode-layout.png)

- **The sidebar**, down the left. It shows the files in whatever folder you've opened. Click a file to open it.
- **The editor**, in the middle. Where you type code. The numbers down its left edge are line numbers; later posts use them as a sanity check.
- **The terminal**, a panel across the bottom. You type a command, press Enter, and read what comes back. It isn't open until you open it: choose **Terminal > New Terminal** from the menu bar at the top of the screen, or press Ctrl+` (the backtick key, top left of most keyboards). If the panel ever disappears, the menu brings it back.

Four things you'll want by the third post, all in the editor:

- **Find:** Cmd+F on Mac, Ctrl+F on Windows, then type the text you're looking for. When a post says "find the line that says X", this is how.
- **Outline:** in the sidebar, below your files, there's a section called Outline. It lists every function in the open file, and clicking one jumps to it. Once your agent is a couple of hundred lines long, this is the map.
- **Compare two files:** right-click a file in the sidebar and choose **Select for Compare**, then right-click another file and choose **Compare with Selected**. Every line that differs is highlighted side by side. This is how you'll check your file against the course's copy when a checkpoint doesn't match.
- **Indent guides:** faint vertical lines run down the editor, one for each level of indentation. Python builds its structure out of those levels, so the lines show you which block a line belongs to. The build post explains why that matters.

## 2. Install Python

Python is the language the agent is written in. You may already have it. Open the terminal (Terminal > New Terminal) and type the command for your machine, then press Enter:

**Mac**

```bash
python3 --version
```

**Windows**

```powershell
python --version
```

Anything that starts with 3.10 or higher is fine. If you get "command not found", or a number below 3.10, install it:

- **Mac:** download the installer from python.org and run it.
- **Windows:** download from python.org and run the installer. On the first screen, **tick the box that says "Add python.exe to PATH"** before clicking Install. Forgetting that box is the most common setup failure on Windows. If you missed it, run the installer again and tick it.

![The Windows Python installer, with the Add python.exe to PATH box ticked](images/02-windows-python-path.png)

After installing, close VS Code completely and reopen it, then open a new terminal and run the version check again. A terminal only notices new software when it starts.

**Checkpoint: the terminal prints a version number of 3.10 or higher.**

## 3. Make the project folder

Everything we build lives in one folder. Create an empty folder called `my-first-agent` directly inside your **home folder**, using Finder or File Explorer as you normally would. On Mac, that's the folder with the house icon (in Finder, choose Go > Home). On Windows, it's `C:\Users\` followed by your name.

Why not Documents? Later in the course the agent runs on a schedule, and on a Mac the scheduler isn't allowed into Documents, Desktop or Downloads. It fails with "Operation not permitted". The home folder avoids that trap from the start.

In VS Code, choose **File > Open Folder** and pick `my-first-agent`. If VS Code asks whether you trust the authors of the files in this folder, say yes. You are the author.

Now open a new terminal (**Terminal > New Terminal**). Because you opened the folder first, the terminal starts inside it. Check:

**Mac**

```bash
pwd
```

**Windows**

```powershell
Get-Location
```

**Checkpoint: the path printed ends in `my-first-agent`.** When a later post says "in your project folder", this is what it means: VS Code open on this folder, with a terminal at the bottom.

## 4. Give the project its own Python

We're going to create a virtual environment. It sounds grand, but it's just a private copy of Python that lives inside your project folder, in a subfolder called `.venv`. Anything you install goes into that copy and nowhere else, so this project can't break other software on your machine.

In the terminal:

**Mac**

```bash
python3 -m venv .venv
```

**Windows**

```powershell
python -m venv .venv
```

A `.venv` folder appears in the sidebar on the left. VS Code may pop up a message asking whether to use this environment for the workspace. Say yes.

Now switch it on. Close the terminal (the bin icon on the terminal panel) and open a new one. The Python extension notices `.venv` and switches it on for you. You'll see `(.venv)` at the start of the terminal line.

![The terminal line beginning with (.venv)](images/02-venv-prefix.png)

If `(.venv)` doesn't appear, switch it on by hand:

**Mac**

```bash
source .venv/bin/activate
```

**Windows**

```powershell
.venv\Scripts\Activate.ps1
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

## 6. Get the course files

The course has a public folder of files on GitHub: a messy demo folder for the agent to practise on, a test folder for a later post, and a copy of the finished code at the end of every post, so you can compare when something doesn't match. GitHub has no download button for a single folder, so we'll fetch the whole thing the way programmers do, with a tool called **git**.

Git is also how the version control side post works later, so it earns its place. For now it's one command.

### Install git

Check whether you already have it:

```bash
git --version
```

- **Mac:** if a dialog pops up offering to install the command line developer tools, click Install. It's a big download and takes a few minutes. When it finishes, run the command again.
- **Windows:** download the installer from git-scm.com and run it. It has a lot of option screens; accept the defaults on all of them. Then close VS Code, reopen it, open a new terminal and run the command again.

**Checkpoint: the terminal prints a git version number.**

### Clone the repo

"Clone" means copy a project from GitHub to your machine, with a link back so you can fetch updates later. We'll put it in your home folder, next to `my-first-agent`, not inside it. In the terminal:

**Mac**

```bash
cd ~
git clone https://github.com/themitchelli/your-first-agent.git
cd ~/my-first-agent
```

**Windows**

```powershell
cd ~
git clone https://github.com/themitchelli/your-first-agent.git
cd ~\my-first-agent
```

The first line goes to your home folder. The second fetches the course files into a new folder called `your-first-agent`. The third takes you back to your project. `~` is shorthand for your home folder on both systems.

**Checkpoint: your home folder now contains `your-first-agent` alongside `my-first-agent`.** Look in Finder or File Explorer if you're not sure.

Two things to know about the new folder:

- It has a hidden `.git` folder inside it. That's git's memory of the project. Leave it alone.
- **Your agent never goes in there.** You build in `my-first-agent`. The course folder is for copying from and comparing against. If you need the latest version of the course files, run `git pull` from inside `your-first-agent` and it fetches whatever changed.

When a later post says "compare with `lessons/03-build-your-first-agent/stages/stage2.py` in the course files", that's a path inside this folder. Open it with File > Open File, or use the compare trick from step 1.

## 7. Get an API key

This is the step that confuses almost everyone, including people who have paid for AI subscriptions for years. **A Claude or ChatGPT subscription is not an API key.** A subscription pays for the chat app. Programs talk to the model through a separate door, called the API, which has its own account and its own credit. Subscribers need to do this step too.

1. Go to console.anthropic.com and sign up.
2. Find Billing and add credit. £5 is plenty. A run of the agent in this course costs a few pence at most, so £5 covers far more practice than you'll need (as of September 2026).
3. While you're there, set a monthly spend limit. A few pounds. It's the one setting that stops a bug from becoming a bill, and a later post tells the story of why.
4. Find API Keys and create a key. Copy it straight away, because it's shown once. It starts with `sk-ant-` followed by a long string.

Treat the key like a bank card number. Don't paste it into a file you might share, a chat, an email or a screenshot. For this course it goes in one place only: an environment variable. That's a value the terminal holds and hands to any program you run from it.

In the terminal, with your own key in place of the placeholder:

**Mac**

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Windows**

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

This value disappears when the terminal closes. That's annoying, but it's also safe. Set it again in each new terminal you open for the course. You will forget. Everyone does. The error it produces is in the last section of this post, and it means nothing is broken.

**Checkpoint: this prints `sk-ant` and nothing more.** It shows only the first six characters, so the rest of the key doesn't end up on screen.

**Mac**

```bash
python3 -c "import os; print(os.environ['ANTHROPIC_API_KEY'][:6])"
```

**Windows**

```powershell
python -c "import os; print(os.environ['ANTHROPIC_API_KEY'][:6])"
```

## 8. The end-to-end test

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

Keep `check.py`. It's your smoke test. Months from now, if the agent misbehaves, run this first to prove the setup still works before you go looking for bugs in your code.

## When it goes wrong

Errors in Python arrive as a block of red text called a traceback. Read it from the bottom. The last line is the message, and everything above it is the trail of where the error came from. Here are the last lines you're most likely to see in this course, what each one means, and which step fixes it.

```
ModuleNotFoundError: No module named 'anthropic'
```

The `(.venv)` prefix is missing from your terminal line, so you're running the wrong Python. Open a new terminal or run the activate line. Step 4.

```
TypeError: "Could not resolve authentication method. Expected one of api_key, auth_token, or credentials to be set. ..."
```

The key isn't set in this terminal. Usually you opened a new terminal, or restarted VS Code, and didn't set it again. Run the export line. Step 7.

```
anthropic.AuthenticationError: Error code: 401 - ... 'invalid x-api-key'
```

A key is set, but it's wrong. Usually a copy-and-paste missed a character or picked up a space. Create a fresh key in the console and set it again. Step 7.

```
anthropic.BadRequestError: ... credit balance is too low
```

The key works and the account has run out of credit. Add credit in the console. Step 7.

```
python: command not found
```

Mac only. Use `python3 check.py`, or check that `(.venv)` is showing, because inside the environment `python` works too.

```
IndentationError: unexpected indent
IndentationError: expected an indented block
```

You won't see these until the next post, but they belong here. Python builds its structure out of the spaces at the start of lines. The first means a line is pushed in further than it should be. The second means the line after a colon isn't pushed in at all. The build post has a section on this.

Every later post starts with the same routine, folder open, terminal, `(.venv)`, key, and every later post can send you back here. Bookmark this section.

## Try this

Quit VS Code completely. Reopen it, open the `my-first-agent` folder, open a new terminal, check for `(.venv)`, set your key, and run `check.py`. Do it without this post open. That's the exact routine at the start of the next post, and doing it once from memory is worth more than reading this post three times. If it fails, the section above says why.

---

← [Part 1](01-what-an-agent-actually-is.md) · [Series page](README.md) · [Part 3](03-build-your-first-agent.md) →
