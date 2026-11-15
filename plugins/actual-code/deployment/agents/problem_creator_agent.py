"""Agent 6: Problem Creator

Creates detailed, implementable coding problems based on repository analysis.
This is the core agent that generates the actual assessment.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.json_parser import extract_json_from_response


class ProblemCreatorAgent(BaseGeminiAgent):
    """Generates coding assessment problems"""
    
    def __init__(self):
        system_instruction = """You are an expert technical interviewer and assessment creator.

Your job is to create REALISTIC, IMPLEMENTABLE coding assessments that test relevant skills for the given codebase.

CRITICAL REQUIREMENTS:
1. Problem must be completable in 2-4 hours
2. Must align with repository's technology and patterns
3. Must be self-contained (no private repo access needed)
4. Starter code provides structure, NOT the solution
5. Requirements must be testable and objective
6. Must use the actual tech stack from the repository

PROBLEM STRUCTURE:
- Clear business context that makes the problem realistic
- Specific, measurable requirements
- Objective acceptance criteria
- Helpful starter code
- Appropriate hints (without giving away the solution)
- Realistic difficulty estimate

CRITICAL JSON FORMATTING:
- Return ONLY valid, parseable JSON (no markdown, no extra text)
- Use \\n for newlines within strings, NOT actual newlines
- Keep ALL text fields concise (max 150 words per field)
- Use single-line strings where possible
- Ensure all strings are properly escaped
- Close all brackets and braces
- Do NOT include multi-line code in starter_code content

