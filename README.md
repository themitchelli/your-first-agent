# Your First Agent

A course that builds a real AI agent from a single readable Python file up to something you'd trust to run on a schedule. Companion code for the "Your First Agent" series on [stevesaidiaries.com](https://stevesaidiaries.com).

An agent is four things: a **model** (the LLM), **tools** (functions that let it act on your machine), **memory** (a file it reads at the start and updates at the end), and a **trigger** (what starts a run).

## How this repo works

Each lesson folder is the complete, working project as it stands at the end of that lesson. Code along in your own folder and compare, or copy a lesson folder and run it as-is. The differences between one lesson and the next are the lesson.

| Lesson | Folder | What changes |
|---|---|---|
| 1 | [`lessons/01-your-first-agent`](lessons/01-your-first-agent) | The whole agent in one file you can read in ten minutes |
| 2+ | coming | Memory and a schedule; structure when the code earns it; production |

## Setup

Python 3.9+ and an Anthropic API key ([console.anthropic.com](https://console.anthropic.com), about £5 of credit is plenty). An API key is separate from a Claude subscription — even subscribers need to create one.

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

Then start with [lesson 1](lessons/01-your-first-agent).
