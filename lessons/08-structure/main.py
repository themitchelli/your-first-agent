"""How a person or a schedule starts the agent.

Run:  python main.py demo "Organise any new files in this folder the same way as before."
      python main.py demo "Organise any new files in this folder the same way as before." --auto-approve
"""

import datetime
import pathlib
import sys

import anthropic

import agent
import runlog
import tools

MONTHLY_LIMIT_USD = 2.00

def main():
    auto = "--auto-approve" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--auto-approve"]
    workspace = pathlib.Path(args[0])
    task = args[1]
    approve = tools.auto_approve if auto else tools.ask_human
    record = runlog.new_record(task)
    report = [f"# Run at {datetime.datetime.now():%Y-%m-%d %H:%M}", f"Task: {task}", ""]

    spent = runlog.spent_this_month()
    if spent >= MONTHLY_LIMIT_USD:
        record["result"] = f"refused: ${spent:.2f} already spent this month, limit is ${MONTHLY_LIMIT_USD:.2f}"
        runlog.finish(record, report)
        sys.exit(1)

    try:
        client = anthropic.Anthropic()
        agent.run(client, workspace, task, approve, record, report)
    except Exception as error:
        record["result"] = f"FAILED: {error}"

    runlog.finish(record, report)
    if record["result"] != "ok":
        sys.exit(1)

if __name__ == "__main__":
    main()
