# Testing the course

Thank you for reading this before it goes live. The course is a series of blog posts that has you build a real AI agent from one Python file up to something you'd trust to run on a schedule. The posts are in [`posts/`](posts/README.md), and each has a matching code folder in [`lessons/`](lessons/).

You don't need to know Python. If you do, that's fine too, but please say which you are when you report back, because the posts are written for someone who doesn't.

## How to read along

1. Start at [part 1](posts/01-what-an-agent-actually-is.md) and go in order. Part 2 is the setup; don't skip it even if you think your machine is ready.
2. **Type the code from the posts.** Don't copy from the `lessons` folders, and don't use Copilot, Cursor, Claude Code or any AI helper while you do the course. The posts explain how to switch them off. The whole point is that you understand every line, and the test is whether the explanations are enough on their own.
3. Work in a fresh folder called `my-first-agent` in your home folder, exactly as part 2 says. The `lessons` folders are for comparing when a checkpoint doesn't match.
4. Every step ends with a **Checkpoint** in bold saying what you should see. If you don't see it, that's a finding. Note it and try to fix it from the post before looking at the code folder.
5. Use a new API key made just for this, with a monthly spend limit set in the Anthropic console. About £5 of credit covers the whole course. A Claude or ChatGPT subscription is not an API key; part 2 explains.

## What to report

Anything that slowed you down, however small. In rough order of how much it helps:

- A checkpoint you didn't hit, and what you saw instead.
- A step where you didn't know what to do next, or where to type something.
- An explanation that didn't land. "I typed it but I don't know why" is a valid finding.
- An error message the post didn't prepare you for.
- A place where you were bored, or where a post was too long for one sitting.
- Anything on Windows. The Mac path is tested; Windows is not.

Please don't fix the posts or the code for me. Tell me what happened and I'll fix it in one batch.

## How to report

[Open an issue](../../issues) on this repo, one per finding, in this shape:

```
Part 5, step 3c: crontab -e opened vim, not nano, and I couldn't get out
```

Put the part number and the section in the title, then what happened, what you expected, and Mac or Windows. A screenshot of the terminal helps. If you'd rather not use GitHub, email me the same thing.

## What happens next

I collect every finding, fix the posts and code in one pass, and the series goes live on [stevesaidiaries.com](https://stevesaidiaries.com). These draft copies get replaced with links to the published posts. Your name goes nowhere unless you want it to.
