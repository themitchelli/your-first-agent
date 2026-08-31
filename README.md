# Your First Agent

A complete AI agent in one Python file, small enough to read in ten minutes.

An agent is four things: a **model** (the LLM), **tools** (functions that let it act on your machine), **memory** (a file it reads at the start and updates at the end), and a **trigger** (what starts a run; here, you). This repo is the companion code for the "Your First Agent" series on [stevesaidiaries.com](https://stevesaidiaries.com).

## Setup

You need Python 3.9+ and an Anthropic API key ([console.anthropic.com](https://console.anthropic.com), about £5 of credit is plenty).

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...   # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```

## First run

The repo ships with a `demo/` folder of deliberately messy files. Point the agent at it:

```bash
python agent.py demo "Organise this folder: rename the files sensibly, group them into subfolders, and tell me what's in it"
```

The agent will list the files, read them, then ask your permission before every rename or write. When it finishes it updates `demo/memory.md` with what it did, so the next run starts with that knowledge.

Then try it on a real messy folder. It can only see and touch the folder you name; nothing else.

## How it works

Open `agent.py`. The heart of it is one loop:

1. Send the model the task (plus its memory) and the list of tools.
2. If the model asks to use a tool, run the function and send back the result.
3. Repeat until the model stops asking for tools. That's the answer.

Everything else is the three file tools, a path check so the agent can't escape its folder, a y/n prompt before any change, and a 20-turn safety limit so a confused run can't spend money forever.

## Using a different provider

The code uses Anthropic's API. Any provider with tool calling works the same way; swap the client and the request call, keep the loop.
