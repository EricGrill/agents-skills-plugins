---
description: Check the content pipeline status for Ralph the Marketer
allowed-tools: [Bash, Read]
model: haiku
---

# Ralph Marketer Status

Check the current status of the content pipeline and Ralph's progress.

## Run Status Commands

```bash
# Database status
npm run db:status

# Available content sources
node src/content/list.js

# PRD status
cat scripts/ralph/prd.json | jq '.userStories[] | {id, title, passes, priority}'

# Recent progress
tail -50 scripts/ralph/progress.txt

# Recent commits
git log --oneline -10

# Content counts
echo "Drafts:" && ls -la content/drafts/ 2>/dev/null || echo "  No drafts yet"
echo "Published:" && ls -la content/published/ 2>/dev/null || echo "  No published content yet"
```

Summarize the status for the user:
- How many stories are complete vs remaining
- What content has been created
- Any blockers or issues
