"""
Tools for the Prompting Guide Updater Agent.
Uses Anthropic's native tool calling format.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Any
from datetime import datetime

from firecrawl import FirecrawlApp

from config import DOCS_DIR, FIRECRAWL_API_KEY, PROVIDER_CONFIGS


# Initialize Firecrawl client
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)


# Tool definitions for Anthropic API
TOOL_DEFINITIONS = [
    {
        "name": "list_providers",
        "description": "List all available AI providers that have prompting guides configured, including their documentation URLs",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "read_current_guide",
        "description": "Read the current prompting guide markdown file for a specific provider",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider_id": {
                    "type": "string",
                    "description": "The provider ID (e.g., 'anthropic', 'openai', 'google', 'kimi')"
                }
            },
            "required": ["provider_id"]
        }
    },
    {
        "name": "scrape_url",
        "description": "Scrape a single URL using Firecrawl to get its content in markdown format",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "batch_scrape_urls",
        "description": "Scrape multiple URLs at once using Firecrawl batch scraping. More efficient than scraping one by one.",
        "input_schema": {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to scrape"
                }
            },
            "required": ["urls"]
        }
    },
    {
        "name": "update_guide",
        "description": "Update the prompting guide file for a specific provider with new synthesized content",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider_id": {
                    "type": "string",
                    "description": "The provider ID"
                },
                "new_content": {
                    "type": "string",
                    "description": "The new markdown content for the prompting guide"
                }
            },
            "required": ["provider_id", "new_content"]
        }
    },
    {
        "name": "write_update_log",
        "description": "Write an entry to the update log after completing updates for a provider",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider_id": {
                    "type": "string",
                    "description": "The provider ID"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the update (success, error, skipped)"
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary of what was updated or why it failed"
                }
            },
            "required": ["provider_id", "status", "summary"]
        }
    }
]


def list_providers() -> str:
    """List all configured providers and their documentation URLs."""
    providers_info = []
    for provider_id, config in PROVIDER_CONFIGS.items():
        doc_path = DOCS_DIR / provider_id / config["doc_file"]
        exists = doc_path.exists()
        providers_info.append({
            "id": provider_id,
            "name": config["name"],
            "urls": config["urls"],
            "doc_file": config["doc_file"],
            "current_doc_exists": exists
        })
    
    return json.dumps(providers_info, indent=2)


def read_current_guide(provider_id: str) -> str:
    """Read the current prompting guide markdown file for a provider."""
    if provider_id not in PROVIDER_CONFIGS:
        return f"Error: Unknown provider '{provider_id}'. Available: {list(PROVIDER_CONFIGS.keys())}"
    
    config = PROVIDER_CONFIGS[provider_id]
    doc_path = DOCS_DIR / provider_id / config["doc_file"]
    
    if not doc_path.exists():
        return f"No existing guide found at {doc_path}. This will be a new file."
    
    try:
        content = doc_path.read_text(encoding="utf-8")
        return f"Current guide for {config['name']} ({len(content)} chars):\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def scrape_url(url: str) -> str:
    """Scrape a URL and return its content as markdown."""
    try:
        result = firecrawl.scrape(url, formats=["markdown"])
        
        if not result:
            return f"Error: No content returned from {url}"
        
        # Result is a Document object, access attributes directly
        markdown_content = getattr(result, "markdown", "") or ""
        metadata = getattr(result, "metadata", {}) or {}
        title = metadata.get("title", "Unknown") if isinstance(metadata, dict) else "Unknown"
        
        if not markdown_content:
            return f"Error: Empty markdown content from {url}"
        
        return f"=== Scraped: '{title}' ===\nURL: {url}\n\n{markdown_content[:40000]}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


def batch_scrape_urls(urls: list[str]) -> str:
    """Scrape multiple URLs in batch and return combined markdown content."""
    if not urls:
        return "Error: No URLs provided"
    
    try:
        # Use Firecrawl's batch scrape with correct API
        result = firecrawl.batch_scrape(urls, formats=["markdown"])
        
        if not result:
            return "Error: No content returned from batch scrape"
        
        # Combine all scraped content
        combined_content = []
        
        # Result might be a BatchScrapeResponse object with data attribute
        data = getattr(result, "data", result) if hasattr(result, "data") else result
        if isinstance(data, dict):
            data = data.get("data", [])
        
        for item in data:
            # Item might be a Document object
            if hasattr(item, "markdown"):
                markdown = item.markdown or ""
                metadata = getattr(item, "metadata", {}) or {}
                title = metadata.get("title", "Unknown") if isinstance(metadata, dict) else "Unknown"
                url = metadata.get("sourceURL", metadata.get("url", "Unknown URL")) if isinstance(metadata, dict) else "Unknown URL"
            elif isinstance(item, dict):
                markdown = item.get("markdown", "")
                metadata = item.get("metadata", {})
                title = metadata.get("title", "Unknown")
                url = metadata.get("sourceURL", metadata.get("url", "Unknown URL"))
            else:
                continue
            
            if markdown:
                combined_content.append(f"=== {title} ===\nSource: {url}\n\n{markdown[:25000]}")
        
        if not combined_content:
            return f"Error: No valid content extracted from {len(urls)} URLs"
        
        full_text = "\n\n" + "="*60 + "\n\n".join(combined_content)
        
        return f"Batch scraped {len(combined_content)} of {len(urls)} URLs:\n{full_text[:80000]}"
    except Exception as e:
        return f"Error in batch scrape: {str(e)}"


def update_guide(provider_id: str, new_content: str) -> str:
    """Write updated prompting guide content to the provider's doc file."""
    if provider_id not in PROVIDER_CONFIGS:
        return f"Error: Unknown provider '{provider_id}'. Available: {list(PROVIDER_CONFIGS.keys())}"
    
    if not new_content or len(new_content.strip()) < 100:
        return "Error: Content too short. Guide must be at least 100 characters."
    
    config = PROVIDER_CONFIGS[provider_id]
    doc_dir = DOCS_DIR / provider_id
    doc_path = doc_dir / config["doc_file"]
    
    try:
        # Ensure directory exists
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file if it exists
        if doc_path.exists():
            backup_path = doc_dir / f"{config['doc_file']}.backup"
            import shutil
            shutil.copy2(doc_path, backup_path)
        
        # Write new content
        doc_path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully updated {config['name']} guide at {doc_path} ({len(new_content)} chars)"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def write_update_log(provider_id: str, status: str, summary: str) -> str:
    """Append an update entry to the log file."""
    log_path = DOCS_DIR / "update_log.json"
    
    try:
        if log_path.exists():
            log_data = json.loads(log_path.read_text(encoding="utf-8"))
        else:
            log_data = {"updates": []}
        
        log_data["updates"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "provider_id": provider_id,
            "status": status,
            "summary": summary
        })
        
        # Keep only last 100 entries
        log_data["updates"] = log_data["updates"][-100:]
        
        log_path.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
        
        return f"Logged update for {provider_id}: {status}"
    except Exception as e:
        return f"Error writing log: {str(e)}"


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name with given input."""
    if tool_name == "list_providers":
        return list_providers()
    elif tool_name == "read_current_guide":
        return read_current_guide(tool_input.get("provider_id", ""))
    elif tool_name == "scrape_url":
        return scrape_url(tool_input.get("url", ""))
    elif tool_name == "batch_scrape_urls":
        return batch_scrape_urls(tool_input.get("urls", []))
    elif tool_name == "update_guide":
        return update_guide(tool_input.get("provider_id", ""), tool_input.get("new_content", ""))
    elif tool_name == "write_update_log":
        return write_update_log(
            tool_input.get("provider_id", ""),
            tool_input.get("status", ""),
            tool_input.get("summary", "")
        )
    else:
        return f"Unknown tool: {tool_name}"
