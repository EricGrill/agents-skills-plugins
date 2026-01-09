# AGENTS.md

Instructions for AI agents working with this Claude Code plugin.

## Plugin Overview

**Ralph Wiggum Marketer** is a Claude Code plugin that provides an autonomous AI copywriter for SaaS content marketing.

## Available Commands

| Command | Description |
|---------|-------------|
| `/ralph-init` | Initialize a new content project |
| `/ralph-marketer` | Start the autonomous copywriter loop |
| `/ralph-status` | Check content pipeline status |
| `/ralph-cancel` | Cancel the active loop |

## For Ralph: Your Workflow

When running in a Ralph loop:

1. **Check status**: `npm run db:status`
2. **Read tasks**: `cat scripts/ralph/prd.json`
3. **Find next task**: Highest priority where `passes: false`
4. **Execute**: Follow story-specific instructions
5. **Verify**: `npm test`
6. **Commit**: `git commit -m "content: [ID] - [Title]"`
7. **Update**: Mark story done, log to progress.txt
8. **Signal**: Output `<promise>COMPLETE</promise>` when ALL done

## Database Patterns

### Connecting
```javascript
import Database from 'better-sqlite3';
const db = new Database('./data/content.db');
// ... do work ...
db.close();  // Always close!
```

### JSON Columns
Parse these with `JSON.parse()`:
- `research.key_findings`, `data_points`, `sources`
- `communications.key_messages`
- `content_plan.target_keywords`

### Status Transitions

| Table | Flow |
|-------|------|
| Communications | `pending` → `assigned` → `completed` |
| Trends | `active` → `used` → `expired` |
| Research | `available` → `used` → `archived` |
| Content Plan | `planned` → `writing` → `review` → `published` |

## Content Patterns

### File Naming
- Drafts: `content/drafts/[slug]-v[version].md`
- Published: `content/published/[slug]-final.md`

### Word Count
```javascript
const count = content.split(/\s+/).filter(w => w.length > 0).length;
```

### Quality Minimums
- Blog posts: 800-2000 words
- Case studies: 1000-1500 words
- Social posts: Under 280 chars
- Newsletters: 500-800 words

## Commit Convention

```
content: [STORY-ID] - Short description
```

## Plugin Development

### Directory Structure
```
ralph-wiggum-marketer/
├── .claude-plugin/plugin.json    # Manifest
├── commands/                      # Slash commands
├── skills/copywriter/             # Copywriter skill
├── hooks/                         # Stop hook for loop
├── scripts/src/                   # Database utilities
└── templates/                     # Project templates
```

### Testing Changes
```bash
npm install
npm run db:reset
npm test
```
