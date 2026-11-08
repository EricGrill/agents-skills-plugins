"""Agent 7: QA/Validation Agent

Validates problem quality and ensures feasibility through rigorous scoring
across multiple dimensions.
"""

import json
from typing import Dict, Any, Tuple
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class QAValidatorAgent(BaseGeminiAgent):
    """Validates and improves coding assessment quality"""
    
    def __init__(self, quality_threshold: int = 85):
        system_instruction = """You are a strict quality assurance reviewer for coding assessments.

Your job is to validate assessments on 4 critical dimensions and provide detailed feedback.

VALIDATION DIMENSIONS:

1. **Feasibility (0-100)**:
   - Can be completed in stated time limit
   - All required context is provided
   - No private repository access needed
   - Starter code is functional
   - Dependencies are accessible

2. **Quality (0-100)**:
   - Problem statement is clear and unambiguous
   - Requirements are specific and testable
   - Acceptance criteria are objective
   - Hints are appropriate (helpful but not solutions)
   - Business context is realistic

3. **Technical (0-100)**:
   - Uses repository's actual tech stack
   - Code patterns match repository style
   - Complexity matches stated difficulty level
   - Code examples are correct
   - APIs/interfaces are well-defined

4. **Educational (0-100)**:
   - Tests relevant skills for the codebase
   - Difficulty is appropriate
   - Learning objectives are clear
   - Problem is non-trivial
   - Solution approach is not obvious

CRITICAL REQUIREMENTS:
- Be STRICT - only approve high-quality problems
- Provide SPECIFIC, ACTIONABLE feedback
- If overall score < 85, suggest concrete improvements
- Focus on what makes the problem realistic and valuable

OUTPUT FORMAT:
You MUST return ONLY a valid JSON object - NO markdown, NO code blocks, NO extra text.
Ensure ALL JSON is complete with proper closing brackets.
Return ONLY this JSON structure:
{
  "is_approved": true/false,
  "overall_score": 0-100,
  "scores": {
    "feasibility": 0-100,
    "quality": 0-100,
    "technical": 0-100,
    "educational": 0-100
  },
  "issues": [
    "Specific issue 1",
    "Specific issue 2",
    ...
  ],
  "suggestions": [
    "Specific improvement 1",
    "Specific improvement 2",
    ...
  ],
  "feedback": {
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "improvements": ["improvement 1", "improvement 2"]
  }
}"""
        
        super().__init__(
            name="qa_validator",
            model="gemini-2.5-flash",  # Using stable experimental model
            system_instruction=system_instruction,
            temperature=0.3,  # Slightly higher for better JSON generation
            max_output_tokens=8192  # Increased for complete validation output
        )
        
        self.quality_threshold = quality_threshold
    
    async def validate_problem(
        self,
        problem: Dict[str, Any],
        repository_report: Dict[str, Any],
        conversation_id: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate a coding problem
        
        Args:
            problem: Generated problem to validate
            repository_report: Repository analysis for context
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Tuple of (is_approved, validation_result)
        """
        
        self.logger.info(
            "Validating problem",
            title=problem.get('title', 'Unknown'),
            conversation_id=conversation_id
        )
        
        # Prepare validation prompt with full problem details
        problem_json = json.dumps(problem, indent=2)
        tech_stack = repository_report.get('repository_profile', {}).get('tech_stack', problem.get('tech_stack', []))
        
        prompt = f"""Validate this coding assessment and return ONLY valid JSON.

PROBLEM:
Title: {problem.get('title', 'N/A')}
Description: {problem.get('description', 'N/A')[:300]}...
Tech Stack: {problem.get('tech_stack', [])}
Difficulty: {problem.get('difficulty', 'N/A')}
Requirements: {len(problem.get('requirements', []))} requirements
Acceptance Criteria: {len(problem.get('acceptance_criteria', []))} criteria
Starter Code: {len(problem.get('starter_code', []))} files

EVALUATION DIMENSIONS:
1. Feasibility (0-100): Can it be completed in the time limit? Is context sufficient?
2. Quality (0-100): Are requirements clear and testable?
3. Technical (0-100): Does it match the repository's tech stack and patterns?
4. Educational (0-100): Is it realistic and valuable for assessing skills?

INSTRUCTIONS:
- Be FAIR in scoring - a well-structured problem should score 70-85
- Provide 2-3 specific issues if score < 85
- Provide 2-3 actionable suggestions for improvement
- Keep feedback concise (under 100 chars each)

OUTPUT FORMAT - Return ONLY this JSON structure (no markdown, no code blocks):
{{
  "is_approved": false,
  "overall_score": 75,
  "scores": {{
    "feasibility": 80,
    "quality": 75,
    "technical": 70,
    "educational": 75
  }},
  "issues": ["Issue 1", "Issue 2"],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "feedback": {{
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1"],
    "improvements": ["Improvement 1"]
  }}
}}

Now return ONLY the JSON for this problem:"""
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="validator",
                recipient_id="orchestrator",
                data={"status": "validating", "problem_title": problem.get('title')},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Run validation
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Log response for debugging
        self.logger.info(f"QA Validator response length: {len(response)} characters")
        
        # Parse JSON response using robust parser
        validation_result = extract_json_from_response(response)
        
        # Log parsing result
        if validation_result and validation_result.get('parse_failed'):
            self.logger.warning(f"JSON parsing had issues: {validation_result.get('error', 'Unknown')}")
            self.logger.warning(f"Raw response preview: {response[:500]}...")
        
        if validation_result and not validation_result.get('parse_failed'):
            
            is_approved = validation_result.get('overall_score', 0) >= self.quality_threshold
            validation_result['is_approved'] = is_approved
            
            self.logger.info(
                "Validation complete",
                approved=is_approved,
                overall_score=validation_result.get('overall_score')
            )
            
            # Send A2A response
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="validator",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "approved": is_approved,
                        "overall_score": validation_result.get('overall_score'),
                        "scores": validation_result.get('scores')
                    },
                    conversation_id=conversation_id,
                    message_type="response"
                )
            
            return is_approved, validation_result
        else:
            error_msg = validation_result.get('error', 'Unknown parsing error') if validation_result else 'Failed to extract JSON'
            self.logger.error(f"Failed to parse JSON response: {error_msg}")
            # Return a failing validation
            return False, {
                "is_approved": False,
                "overall_score": 0,
                "scores": {"feasibility": 0, "quality": 0, "technical": 0, "educational": 0},
                "issues": ["Failed to parse validation response"],
                "suggestions": [],
                "feedback": {"strengths": [], "weaknesses": ["Validation error"], "improvements": []},
                "error": error_msg
            }


# Create singleton instance
qa_validator = QAValidatorAgent(quality_threshold=85)
