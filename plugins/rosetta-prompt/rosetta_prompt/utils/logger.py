"""
Agent execution logger that writes detailed logs to files.

Logs are written to: rosetta_prompt/logs/
Each optimization request creates a timestamped log file.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Log directory
LOGS_DIR = Path(__file__).parent.parent / "logs"


def ensure_logs_dir():
    """Create logs directory if it doesn't exist."""
    LOGS_DIR.mkdir(exist_ok=True)


def create_log_file(provider: str) -> Path:
    """Create a new log file for an optimization run."""
    ensure_logs_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}_{provider}.log"
    return LOGS_DIR / filename


class FileLogger:
    """
    Writes detailed agent execution logs to a file.
    
    Usage:
        logger = FileLogger("openai")
        logger.log("system", "Starting optimization")
        logger.log("llm_input", full_prompt_text)
        logger.log("llm_output", response_text)
        logger.close()
    """
    
    def __init__(self, provider: str):
        self.provider = provider
        self.filepath = create_log_file(provider)
        self.start_time = datetime.now()
        self.entries = []
        
        # Write header
        self._write_header()
    
    def _write_header(self):
        """Write log file header."""
        header = f"""
{'='*80}
ROSETTA PROMPT - AGENT EXECUTION LOG
{'='*80}
Provider: {self.provider.upper()}
Started: {self.start_time.isoformat()}
Log File: {self.filepath.name}
{'='*80}

"""
        with open(self.filepath, 'w') as f:
            f.write(header)
    
    def log(self, event_type: str, content: str, metadata: dict = None):
        """
        Log an event to the file.
        
        Event types:
        - system: System messages
        - llm_input: Full input sent to LLM
        - llm_output: Full output received from LLM
        - tool_call: Tool being called with args
        - tool_result: Result from tool execution
        - error: Error messages
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "elapsed_seconds": round(elapsed, 3),
            "type": event_type,
            "content_length": len(content),
            "metadata": metadata or {}
        }
        self.entries.append(entry)
        
        # Format for file
        separator = "-" * 60
        
        log_text = f"""
{separator}
[{timestamp}] [{elapsed:.3f}s] {event_type.upper()}
{separator}
"""
        
        if metadata:
            log_text += f"Metadata: {json.dumps(metadata, indent=2)}\n\n"
        
        log_text += f"{content}\n"
        
        # Write to file immediately
        with open(self.filepath, 'a') as f:
            f.write(log_text)
    
    def log_llm_messages(self, messages: list):
        """Log the full message array sent to LLM."""
        formatted = []
        for msg in messages:
            role = msg.__class__.__name__
            content = msg.content
            formatted.append(f"[{role}]\n{content}")
        
        full_input = "\n\n".join(formatted)
        self.log("llm_input", full_input, {"message_count": len(messages)})
    
    def close(self, success: bool, result_summary: str = ""):
        """Close the log file with a summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        summary = f"""
{'='*80}
EXECUTION COMPLETE
{'='*80}
Provider: {self.provider.upper()}
Success: {success}
Total Time: {elapsed:.3f} seconds
Events Logged: {len(self.entries)}
{result_summary}
{'='*80}
"""
        
        with open(self.filepath, 'a') as f:
            f.write(summary)
        
        print(f"[ROSETTA] Agent log saved: {self.filepath}")
        return self.filepath


def get_recent_logs(limit: int = 10) -> list[Path]:
    """Get the most recent log files."""
    ensure_logs_dir()
    logs = sorted(LOGS_DIR.glob("*.log"), reverse=True)
    return logs[:limit]


def read_log(filepath: Path) -> str:
    """Read a log file."""
    if filepath.exists():
        return filepath.read_text()
    return f"Log file not found: {filepath}"


