# The Rosetta Prompt

A prompt optimization system that adapts your prompts for different AI providers. 

[![LangChain v1](https://img.shields.io/badge/LangChain-v1.0-blue)](https://docs.langchain.com/oss/python/releases/langchain-v1)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)

## What Makes This Agentic?

This is **not** a simple prompt-in/prompt-out system. Each **Optimizer Agent** is a true autonomous agent that:

1. **Discovers knowledge** - Uses `list_provider_docs` tool to find available documentation
2. **Reads selectively** - Uses `read_provider_doc` tool to retrieve specific guidelines (12K+ chars each)
3. **Applies learning** - Transforms prompts based on provider-specific patterns it learned
4. **Reports changes** - Uses `submit_optimization` to return structured results with detailed changelog

The agent makes **autonomous decisions** in a ReAct loop (Reason → Act → Observe → Repeat).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AGENTIC SYSTEM                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   ┌───────────────────────────────────────────────────────────────────────────────┐     │
│   │                           ORCHESTRATOR AGENT                                  │     │
│   │                                                                               │     │
│   │   • Validates providers against docs/ directory                               │     |
│   │   • Spawns parallel optimizer agents (asyncio.gather)                         │     │
│   │   • Aggregates results from all agents                                        │     │
│   └───────────────────────────────────────────────────────────────────────────────┘     │
│                                       │                                                 │
│               ┌───────────────────────┼───────────────────────┐                         │
│               │                       │                       │                         │
│               ▼                       ▼                       ▼                         │
│   ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐               │
│   │   OPTIMIZER AGENT   │ │   OPTIMIZER AGENT   │ │   OPTIMIZER AGENT   │               │
│   │      (OpenAI)       │ │    (Anthropic)      │ │     (Google)        │               │
│   │                     │ │                     │ │                     │               │
│   │  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │               │ 
│   │  │ ReAct Loop    │  │ │  │ ReAct Loop    │  │ │  │ ReAct Loop    │  │               │
│   │  │               │  │ │  │               │  │ │  │               │  │               │
│   │  │ 1. Reason     │  │ │  │ 1. Reason     │  │ │  │ 1. Reason     │  │               │
│   │  │ 2. Act (Tool) │  │ │  │ 2. Act (Tool) │  │ │  │ 2. Act (Tool) │  │               │
│   │  │ 3. Observe    │  │ │  │ 3. Observe    │  │ │  │ 3. Observe    │  │               │
│   │  │ 4. Repeat     │  │ │  │ 4. Repeat     │  │ │  │ 4. Repeat     │  │               │
│   │  └───────┬───────┘  │ │  └───────┬───────┘  │ │  └───────┬───────┘  │               │
│   │          │          │ │          │          │ │          │          │               │
│   │     [FileLogger]    │ │     [FileLogger]    │ │     [FileLogger]    │               │
│   └──────────┼──────────┘ └──────────┼──────────┘ └──────────┼──────────┘               │
│              │                       │                       │                          │
│              └───────────────────────┴───────────────────────┘                          │
│                                      │                                                  │
│                                      ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────────┐       │
│   │                              TOOL LAYER                                     │       │
│   │                                                                             │       │
│   │   list_provider_docs(provider) → ["index.md", "prompting.md"]               │       │
│   │   read_provider_doc(provider, doc_name) → "12K chars of guidelines..."      │       │ 
│   │   submit_optimization(prompt, changes) → Final structured result            │       │
│   │                                                                             │       │
│   └─────────────────────────────────────┬───────────────────────────────────────┘       │
│                                         │                                               │
│                                         ▼                                               │
│   ┌─────────────────────────────────────────────────────────────────────────────┐       │
│   │                           KNOWLEDGE BASE (docs/)                            │       │
│   │                                                                             │       │
│   │   ├── openai/prompting.md      (Official prompting guide)                   │       │
│   │   ├── anthropic/prompting.md   (Be clear, direct, detailed)                 │       │
│   │   ├── google/prompting.md      (Prompt design strategies)                   │       │
│   │   └── kimi/prompting.md        (Kimi-specific guidelines)                   │       │
│   │                                                                             │       │
│   │   → Auto-detected on startup (add folder = new provider)                    │       │
│   └─────────────────────────────────────────────────────────────────────────────┘       │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Agent System Deep Dive

### The ReAct Agent Loop (`agents/optimizer.py`)

Each optimizer runs an autonomous **ReAct loop** (Reasoning + Acting):

```python
class OptimizerAgent:
    """
    Agentic optimizer using ReAct pattern.
    
    The agent autonomously decides which documents to read,
    rather than having context pre-loaded (prevents context rot).
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=PRIMARY_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            max_tokens=16384,  # Prevent output truncation
        )
    
    async def _run_agent_loop(self, task, provider, original, log, file_log):
        """
        The core ReAct loop:
        1. Send messages to LLM
        2. Parse tool call from response
        3. Execute tool, get result
        4. Add result to conversation
        5. Repeat until submission
        """
        messages = [
            SystemMessage(content=AGENT_SYSTEM_PROMPT),
            HumanMessage(content=task),
        ]
        
        for iteration in range(max_iterations):
            # REASON: LLM decides what to do
            response = await self.llm.ainvoke(messages)
            
            # Check for final submission
            if "submit_optimization" in response.content:
                return self._parse_final_submission(response.content, ...)
            
            # ACT: Parse and execute tool
            tool_call = self._parse_tool_call(response.content)
            if tool_call:
                name, args = tool_call
                result = self._execute_tool(name, args)  # Tool execution
                
                # OBSERVE: Add result to conversation
                messages.append(AIMessage(content=response.content))
                messages.append(HumanMessage(content=f"TOOL RESULT:\n{result}"))
```

### Tool Definitions

The agent uses a simple text-based tool calling format:

```python
# Tool format the agent uses:
# TOOL: list_provider_docs | ARGS: provider=openai
# TOOL: read_provider_doc | ARGS: provider=openai, doc_name=prompting.md
# TOOL: submit_optimization | ARGS: done

def _list_provider_docs(provider: str) -> str:
    """List available docs for a provider."""
    provider_path = Path(DOCS_BASE_PATH) / provider.lower()
    files = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]
    return f"Available docs for {provider.upper()}: {', '.join(files)}"

def _read_provider_doc(provider: str, doc_name: str) -> str:
    """Read specific documentation file (returns full content ~12K chars)."""
    doc_path = Path(DOCS_BASE_PATH) / provider.lower() / doc_name
    content = doc_path.read_text()
    return f"=== {provider.upper()}: {doc_name} ===\n\n{content}"
```

### Agent Execution Flow (Real Example)

```
User: "Optimize 'You are a helpful assistant' for Anthropic"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 1 (0ms)                                               │
│                                                                 │
│ LLM Response: "TOOL: list_provider_docs | ARGS: provider=anthropic"
│                                                                 │
│ Tool Result: "Available docs for ANTHROPIC: index.md, prompting.md"
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 2 (2.5s)                                              │
│                                                                 │
│ LLM Response: "TOOL: read_provider_doc | ARGS: provider=anthropic, doc_name=prompting.md"
│                                                                 │
│ Tool Result: "=== ANTHROPIC: prompting.md ===                   │
│                                                                 │
│ Prompt engineering                                              │
│ Be clear, direct, and detailed                                  │
│                                                                 │
│ When interacting with Claude, think of it as a brilliant but    │
│ very new employee (with amnesia) who needs explicit instructions│
│ ..." (12,082 characters)                                        │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 3 (8.8s)                                              │
│                                                                 │
│ LLM Response: "TOOL: read_provider_doc | ARGS: provider=anthropic, doc_name=index.md"
│                                                                 │
│ Tool Result: (416 characters of index content)                  │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 4 (11.8s) - FINAL SUBMISSION                          │
│                                                                 │
│ LLM Response:                                                   │
│ "Based on my review of Anthropic's prompting guidelines...      │
│                                                                 │
│ TOOL: submit_optimization | ARGS: done                          │
│                                                                 │
│ OPTIMIZED_PROMPT:                                               │
│ ```                                                             │
│ You are a helpful assistant designed to provide clear,          │
│ accurate, and thoughtful responses to user questions...         │
│ ```                                                             │
│                                                                 │
│ CHANGES:                                                        │
│ 1. [clarity] - Added explicit description following the         │
│    guideline to be specific about what you want Claude to do"   │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
              OPTIMIZATION COMPLETE (26s total, 4 iterations)
```

## Comprehensive Logging

Every agent execution is logged in two ways:

### 1. API Response Logs (`agent_logs`)

Each optimization result includes detailed logs in the JSON response:

```json
{
  "agent_logs": [
    {"timestamp": "...", "elapsed_ms": 0, "type": "system", "content": "Starting optimization for ANTHROPIC"},
    {"timestamp": "...", "elapsed_ms": 2475, "type": "tool_call", "content": "Calling tool: list_provider_docs", "metadata": {"args": {"provider": "anthropic"}}},
    {"timestamp": "...", "elapsed_ms": 2476, "type": "tool_result", "content": "Available docs for ANTHROPIC: index.md, prompting.md"},
    {"timestamp": "...", "elapsed_ms": 8790, "type": "tool_call", "content": "Calling tool: read_provider_doc", "metadata": {"args": {"provider": "anthropic", "doc_name": "prompting.md"}}},
    {"timestamp": "...", "elapsed_ms": 8792, "type": "tool_result", "content": "=== ANTHROPIC: prompting.md ===...", "metadata": {"result_length": 12082}},
    {"timestamp": "...", "elapsed_ms": 26142, "type": "submit", "content": "Agent submitting final result"}
  ]
}
```

### 2. Local File Logs (`logs/`)

Full execution traces are saved to `rosetta_prompt/logs/`:

```bash
$ ls rosetta_prompt/logs/
20251205_055106_859143_anthropic.log  # 37KB
20251205_055106_861382_google.log     # 37KB

$ cat rosetta_prompt/logs/20251205_055106_859143_anthropic.log
================================================================================
ROSETTA PROMPT - AGENT EXECUTION LOG
================================================================================
Provider: ANTHROPIC
Started: 2025-12-05T05:51:06.859193
================================================================================

------------------------------------------------------------
[2025-12-05T05:51:06.859383] [0.000s] SYSTEM
------------------------------------------------------------
Starting optimization for ANTHROPIC
Model: anthropic/claude-opus-4.5
Original prompt length: 28 chars

------------------------------------------------------------
[2025-12-05T05:51:06.859441] [0.000s] TASK_INPUT
------------------------------------------------------------
## TASK: Optimize for ANTHROPIC
...

------------------------------------------------------------
[2025-12-05T05:51:15.651451] [8.792s] TOOL_RESULT
------------------------------------------------------------
Tool: read_provider_doc
Result (12082 chars):
=== ANTHROPIC: prompting.md ===

Prompt engineering
Be clear, direct, and detailed
...
```

Log files contain:
- **Full system prompt** sent to LLM
- **Complete LLM responses** (not truncated)
- **Full tool results** (12K+ chars of documentation)
- **Timing data** for each step
- **Final parsed output**

## API Usage

### Optimize Endpoint

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "You are a helpful assistant.",
    "providers": ["openai", "anthropic", "google"]
  }'
```

Response:

```json
{
  "original": "You are a helpful assistant.",
  "optimized": {
    "openai": {
      "provider": "openai",
      "prompt": "# Identity\nYou are an AI assistant designed to help...",
      "changes": [
        {"category": "structure", "description": "Added markdown sections..."},
        {"category": "formatting", "description": "Included examples..."}
      ],
      "success": true,
      "agent_logs": [...]
    },
    "anthropic": {
      "provider": "anthropic", 
      "prompt": "You are a helpful assistant designed to provide clear...",
      "changes": [...],
      "success": true,
      "agent_logs": [...]
    }
  }
}
```

### Get Available Providers

```bash
curl http://localhost:8000/providers
# ["anthropic", "google", "kimi", "openai"]
```

## Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **LLM** | OpenRouter (free tier) | Zero cost to experiment |
| **Agent Pattern** | ReAct (Reason + Act) | Industry standard for tool-using agents |
| **Messages** | LangChain `SystemMessage`, `HumanMessage`, `AIMessage` | Clean conversation management |
| **LLM Client** | `langchain_openai.ChatOpenAI` | OpenRouter compatible |
| **API** | FastAPI | Async support for parallel agents |
| **Frontend** | React + Three.js | 3D visualization of results |
| **State** | Zustand | Minimal React state management |

### Key LangChain Components Used

```python
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage

# LLM client compatible with OpenRouter
llm = ChatOpenAI(
    model="amazon/nova-2-lite-v1:free",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Async invocation
response = await llm.ainvoke([
    SystemMessage(content="You are an optimizer agent..."),
    HumanMessage(content="Optimize this prompt for OpenAI..."),
])
```

## Project Structure

```
TheRosettaPrompt/
├── rosetta_prompt/
│   ├── main.py                    # FastAPI endpoints
│   ├── config.py                  # LLM + provider config
│   │
│   ├── agents/
│   │   ├── orchestrator.py        # Parallel agent coordination
│   │   └── optimizer.py           # ReAct agent with tool loop
│   │
│   ├── utils/
│   │   └── logger.py              # FileLogger for local logs
│   │
│   ├── models/
│   │   └── schemas.py             # Pydantic models + AgentLogEntry
│   │
│   ├── logs/                      # Agent execution logs (auto-created)
│   │   └── *.log
│   │
│   └── docs/                      # Knowledge base (auto-detected)
│       ├── openai/prompting.md
│       ├── anthropic/prompting.md
│       ├── google/prompting.md
│       └── kimi/prompting.md
│
├── updater/                       # Claude Agent SDK doc updater
│   ├── agent.py                   # Main updater agent
│   ├── tools.py                   # Custom tools (Firecrawl, file ops)
│   ├── config.py                  # Provider URLs configuration
│   └── scheduler.py               # Weekly update scheduler
│
└── ui/
    └── src/
        ├── components/
        │   ├── InputScreen.js     # Prompt input + provider selection
        │   ├── ProcessingScreen.js # Live agent logs
        │   └── ResultsScreen.js   # 3D card carousel
        └── store.js               # API calls + Zustand state
```

## Adding New Providers

Providers are **auto-detected** from `docs/`. To add one:

```bash
# 1. Create provider directory
mkdir rosetta_prompt/docs/mistral

# 2. Add documentation (scrape from official docs)
cat > rosetta_prompt/docs/mistral/prompting.md << 'EOF'
# Mistral Prompting Guidelines

## Best Practices
- Use clear, structured instructions
- Mistral models respond well to...
EOF

# 3. Restart server - new provider appears automatically
```

The agent will now:
1. `list_provider_docs("mistral")` → `["prompting.md"]`
2. `read_provider_doc("mistral", "prompting.md")` → Full guidelines
3. Apply Mistral-specific patterns to optimize prompts

## Automatic Documentation Updates

The `updater/` directory contains an autonomous agent that automatically updates prompting guides by scraping provider documentation using **Firecrawl** and synthesizing content with **Claude Opus**.

### Updater Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler (Weekly)                        │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Claude Opus (Anthropic SDK)                 │    │
│  │         Native Tool Calling + ReAct Loop            │    │
│  │                                                     │    │
│  │  Tools:                                             │    │
│  │  • list_providers → Get configured providers        │    │
│  │  • batch_scrape_urls (Firecrawl) → Fetch all docs   │    │
│  │  • read_current_guide → Compare with existing       │    │
│  │  • update_guide → Write synthesized content         │    │
│  │  • write_update_log → Record update status          │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│              rosetta_prompt/docs/*.md                        │
└─────────────────────────────────────────────────────────────┘
```

### Running the Updater

```bash
cd updater
pip install -r requirements.txt

# Manual update (all providers)
python agent.py

# Update specific providers
python agent.py anthropic openai

# Update multiple providers
python agent.py google kimi

# Weekly scheduler
python scheduler.py
```

### Configuration

Add URLs for new providers in `updater/config.py`:

```python
PROVIDER_CONFIGS = {
    "mistral": {
        "name": "Mistral",
        "urls": ["https://docs.mistral.ai/capabilities/completion/"],
        "doc_file": "prompting.md"
    }
}

CLAUDE_MODEL = "claude-opus-4-5-20251101"  # Model for synthesis
MAX_TURNS = 5  # Max agent iterations
```

Requires `ANTHROPIC_API_KEY` and `FIRECRAWL_API_KEY` in `.env`.

## Setup

```bash
# Backend
cd rosetta_prompt
pip install -r requirements.txt
echo "OPENROUTER_API_KEY=your_key" > .env
uvicorn main:app --reload --port 8000

# Frontend
cd ui
npm install
npm start
```

## License

MIT
