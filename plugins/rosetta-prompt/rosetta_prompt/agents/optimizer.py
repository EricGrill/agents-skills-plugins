"""
Optimizer agent for single-provider prompt optimization.

This is a TRUE AGENTIC implementation using LangChain v1.
The agent autonomously decides which documentation to read using tools,
then applies the guidelines to optimize the prompt.

Includes comprehensive logging of all agent activity.
Logs are saved to: rosetta_prompt/logs/
"""

import json
import re
from typing import Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from pathlib import Path

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    PRIMARY_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DOCS_BASE_PATH,
    SUPPORTED_PROVIDERS,
)
from models.schemas import OptimizedPrompt, PromptChange
from utils.logger import FileLogger


# =============================================================================
# AGENT LOG - Captures all agent activity
# =============================================================================

class AgentLog:
    """Captures detailed logs of agent execution."""
    
    def __init__(self, provider: str):
        self.provider = provider
        self.entries = []
        self.start_time = datetime.now()
    
    def log(self, event_type: str, content: str, metadata: dict = None):
        """Add a log entry."""
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "type": event_type,
            "content": content[:500] if len(content) > 500 else content,  # Truncate for display
            "full_content": content,
            "metadata": metadata or {}
        })
    
    def to_dict(self) -> list:
        """Return logs as list of dicts (without full_content for API response)."""
        return [{
            "timestamp": e["timestamp"],
            "elapsed_ms": e["elapsed_ms"],
            "type": e["type"],
            "content": e["content"],
            "metadata": e["metadata"]
        } for e in self.entries]


# =============================================================================
# TOOL FUNCTIONS
# =============================================================================

def _list_provider_docs(provider: str) -> str:
    """List available documentation files for a provider."""
    provider_path = Path(DOCS_BASE_PATH) / provider.lower()
    
    if not provider_path.exists():
        return f"Error: Provider '{provider}' not found. Available: {SUPPORTED_PROVIDERS}"
    
    files = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]
    
    if not files:
        return f"No documentation found for '{provider}'."
    
    return f"Available docs for {provider.upper()}: {', '.join(sorted(files))}. Call read_provider_doc to read them."


def _read_provider_doc(provider: str, doc_name: str) -> str:
    """Read a specific documentation file."""
    if not doc_name.endswith(".md"):
        doc_name = f"{doc_name}.md"
    
    doc_path = Path(DOCS_BASE_PATH) / provider.lower() / doc_name
    
    if not doc_path.exists():
        provider_path = Path(DOCS_BASE_PATH) / provider.lower()
        if provider_path.exists():
            available = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]
            return f"Not found. Available files: {available}"
        return f"Provider '{provider}' not found."
    
    content = doc_path.read_text()
    # Truncate very long docs to avoid context overflow
    if len(content) > 12000:
        content = content[:12000] + "\n\n[Truncated - apply the patterns you've learned]"
    
    return f"=== {provider.upper()}: {doc_name} ===\n\n{content}"


# =============================================================================
# AGENT SYSTEM PROMPT
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are a prompt optimization expert. You use TOOLS to read documentation then optimize prompts.

## TOOLS (use EXACTLY this format)

TOOL: list_provider_docs | ARGS: provider=PROVIDER_NAME
TOOL: read_provider_doc | ARGS: provider=PROVIDER_NAME, doc_name=FILENAME
TOOL: submit_optimization | ARGS: see below

## YOUR WORKFLOW

1. Call list_provider_docs to see available docs
2. Call read_provider_doc to read the prompting guidelines  
3. Study the guidelines carefully
4. Call submit_optimization with your result

## SUBMIT FORMAT (CRITICAL - follow exactly)

When ready to submit, output in this EXACT format:

TOOL: submit_optimization | ARGS: done

OPTIMIZED_PROMPT:
```
[Write the COMPLETE optimized prompt here - NOT a placeholder]
```

CHANGES:
1. [Category: structure/formatting/clarity] - [Specific description of what you changed]
2. [Category: ...] - [...]
3. ...

## RULES

- You MUST read documentation before optimizing
- Write the ACTUAL optimized prompt, not "<optimized_prompt_here>" or placeholders
- List SPECIFIC changes you made, not generic "Applied guidelines"
- Each change should describe: what was changed, why, based on which guideline

