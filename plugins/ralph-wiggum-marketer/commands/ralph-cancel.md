---
description: Cancel the active Ralph Marketer loop
allowed-tools: [Bash, Write]
model: haiku
---

# Cancel Ralph Marketer Loop

The user wants to cancel the Ralph Marketer loop.

## Actions

1. Remove the loop state file if it exists:
```bash
rm -f .claude/ralph-marketer-loop.local.md 2>/dev/null && echo "Loop state cleared" || echo "No active loop found"
```

2. Inform the user:
- The Ralph loop has been cancelled
- Any in-progress work has been preserved in git
- They can check progress with `/ralph-status`
- They can restart with `/ralph-marketer`

The loop is now cancelled. You will no longer receive repeated prompts.
