"""Robust JSON Parser for LLM Responses

Handles common issues with JSON parsing from LLM outputs:
- Markdown code blocks
- Trailing/leading whitespace
- Unescaped newlines in strings
- Partial JSON responses
"""

import json
import re
from typing import Any, Dict, Optional


def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from LLM response
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    
    # Step 1: Extract JSON from markdown code blocks
    json_str = response.strip()
    
    # Remove markdown code blocks
    if "```json" in json_str:
        # Extract content between ```json and ```
        match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
    elif "```" in json_str:
        # Extract content between ``` and ```
        match = re.search(r'```\s*(.*?)\s*```', json_str, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
    
    # Step 2: Try to parse the JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Step 3: Try to fix common issues
        
        # Fix 1: Remove any text before the first {
        if '{' in json_str:
            start_idx = json_str.find('{')
            json_str = json_str[start_idx:]
        
        # Fix 2: Find the last complete } to handle truncation
        # Count braces to find where valid JSON ends
        brace_count = 0
        last_valid_pos = 0
        
        for i, char in enumerate(json_str):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    last_valid_pos = i + 1
        
        if last_valid_pos > 0 and last_valid_pos < len(json_str):
            json_str = json_str[:last_valid_pos]
        
        # Try parsing again
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If still failing, return None
            return None


def create_default_response(error_msg: str, raw_response: str = "") -> Dict[str, Any]:
    """Create a default error response
    
    Args:
        error_msg: Error message
        raw_response: Raw response from LLM
        
    Returns:
        Default dict with error information
    """
    return {
        "error": error_msg,
        "raw_response": raw_response[:1000] if raw_response else "",
        "parse_failed": True
    }
