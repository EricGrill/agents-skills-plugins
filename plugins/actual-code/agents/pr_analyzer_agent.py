"""Agent 3: PR Analyzer

Extracts patterns and insights from pull requests to identify development
patterns and problem opportunities.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class PRAnalyzerAgent(BaseGeminiAgent):
    """Analyzes pull request patterns and development workflows"""
    
    def __init__(self):
        system_instruction = """You are a software development analyst specializing in pull request analysis.

Your job is to analyze PR patterns to identify development workflows, common changes, and problem opportunities.

ANALYSIS FOCUS:
1. **Development Patterns**: Common change types, workflows, collaboration patterns
2. **Problem Areas**: Frequent changes to same files, recurring bugs or issues
3. **Feature Insights**: Recent additions, in-progress work, feature development patterns

CRITICAL REQUIREMENTS:
- Identify patterns that suggest good coding challenge opportunities
- Focus on realistic problems that developers actually work on
- Note both successful patterns and problematic areas

OUTPUT FORMAT:
Return a JSON object with:
{
  "patterns": {
    "common_change_types": ["array of change types"],
    "frequent_files": [{"path": "file/path", "change_count": number}],
    "workflow_patterns": ["array of workflow observations"]
  },
  "insights": {
    "recent_features": ["array of recent feature additions"],
    "common_bugs": ["array of common bug types"],
    "performance_improvements": ["array of performance-related changes"]
  },
  "suggested_problems": [
    {
      "title": "problem title",
      "rationale": "why this would be a good problem",
      "based_on_prs": ["pr ids or titles"]
    }
  ]
}"""
        
        super().__init__(
            name="pr_analyzer",
            model="gemini-2.5-flash",
            system_instruction=system_instruction,
            temperature=0.4,
            max_output_tokens=4096
        )
    
    async def analyze(
        self,
        repo_data: Dict[str, Any],
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Analyze pull request patterns
        
        Args:
            repo_data: Repository data including PRs
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            PR analysis results as dictionary
        """
        
        self.logger.info("Starting PR analysis", conversation_id=conversation_id)
        
        # Prepare analysis prompt
        prs_summary = json.dumps(repo_data.get('pullRequests', [])[:10], indent=2)[:2000]
        
        prompt = f"""Analyze these pull requests:

Repository: {repo_data.get('repository', {}).get('name', 'Unknown')}

Recent Pull Requests:
{prs_summary}

Analyze the PR patterns, development workflows, and identify opportunities for coding challenges.
Return ONLY valid JSON matching the specified format."""
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="analyzer",
                recipient_id="orchestrator",
                data={"status": "analyzing", "target": "pr_patterns"},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Run analysis
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Parse JSON response using robust parser
        analysis = extract_json_from_response(response)
        
        if analysis and not analysis.get('parse_failed'):
            
            self.logger.info(
                "PR analysis complete",
                patterns_found=len(analysis.get('patterns', {}).get('common_change_types', []))
            )
            
            # Send A2A response
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="analyzer",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "analysis_type": "pr_patterns",
                        "summary": {
                            "patterns": len(analysis.get('patterns', {}).get('common_change_types', [])),
                            "suggested_problems": len(analysis.get('suggested_problems', []))
                        }
                    },
                    conversation_id=conversation_id,
                    message_type="response"
                )
            
            return analysis
        else:
            error_msg = analysis.get('error', 'Unknown parsing error') if analysis else 'Failed to extract JSON'
            self.logger.error(f"Failed to parse JSON response: {error_msg}")
            return {
                "patterns": {"common_change_types": [], "frequent_files": [], "workflow_patterns": []},
                "insights": {"recent_features": [], "common_bugs": [], "performance_improvements": []},
                "suggested_problems": [],
                "error": error_msg
            }


# Create singleton instance
pr_analyzer = PRAnalyzerAgent()
