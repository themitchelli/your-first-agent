# Post 4: Give your agent hands and a memory

Stages 3 and 4: tools that read, write and move files inside a fence, with your approval, then a memory file.

```bash
python agent.py demo "Organise this folder: rename the files sensibly, group them into subfolders, and tell me what's in it"
```

- `stages/stage3.py` is your `agent.py` at the end of stage 3: the fence, read, write and move, with y/n approval.
- `agent.py` is the finished agent at the end of the post, with memory.
- `demo/` is the practice folder.

The agent can only see and touch the folder you name, and it asks before every write or move. When it finishes it updates `demo/memory.md`; run it again and it starts from what it learned.
