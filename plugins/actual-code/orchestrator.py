"""
Multi-Agent Orchestrator

Coordinates all 7 agents through a 3-loop analysis pattern to generate
high-quality coding assessments from GitHub repositories.

Flow:
1. Scanner Agent retrieves repository data
2. 3-Loop Analysis (Agents 2-5):
   - Loop 1: Independent analysis
   - Loop 2: Cross-validation with other agents' results
   - Loop 3: Consensus building
3. Problem Creator generates assessment
4. QA Validator validates (iterate up to 2x if score < 85)
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import all agents
from agents.scanner_agent import scanner
from agents.code_analyzer_agent import code_analyzer
from agents.pr_analyzer_agent import pr_analyzer
from agents.issue_analyzer_agent import issue_analyzer
from agents.dependency_analyzer_agent import dependency_analyzer
from agents.problem_creator_agent import problem_creator
from agents.qa_validator_agent import qa_validator

# Import utilities
from utils.a2a_protocol import a2a_protocol
from utils.monitoring import AgentLogger, PerformanceMonitor


class AssessmentOrchestrator:
    """Orchestrates the multi-agent system for assessment generation"""
    
    def __init__(self):
        self.logger = AgentLogger("orchestrator")
        self.performance = PerformanceMonitor()
        self.conversation_id = f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def generate_assessment(
        self,
        github_repo_url: str,
        difficulty: str = "medium",
        time_limit: int = 240,
        problem_type: str = "feature",
        repo_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete coding assessment from a GitHub repository
        
        Args:
            github_repo_url: GitHub repository URL
            difficulty: easy, medium, hard, expert
            time_limit: Time limit in minutes
            problem_type: feature, bug-fix, refactor, optimization
            
        Returns:
            Complete assessment with problem, validation, and metadata
        """
        
        self.performance.start_timer("total")
        
        self._print_header()
        
        try:
            # Step 1: Scan Repository (use pre-fetched data if available)
            if repo_data is None:
                repo_data = await self._scan_repository(github_repo_url)
            else:
                print(f"📦 Using pre-fetched repository data")
            
            # Step 2-5: Multi-Agent Analysis (Single Pass - Faster!)
            analysis_report = await self._run_single_analysis(repo_data)
            
            # Step 6: Create Problem
            problem = await self._create_problem(
                analysis_report,
                difficulty,
                time_limit,
                problem_type
            )
            
            # Step 7: Validate & Improve (Single Pass)
            final_problem, validation = await self._validate_and_improve(problem, analysis_report)
            
            # Generate final result
            result = self._compile_final_result(
                repo_data,
                analysis_report,
                final_problem,
                validation
            )
            
            self.performance.end_timer("total")
            self._print_summary(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}")
            raise
    
    async def _scan_repository(self, github_repo_url: str) -> Dict[str, Any]:
        """Step 1: Retrieve repository data"""
        
        self._print_section("STEP 1: REPOSITORY SCANNING", "🔍")
        
        print(f"\n📥 INPUT:")
        print(f"   Repository: {github_repo_url}")
        
        self.performance.start_timer("scan")
        
        # Use scanner agent
        repo_data = await scanner.scan_repository(
            repo_url=github_repo_url,
            conversation_id=self.conversation_id
        )
        
        self.performance.end_timer("scan")
        
        print(f"\n📤 OUTPUT:")
        print(f"   ✅ Files scanned: {repo_data.get('codebase', {}).get('total_files', 0)}")
        print(f"   ✅ PRs retrieved: {len(repo_data.get('pull_requests', []))}")
        print(f"   ✅ Issues retrieved: {len(repo_data.get('issues', []))}")
        print(f"   ✅ Language: {repo_data.get('repository', {}).get('language', 'Unknown')}")
        print(f"   ⏱️  Time: {self.performance.get_duration('scan'):.2f}s")
        
        return repo_data
    
    async def _run_single_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2-5: Single-pass multi-agent analysis (NO LOOPS for speed)"""
        
        self._print_section("STEP 2-5: MULTI-AGENT ANALYSIS (SINGLE PASS)", "🔄")
        
        self.performance.start_timer("analysis")
        
        print(f"\n⚙️  Running 4 analysis agents in parallel...")
        
        # Run all analyzers ONCE in parallel
        tasks = [
            self._run_code_analyzer(repo_data),
            self._run_pr_analyzer(repo_data),
            self._run_issue_analyzer(repo_data),
            self._run_dependency_analyzer(repo_data)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Store results
        analysis_data = {
            "code_analysis": results[0],
            "pr_analysis": results[1],
            "issue_analysis": results[2],
            "dependency_analysis": results[3],
            "timestamp": datetime.now().isoformat()
        }
        
        # Synthesize final report
        print(f"\n{'='*80}")
        print("🔨 Synthesizing analysis report...")
        print(f"{'='*80}")
        
        final_report = self._synthesize_single_report(analysis_data, repo_data)
        
        self.performance.end_timer("analysis")
        
        print(f"\n✅ Analysis complete!")
        print(f"   Total analysis time: {self.performance.get_duration('analysis'):.2f}s")
        print(f"   Suggested problems: {len(final_report.get('ranked_suggestions', []))}")
        
        return final_report
    
    async def _run_code_analyzer(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Code Analyzer agent with real-time logging"""
        
        print(f"\n  🤖 Agent 2: Code Analyzer...")
        
        # Show actual input data
        print(f"     📥 INPUT DATA:")
        print(f"        Repository: {repo_data.get('repository', {}).get('name', 'N/A')}")
        print(f"        Language: {repo_data.get('repository', {}).get('language', 'N/A')}")
        print(f"        Files: {repo_data.get('codebase', {}).get('total_files', 0)}")
        print(f"        README: {len(repo_data.get('readme', ''))} chars")
        
        result = await code_analyzer.analyze(
            repo_data=repo_data,
            conversation_id=self.conversation_id
        )
        
        # Show actual output data
        print(f"     📤 OUTPUT DATA:")
        print(json.dumps(result, indent=8)[:1000] + "..." if len(json.dumps(result)) > 1000 else json.dumps(result, indent=8))
        
        return result
    
    async def _run_pr_analyzer(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run PR Analyzer agent"""
        
        print(f"\n  🤖 Agent 3: PR Analyzer...")
        
        prs = repo_data.get('pull_requests', [])
        print(f"     📥 INPUT DATA:")
        print(f"        Pull Requests: {len(prs)}")
        if prs:
            for i, pr in enumerate(prs[:3], 1):
                print(f"          {i}. {pr.get('title', 'N/A')[:60]}")
        
        result = await pr_analyzer.analyze(
            repo_data=repo_data,
            conversation_id=self.conversation_id
        )
        
        # Show actual output data
        print(f"     📤 OUTPUT DATA:")
        print(json.dumps(result, indent=8)[:1000] + "..." if len(json.dumps(result)) > 1000 else json.dumps(result, indent=8))
        
        return result
    
    async def _run_issue_analyzer(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Issue Analyzer agent"""
        
        print(f"\n  🤖 Agent 4: Issue Analyzer...")
        
        issues = repo_data.get('issues', [])
        print(f"     📥 INPUT DATA:")
        print(f"        Issues: {len(issues)}")
        if issues:
            for i, issue in enumerate(issues[:3], 1):
                print(f"          {i}. {issue.get('title', 'N/A')[:60]}")
        
        result = await issue_analyzer.analyze(
            repo_data=repo_data,
            conversation_id=self.conversation_id
        )
        
        # Show actual output data
        print(f"     📤 OUTPUT DATA:")
        print(json.dumps(result, indent=8)[:1000] + "..." if len(json.dumps(result)) > 1000 else json.dumps(result, indent=8))
        
        return result
    
    async def _run_dependency_analyzer(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Dependency Analyzer agent"""
        
        print(f"\n  🤖 Agent 5: Dependency Analyzer...")
        
        deps = repo_data.get('dependencies', [])
        print(f"     📥 INPUT DATA:")
        print(f"        Dependency Files: {len(deps)}")
        if deps:
            for i, dep in enumerate(deps[:3], 1):
                dep_file = dep.get('file', 'N/A')
                content_len = len(dep.get('content', ''))
                print(f"          {i}. {dep_file} ({content_len} chars)")
        
        result = await dependency_analyzer.analyze(
            repo_data=repo_data,
            conversation_id=self.conversation_id
        )
        
        # Show actual output data
        print(f"     📤 OUTPUT DATA:")
        print(json.dumps(result, indent=8)[:1000] + "..." if len(json.dumps(result)) > 1000 else json.dumps(result, indent=8))
        
        return result
    
    def _synthesize_single_report(self, analysis_data: Dict[str, Any], repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final report from single-pass analysis"""
        
        # Collect all suggestions
        all_suggestions = []
        all_suggestions.extend(analysis_data['pr_analysis'].get('suggested_problems', []))
        all_suggestions.extend(analysis_data['issue_analysis'].get('suggested_problems', []))
        
        # Rank suggestions
        ranked_suggestions = self._rank_suggestions(all_suggestions)
        
        return {
            "repository_profile": {
                "name": repo_data.get('repository', {}).get('name', 'Unknown'),
                "description": repo_data.get('repository', {}).get('description', ''),
                "language": repo_data.get('repository', {}).get('language', 'Unknown'),
                "architecture": analysis_data['code_analysis'].get('architecture', {}),
                "quality": analysis_data['code_analysis'].get('code_quality', {}),
                "tech_stack": analysis_data['dependency_analysis'].get('tech_stack', {}),
                "development_patterns": analysis_data['pr_analysis'].get('patterns', {}),
                "issue_patterns": analysis_data['issue_analysis'].get('categories', {})
            },
            "code_analysis": analysis_data['code_analysis'],
            "pr_analysis": analysis_data['pr_analysis'],
            "issue_analysis": analysis_data['issue_analysis'],
            "dependency_analysis": analysis_data['dependency_analysis'],
            "opportunities": analysis_data['code_analysis'].get('opportunities', {}),
            "ranked_suggestions": ranked_suggestions[:10],
            "readme_summary": repo_data.get('readme', '')[:500]
        }
    
    def _rank_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank problem suggestions by quality"""
        
        # Remove duplicates and score
        seen_titles = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            title = suggestion.get('title', '').lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_suggestions.append(suggestion)
        
        # Simple ranking (can be enhanced)
        return unique_suggestions
    
    
    async def _create_problem(
        self,
        analysis_report: Dict[str, Any],
        difficulty: str,
        time_limit: int,
        problem_type: str
    ) -> Dict[str, Any]:
        """Step 6: Create coding problem"""
        
        self._print_section("STEP 6: PROBLEM CREATION", "✨")
        
        print(f"\n📥 INPUT:")
        print(f"   Difficulty: {difficulty}")
        print(f"   Time Limit: {time_limit} minutes")
        print(f"   Problem Type: {problem_type}")
        print(f"   Suggestions Available: {len(analysis_report.get('ranked_suggestions', []))}")
        
        # Show top suggestions
        suggestions = analysis_report.get('ranked_suggestions', [])
        if suggestions:
            print(f"\n   Top Suggestions:")
            for i, sugg in enumerate(suggestions[:3], 1):
                print(f"     {i}. {sugg.get('title', 'N/A')[:70]}")
        
        print(f"\n⚙️  Generating problem...")
        
        self.performance.start_timer("creation")
        
        problem = await problem_creator.create_problem(
            repository_report=analysis_report,
            difficulty=difficulty,
            problem_type=problem_type,
            focus_area=f"{time_limit} minutes",
            conversation_id=self.conversation_id
        )
        
        self.performance.end_timer("creation")
        
        print(f"\n📤 OUTPUT:")
        print(f"   ✅ Title: {problem.get('title', 'N/A')}")
        description = problem.get('description', 'N/A')
        print(f"   ✅ Description: {description[:100]}..." if len(description) > 100 else f"   ✅ Description: {description}")
        print(f"   ✅ Requirements: {len(problem.get('requirements', []))}")
        for i, req in enumerate(problem.get('requirements', [])[:3], 1):
            print(f"       {i}. {req[:70]}...")
        print(f"   ✅ Acceptance Criteria: {len(problem.get('acceptance_criteria', []))}")
        print(f"   ✅ Starter Files: {len(problem.get('starter_code', []))}")
        if problem.get('starter_code'):
            for sf in problem['starter_code']:
                print(f"       - {sf.get('filename', 'N/A')}")
        print(f"   ⏱️  Time: {self.performance.get_duration('creation'):.2f}s")
        
        return problem
    
    async def _validate_and_improve(
        self,
        problem: Dict[str, Any],
        analysis_report: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Step 7: Single-pass validation with feedback-based improvement"""
        
        self._print_section("STEP 7: VALIDATION & IMPROVEMENT", "🎯")
        
        self.performance.start_timer("validation")
        
        # Single validation pass
        print(f"\n{'─'*80}")
        print(f"🔍 Validating Generated Problem")
        print(f"{'─'*80}")
        
        print(f"\n📥 INPUT: Validating problem '{problem.get('title', 'N/A')[:60]}'")
        
        is_approved, validation_result = await qa_validator.validate_problem(
            problem=problem,
            repository_report=analysis_report,
            conversation_id=self.conversation_id
        )
        
        score = validation_result.get('overall_score', 0)
        issues = len(validation_result.get('issues', []))
        suggestions = len(validation_result.get('suggestions', []))
        scores = validation_result.get('scores', {})
        
        print(f"\n📤 OUTPUT - Validation Result:")
        print(f"   Overall Score: {score}/100")
        print(f"   Status: {'✅ APPROVED' if is_approved else '⚠️ NEEDS REFINEMENT'}")
        print(f"\n   Dimension Scores:")
        print(f"     Feasibility:  {scores.get('feasibility', 0)}/100")
        print(f"     Quality:      {scores.get('quality', 0)}/100")
        print(f"     Technical:    {scores.get('technical', 0)}/100")
        print(f"     Educational:  {scores.get('educational', 0)}/100")
        print(f"\n   Issues Found: {issues}")
        if issues > 0:
            for i, issue in enumerate(validation_result.get('issues', [])[:3], 1):
                print(f"     {i}. {issue[:100]}...")
        print(f"   Suggestions: {suggestions}")
        if suggestions > 0:
            for i, sugg in enumerate(validation_result.get('suggestions', [])[:3], 1):
                print(f"     {i}. {sugg[:100]}...")
        
        # Always improve based on feedback (even if approved)
        print(f"\n🔧 Sending feedback to Problem Creator for refinement...")
        
        improvement_context = {
            "original_problem": problem,
            "validation_feedback": validation_result,
            "improvement_instructions": self._create_improvement_instructions(validation_result),
            "target_score": 100,
            "current_score": score
        }
        
        # Get improved problem from Problem Creator
        improved_problem = await problem_creator.create_problem(
            repository_report={
                **analysis_report,
                "improvement_context": improvement_context
            },
            difficulty=problem.get('difficulty', 'medium'),
            problem_type="improvement",
            focus_area=f"Refined version incorporating QA feedback - {problem.get('estimated_time', 240)} minutes",
            conversation_id=self.conversation_id
        )
        
        self.performance.end_timer("validation")
        
        print(f"\n✅ Problem refined based on QA feedback")
        print(f"   Original title: {problem.get('title', 'N/A')}")
        print(f"   Refined title: {improved_problem.get('title', 'N/A')}")
        print(f"⏱️  Total validation & improvement time: {self.performance.get_duration('validation'):.2f}s")
        
        # Return improved problem with original validation
        return improved_problem, validation_result
    
    def _create_improvement_instructions(
        self,
        validation: Dict[str, Any]
    ) -> str:
        """Create detailed improvement instructions from validation feedback"""
        
        issues = validation.get('issues', [])
        suggestions = validation.get('suggestions', [])
        feedback = validation.get('feedback', {})
        
        instructions = "REFINEMENT INSTRUCTIONS:\n\n"
        
        instructions += "Based on QA validation, refine the problem by addressing:\n\n"
        
        if issues:
            instructions += "CRITICAL ISSUES TO FIX:\n"
            for i, issue in enumerate(issues, 1):
                instructions += f"{i}. {issue}\n"
            instructions += "\n"
        
        if suggestions:
            instructions += "IMPROVEMENTS TO IMPLEMENT:\n"
            for i, suggestion in enumerate(suggestions, 1):
                instructions += f"{i}. {suggestion}\n"
            instructions += "\n"
        
        if feedback.get('weaknesses'):
            instructions += "WEAKNESSES TO ADDRESS:\n"
            for i, weakness in enumerate(feedback['weaknesses'], 1):
                instructions += f"{i}. {weakness}\n"
            instructions += "\n"
        
        instructions += "MAINTAIN STRENGTHS:\n"
        for i, strength in enumerate(feedback.get('strengths', [])[:3], 1):
            instructions += f"{i}. {strength}\n"
        
        instructions += "\nIMPORTANT: Keep the same difficulty level and problem type, but refine all aspects based on the feedback above."
        
        return instructions
    
    def _compile_final_result(
        self,
        repo_data: Dict[str, Any],
        analysis_report: Dict[str, Any],
        problem: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile final assessment result"""
        
        return {
            "success": True,
            "assessment": {
                "problem": problem,
                "validation": validation,
                "metadata": {
                "repository": repo_data.get('repository', {}),
                "analysis_summary": {
                    "suggestions_evaluated": len(analysis_report.get('ranked_suggestions', []))
                },
                    "performance": self.performance.get_all_metrics(),
                    "conversation_id": self.conversation_id,
                    "generated_at": datetime.now().isoformat()
                }
            },
            # Include full context for debugging/analysis
            "debug": {
                "repo_data": repo_data,
                "analysis_report": analysis_report
            }
        }
    
    def _print_header(self):
        """Print orchestrator header"""
        print("\n" + "="*80)
        print("🎭 ACTUALCODE ASSESSMENT GENERATOR")
        print("   Multi-Agent System with 3-Loop Analysis")
        print("="*80)
        print(f"Conversation ID: {self.conversation_id}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def _print_section(self, title: str, emoji: str):
        """Print section header"""
        print(f"\n\n{'='*80}")
        print(f"{emoji} {title}")
        print(f"{'='*80}")
    
    def _print_summary(self, result: Dict[str, Any]):
        """Print final summary"""
        
        print("\n\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        
        metrics = result['assessment']['metadata']['performance']
        problem = result['assessment']['problem']
        validation = result['assessment']['validation']
        
        print(f"\n⏱️  Performance:")
        print(f"   Total Time: {metrics.get('total', {}).get('duration', 0):.2f}s")
        print(f"   - Scanning: {metrics.get('scan', {}).get('duration', 0):.2f}s")
        print(f"   - Analysis: {metrics.get('analysis', {}).get('duration', 0):.2f}s")
        print(f"   - Creation: {metrics.get('creation', {}).get('duration', 0):.2f}s")
        print(f"   - Validation: {metrics.get('validation', {}).get('duration', 0):.2f}s")
        
        print(f"\n✅ Generated Assessment:")
        print(f"   Title: {problem.get('title', 'N/A')}")
        print(f"   Difficulty: {problem.get('difficulty', 'N/A')}")
        print(f"   Estimated Time: {problem.get('estimated_time', 0)} minutes")
        print(f"   Tech Stack: {', '.join(problem.get('tech_stack', []))}")
        
        print(f"\n🎯 Validation:")
        print(f"   Score: {validation.get('overall_score', 0)}/100")
        print(f"   Status: {'✅ APPROVED' if validation.get('is_approved', False) else '⚠️  NEEDS REVIEW'}")
        
        print(f"\n{'='*80}")
        print("✅ ASSESSMENT GENERATION COMPLETE!")
        print("="*80 + "\n")


# Create singleton instance
orchestrator = AssessmentOrchestrator()


# Main entry point for testing
async def main():
    """Test orchestrator with mock GitHub repo"""
    
    result = await orchestrator.generate_assessment(
        github_repo_url="https://github.com/example/test-repo",
        difficulty="medium",
        time_limit=240,
        problem_type="feature"
    )
    
    # Save result to file
    output_file = "orchestrator_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Full result saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
