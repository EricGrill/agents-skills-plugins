"""Agent 4: Issue Analyzer

Extracts problem patterns and feature requests from issues to identify
coding challenge opportunities.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class IssueAnalyzerAgent(BaseGeminiAgent):
    """Analyzes issue patterns and feature requests"""
    
    def __init__(self):
        system_instruction = """You are a product analyst specializing in issue tracking analysis.

Your job is to analyze issues to identify problem patterns, feature requests, and coding challenge opportunities.

ANALYSIS FOCUS:
1. **Issue Categories**: Bugs, feature requests, enhancements, questions
2. **Priority Signals**: Community upvotes, maintainer responses, labels
3. **Problem Patterns**: Common complaints, requested features, pain points

CRITICAL REQUIREMENTS:
- Identify realistic problems that matter to users
- Focus on issues that would make good coding challenges
- Note both technical and user-facing problems

OUTPUT FORMAT:
Return a JSON object with:
{
  "categories": {
    "bugs": {"count": number, "examples": ["bug titles"]},
    "features": {"count": number, "examples": ["feature titles"]},
    "enhancements": {"count": number, "examples": ["enhancement titles"]}
  },
  "priority_issues": [
    {"title": "issue title", "reason": "why it's high priority"}
  ],
  "problem_patterns": [
    {"pattern": "pattern description", "frequency": "high|medium|low"}
  ],
  "suggested_problems": [
    {
      "title": "problem title",
      "rationale": "why this would be a good problem",
      "difficulty": "easy|medium|hard",
      "based_on_issues": ["issue ids or titles"]
    }
  ]
}"""
        
        super().__init__(
            name="issue_analyzer",
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
        """Analyze issue patterns
        
        Args:
            repo_data: Repository data including issues
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Issue analysis results as dictionary
        """
        
        self.logger.info("Starting issue analysis", conversation_id=conversation_id)
        
        # Prepare analysis prompt
        issues_summary = json.dumps(repo_data.get('issues', [])[:15], indent=2)[:2000]
        
        prompt = f"""Analyze these GitHub issues:

Repository: {repo_data.get('repository', {}).get('name', 'Unknown')}

Recent Issues:
{issues_summary}

Analyze the issue patterns, feature requests, and identify opportunities for coding challenges.
Return ONLY valid JSON matching the specified format."""
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="analyzer",
                recipient_id="orchestrator",
                data={"status": "analyzing", "target": "issue_patterns"},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Run analysis
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Parse JSON response using robust parser
        analysis = extract_json_from_response(response)
        
        if analysis and not analysis.get('parse_failed'):
            
            self.logger.info(
                "Issue analysis complete",
                suggested_problems=len(analysis.get('suggested_problems', []))
            )
            
            # Send A2A response
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="analyzer",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "analysis_type": "issue_patterns",
                        "summary": {
                            "total_issues": sum(c.get('count', 0) for c in analysis.get('categories', {}).values() if isinstance(c, dict)),
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
                "categories": {"bugs": {"count": 0, "examples": []}, "features": {"count": 0, "examples": []}, "enhancements": {"count": 0, "examples": []}},
                "priority_issues": [],
                "problem_patterns": [],
                "suggested_problems": [],
                "error": error_msg
            }


# Create singleton instance
issue_analyzer = IssueAnalyzerAgent()
