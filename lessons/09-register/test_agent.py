"""Tests that run the whole agent without the API: free, fast, and the same every time.

Run:  python test_agent.py
"""

import json
import pathlib
import tempfile
from types import SimpleNamespace

import agent
import harness
import main
import runlog
import tools

HERE = pathlib.Path(__file__).parent

class FakeClient:
    """Stands in for anthropic.Anthropic(). Plays back scripted replies and remembers what it was sent."""
    def __init__(self, replies):
        self.replies = replies
        self.sent = []
        self.messages = self                       # so fake.messages.create(...) works like the real client

    def create(self, **request):
        self.sent.append(request)
        return self.replies.pop(0)

def reply(stop_reason, *blocks):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks),
                           usage=SimpleNamespace(input_tokens=100, output_tokens=20))

def text(words):
    return SimpleNamespace(type="text", text=words)

def tool_use(tool, inputs):
    return SimpleNamespace(type="tool_use", id=f"call-{tool}", name=tool, input=inputs)

def test_fence_refuses_paths_outside_the_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        (pathlib.Path(tmp) / "secret.txt").write_text("private", encoding="utf-8")      # a real file, just outside
        workspace = pathlib.Path(tmp) / "workspace"
        workspace.mkdir()
        try:
            tools.read_file(workspace, "../secret.txt")
        except ValueError:
            return
        raise AssertionError("read_file escaped the workspace")

def test_declined_write_changes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        answer = tools.write_file(workspace, "note.txt", "hello", approve=lambda question: False)
        assert answer == "The user declined this write."
        assert not (workspace / "note.txt").exists()

def test_loop_runs_the_requested_tool_and_hands_back_the_result():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        (workspace / "asdfgh.txt").write_text("Banana bread recipe", encoding="utf-8")
        fake = FakeClient([
            reply("tool_use", tool_use("move_file", {"name": "asdfgh.txt", "new_name": "Recipes/banana_bread.txt"})),
            reply("end_turn", text("Moved the recipe.")),
        ])
        record = {"tools": [], "input_tokens": 0, "output_tokens": 0}
        report = []

        agent.run(fake, workspace, "Tidy up", lambda question: True, record, report)

        assert (workspace / "Recipes" / "banana_bread.txt").exists(), "the file was not moved"
        assert len(fake.sent) == 2, "the loop should call the model twice"
        handed_back = fake.sent[1]["messages"][-1]["content"][0]
        assert handed_back["tool_use_id"] == "call-move_file"
        assert handed_back["content"] == "Moved asdfgh.txt to Recipes/banana_bread.txt."
        assert record["input_tokens"] == 200 and len(record["tools"]) == 1
        assert "Moved the recipe." in report

def read_register():
    return json.loads((HERE / "register.json").read_text(encoding="utf-8"))

def test_register_lists_exactly_the_agents_tools():
    in_code = {tool["name"] for tool in tools.TOOLS}
    in_register = set(read_register()["tools"])
    assert in_code == in_register, (f"tools in the code but not the register: {in_code - in_register or 'none'}. "
                                    f"In the register but not the code: {in_register - in_code or 'none'}.")

def test_register_matches_the_model_and_the_spend_limit():
    register = read_register()
    fake = FakeClient([reply("end_turn", text("Nothing to do."))])
    with tempfile.TemporaryDirectory() as tmp:
        agent.run(fake, pathlib.Path(tmp), "Check", lambda question: True,
                  {"tools": [], "input_tokens": 0, "output_tokens": 0}, [])
    assert fake.sent[0]["model"] == register["model"], (
        f"the agent asks for {fake.sent[0]['model']}, the register says {register['model']}")
    assert main.MONTHLY_LIMIT_USD == register["monthly_limit_usd"], (
        f"main.py's limit is {main.MONTHLY_LIMIT_USD}, the register says {register['monthly_limit_usd']}")

def test_every_run_record_carries_the_register_id():
    register_id = read_register()["id"]
    assert register_id, "the register's id is empty. Make one with: python -c \"import uuid; print(uuid.uuid4())\""
    stamped = runlog.new_record("Check")["agent"]
    assert stamped == register_id, f"new run records say agent {stamped}, the register's id is {register_id}"

def test_register_score_was_measured_on_the_code_that_runs():
    scores = read_register()["scores"]
    assert scores, "the register has no scores yet. Run the harness and add one to 'scores'."
    latest = scores[0]
    for name in ["tools.py", "agent.py"]:
        now = harness.code_fingerprint(HERE / name)
        assert latest[name] == now, (f"{name} has changed since the latest score was measured "
                                     f"(the register says {latest[name]}, the file is now {now}). "
                                     f"Run the harness and add a new score at the top of 'scores'.")

if __name__ == "__main__":
    tests = [value for name, value in dict(globals()).items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"passed  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed. No API calls, no cost.")
