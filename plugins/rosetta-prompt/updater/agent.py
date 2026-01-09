"""
Prompting Guide Updater Agent using Anthropic Python SDK.

This agent:
1. Scrapes prompting documentation from AI providers using Firecrawl
2. Compares scraped content with existing guides
3. Updates local prompting.md files with fresh content
4. Logs all updates for tracking

Designed to run weekly via scheduler or manual trigger.
"""
import asyncio
import os
from datetime import datetime

import anthropic
from dotenv import load_dotenv

from tools import TOOL_DEFINITIONS, execute_tool
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TURNS, PROVIDER_CONFIGS


# Ensure API key is set
load_dotenv()


SYSTEM_PROMPT = """You are a Prompting Guide Updater Agent responsible for keeping AI provider prompting documentation up to date.

Your task is to:
1. First, call list_providers to see all available providers and their documentation URLs
2. For each provider you need to update:
   a. Call read_current_guide to see the existing content
   b. Call batch_scrape_urls with ALL the provider's URLs at once (this is more efficient than scraping one by one)
   c. Synthesize the scraped content into a clean, comprehensive prompting guide
   d. Call update_guide with the new content
   e. Call write_update_log to record the update

Guidelines for synthesizing content:
- Extract the core prompting best practices, techniques, and examples
- Remove navigation elements, headers, footers, and irrelevant website chrome
- Maintain a consistent markdown format
- Include practical examples where available
- Keep the guide focused and actionable (aim for 5000-15000 characters)
- Preserve provider-specific terminology and recommendations

Format for each guide:
```markdown
# {Provider Name} Prompting Guide
Last updated: {today's date}

## Overview
Brief introduction to the provider's approach to prompting.

## Key Principles
Core principles and best practices (3-5 main points).

## Techniques
Specific prompting techniques with examples.

## Examples
2-3 practical examples demonstrating best practices.

## Tips
Provider-specific tips and common pitfalls.
```

Process providers sequentially. If a scrape fails, log the error and continue with the next provider.
After completing all updates, provide a summary of what was updated."""


async def run_updater(providers: list[str] | None = None):
    """
    Run the prompting guide updater agent.
    
    Args:
        providers: Optional list of specific provider IDs to update.
                   If None, updates all providers.
    """
    api_key = ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build the prompt based on whether specific providers are requested
    if providers:
        valid_providers = [p for p in providers if p in PROVIDER_CONFIGS]
        if not valid_providers:
            print(f"No valid providers specified. Available: {list(PROVIDER_CONFIGS.keys())}")
            return
        
        user_message = f"Please update prompting guides for these specific providers: {', '.join(valid_providers)}. Start by listing providers to get their URLs."
    else:
        user_message = "Please update all prompting guides. Start by listing providers to get their URLs."
    
    print("=" * 60)
    print("PROMPTING GUIDE UPDATER AGENT")
    print("=" * 60)
    print(f"Model: {CLAUDE_MODEL}")
    print(f"Providers: {providers or 'all'}")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    messages = [{"role": "user", "content": user_message}]
    
    for turn in range(MAX_TURNS):
        print(f"\n--- Turn {turn + 1}/{MAX_TURNS} ---")
        
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=16384,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages
            )
        except Exception as e:
            print(f"\n[API Error]: {type(e).__name__}: {str(e)}")
            break
        
        print(f"Stop reason: {response.stop_reason}")
        
        # Process response content
        assistant_content = []
        has_tool_use = False
        
        for block in response.content:
            if block.type == "text":
                print(f"\n[Agent]: {block.text[:1000]}{'...' if len(block.text) > 1000 else ''}")
                assistant_content.append({"type": "text", "text": block.text})
            
            elif block.type == "tool_use":
                has_tool_use = True
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id
                
                print(f"\n[Tool Call]: {tool_name}")
                input_str = str(tool_input)
                if len(input_str) > 200:
                    input_str = input_str[:200] + "..."
                print(f"  Input: {input_str}")
                
                assistant_content.append({
                    "type": "tool_use",
                    "id": tool_use_id,
                    "name": tool_name,
                    "input": tool_input
                })
        
        # Add assistant message
        messages.append({"role": "assistant", "content": assistant_content})
        
        # If there were tool uses, execute them and add results
        if has_tool_use:
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[Executing]: {block.name}...")
                    result = execute_tool(block.name, block.input)
                    result_preview = result[:500] + "..." if len(result) > 500 else result
                    print(f"[Result]: {result_preview}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages.append({"role": "user", "content": tool_results})
        
        # Check if we're done
        if response.stop_reason == "end_turn" and not has_tool_use:
            print(f"\n{'=' * 60}")
            print("UPDATE COMPLETE")
            print(f"{'=' * 60}")
            break
    
    else:
        print(f"\n[Warning]: Reached max turns ({MAX_TURNS})")


async def run_single_provider(provider_id: str):
    """Run update for a single provider."""
    await run_updater(providers=[provider_id])


def main():
    """Entry point for the updater."""
    import sys
    
    if len(sys.argv) > 1:
        # Update specific providers
        providers = sys.argv[1:]
        asyncio.run(run_updater(providers=providers))
    else:
        # Update all providers
        asyncio.run(run_updater())


if __name__ == "__main__":
    main()
