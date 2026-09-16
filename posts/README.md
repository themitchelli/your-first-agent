# Your First Agent

*Draft posts for testers. The finished series will live at stevesaidiaries.com; these copies will be replaced by links when each post goes live. Please read [TESTING.md](../TESTING.md) first.*

Everyone is selling you agents. This series has you build one instead, from a single Python file you can read in ten minutes to something you'd trust to run every morning while you sleep. No framework, no platform, no prior Python. You type every line yourself and you understand every line you type.

## What you need

- A Mac or Windows machine you can install software on.
- About £5 of API credit at console.anthropic.com. As of September 2026 that covers the whole course, including the post where you test three models against each other. A Claude or ChatGPT subscription is not an API key; the setup post explains the difference.
- Two or three hours a week for a few weeks. Each post is one sitting.

Keep your editor's AI helpers switched off for the course. The point is to understand how the agent works, and you only get that by typing it.

## The posts

| Part | Post | What you build | Time |
|---|---|---|---|
| 1 | [What an agent actually is](01-what-an-agent-actually-is.md) | Nothing yet. The five boxes every agent is made of, and the ladder of triggers. | 15 minutes |
| 2 | [Setting up](02-setting-up.md) | VS Code, Python, one package, an API key, and a smoke test that proves they all work together. | 45 minutes |
| 3 | [Build your first agent](03-build-your-first-agent.md) | One tool, then the model, its instructions and the loop. About 25 lines that make it an agent. | 1 hour |
| 4 | [Give your agent hands and a memory](04-give-your-agent-hands-and-a-memory.md) | Tools that read, write and move files inside a fence, with your permission, and a memory file. | 1 hour |
| 5 | [Put your agent on a schedule](05-put-your-agent-on-a-schedule.md) | Auto-approve, a report per run, and cron or Task Scheduler. It works while you don't. | 1 hour |
| 6 | [What production means for an agent](06-what-production-means-for-an-agent.md) | A run log, a spend limit, failures you'll notice, and the code version in every record. | 1 hour |
| 7 | [Swap the model](07-swap-the-model.md) | A small harness that runs three models on the same task and scores the result, not the words. | 1.5 hours |
| 8 | [When to break it up](08-when-to-break-it-up.md) | The agent in four files, each split for a pain you'll have felt, and tests that need no API. | 1.5 hours |
| 9 | Keep a register | One file that says what each agent is, and a check that fails when the file and the code disagree. | coming |

One agent, the whole way through. Each post ends with the same agent, slightly more grown up.

## The code

Every post has a matching folder in the public repo at [github.com/themitchelli/your-first-agent](../). Each folder is the complete project as it stands at the end of that post. Code along and compare when a checkpoint doesn't match, or copy a folder and run it. The differences between one folder and the next are the lesson.

## Side posts

Some posts hit a need the series doesn't teach, such as version control, and link out to a side post that teaches it on the agent you just built. They're optional. The main series never depends on them.

## Where to start

If you've never written code, start at part 1 and don't skip part 2. If you write Python already, read part 1 for the framework, skim part 2 for the API key, and start building at part 3.
