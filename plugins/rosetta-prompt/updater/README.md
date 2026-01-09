# Prompting Guide Updater Agent

An autonomous agent that keeps AI provider prompting documentation up to date using Claude (Anthropic SDK) and Firecrawl.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler (Weekly)                       │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Claude Opus (Anthropic SDK)            │    │
│  │                                                     │    │
│  │  Native Tool Calling with ReAct Pattern:            │    │
│  │  1. list_providers → Get configured providers       │    │
│  │  2. batch_scrape_urls (Firecrawl) → Fetch docs      │    │
│  │  3. read_current_guide → Compare with existing      │    │
│  │  4. update_guide → Write synthesized content        │    │
│  │  5. write_update_log → Record the update            │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│              rosetta_prompt/docs/*.md                       │
└─────────────────────────────────────────────────────────────┘
```

## Tools

The agent uses these tools via Anthropic's native tool calling:

| Tool | Description |
|------|-------------|
| `list_providers` | List all configured AI providers and their doc URLs |
| `read_current_guide` | Read the current prompting.md for a provider |
| `scrape_url` | Scrape a single URL using Firecrawl |
| `batch_scrape_urls` | Scrape multiple URLs efficiently in one call |
| `update_guide` | Write updated content to a provider's prompting.md |
| `write_update_log` | Log an update entry after completion |

## Setup

1. Install dependencies:
```bash
cd updater
pip install -r requirements.txt
```

2. Set environment variables in `.env` (at project root or in `rosetta_prompt/`):
```
ANTHROPIC_API_KEY=your_anthropic_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

3. Run manually:
```bash
# Update all providers
python agent.py

# Update specific providers
python agent.py anthropic openai

# Update multiple specific providers
python agent.py google kimi
```

4. Run with scheduler (weekly updates):
```bash
python scheduler.py
```

## Configuration

Edit `config.py` to:
- Add new providers
- Change documentation URLs
- Adjust model settings

```python
PROVIDER_CONFIGS = {
    "mistral": {
        "name": "Mistral",
        "urls": [
            "https://docs.mistral.ai/capabilities/completion/",
        ],
        "doc_file": "prompting.md"
    }
}

# Model settings
CLAUDE_MODEL = "claude-opus-4-5-20251101"  # Or claude-sonnet-4-20250514
MAX_TURNS = 5
```

## How It Works

1. **Scheduler** triggers the agent weekly (or on demand)
2. **Agent** receives task to update specified providers
3. For each provider:
   - Lists providers to get documentation URLs
   - Reads current guide content for comparison
   - Batch scrapes all documentation URLs via Firecrawl
   - Synthesizes content into clean, structured markdown
   - Updates the local file
   - Logs the update with status and summary
4. **Agent** provides summary of all updates

The agent uses Claude's native tool calling with a ReAct-style loop, deciding autonomously which tools to call based on the task.

## Example Output

```
============================================================
PROMPTING GUIDE UPDATER AGENT
============================================================
Model: claude-opus-4-5-20251101
Providers: ['anthropic']
Started: 2025-12-07T18:13:38.091272
============================================================

--- Turn 1/5 ---
[Agent]: I'll start by listing all available providers...
[Tool Call]: list_providers

--- Turn 2/5 ---
[Agent]: Now I'll read the current guide and batch scrape all URLs...
[Tool Call]: read_current_guide
[Tool Call]: batch_scrape_urls
[Result]: Batch scraped 10 of 10 URLs...

--- Turn 3/5 ---
[Agent]: Synthesizing content into comprehensive guide...
[Tool Call]: update_guide
[Result]: Successfully updated guide (8594 chars)

--- Turn 4/5 ---
[Tool Call]: write_update_log
[Result]: Logged update for anthropic: success

============================================================
UPDATE COMPLETE
============================================================
```

## Logs

Update history is stored in `rosetta_prompt/docs/update_log.json`:

```json
{
  "updates": [
    {
      "timestamp": "2025-12-07T18:14:51",
      "provider_id": "anthropic",
      "status": "success",
      "summary": "Successfully updated Anthropic prompting guide. Synthesized content from 10 documentation URLs..."
    }
  ]
}
```

## Adding New Providers

1. Add provider config to `config.py`:
```python
PROVIDER_CONFIGS = {
    "new_provider": {
        "name": "New Provider",
        "urls": [
            "https://docs.newprovider.com/prompting-guide",
        ],
        "doc_file": "prompting.md"
    }
}
```

2. Create the directory:
```bash
mkdir -p rosetta_prompt/docs/new_provider
```

3. Run the updater:
```bash
python agent.py new_provider
```
