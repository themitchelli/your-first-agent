# Lesson 1 — Your first agent

One file, one folder, four ideas: a **model**, three file **tools**, a **memory** file, and you as the **trigger**.

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...   # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python agent.py demo "Organise this folder: rename the files sensibly, group them into subfolders, and tell me what's in it"
```

The agent can only see and touch the folder you name, and it asks before every write or move. When it finishes it updates `demo/memory.md`; run it again and it starts from what it learned.

Read `agent.py` top to bottom — it is written to be read. The heart is the 25-line loop at the bottom: ask the model, run the tool it asks for, show it the result, repeat.
