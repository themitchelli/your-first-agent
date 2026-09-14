# Your First Agent

A course that builds a real AI agent from a single readable Python file up to something you'd trust to run on a schedule. Companion code for the "Your First Agent" series on [stevesaidiaries.com](https://stevesaidiaries.com).

An agent is four things: a **model** (the LLM), **tools** (functions that let it act on your machine), **memory** (a file it reads at the start and updates at the end), and a **trigger** (what starts a run).

## How this repo works

Each lesson folder is the complete, working project as it stands at the end of that post. Code along in your own folder and compare, or copy a lesson folder and run it as-is. The differences between one lesson and the next are the lesson.

Folder numbers match post numbers. Posts 1 and 2 have no agent code; post 2's smoke test is in `02-setting-up`.

| Post | Folder | What you build |
|---|---|---|
| 1. What an agent actually is | none | The four boxes and the trigger ladder, no code |
| 2. Setting up | [`lessons/02-setting-up`](lessons/02-setting-up) | VS Code, Python, the package, an API key and `check.py` |
| 3. Build your first agent | [`lessons/03-build-your-first-agent`](lessons/03-build-your-first-agent) | One tool, then the model and the loop: about 25 lines that make it an agent |
| 4. Give your agent hands and a memory | [`lessons/04-hands-and-memory`](lessons/04-hands-and-memory) | Read, write and move inside a fence, with your approval, plus memory |
| 5. Put your agent on a schedule | [`lessons/05-a-schedule`](lessons/05-a-schedule) | Auto-approve, a report per run, and cron or Task Scheduler |
| 6. What production means for an agent | [`lessons/06-production`](lessons/06-production) | A run log, a spend limit, failures you'll notice, and the code version |
| 7. Swap the model | [`lessons/07-swap-the-model`](lessons/07-swap-the-model) | A tiny harness: same agent, three models, scored on the result |
| 8. When to break it up | [`lessons/08-structure`](lessons/08-structure) | The agent in four files, and tests that need no API |

## Setup

Python 3.10+ (the anthropic package requires it) and an Anthropic API key ([console.anthropic.com](https://console.anthropic.com), about £5 of credit is plenty). An API key is separate from a Claude subscription; even subscribers need to create one.

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

Then start with [post 3](lessons/03-build-your-first-agent), or [post 2](lessons/02-setting-up) if you haven't run `check.py` yet.