START by listing docs for the target provider."""


# =============================================================================
# OPTIMIZER AGENT CLASS
# =============================================================================

class OptimizerAgent:
    """Agentic optimizer that uses tools to read documentation and optimize prompts."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=PRIMARY_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
    
    async def optimize(
        self,
        prompt: str,
        provider: str,
        preserve_structure: bool = True,
    ) -> OptimizedPrompt:
        """Run agentic optimization with tool calls."""
        log = AgentLog(provider)
        file_log = FileLogger(provider)  # Save full logs to disk
        
        try:
            log.log("system", f"Starting optimization for {provider.upper()}", {
                "original_prompt_length": len(prompt),
                "model": PRIMARY_MODEL
            })
            file_log.log("system", f"Starting optimization for {provider.upper()}\nModel: {PRIMARY_MODEL}\nOriginal prompt length: {len(prompt)} chars")
            
            task = f"""## TASK: Optimize for {provider.upper()}

ORIGINAL PROMPT:
```
{prompt}
```

Length: {len(prompt)} chars

## STEPS
1. Call: TOOL: list_provider_docs | ARGS: provider={provider}
2. Call: TOOL: read_provider_doc | ARGS: provider={provider}, doc_name=prompting.md
3. Read and understand the guidelines
4. Submit your optimization using the exact format in my instructions

BEGIN NOW."""

            log.log("input", f"Task assigned to agent", {"task_length": len(task)})
            file_log.log("task_input", task)
            
            result = await self._run_agent_loop(task, provider, prompt, log, file_log)
            
            # Attach logs to result
            result.agent_logs = log.to_dict()
            
            log.log("complete", f"Optimization finished", {
                "success": result.success,
                "changes_count": len(result.changes),
                "output_length": len(result.prompt)
            })
            
            # Close file log
            file_log.close(
                success=result.success,
                result_summary=f"Changes: {len(result.changes)}\nOutput Length: {len(result.prompt)} chars"
            )
            
            return result
            
        except Exception as e:
            log.log("error", str(e))
            file_log.log("error", str(e))
            file_log.close(success=False, result_summary=f"Error: {str(e)}")
            
            result = OptimizedPrompt(
                provider=provider,
                prompt=prompt,
                changes=[PromptChange(category="error", description=str(e))],
                success=False,
                error=str(e),
            )
            result.agent_logs = log.to_dict()
            return result
    
    async def _run_agent_loop(
        self,
        task: str,
        provider: str,
        original: str,
        log: AgentLog,
        file_log: FileLogger,
    ) -> OptimizedPrompt:
        """Run the agent loop with tool calls."""
        messages = [
            SystemMessage(content=AGENT_SYSTEM_PROMPT),
            HumanMessage(content=task),
        ]
        
        # Log the full system prompt and task
        file_log.log("system_prompt", AGENT_SYSTEM_PROMPT)
        
        docs_read = []
        docs_content = {}  # Store full doc content
        max_iterations = 8
        
        for iteration in range(max_iterations):
            log.log("llm_call", f"Iteration {iteration + 1}: Calling LLM", {"iteration": iteration + 1})
            file_log.log("llm_call", f"=== ITERATION {iteration + 1} ===\n\nSending {len(messages)} messages to LLM")
            
            # Log full messages to file
            for i, msg in enumerate(messages[-2:]):  # Log last 2 messages
                role = msg.__class__.__name__
                file_log.log(f"message_{role}", msg.content)
            
            response = await self.llm.ainvoke(messages)
            text = response.content
            
            log.log("llm_response", text[:300] + "..." if len(text) > 300 else text, {
                "response_length": len(text),
                "iteration": iteration + 1
            })
            file_log.log("llm_response", text)  # Full response to file
            
            # Check for submission
            if "submit_optimization" in text.lower() and ("OPTIMIZED_PROMPT:" in text or "```" in text):
                log.log("submit", "Agent submitting final result")
                file_log.log("submit", "Agent submitting final result")
                return self._parse_final_submission(text, provider, original, docs_read, log)
            
            # Parse tool call
            tool_call = self._parse_tool_call(text)
            
            if tool_call:
                name, args = tool_call
                
                log.log("tool_call", f"Calling tool: {name}", {
                    "tool": name,
                    "args": args
                })
                file_log.log("tool_call", f"Tool: {name}\nArgs: {json.dumps(args, indent=2)}")
                
                result = self._execute_tool(name, args)
                
                log.log("tool_result", result[:300] + "..." if len(result) > 300 else result, {
                    "tool": name,
                    "result_length": len(result)
                })
                file_log.log("tool_result", f"Tool: {name}\nResult ({len(result)} chars):\n{result}")  # Full result!
                
                # Track which docs were read and their content
                if name == "read_provider_doc":
                    doc_key = f"{args.get('provider', '')}/{args.get('doc_name', '')}"
                    docs_read.append(doc_key)
                    docs_content[doc_key] = result
                
                messages.append(AIMessage(content=text))
                messages.append(HumanMessage(content=f"TOOL RESULT:\n{result}\n\nContinue. When ready, use submit_optimization with the format I specified."))
            else:
                log.log("no_tool", "No tool call detected, nudging agent")
                file_log.log("no_tool", f"No tool call detected in response:\n{text[:500]}")
                messages.append(AIMessage(content=text))
                messages.append(HumanMessage(
                    content=f"Please use the tool format. Start with:\nTOOL: list_provider_docs | ARGS: provider={provider}"
                ))
        
        # Max iterations - return error
        log.log("error", "Max iterations reached without completion")
        result = OptimizedPrompt(
            provider=provider,
            prompt=original,
            changes=[PromptChange(category="error", description="Optimization did not complete")],
            success=False,
            error="Max iterations reached",
        )
        return result
    
    def _parse_tool_call(self, text: str) -> Optional[tuple[str, dict]]:
        """Parse tool call from agent response."""
        match = re.search(r'TOOL:\s*(\w+)\s*\|\s*ARGS:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        
        if not match:
            return None
        
        name = match.group(1).strip().lower()
        args_str = match.group(2).strip()
        
        if name == "list_provider_docs":
            m = re.search(r'provider\s*=\s*(\w+)', args_str, re.IGNORECASE)
            if m:
                return (name, {'provider': m.group(1)})
        
        elif name == "read_provider_doc":
            p = re.search(r'provider\s*=\s*(\w+)', args_str, re.IGNORECASE)
            d = re.search(r'doc_name\s*=\s*([^\s,|]+)', args_str, re.IGNORECASE)
            if p and d:
                return (name, {'provider': p.group(1), 'doc_name': d.group(1)})
        
        elif name == "submit_optimization":
            return (name, {'raw': text})
        
        return None
    
    def _execute_tool(self, name: str, args: dict) -> str:
        """Execute a tool."""
        if name == "list_provider_docs":
            return _list_provider_docs(args.get('provider', ''))
        elif name == "read_provider_doc":
            return _read_provider_doc(args.get('provider', ''), args.get('doc_name', ''))
        return "Unknown tool"
    
    def _parse_final_submission(
        self,
        text: str,
        provider: str,
        original: str,
        docs_read: list,
        log: AgentLog,
    ) -> OptimizedPrompt:
        """Parse the final submission from agent."""
        
        # Extract optimized prompt from code block
        optimized = ""
        
        # Try to find content in code block after OPTIMIZED_PROMPT:
        prompt_section = re.search(
            r'OPTIMIZED_PROMPT:\s*```\s*\n?(.*?)```',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if prompt_section:
            optimized = prompt_section.group(1).strip()
        
        # Fallback: any code block
        if not optimized or len(optimized) < 10:
            blocks = re.findall(r'```(?:\w+)?\s*\n?(.*?)```', text, re.DOTALL)
            for block in blocks:
                block = block.strip()
                # Skip if it's clearly not a prompt
                if block and len(block) > 20 and not block.startswith('TOOL:'):
                    optimized = block
                    break
        
        # Check for placeholder/empty responses
        invalid_patterns = [
            r'^<.*>$',  # <optimized_prompt_here>
            r'^\[.*\]$',  # [your prompt here]
            r'^placeholder',
            r'^your\s+optimized',
            r'^insert\s+',
            r'^write\s+the\s+',
        ]
        
        is_invalid = False
        if optimized:
            for pattern in invalid_patterns:
                if re.match(pattern, optimized.lower().strip()):
                    is_invalid = True
                    break
        
        if not optimized or len(optimized) < 15 or is_invalid:
            log.log("parse_error", "Failed to extract valid optimized prompt")
            return OptimizedPrompt(
                provider=provider,
                prompt=original,
                changes=[PromptChange(
                    category="error",
                    description="Agent did not produce valid optimized prompt"
                )],
                success=False,
                error="Empty or placeholder output",
            )
        
        log.log("parse_success", f"Extracted optimized prompt ({len(optimized)} chars)")
        
        # Parse changes
        changes = self._parse_changes(text, provider, docs_read)
        log.log("changes_parsed", f"Parsed {len(changes)} changes")
        
        return OptimizedPrompt(
            provider=provider,
            prompt=optimized,
            changes=changes,
            success=True,
        )
    
    def _parse_changes(self, text: str, provider: str, docs_read: list) -> list[PromptChange]:
        """Parse changes from agent response."""
        changes = []
        
        # Look for numbered list after CHANGES:
        changes_section = re.search(r'CHANGES:\s*\n((?:\d+\..*\n?)+)', text, re.IGNORECASE)
        
        if changes_section:
            lines = changes_section.group(1).strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove number prefix
                line = re.sub(r'^\d+\.\s*', '', line)
                
                # Try to parse category and description
                cat_match = re.match(r'\[?(\w+)[:\]]\s*[-–]?\s*(.+)', line, re.IGNORECASE)
                if cat_match:
                    category = cat_match.group(1).lower()
                    description = cat_match.group(2).strip()
                else:
                    category = "optimization"
                    description = line
                
                if description and len(description) > 5:
                    changes.append(PromptChange(
                        category=category,
                        description=description
                    ))
        
        # If no changes parsed, create based on docs read
        if not changes:
            if docs_read:
                for doc in docs_read:
                    changes.append(PromptChange(
                        category="provider_pattern",
                        description=f"Applied guidelines from {doc}"
                    ))
            else:
                changes.append(PromptChange(
                    category="optimization",
                    description=f"Optimized for {provider.upper()}"
                ))
        
        return changes
