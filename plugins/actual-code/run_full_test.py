"""
Complete Orchestrator Test with Real-Time Logging

This test runs the full multi-agent assessment generation pipeline,
showing all agent inputs and outputs as they happen in real-time.
"""

import asyncio
import json
import sys
from datetime import datetime
from orchestrator import orchestrator


def print_banner(text: str, char: str = "="):
    """Print a formatted banner"""
    print(f"\n{char * 80}")
    print(f"{text}")
    print(f"{char * 80}\n")


async def main():
    """Run the complete orchestrator test"""
    
    print("\n" + "🚀 " * 40)
    print("ACTUALCODE - MULTI-AGENT ASSESSMENT GENERATOR")
    print("Real-Time Agent Input/Output Monitoring")
    print("🚀 " * 40)
    
    # Test configuration
    test_repo = "https://github.com/example/ayurvedic-remedy"  # Mock URL
    config = {
        "github_repo_url": test_repo,
        "difficulty": "medium",
        "time_limit": 180,  # 3 hours
        "problem_type": "feature"
    }
    
    print_banner("TEST CONFIGURATION")
    print(f"Repository URL: {config['github_repo_url']}")
    print(f"Difficulty Level: {config['difficulty']}")
    print(f"Time Limit: {config['time_limit']} minutes")
    print(f"Problem Type: {config['problem_type']}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "─" * 80)
    print("The orchestrator will now:")
    print("  1. Scan the repository (mock data)")
    print("  2. Run 3 loops of multi-agent analysis")
    print("  3. Generate a coding problem")
    print("  4. Validate and improve the problem")
    print("─" * 80)
    
    input("\nPress ENTER to start the test...")
    
    try:
        # Run the orchestrator
        print_banner("STARTING ORCHESTRATOR", "=")
        
        result = await orchestrator.generate_assessment(
            github_repo_url=config['github_repo_url'],
            difficulty=config['difficulty'],
            time_limit=config['time_limit'],
            problem_type=config['problem_type']
        )
        
        # Save results
        output_file = f"assessment_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print_banner("TEST COMPLETED SUCCESSFULLY!", "=")
        
        # Display summary
        assessment = result.get('assessment', {})
        problem = assessment.get('problem', {})
        validation = assessment.get('validation', {})
        metadata = assessment.get('metadata', {})
        
        print("📊 FINAL RESULTS:")
        print("\n" + "─" * 80)
        print("GENERATED PROBLEM:")
        print("─" * 80)
        print(f"Title: {problem.get('title', 'N/A')}")
        print(f"Difficulty: {problem.get('difficulty', 'N/A')}")
        print(f"Estimated Time: {problem.get('estimated_time', 0)} minutes")
        print(f"Tech Stack: {', '.join(problem.get('tech_stack', []))}")
        
        print(f"\nDescription:")
        desc = problem.get('description', 'N/A')
        print(f"{desc[:200]}..." if len(desc) > 200 else desc)
        
        print(f"\nRequirements: {len(problem.get('requirements', []))}")
        for i, req in enumerate(problem.get('requirements', [])[:5], 1):
            print(f"  {i}. {req[:80]}...")
        
        print(f"\nAcceptance Criteria: {len(problem.get('acceptance_criteria', []))}")
        for i, ac in enumerate(problem.get('acceptance_criteria', [])[:5], 1):
            print(f"  {i}. {ac[:80]}...")
        
        print(f"\nStarter Code Files: {len(problem.get('starter_code', []))}")
        for sf in problem.get('starter_code', []):
            print(f"  - {sf.get('filename', 'N/A')}")
        
        print("\n" + "─" * 80)
        print("VALIDATION RESULTS:")
        print("─" * 80)
        print(f"Overall Score: {validation.get('overall_score', 0)}/100")
        print(f"Status: {'✅ APPROVED' if validation.get('is_approved', False) else '⚠️ NEEDS REVIEW'}")
        
        scores = validation.get('scores', {})
        print(f"\nDimension Scores:")
        print(f"  Feasibility:  {scores.get('feasibility', 0)}/100")
        print(f"  Quality:      {scores.get('quality', 0)}/100")
        print(f"  Technical:    {scores.get('technical', 0)}/100")
        print(f"  Educational:  {scores.get('educational', 0)}/100")
        
        issues = validation.get('issues', [])
        if issues:
            print(f"\nIssues Found: {len(issues)}")
            for i, issue in enumerate(issues[:3], 1):
                print(f"  {i}. {issue[:100]}...")
        
        suggestions = validation.get('suggestions', [])
        if suggestions:
            print(f"\nSuggestions: {len(suggestions)}")
            for i, sugg in enumerate(suggestions[:3], 1):
                print(f"  {i}. {sugg[:100]}...")
        
        print("\n" + "─" * 80)
        print("PERFORMANCE METRICS:")
        print("─" * 80)
        perf = metadata.get('performance', {})
        print(f"Total Time: {perf.get('total', {}).get('duration', 0):.2f}s")
        print(f"  - Scanning: {perf.get('scan', {}).get('duration', 0):.2f}s")
        print(f"  - Analysis: {perf.get('analysis', {}).get('duration', 0):.2f}s")
        print(f"  - Creation: {perf.get('creation', {}).get('duration', 0):.2f}s")
        print(f"  - Validation: {perf.get('validation', {}).get('duration', 0):.2f}s")
        
        print(f"\nAnalysis Summary:")
        analysis_summary = metadata.get('analysis_summary', {})
        print(f"  Confidence Score: {analysis_summary.get('confidence', 0):.1f}%")
        print(f"  Iterations: {analysis_summary.get('iterations', 0)}/3")
        print(f"  Suggestions Evaluated: {analysis_summary.get('suggestions_evaluated', 0)}")
        
        print("\n" + "─" * 80)
        print(f"💾 Full results saved to: {output_file}")
        print(f"   File size: {len(json.dumps(result)) / 1024:.2f} KB")
        print("─" * 80)
        
        print_banner("✅ ALL TESTS PASSED!", "=")
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print_banner("❌ TEST FAILED", "=")
        print(f"Error: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n" * 2)
    asyncio.run(main())
    print("\n" * 2)
