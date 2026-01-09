"""
ActualCode - Vertex AI Agent Engine Entry Point

This module serves as the entry point for the deployed multi-agent system
on Vertex AI Agent Engine Runtime.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import our modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from orchestrator import AssessmentOrchestrator


async def run_assessment(request):
    """
    Entry point for Vertex AI Agent Engine
    
    This function is called by Agent Engine Runtime when a request is received.
    It orchestrates the 7-agent system to generate a code assessment.
    
    Args:
        request (dict): Agent Engine request containing:
            - repo_url (str): GitHub repository URL
            - difficulty (str): easy/medium/hard/expert
            - problem_type (str): feature/bug-fix/refactor/optimization
            - time_limit (int): Time limit in minutes
            
    Returns:
        dict: Complete assessment with:
            - success (bool): Whether generation succeeded
            - assessment (dict): Generated problem and validation
            - metadata (dict): Processing info, A2A messages count, etc.
    """
    
    print(f"🚀 ActualCode Multi-Agent System - Vertex AI Agent Engine")
    print(f"📥 Received request: {request.get('repo_url')}")
    
    # Initialize orchestrator
    orchestrator = AssessmentOrchestrator()
    
    # Generate assessment using our 7-agent system
    result = await orchestrator.generate_assessment(
        github_repo_url=request.get('repo_url'),
        difficulty=request.get('difficulty', 'medium'),
        problem_type=request.get('problem_type', 'feature'),
        time_limit=request.get('time_limit', 180)
    )
    
    print(f"✅ Assessment generated successfully!")
    print(f"   Processing time: {result['metadata']['processing_time']:.2f}s")
    print(f"   A2A messages: {result['metadata'].get('a2a_messages', 0)}")
    
    return result


# For local testing and development
if __name__ == "__main__":
    # Test request
    test_request = {
        'repo_url': 'https://github.com/google-gemini/example-chat-app',
        'difficulty': 'medium',
        'problem_type': 'feature',
        'time_limit': 180
    }
    
    print("🧪 Running local test...")
    result = asyncio.run(run_assessment(test_request))
    
    if result.get('success'):
        print(f"\n✅ Test completed successfully!")
        print(f"   Title: {result['assessment']['problem']['title']}")
        print(f"   Quality Score: {result['assessment']['validation']['overall_score']}/100")
    else:
        print(f"\n❌ Test failed: {result.get('error')}")
