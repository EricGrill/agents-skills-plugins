"""
Document retrieval tools for navigating the provider knowledge base.

Uses LangChain v1's @tool decorator for tool definitions.
Reference: https://docs.langchain.com/oss/python/releases/langchain-v1
"""

import os
from pathlib import Path
from langchain.tools import tool

from config import DOCS_BASE_PATH, SUPPORTED_PROVIDERS


@tool
def get_available_providers() -> list[str]:
    """
    Get the list of available AI providers that can be optimized for.
    
    Returns:
        List of provider names (e.g., ['openai', 'anthropic', 'google', 'kimi'])
    """
    return SUPPORTED_PROVIDERS


@tool
def list_provider_docs(provider: str) -> dict:
    """
    List all available documentation files for a specific provider.
    
    Use this tool first to understand what documentation is available
    for a provider before reading specific files.
    
    Args:
        provider: The provider name (e.g., 'openai', 'anthropic')
        
    Returns:
        Dictionary with 'files' list and 'index_content' if index.md exists.
        The index describes what each document contains.
    """
    provider_path = Path(DOCS_BASE_PATH) / provider.lower()
    
    if not provider_path.exists():
        return {
            "error": f"Provider '{provider}' not found",
            "available_providers": SUPPORTED_PROVIDERS
        }
    
    files = []
    for file in provider_path.iterdir():
        if file.is_file() and file.suffix == ".md":
            files.append(file.name)
    
    result = {"provider": provider, "files": sorted(files)}
    
    # Include index content if available (describes what each doc contains)
    index_path = provider_path / "index.md"
    if index_path.exists():
        result["index_content"] = index_path.read_text()
    
    return result


@tool
def read_provider_doc(provider: str, doc_name: str) -> str:
    """
    Read a specific documentation file for a provider.
    
    Args:
        provider: The provider name (e.g., 'openai', 'anthropic')
        doc_name: The document filename (e.g., 'prompting.md')
        
    Returns:
        The content of the documentation file.
    """
    # Ensure doc_name has .md extension
    if not doc_name.endswith(".md"):
        doc_name = f"{doc_name}.md"
    
    doc_path = Path(DOCS_BASE_PATH) / provider.lower() / doc_name
    
    if not doc_path.exists():
        # List available files for helpful error
        provider_path = Path(DOCS_BASE_PATH) / provider.lower()
        if provider_path.exists():
            available = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]
            return f"Document '{doc_name}' not found for provider '{provider}'. Available: {available}"
        return f"Provider '{provider}' not found. Available: {SUPPORTED_PROVIDERS}"
    
    return doc_path.read_text()


def load_provider_guidelines(provider: str) -> str:
    """
    Load the complete prompting guidelines for a provider.
    
    This is a direct function (not a tool) called by the optimizer agent
    to get all relevant context for a specific provider in one call.
    
    Design Decision: We load ALL documentation rather than using RAG because:
    1. Documents are small enough to fit in context
    2. Full context prevents "context rot" from chunking
    3. Deterministic - same input always produces same context
    4. Debuggable - you can see exactly what the agent receives
    
    Args:
        provider: The provider name
        
    Returns:
        Combined content of all provider documentation
    """
    provider_path = Path(DOCS_BASE_PATH) / provider.lower()
    
    if not provider_path.exists():
        return f"No documentation found for provider: {provider}"
    
    content_parts = []
    
    # Read index first if it exists
    index_path = provider_path / "index.md"
    if index_path.exists():
        content_parts.append(f"# {provider.upper()} Prompting Guidelines\n")
        content_parts.append(index_path.read_text())
        content_parts.append("\n---\n")
    
    # Read all other documentation files
    for doc_file in sorted(provider_path.iterdir()):
        if doc_file.is_file() and doc_file.suffix == ".md" and doc_file.name != "index.md":
            content_parts.append(f"\n## {doc_file.stem.replace('_', ' ').title()}\n")
            content_parts.append(doc_file.read_text())
            content_parts.append("\n")
    
    return "\n".join(content_parts)
