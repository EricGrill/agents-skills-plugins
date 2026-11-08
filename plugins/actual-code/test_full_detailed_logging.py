"""
Complete Agent Pipeline with FULL Detailed Logging

This test:
1. Increases token limits to prevent truncation
2. Logs EVERY agent input and output to a TXT file
3. Shows complete JSON data (no truncation)
4. Creates human-readable logs with all details
"""

import asyncio
import json
import sys
import os
from datetime import datetime


class DetailedLogger:
    """Comprehensive logger for all agent interactions"""
    
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'w', encoding='utf-8')
        self.log_count = 0
        
    def write(self, message):
        """Write to both console and file"""
        print(message)
        self.file.write(message + '\n')
        self.file.flush()
        
    def log_section(self, title, char='='):
        """Log a section header"""
        line = char * 100
        self.write(f"\n{line}")
        self.write(f"  {title}")
        self.write(f"{line}\n")
        
    def log_agent_input(self, agent_name, input_data):
        """Log complete agent input"""
        self.log_count += 1
        self.write(f"\n{'─'*100}")
        self.write(f"[{self.log_count}] AGENT INPUT: {agent_name}")
        self.write(f"{'─'*100}")
        self.write(json.dumps(input_data, indent=2))
        self.write(f"{'─'*100}\n")
        
    def log_agent_output(self, agent_name, output_data):
        """Log complete agent output"""
        self.write(f"\n{'─'*100}")
        self.write(f"[{self.log_count}] AGENT OUTPUT: {agent_name}")
        self.write(f"{'─'*100}")
        self.write(json.dumps(output_data, indent=2))
        self.write(f"{'─'*100}\n")
        
    def close(self):
        """Close the log file"""
        self.file.close()


