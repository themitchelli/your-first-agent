"""What happened: the run log, the reports, the spend total and the code version.

Kept apart from the agent on purpose. The agent can edit files in its workspace;
it has no business near the record of what it did.
"""

import datetime
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
RUN_LOG = HERE / "runs.jsonl"
PRICE_PER_MILLION_USD = {"input": 1.00, "output": 5.00}     # Claude Haiku 4.5, as of September 2026

def new_record(task):
    return {"agent": agent_id(), "started": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", "task": task,
            "version": code_version(), "tools": [], "input_tokens": 0, "output_tokens": 0, "result": "ok"}

def spent_this_month():
    if not RUN_LOG.exists():
        return 0.0
    this_month = f"{datetime.datetime.now():%Y-%m}"
    total = 0.0
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["started"].startswith(this_month):
            total += record["cost_usd"]
    return total

def agent_id():
    try:
        return json.loads((HERE / "register.json").read_text(encoding="utf-8"))["id"]
    except Exception:
        return "unregistered"

def code_version():
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                cwd=HERE, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return "unknown (not a git repo)"

def finish(record, report):
    record["cost_usd"] = round((record["input_tokens"] * PRICE_PER_MILLION_USD["input"]
                                + record["output_tokens"] * PRICE_PER_MILLION_USD["output"]) / 1_000_000, 5)
    reports = HERE / "reports"
    reports.mkdir(exist_ok=True)
    failed = "" if record["result"] == "ok" else "-FAILED"
    report_path = reports / f"{datetime.datetime.now():%Y-%m-%d-%H%M%S}{failed}.md"
    report.append(f"\nResult: {record['result']}  |  cost ${record['cost_usd']}  |  version {record['version']}")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    with RUN_LOG.open("a", encoding="utf-8") as log:
        log.write(json.dumps(record) + "\n")
    print(f"\nReport written to {report_path}")
