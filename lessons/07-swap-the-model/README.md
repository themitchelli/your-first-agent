# Post 7: Swap the model

*Read-along: [posts/07-swap-the-model.md](../../posts/07-swap-the-model.md). Type the code from the post; use this folder to compare.*

The harness post. `agent.py` is the lesson 04 agent with two seams cut in (model as a parameter, approver passed in). `harness.py` runs it against `fixture/` for each model and scores the result using `answer_key.json`. Run `python harness.py 1` for a quick look.
