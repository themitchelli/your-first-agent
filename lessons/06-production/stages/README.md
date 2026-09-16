# Post 6 checkpoints

Post 6 ("What production means for an agent") starts from
`lessons/05-a-schedule/agent.py` and builds up to `lessons/06-production/agent.py`
(the finished file for this lesson) by answering five questions.

- **Question 1: what is it allowed to do?** No new code (`safe_path` and the approval
  dial from post 5 already answer it), so there is no stage file for it.

- `stage2.py` — end of **Question 2: what did it do?** (2a to 2d): the `json` and
  `subprocess` imports, `HERE`/`RUN_LOG`/`MONTHLY_LIMIT_USD`/`PRICE_PER_MILLION_USD`
  settings, the `run` dict (`"version"` still `"unknown"`), token counting, tool calls
  recorded on `run["tools"]`, and `finish()` writing the report then appending to
  `runs.jsonl`. No spend guard yet, no try/except, no `code_version()`.

- `stage3.py` — end of **Question 3: what can it spend?** (3a, 3b): adds
  `spent_this_month()` and the refuse-to-start guard in `main`, checked before any
  API call.

- `stage4.py` — end of **Question 4: what happens when it fails?** (4a, 4b): wraps
  `client = anthropic.Anthropic()` and the whole loop in `try`/`except`, and exits
  with code 1 when `run["result"] != "ok"`. `"version"` is still `"unknown"`.

- **Question 5: which version is running?** adds `code_version()` and uses it for
  `"version"`. That step's end state is already `lessons/06-production/agent.py`
  itself, so there is no `stage5.py` here — compare your file against `../agent.py`.

If you're stuck partway through a question, diff your file against the matching
stage file (or `../agent.py` for question 5).
