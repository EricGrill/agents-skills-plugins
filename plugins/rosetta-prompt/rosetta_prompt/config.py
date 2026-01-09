"""Configuration for OpenRouter LLM and application settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model configuration - using free tier models with good context length
# Using meta-llama for longer context support
PRIMARY_MODEL = "anthropic/claude-opus-4.5"
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

# Application settings
DOCS_BASE_PATH = os.path.join(os.path.dirname(__file__), "docs")


def get_supported_providers() -> list[str]:
    """
    Dynamically detect supported providers by scanning the docs folder.
    Each subfolder in docs/ that contains at least one .md file is a provider.
    """
    docs_path = Path(DOCS_BASE_PATH)
    providers = []
    
    if docs_path.exists():
        for item in docs_path.iterdir():
            if item.is_dir():
                # Check if folder has at least one markdown file
                md_files = list(item.glob("*.md"))
                if md_files:
                    providers.append(item.name)
    
    return sorted(providers)


# Get providers dynamically
SUPPORTED_PROVIDERS = get_supported_providers()

# Model parameters
# Increased max_tokens to handle long prompts (up to 16K output)
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 16384
