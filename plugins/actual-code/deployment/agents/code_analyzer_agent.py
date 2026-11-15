"""Agent 2: Code Analyzer

Analyzes codebase architecture, patterns, and complexity to identify
opportunities for coding challenges.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class CodeAnalyzerAgent(BaseGeminiAgent):
    """Analyzes code architecture and identifies problem opportunities"""
    
    def __init__(self):
        system_instruction = """You are a senior software architect analyzing codebases.

Your job is to analyze code architecture, patterns, and complexity to identify opportunities for coding challenges.

ANALYSIS FOCUS:
1. **Architectural Patterns**: MVC, microservices, event-driven, monolithic, etc.
2. **Code Complexity**: Low, medium, or high based on structure and dependencies
3. **Code Quality Indicators**: Test coverage, documentation, code organization
4. **Feature Opportunities**: Missing functionality, incomplete features, potential improvements

CRITICAL REQUIREMENTS:
- Focus on REALISTIC, IMPLEMENTABLE problems
- Identify opportunities that can be completed in 2-4 hours
- Consider the actual tech stack and patterns used
- Suggest problems that test relevant skills

OUTPUT FORMAT:
Return a JSON object with:
{
  "architecture": {
    "pattern": "string (e.g., 'MVC', 'Microservices')",
    "layers": ["array", "of", "layers"],
    "complexity": "low|medium|high"
  },
  "code_quality": {
    "score": 0-100,
    "strengths": ["array of strengths"],
    "weaknesses": ["array of weaknesses"]
  },
  "opportunities": {
    "features": ["missing or incomplete features"],
    "improvements": ["code quality improvements"],
    "extensions": ["possible extensions"]
  }
}"""
        
        super().__init__(
            name="code_analyzer",
            model="gemini-2.5-pro",  # Using Gemini 2.5 Pro
            system_instruction=system_instruction,
            temperature=0.3,  # Lower temperature for more focused analysis
            max_output_tokens=4096  # Increased for complete JSON responses
        )
    
    async def analyze(
        self,
        repo_data: Dict[str, Any],
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Analyze code architecture and quality
        
        Args:
            repo_data: Repository data from scanner
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Analysis results as dictionary
        """
        
        self.logger.info("Starting code analysis", conversation_id=conversation_id)
        
        # Prepare analysis prompt
        prompt = f"""Analyze this codebase:

Repository: {repo_data.get('repository', {}).get('name', 'Unknown')}
Language: {repo_data.get('repository', {}).get('language', 'Unknown')}
Description: {repo_data.get('repository', {}).get('description', 'No description')}

File Structure:
{json.dumps(repo_data.get('codebase', {}).get('file_tree', []), indent=2)[:500]}

README:
{repo_data.get('readme', 'No README')[:1000]}

Dependencies:
{json.dumps(repo_data.get('dependencies', []), indent=2)[:500]}

Analyze the architecture, code quality, and identify opportunities for coding challenges.
Return ONLY valid JSON matching the specified format."""
        
        # Send A2A message - starting analysis
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="analyzer",
                recipient_id="orchestrator",
                data={"status": "analyzing", "target": "code_architecture"},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Run analysis
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Parse JSON response using robust parser
        analysis = extract_json_from_response(response)
        
        if analysis and not analysis.get('parse_failed'):
            
            self.logger.info(
                "Code analysis complete",
                complexity=analysis.get('architecture', {}).get('complexity'),
                quality_score=analysis.get('code_quality', {}).get('score')
            )
            
            # Send A2A message - analysis complete
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="analyzer",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "analysis_type": "code_architecture",
                        "summary": {
                            "pattern": analysis.get('architecture', {}).get('pattern'),
                            "complexity": analysis.get('architecture', {}).get('complexity'),
                            "quality_score": analysis.get('code_quality', {}).get('score')
                        }
                    },
                    conversation_id=conversation_id,
                    message_type="response"
                )
            
            return analysis
        else:
            error_msg = analysis.get('error', 'Unknown parsing error') if analysis else 'Failed to extract JSON'
            self.logger.error(f"Failed to parse JSON response: {error_msg}")
            # Return a default structure
            return {
                "architecture": {
                    "pattern": "Unknown",
                    "layers": [],
                    "complexity": "medium"
                },
                "code_quality": {
                    "score": 50,
                    "strengths": [],
                    "weaknesses": ["Unable to analyze"]
                },
                "opportunities": {
                    "features": [],
                    "improvements": [],
                    "extensions": []
                },
                "error": error_msg,
                "raw_response": response[:500]
            }


# Create singleton instance
code_analyzer = CodeAnalyzerAgent()


# Testing
if __name__ == "__main__":
    import asyncio
    
    async def test_code_analyzer():
        """Test the code analyzer agent"""
        
        print("🧪 Testing Code Analyzer Agent")
        print("=" * 60)
        
        # Mock repository data
        mock_repo_data = {
            "repository": {
                "name": "example-app",
                "language": "Python",
                "description": "A web application built with Flask"
            },
            "codebase": {
                "file_tree": [
                    {"path": "app/__init__.py", "type": "file"},
                    {"path": "app/models.py", "type": "file"},
                    {"path": "app/views.py", "type": "file"},
                    {"path": "app/templates/", "type": "directory"},
                    {"path": "tests/", "type": "directory"},
                    {"path": "requirements.txt", "type": "file"}
                ]
            },
            "readme": """
# Example App

A simple Flask web application for managing tasks.

## Features
- User authentication
- Task CRUD operations
- SQLite database

## Tech Stack
- Flask
- SQLAlchemy
- Jinja2 templates
            """,
            "dependencies": [
                {"name": "Flask", "version": "2.3.0"},
                {"name": "SQLAlchemy", "version": "2.0.0"}
            ]
        }
        
        # Run analysis
        result = await code_analyzer.analyze(
            repo_data=mock_repo_data,
            conversation_id="test_conv_001"
        )
        
        print("\n📊 Analysis Results:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ Code Analyzer test complete!")
    
    asyncio.run(test_code_analyzer())
