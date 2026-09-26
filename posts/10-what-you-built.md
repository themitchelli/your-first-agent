*Part 10 of [Your First Agent](README.md).*
*This is a draft being tested before publication. Found something confusing or wrong? [Open an issue](../../issues) with the post, the section, and what happened.*

# What you built

In the build post you had a Python file that could look at a folder and talk about it. It was about 70 lines, and the part that made it an agent was a loop of about 30.

Today you have an agent that tidies a folder every morning while you sleep. It asks before it changes anything, unless you've told it not to, and it can't reach outside its folder even if it wants to. It remembers what it did last time. It writes down every run, which agent ran it and what it cost, and refuses to start when the month's money is spent. It has seven tests that run in under a second and cost nothing, a harness that scores it against three models, and a register that says what it is and complains when that stops being true.

This post has no new code. It's here so you can see what you did.

## Open two files side by side

**Checkpoint, one last time.** In VS Code, open `lessons/03-build-your-first-agent/stages/stage2.py` from the course files, and your own `agent.py` from `my-first-agent`. Use the compare trick from the setup post: right-click one, **Select for Compare**, then right-click the other, **Compare with Selected**.

Look at the loop. The `for _ in range(20):`, the call to the model, the check on `stop_reason`, the tool results handed back with their `tool_use_id`. It's the same loop, nearly line for line. The only additions are five lines that write things down as they happen.

Everything else you built went *around* that loop, not into it. The fence, the approvals, the schedule, the log, the spend limit, the tests and the register all sit outside it, in files that each answer one question. That's the most useful thing to take away from the whole series. An agent is a small loop. Making it something you can trust is everything around the loop, and most of that is plain code you already know how to write.

## The five boxes, built

The first post said an agent is five things: a model, instructions, tools, memory and a trigger. At the time that was a diagram. Here's where each box ended up in your own files.

**Model.** One line in `agent.py`: `model="claude-haiku-4-5"`. In the harness post you swapped it and measured what changed, and what the change cost. The register records which model is live, and a test checks the register is right.

**Instructions.** `SYSTEM` in `agent.py`: a few sentences that ask the model to be careful and to keep notes. The harness post's Try this had you reword them and see whether the score moved. And you learned the rule the course keeps coming back to: instructions ask, tools enforce.

**Tools.** `tools.py`: four plain Python functions and their descriptions. The model can only ask for them. Your code decides whether to run them, keeps them inside one folder, and asks you before any write. A test proves the fence holds.

**Memory.** `memory.md`, inside the folder the agent works on. The agent reads it at the start of each run and rewrites it at the end. It's why the second morning's run files things the same way as the first.

**Trigger.** `run.sh` or `run.bat`, started by cron or Task Scheduler at 7am. The step from "I run it" to "it runs" is where the production post's five questions came from.

None of these is a black box to you now. When someone shows you a diagram of an agent platform with fourteen boxes, you can point at each one and say which of the five it is, and which are packaging.

## What you can do now

You can read an agent. Given someone else's, you know to look for the loop, then ask what tools it has, what fences them, what it remembers and what starts it.

You can ask the production questions: what is it allowed to do, what did it do, what can it spend, how would you know it failed, and which version ran. Plenty of agents running at real companies can't answer all five.

You can tell whether a change helped instead of guessing. You've seen a model score perfectly on one run and between 0.33 and 0.67 over three. A number from one run is a guess.

You can test an agent for free, with a fake model that plays back replies you wrote.

And you can say no to an agent. The first post's ladder, existing tool, script, one AI call, agent, is still the most useful thing in the series. The best agent is often the one you didn't need to build.

## Back to your sentence

At the end of the first post you wrote one sentence: "I want an agent that ___ every ___." Find it.

You now have everything you need to build it. Here's the order, and each step is something you've already done once:

1. **Copy `my-first-agent`** to a new folder with a new name. Delete `demo`, `runs.jsonl`, `reports` and `memory.md` from the copy. Then give the copy **a new id** in `register.json`, with the same `uuid` command as the register post. A copy with the old id would stamp its runs as the file organiser's.
2. **Write the tools your job needs** in `tools.py`. Use the recipe from the hands-and-memory post: write the function, describe it in `TOOLS`, route it in `run_tool`. Anything that changes something gets an approval. Delete the tools your job doesn't need. An agent should have no tool it doesn't use.
3. **Rewrite `SYSTEM`** in `agent.py` for your job.
4. **Update the tests.** Keep the fence test and the "no means no" test, pointed at your new tools. Test 3 needs new scripted replies.
5. **Build a fixture and an answer key** for the harness: a small, fixed example of your job with a known right answer. This is the hardest step and the most valuable one. Writing down what "right" means is most of the work of building anything with AI.
6. **Write its register.** Read the `approval` line twice.
7. **Run it by hand for a week** before you put it on a schedule.

If your sentence turned out to need a script rather than an agent, you still have most of this. The fence, the log, the spend limit and the tests are good habits for any program that runs on its own.

## Where this stops

Everything here runs on one machine, for one person, on your own files. The production post described what changes when more people, more machines or other people's data get involved: permissions become identity systems, the log becomes monitoring, the spend limit becomes a gateway, and the register becomes an inventory someone else keeps. If you're thinking of doing this at work, reread "At home or at work?" in the first post first.

Those are bigger versions of things you've built. You'll recognise them.

## Try this

Tell someone what you built. Not the code. Explain the five boxes and the five production questions to someone who hasn't seen this series, using your own agent as the example. If you can do that in ten minutes, you understand it. If you get stuck, the post that covers that part is still here.

---

← [Part 9](09-keep-a-register.md) · [Series page](README.md)
