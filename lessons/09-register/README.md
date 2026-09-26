# Post 9: Keep a register

*Read-along: [posts/09-keep-a-register.md](../../posts/09-keep-a-register.md). Type the code from the post; use this folder to compare.*

The agent from post 8 plus `register.json`, a file that says what the agent is: owner, purpose, where it runs, spend limit, the five boxes, and the harness scores with the fingerprints of the code each was measured on. `test_agent.py` gains three tests that fail when the register and the code disagree, and `harness.py` prints the fingerprints it measured. Run `python test_agent.py` (six tests, no API).
