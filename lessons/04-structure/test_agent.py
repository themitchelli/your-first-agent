"""Tests that run the whole agent without the API: free, fast, and the same every time.

Run:  python test_agent.py
"""

import pathlib
import tempfile
from types import SimpleNamespace

import agent
import tools

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
        (pathlib.Path(tmp) / "secret.txt").write_text("private")      # a real file, just outside
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
        (workspace / "asdfgh.txt").write_text("Banana bread recipe")
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

if __name__ == "__main__":
    tests = [value for name, value in dict(globals()).items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"passed  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed. No API calls, no cost.")