OUTPUT FORMAT:
Return a JSON object with:
{
  "title": "Clear, specific problem title",
  "description": "Detailed problem description with business context",
  "business_context": "Why this problem matters in a real application",
  "requirements": [
    "Specific requirement 1",
    "Specific requirement 2",
    ...
  ],
  "acceptance_criteria": [
    "Testable criterion 1",
    "Testable criterion 2",
    ...
  ],
  "starter_code": [
    {
      "filename": "file.py",
      "content": "// starter code",
      "description": "what this file does"
    }
  ],
  "hints": [
    "Helpful hint 1 (without solution)",
    "Helpful hint 2",
    ...
  ],
  "estimated_time": 180,
  "difficulty": "easy|medium|hard|expert",
  "tech_stack": ["technology", "stack", "used"],
  "evaluation_rubric": [
    {
      "criterion": "what to evaluate",
      "points": 10,
      "description": "how to evaluate it"
    }
  ]
}"""
        
        super().__init__(
            name="problem_creator",
            model="gemini-2.5-flash",  # Using Gemini 2.5 flash
            system_instruction=system_instruction,
            temperature=0.7,  # Higher temperature for creativity
            max_output_tokens=8192  # Increased for complete problem generation
        )
    
    async def create_problem(
        self,
        repository_report: Dict[str, Any],
        difficulty: str = "medium",
        problem_type: str = "feature",
        focus_area: str = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Create a coding problem
        
        Args:
            repository_report: Complete analysis from all analyzer agents
            difficulty: Problem difficulty (easy, medium, hard, expert)
            problem_type: Type of problem (feature, bug-fix, refactor, optimization)
            focus_area: Optional specific area to focus on
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Generated problem as dictionary
        """
        
        self.logger.info(
            "Creating coding problem",
            difficulty=difficulty,
            problem_type=problem_type,
            conversation_id=conversation_id
        )
        
        # Check if this is a refinement request
        improvement_context = repository_report.get('improvement_context')
        
        if improvement_context:
            # REFINEMENT MODE: Improve existing problem with MINIMAL changes
            original_problem = improvement_context.get('original_problem', {})
            validation_feedback = improvement_context.get('validation_feedback', {})
            issues = validation_feedback.get('issues', [])
            suggestions = validation_feedback.get('suggestions', [])
            
            self.logger.info("Refinement mode: improving existing problem with minimal changes")
            
            prompt = f"""TASK: Refine this coding problem based on QA feedback. Make ONLY MINIMAL improvements.

ORIGINAL PROBLEM (Keep this as the base):
{json.dumps(original_problem, indent=2)}

QA FEEDBACK:
Score: {validation_feedback.get('overall_score', 0)}/100

Issues: {json.dumps(issues, indent=2) if issues else 'None - problem is generally good'}

Suggestions: {json.dumps(suggestions, indent=2) if suggestions else 'None - minor polish only'}

Strengths to Preserve: {json.dumps(validation_feedback.get('feedback', {}).get('strengths', []), indent=2)}

REFINEMENT RULES:
1. Keep EXACT same title, description, and tech stack
2. Only fix critical issues if any
3. Make small clarifications to requirements/criteria if needed
4. Preserve 90% of the original problem
5. If feedback is empty/minimal, return nearly identical problem

Return the refined problem as JSON."""
        else:
            # CREATION MODE: Create brand new problem
            repo_profile = repository_report.get('repository_profile', {})
            tech_stack = repository_report.get('dependency_analysis', {}).get('tech_stack', {})
            
            prompt = f"""Create a {difficulty} {problem_type} coding assessment for THIS SPECIFIC REPOSITORY:

CRITICAL: This problem MUST be about THIS repository, not a generic problem!

REPOSITORY DETAILS:
Name: {repo_profile.get('name', 'Unknown')}
Description: {repo_profile.get('description', 'N/A')[:200]}
Primary Language: {repo_profile.get('language', 'Unknown')}

README Summary:
{repository_report.get('readme_summary', 'N/A')[:400]}

TECH STACK (USE THESE EXACT TECHNOLOGIES):
Frameworks: {json.dumps(tech_stack.get('frameworks', []))}
Libraries: {json.dumps(tech_stack.get('libraries', [])[:8])}
Runtime: {tech_stack.get('runtime', 'Unknown')}

ARCHITECTURE:
Pattern: {repository_report.get('code_analysis', {}).get('architecture', {}).get('pattern', 'Unknown')}
Complexity: {repository_report.get('code_analysis', {}).get('architecture', {}).get('complexity', 'unknown')}

CODE QUALITY (Current State):
Score: {repository_report.get('code_analysis', {}).get('code_quality', {}).get('score', 0)}/100
Weaknesses: {json.dumps(repository_report.get('code_analysis', {}).get('code_quality', {}).get('weaknesses', [])[:3])}

IMPROVEMENT OPPORTUNITIES:
{json.dumps(repository_report.get('opportunities', {}).get('features', [])[:3], indent=2)}

REQUIREMENTS:
1. Problem MUST use the repository's actual tech stack: {', '.join(tech_stack.get('frameworks', []) + tech_stack.get('libraries', [])[:5])}
2. Problem MUST address weaknesses or opportunities identified above
3. Problem MUST be implementable within {focus_area or f'{240} minutes'}
4. NO generic problems (no To-Do apps, no unrelated topics)
5. Use repository name "{repo_profile.get('name', 'Unknown')}" as context

Difficulty: {difficulty}
Problem Type: {problem_type}

Return ONLY valid JSON matching the specified format."""
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="creator",
                recipient_id="orchestrator",
                data={"status": "creating", "difficulty": difficulty, "type": problem_type},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Generate problem
        response = await self.run(prompt, conversation_id=conversation_id)
        
        # Parse JSON response using robust parser
        problem = extract_json_from_response(response)
        
        if problem and not problem.get('parse_failed'):
            
            self.logger.info(
                "Problem created",
                title=problem.get('title', 'Unknown'),
                difficulty=problem.get('difficulty')
            )
            
            # Send A2A response
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="creator",
                    recipient_id="qa_validator",
                    data={
                        "status": "completed",
                        "problem": {
                            "title": problem.get('title'),
                            "difficulty": problem.get('difficulty'),
                            "estimated_time": problem.get('estimated_time')
                        }
                    },
                    conversation_id=conversation_id,
                    message_type="request"
                )
            
            return problem
        else:
            error_msg = problem.get('error', 'Unknown parsing error') if problem else 'Failed to extract JSON'
            self.logger.error(f"Failed to parse JSON response: {error_msg}")
            return {
                "title": "Error Creating Problem",
                "description": "Failed to generate valid problem",
                "error": error_msg,
                "raw_response": response[:1000]
            }


# Create singleton instance
problem_creator = ProblemCreatorAgent()
