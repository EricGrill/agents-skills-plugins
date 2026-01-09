"""
Configuration for the Prompting Guide Updater Agent.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (check both project root and rosetta_prompt/)
env_paths = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent / "rosetta_prompt" / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Paths
DOCS_DIR = Path(__file__).parent.parent / "rosetta_prompt" / "docs"

# Provider configurations with their documentation URLs
PROVIDER_CONFIGS = {
    "anthropic": {
        "name": "Anthropic",
        "urls": [
            "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct",
            "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-examples",
            "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/let-claude-think",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/extended-thinking-tips",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/long-context-tips",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prefill-claudes-response",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/system-prompts",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/chain-of-thought",
            "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/multishot-prompting",
        ],
        "doc_file": "prompting.md"
    },
    "openai": {
        "name": "OpenAI",
        "urls": [
            "https://platform.openai.com/docs/guides/prompt-engineering",
            "https://platform.openai.com/docs/guides/text-generation",
            "https://cookbook.openai.com/examples/gpt-5/gpt-5-1_prompting_guide",
        ],
        "doc_file": "prompting.md"
    },
    "google": {
        "name": "Google (Gemini)",
        "urls": [
            "https://ai.google.dev/gemini-api/docs/prompting-strategies",
            "https://ai.google.dev/gemini-api/docs/system-instructions",
        ],
        "doc_file": "prompting.md"
    },
    "kimi": {
        "name": "Kimi (Moonshot)",
        "urls": [
            "https://platform.moonshot.ai/docs/guide/prompt-best-practice",
        ],
        "doc_file": "prompting.md"
    }
}

# Agent settings
CLAUDE_MODEL = "claude-opus-4-5-20251101" 
MAX_TURNS = 5

