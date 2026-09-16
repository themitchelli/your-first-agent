"""A tiny evaluation harness: does swapping the model change the result?

Same agent, same task, same tools, same messy folder. Only the model changes.
Each model runs several times, because one run proves nothing.

Since the structure post this drives the real agent (agent.run), not a copy.
Harness runs are not written to runs.jsonl, so they don't count towards the
monthly limit in main.py. The spend limit in the Anthropic console still applies.

Run:  python harness.py            (3 models x 3 runs, roughly $1 as of Sept 2026)
      python harness.py 1          (1 run each, for a quick look)

We score the OUTCOME, not the prompt: after the agent finishes, did files that
belong together end up in the same folder? Folder names don't matter, so
"Invoices", "Bills" and "Money" all count as right.
"""

import contextlib
import hashlib
import io
import itertools
import json
import pathlib
import shutil
import sys
import tempfile
import time

import anthropic

import agent

MODELS = {                      # price per million tokens (input, output), as of Sept 2026
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
}
TASK = "Organise this folder: group the files into sensibly named subfolders. Rename them if it helps."
HERE = pathlib.Path(__file__).parent

def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def where_did_files_go(workspace, originals):
    """Map each original filename to the folder it ended up in. Contents identify files, so renames are fine."""
    by_content = {fingerprint(HERE / "fixture" / name): name for name in originals}
    placed = {}
    for path in workspace.rglob("*"):
        name = by_content.get(fingerprint(path)) if path.is_file() else None
        if name and path.parent != workspace:
            placed[name] = str(path.parent.relative_to(workspace))
    for name in originals:
        placed.setdefault(name, f"UNGROUPED:{name}")   # left at the top, or lost: sits alone, scores as wrong
    return placed

def grouping_score(placed, answer_key):
    """F1 over pairs: of the pairs that belong together, how many ended up together, without lumping in wrong ones."""
    truth = {name: group for group, names in answer_key.items() for name in names}
    should = did = both = 0
    for a, b in itertools.combinations(truth, 2):
        together_in_key = truth[a] == truth[b]
        together_now = placed[a] == placed[b]
        should += together_in_key
        did += together_now
        both += together_in_key and together_now
    if both == 0:
        return 0.0
    precision, recall = both / did, both / should
    return 2 * precision * recall / (precision + recall)

def run_once(client, model, answer_key):
    approvals = []
    def always_yes(question):
        approvals.append(question)
        return True
    record = {"tools": [], "input_tokens": 0, "output_tokens": 0}
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp) / "fixture"
        shutil.copytree(HERE / "fixture", workspace)      # a fresh mess every run
        started = time.time()
        with contextlib.redirect_stdout(io.StringIO()):   # the agent prints as it works; keep nine runs off the screen
            agent.run(client, workspace, TASK, always_yes, record, [], model=model)
        seconds = time.time() - started
        placed = where_did_files_go(workspace, [n for names in answer_key.values() for n in names])
    price_in, price_out = MODELS[model]
    cost = (record["input_tokens"] * price_in + record["output_tokens"] * price_out) / 1_000_000
    return {"score": grouping_score(placed, answer_key), "cost": cost, "seconds": seconds,
            "tool_calls": len(record["tools"]), "approvals": len(approvals)}

def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    answer_key = json.loads((HERE / "answer_key.json").read_text(encoding="utf-8"))
    client = anthropic.Anthropic()
    print(f"{'model':<18} {'score':>11} {'cost':>8} {'secs':>6} {'tools':>6} {'approvals':>9}")
    for model in MODELS:
        results = [run_once(client, model, answer_key) for _ in range(runs)]
        scores = [r["score"] for r in results]
        mean = lambda key: sum(r[key] for r in results) / runs
        print(f"{model:<18} {min(scores):.2f}-{max(scores):.2f}  ${mean('cost'):.3f} "
              f"{mean('seconds'):>6.0f} {mean('tool_calls'):>6.0f} {mean('approvals'):>9.0f}")
    print(f"\nscore: lowest-highest over {runs} runs (1.00 = perfect grouping). Other columns: average per run.")

if __name__ == "__main__":
    main()