async def run_full_detailed_test():
    """Run complete test with full detailed logging"""
    
    # Create detailed logger
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"FULL_AGENT_LOGS_{timestamp}.txt"
    logger = DetailedLogger(log_file)
    
    logger.log_section("ACTUALCODE - COMPLETE AGENT PIPELINE TEST WITH FULL LOGGING")
    logger.write(f"Started at: {datetime.now().isoformat()}")
    logger.write(f"Log file: {log_file}")
    
    # Load actual Test_Repo files
    logger.log_section("STEP 1: LOADING ACTUAL REPOSITORY FILES")
    
    test_repo_path = "/Users/muratcankoylan/ActualCode/Test_Repo/Ayurvedic-Remedy-main"
    file_contents = {}
    
    try:
        for filename in ["index.html", "app.js", "app.css", "README.md"]:
            filepath = os.path.join(test_repo_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_contents[filename] = f.read()
                logger.write(f"✅ Loaded {filename}: {len(file_contents[filename])} characters")
    except Exception as e:
        logger.write(f"⚠️  Error loading files: {e}")
        return
    
    # Import agents
    logger.log_section("STEP 2: INITIALIZING ALL AGENTS")
    
    from agents.code_analyzer_agent import code_analyzer  
    from agents.pr_analyzer_agent import pr_analyzer
    from agents.issue_analyzer_agent import issue_analyzer
    from agents.dependency_analyzer_agent import dependency_analyzer
    from agents.problem_creator_agent import problem_creator
    from agents.qa_validator_agent import qa_validator
    
    conversation_id = f"full_test_{timestamp}"
    logger.write(f"✅ All 6 agents initialized")
    logger.write(f"📋 Conversation ID: {conversation_id}")
    
    # Create comprehensive repository data with ACTUAL files
    logger.log_section("STEP 3: PREPARING REPOSITORY DATA WITH ACTUAL FILES")
    
    repo_data = {
        "repository": {
            "name": "Ayurvedic-Remedy",
            "description": "AI-powered Ayurvedic remedy generator using Google Gemini API",
            "language": "JavaScript",
            "url": "https://github.com/test/Ayurvedic-Remedy",
            "stars": 5,
            "tech_stack": "Vanilla JS, HTML5, CSS3, Google Gemini AI"
        },
        "codebase": {
            "files": file_contents,  # ACTUAL file contents
            "file_list": list(file_contents.keys()),
            "total_files": len(file_contents),
            "summary": {
                "index.html": f"{len(file_contents.get('index.html', ''))} chars - Main HTML with Gemini AI import",
                "app.js": f"{len(file_contents.get('app.js', ''))} chars - JavaScript with Gemini API integration",
                "app.css": f"{len(file_contents.get('app.css', ''))} chars - Styling with animations",
                "README.md": f"{len(file_contents.get('README.md', ''))} chars - Project description"
            }
        },
        "pullRequests": [
            {
                "title": "Add error handling for API failures",
                "description": "Handle Gemini API errors gracefully with user-friendly messages",
                "files": ["app.js"],
                "code_reference": "Around line 47 in generateText function"
            },
            {
                "title": "Optimize typing animation",
                "description": "Improve performance of character-by-character display",
                "files": ["app.js"],
                "current_implementation": "setTimeout with 28ms delay"
            },
            {
                "title": "Add loading indicator",
                "description": "Show spinner while waiting for AI response",
                "files": ["index.html", "app.css", "app.js"]
            }
        ],
        "issues": [
            {
                "title": "Add remedy history with localStorage",
                "description": "Save past searches for user reference",
                "priority": "high",
                "technical_details": "Use localStorage.setItem/getItem with JSON.stringify"
            },
            {
                "title": "Typing animation stutters on mobile",
                "description": "Performance issue on slower devices",
                "priority": "medium",
                "affected_code": "typeAnswer() function with setTimeout"
            },
            {
                "title": "Multilingual support (Hindi/Sanskrit)",
                "description": "Support Indian languages in remedy responses",
                "priority": "low",
                "implementation": "Add language parameter to Gemini prompt"
            }
        ],
        "dependencies": [
            {
                "name": "@google/generative-ai",
                "version": "latest",
                "usage": "Core AI functionality via Gemini Pro model"
            },
            {
                "name": "dotenv",
                "version": "16.0.0",
                "usage": "Environment variable management for API keys"
            }
        ]
    }
    
    logger.write(f"✅ Repository data prepared with {len(file_contents)} actual files")
    logger.log_agent_input("REPOSITORY_DATA", repo_data)
    
    try:
        # =====================================================================
        # AGENT 2: CODE ANALYZER
        # =====================================================================
        logger.log_section("AGENT 2: CODE ANALYZER - ANALYZING ACTUAL CODE")
        
        logger.write("📥 Sending repository data to Code Analyzer...")
        code_analysis_input = repo_data.copy()
        logger.log_agent_input("Code Analyzer", code_analysis_input)
        
        logger.write("⚙️  Executing Code Analyzer Agent...")
        code_analysis = await code_analyzer.analyze(
            repo_data=code_analysis_input,
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("Code Analyzer", code_analysis)
        logger.write(f"✅ Code analysis complete")
        logger.write(f"   Architecture: {code_analysis.get('architecture', {}).get('pattern', 'N/A')}")
        logger.write(f"   Quality Score: {code_analysis.get('code_quality', {}).get('score', 0)}/100")
        logger.write(f"   Opportunities: {len(code_analysis.get('opportunities', {}).get('features', []))}")
        
        # =====================================================================
        # AGENT 3: PR ANALYZER
        # =====================================================================
        logger.log_section("AGENT 3: PR ANALYZER - ANALYZING PULL REQUESTS")
        
        logger.write("📥 Sending PR data to PR Analyzer...")
        pr_analysis_input = repo_data.copy()
        logger.log_agent_input("PR Analyzer", pr_analysis_input)
        
        logger.write("⚙️  Executing PR Analyzer Agent...")
        pr_analysis = await pr_analyzer.analyze(
            repo_data=pr_analysis_input,
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("PR Analyzer", pr_analysis)
        logger.write(f"✅ PR analysis complete")
        logger.write(f"   Patterns: {len(pr_analysis.get('patterns', {}).get('common_change_types', []))}")
        logger.write(f"   Insights: {len(pr_analysis.get('insights', {}).get('recent_features', []))}")
        logger.write(f"   Suggestions: {len(pr_analysis.get('suggested_problems', []))}")
        
        # =====================================================================
        # AGENT 4: ISSUE ANALYZER
        # =====================================================================
        logger.log_section("AGENT 4: ISSUE ANALYZER - ANALYZING ISSUES")
        
        logger.write("📥 Sending issue data to Issue Analyzer...")
        issue_analysis_input = repo_data.copy()
        logger.log_agent_input("Issue Analyzer", issue_analysis_input)
        
        logger.write("⚙️  Executing Issue Analyzer Agent...")
        issue_analysis = await issue_analyzer.analyze(
            repo_data=issue_analysis_input,
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("Issue Analyzer", issue_analysis)
        logger.write(f"✅ Issue analysis complete")
        logger.write(f"   Categories: {len(issue_analysis.get('categories', {}).keys())}")
        logger.write(f"   Patterns: {len(issue_analysis.get('problem_patterns', []))}")
        logger.write(f"   Suggestions: {len(issue_analysis.get('suggested_problems', []))}")
        
        # =====================================================================
        # AGENT 5: DEPENDENCY ANALYZER
        # =====================================================================
        logger.log_section("AGENT 5: DEPENDENCY ANALYZER - ANALYZING TECH STACK")
        
        logger.write("📥 Sending dependency data to Dependency Analyzer...")
        dep_analysis_input = repo_data.copy()
        logger.log_agent_input("Dependency Analyzer", dep_analysis_input)
        
        logger.write("⚙️  Executing Dependency Analyzer Agent...")
        dep_analysis = await dependency_analyzer.analyze(
            repo_data=dep_analysis_input,
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("Dependency Analyzer", dep_analysis)
        logger.write(f"✅ Dependency analysis complete")
        logger.write(f"   Tech Stack: {dep_analysis.get('tech_stack', {})}")
        logger.write(f"   Integration Opportunities: {len(dep_analysis.get('integration_opportunities', []))}")
        
        # =====================================================================
        # SYNTHESIZE COMBINED REPORT
        # =====================================================================
        logger.log_section("SYNTHESIZING COMBINED ANALYSIS REPORT")
        
        combined_report = {
            "repository_profile": {
                "name": "Ayurvedic Remedy Generator",
                "architecture": code_analysis.get('architecture', {}),
                "quality": code_analysis.get('code_quality', {}),
                "tech_stack": dep_analysis.get('tech_stack', {}),
                "actual_files_analyzed": list(file_contents.keys())
            },
            "opportunities": code_analysis.get('opportunities', {}),
            "pr_insights": pr_analysis.get('insights', {}),
            "issue_patterns": issue_analysis.get('problem_patterns', []),
            "ranked_suggestions": (
                pr_analysis.get('suggested_problems', [])[:5] +
                issue_analysis.get('suggested_problems', [])[:5]
            )
        }
        
        logger.log_agent_output("COMBINED_REPORT", combined_report)
        logger.write(f"✅ Combined report synthesized with {len(combined_report['ranked_suggestions'])} suggestions")
        
        # =====================================================================
        # AGENT 6: PROBLEM CREATOR
        # =====================================================================
        logger.log_section("AGENT 6: PROBLEM CREATOR - GENERATING CODING PROBLEM")
        
        problem_input = {
            "repository_report": combined_report,
            "difficulty": "medium",
            "problem_type": "feature",
            "focus_area": "Based on Ayurvedic Remedy codebase - 180 minutes",
            "context": f"Actual files analyzed: {', '.join(file_contents.keys())}"
        }
        
        logger.write("📥 Sending combined report to Problem Creator...")
        logger.log_agent_input("Problem Creator", problem_input)
        
        logger.write("⚙️  Executing Problem Creator Agent...")
        problem = await problem_creator.create_problem(
            repository_report=combined_report,
            difficulty="medium",
            problem_type="feature",
            focus_area="Based on Ayurvedic Remedy codebase - 180 minutes",
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("Problem Creator", problem)
        logger.write(f"✅ Problem created:")
        logger.write(f"   Title: {problem.get('title', 'N/A')}")
        logger.write(f"   Difficulty: {problem.get('difficulty', 'N/A')}")
        logger.write(f"   Requirements: {len(problem.get('requirements', []))}")
        logger.write(f"   Acceptance Criteria: {len(problem.get('acceptance_criteria', []))}")
        logger.write(f"   Starter Code Files: {len(problem.get('starter_code', []))}")
        
        # =====================================================================
        # AGENT 7: QA VALIDATOR (SINGLE PASS)
        # =====================================================================
        logger.log_section("AGENT 7: QA VALIDATOR - VALIDATING PROBLEM QUALITY (SINGLE PASS)")
        
        validation_input = {
            "problem": problem,
            "repository_report": combined_report
        }
        
        logger.write("📥 Sending problem to QA Validator for single-pass validation...")
        logger.log_agent_input("QA Validator", validation_input)
        
        logger.write("⚙️  Executing QA Validator Agent (validation only, no loop)...")
        is_approved, validation = await qa_validator.validate_problem(
            problem=problem,
            repository_report=combined_report,
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("QA Validator", validation)
        logger.write(f"✅ Validation complete:")
        logger.write(f"   Overall Score: {validation.get('overall_score', 0)}/100")
        logger.write(f"   Status: {'✅ APPROVED' if is_approved else '⚠️ NEEDS REFINEMENT'}")
        logger.write(f"   Feasibility: {validation.get('scores', {}).get('feasibility', 0)}/100")
        logger.write(f"   Quality: {validation.get('scores', {}).get('quality', 0)}/100")
        logger.write(f"   Technical: {validation.get('scores', {}).get('technical', 0)}/100")
        logger.write(f"   Educational: {validation.get('scores', {}).get('educational', 0)}/100")
        
        # =====================================================================
        # REFINEMENT: SEND FEEDBACK BACK TO PROBLEM CREATOR
        # =====================================================================
        logger.log_section("REFINEMENT: PROBLEM CREATOR IMPROVES BASED ON QA FEEDBACK")
        
        improvement_instructions = {
            "original_problem": problem,
            "validation_feedback": validation,
            "issues": validation.get('issues', []),
            "suggestions": validation.get('suggestions', []),
            "target_score": 100,
            "current_score": validation.get('overall_score', 0)
        }
        
        logger.write("📥 Sending QA feedback to Problem Creator for refinement...")
        logger.log_agent_input("Problem Creator (Refinement)", improvement_instructions)
        
        logger.write("⚙️  Problem Creator refining problem based on QA feedback...")
        refined_problem = await problem_creator.create_problem(
            repository_report={
                **combined_report,
                "improvement_context": improvement_instructions
            },
            difficulty=problem.get('difficulty', 'medium'),
            problem_type="improvement",
            focus_area=f"Refined version - {problem.get('estimated_time', 180)} minutes",
            conversation_id=conversation_id
        )
        
        logger.log_agent_output("Problem Creator (Refined)", refined_problem)
        logger.write(f"✅ Problem refined:")
        logger.write(f"   Original Title: {problem.get('title', 'N/A')}")
        logger.write(f"   Refined Title: {refined_problem.get('title', 'N/A')}")
        logger.write(f"   Original Requirements: {len(problem.get('requirements', []))}")
        logger.write(f"   Refined Requirements: {len(refined_problem.get('requirements', []))}")
        
        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        logger.log_section("FINAL TEST SUMMARY")
        
        logger.write(f"\n✅ ALL AGENTS TESTED SUCCESSFULLY\n")
        logger.write(f"Test Summary:")
        logger.write(f"  • Repository files analyzed: {len(file_contents)}")
        logger.write(f"  • Total file content: {sum(len(c) for c in file_contents.values())} characters")
        logger.write(f"  • Code quality score: {code_analysis.get('code_quality', {}).get('score', 0)}/100")
        logger.write(f"  • Problem suggestions generated: {len(combined_report['ranked_suggestions'])}")
        logger.write(f"  • Initial problem validation: {validation.get('overall_score', 0)}/100")
        logger.write(f"  • Problem refined: YES (single-pass improvement)")
        logger.write(f"  • Final problem: {refined_problem.get('title', 'N/A')}")
        logger.write(f"\nWorkflow:")
        logger.write(f"  1. Repository scanned → 2. Multi-agent analysis → 3. Problem created")
        logger.write(f"  4. QA validated (single pass) → 5. Problem refined with feedback → 6. Final output")
        logger.write(f"\nAll agent inputs and outputs logged to: {log_file}")
        logger.write(f"Total log entries: {logger.log_count}")
        
        logger.close()
        
        print(f"\n{'='*100}")
        print(f"✅ COMPLETE TEST FINISHED")
        print(f"{'='*100}")
        print(f"\n📄 FULL DETAILED LOG SAVED TO: {log_file}")
        print(f"   File contains ALL agent inputs and outputs (no truncation)")
        print(f"   Total entries logged: {logger.log_count}")
        print(f"\n{'='*100}\n")
        
        return {
            "log_file": log_file,
            "code_analysis": code_analysis,
            "pr_analysis": pr_analysis,
            "issue_analysis": issue_analysis,
            "dependency_analysis": dep_analysis,
            "combined_report": combined_report,
            "initial_problem": problem,
            "validation": validation,
            "refined_problem": refined_problem,
            "workflow": "Single-pass QA validation with feedback-driven refinement"
        }
        
    except Exception as e:
        logger.write(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        logger.write(traceback.format_exc())
        logger.close()
        raise


if __name__ == "__main__":
    print("\n" * 2)
    asyncio.run(run_full_detailed_test())
    print("\n" * 2)
