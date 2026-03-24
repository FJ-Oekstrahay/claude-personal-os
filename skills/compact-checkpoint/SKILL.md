Context is getting heavy. Before compacting:
1. Run `mkdir -p ~/.openclaw/workspace/compact-checkpoints` first, then write a session summary to `~/.openclaw/workspace/compact-checkpoints/CHECKPOINT-{datetime}.md`
   - What we've done, what files changed, current status, next steps
2. Confirm the file was written
3. Tell the user: "Checkpoint saved at [path]. Running /compact now."
4. Then run /compact with focus: "Continue working on [current task]. See checkpoint at [path]."
