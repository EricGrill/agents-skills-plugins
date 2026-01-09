"""Agent 5: Dependency Analyzer

Analyzes dependencies, tech stack, and framework usage to identify
integration opportunities and technical challenges.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class DependencyAnalyzerAgent(BaseGeminiAgent):
    """Analyzes dependencies and tech stack"""
    
    def __init__(self):
        system_instruction = """You are a technical architect specializing in dependency and technology stack analysis.

Your job is to analyze dependencies, frameworks, and libraries to identify integration opportunities and technical challenges.

ANALYSIS FOCUS:
1. **Tech Stack**: Frameworks, libraries, tools, runtime environment
2. **Dependency Health**: Outdated packages, vulnerabilities, maintenance status
3. **Integration Opportunities**: Underutilized libraries, missing integrations, potential improvements

CRITICAL REQUIREMENTS:
- Identify realistic integration problems suitable for coding challenges
- Focus on common patterns and widely-used technologies
- Suggest problems that test understanding of the tech stack

OUTPUT FORMAT:
Return a JSON object with:
{
  "tech_stack": {
    "frameworks": ["array of frameworks"],
    "libraries": ["array of key libraries"],
    "runtime": "runtime environment",
    "build_tools": ["array of build tools"]
  },
  "dependency_health": {
    "outdated": ["list of outdated dependencies"],
    "vulnerable": ["list of vulnerable dependencies"],
    "well_maintained": ["list of well-maintained dependencies"]
  },
  "integration_opportunities": [
    {
      "opportunity": "opportunity description",
      "technologies": ["technologies involved"],
      "difficulty": "easy|medium|hard",
      "rationale": "why this would be a good problem"
    }
  ]
}"""
        
        super().__init__(
            name="dependency_analyzer",
            model="gemini-2.5-flash",
            system_instruction=system_instruction,
            temperature=0.3,
            max_output_tokens=4096
        )
    
    async def analyze(
        self,
        repo_data: Dict[str, Any],
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Analyze dependencies and tech stack
        
        Args:
            repo_data: Repository data including dependencies
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Dependency analysis results as dictionary
        """
        
        self.logger.info("Starting dependency analysis", conversation_id=conversation_id)
        
        # Prepare analysis prompt
        deps_summary = json.dumps(repo_data.get('dependencies', []), indent=2)[:2000]
        
        prompt = f"""Analyze this tech stack and dependencies:

Repository: {repo_data.get('repository', {}).get('name', 'Unknown')}
Primary Language: {repo_data.get('repository', {}).get('language', 'Unknown')}

Dependencies:
{deps_summary}

README (for context):
{repo_data.get('readme', 'No README')[:500]}

Analyze the technology stack, dependency health, and identify integration opportunities for coding challenges.
Return ONLY valid JSON matching the specified format."""
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="analyzer",
                recipient_id="orchestrator",
                data={"status": "analyzing", "target": "dependencies"},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Run analysis
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Parse JSON response using robust parser
        analysis = extract_json_from_response(response)
        
        if analysis and not analysis.get('parse_failed'):
            
            self.logger.info(
                "Dependency analysis complete",
                frameworks=len(analysis.get('tech_stack', {}).get('frameworks', []))
            )
            
            # Send A2A response
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="analyzer",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "analysis_type": "dependencies",
                        "summary": {
                            "frameworks": analysis.get('tech_stack', {}).get('frameworks', []),
                            "opportunities": len(analysis.get('integration_opportunities', []))
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
                "tech_stack": {"frameworks": [], "libraries": [], "runtime": "Unknown", "build_tools": []},
                "dependency_health": {"outdated": [], "vulnerable": [], "well_maintained": []},
                "integration_opportunities": [],
                "error": error_msg
            }


# Create singleton instance
dependency_analyzer = DependencyAnalyzerAgent()
