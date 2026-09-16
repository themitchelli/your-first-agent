# Post 5 checkpoints

Post 5 ("Put your agent on a schedule") starts from `lessons/04-hands-and-memory/agent.py`
and builds up to `lessons/05-a-schedule/agent.py` (the finished file for this lesson) in
three steps.

- `stage1.py` — end of **Step 1: nobody is there to type y** (sub-steps 1a to 1d):
  the `--auto-approve` flag, the `allowed()` helper, both tools using it, and `main`
  filtering the flag out of `sys.argv`. No report code yet.

- **Step 2: nobody is watching the terminal** adds the report code (2a to 2d). That step's
  end state is already `lessons/05-a-schedule/agent.py` itself, so there is no `stage2.py`
  here — compare your file against `../agent.py` instead.

- **Step 3: the scheduler knows nothing** (3a to 3c) changes no Python. It adds `run.sh` /
  `run.bat` and covers the key file and the scheduler setup, so there's nothing new to
  checkpoint here either — see `../run.sh` and `../run.bat`.

If you're stuck partway through Step 1, diff your file against `stage1.py`. If you're
stuck in Step 2, diff against `../agent.py`.
