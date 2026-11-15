#!/usr/bin/env python3
"""
ActualCode CLI Runner

Interactive terminal interface for generating coding assessments from GitHub repositories.
"""

import asyncio
import sys
import os
from typing import Optional
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.github_mcp import get_github_mcp
from orchestrator import AssessmentOrchestrator


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print ActualCode banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     █████╗  ██████╗████████╗██╗   ██╗ █████╗ ██╗      ██████╗ ██████╗   ║
║    ██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║     ██╔════╝██╔═══██╗  ║
║    ███████║██║        ██║   ██║   ██║███████║██║     ██║     ██║   ██║  ║
║    ██╔══██║██║        ██║   ██║   ██║██╔══██║██║     ██║     ██║   ██║  ║
║    ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝  ║
║    ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝   ║
║                                                                           ║
║              AI-Powered Code Assessment Generator                         ║
║              Powered by Google Gemini & Multi-Agent AI                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def print_section(title: str, emoji: str = ""):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{emoji} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]{Colors.END}: "
    else:
        full_prompt = f"{Colors.CYAN}{prompt}{Colors.END}: "
    
    value = input(full_prompt).strip()
    return value if value else (default or "")


def get_choice(prompt: str, options: list, default: int = 0) -> str:
    """Get user choice from a list of options"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.END}")
    for i, option in enumerate(options, 1):
        marker = f"{Colors.GREEN}→{Colors.END}" if i == default + 1 else " "
        print(f"  {marker} {i}. {option}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}Enter choice (1-{len(options)}) [{default + 1}]{Colors.END}: ").strip()
        if not choice:
            return options[default]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and {len(options)}.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.END}")


async def main():
    """Main CLI runner"""
    print_banner()
    
    print(f"{Colors.YELLOW}Welcome to ActualCode - AI-Powered Code Assessment Generator{Colors.END}")
    print(f"{Colors.YELLOW}Transform any GitHub repository into realistic coding challenges{Colors.END}\n")
    
    # Check environment
    print_section("Environment Check", "🔍")
    
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    if not github_token:
        print(f"{Colors.RED}❌ GitHub token not found!{Colors.END}")
        print(f"{Colors.YELLOW}Please set GITHUB_TOKEN environment variable:{Colors.END}")
        print(f"  export GITHUB_TOKEN='your_github_token_here'")
        return
    else:
        print(f"{Colors.GREEN}✅ GitHub token configured{Colors.END}")
    
    google_project = os.getenv('GOOGLE_CLOUD_PROJECT')
    if google_project:
        print(f"{Colors.GREEN}✅ Google Cloud project: {google_project}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Google Cloud project not set (using defaults){Colors.END}")
    
    # Get user inputs
    print_section("Configuration", "⚙️")
    
    repo_url = get_input("GitHub Repository URL (e.g., owner/repo or full URL)")
    if not repo_url:
        print(f"{Colors.RED}Repository URL is required!{Colors.END}")
        return
    
    difficulty = get_choice(
        "Select Difficulty Level:",
        ["easy", "medium", "hard", "expert"],
        default=1  # medium
    )
    
    problem_type = get_choice(
        "Select Problem Type:",
        ["feature", "bug-fix", "refactor", "optimization"],
        default=0  # feature
    )
    
    time_limit = get_choice(
        "Estimated Time Limit:",
        ["60 minutes", "120 minutes", "180 minutes", "240 minutes"],
        default=2  # 180 minutes
    )
    time_value = int(time_limit.split()[0])
    
    # Confirm
    print(f"\n{Colors.BOLD}Configuration Summary:{Colors.END}")
    print(f"  Repository:  {Colors.CYAN}{repo_url}{Colors.END}")
    print(f"  Difficulty:  {Colors.CYAN}{difficulty}{Colors.END}")
    print(f"  Type:        {Colors.CYAN}{problem_type}{Colors.END}")
    print(f"  Time Limit:  {Colors.CYAN}{time_value} minutes{Colors.END}")
    
    confirm = input(f"\n{Colors.YELLOW}Proceed with generation? (y/n) [y]{Colors.END}: ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        print(f"{Colors.RED}Cancelled.{Colors.END}")
        return
    
    # Start generation
    print_section("Generating Assessment", "🚀")
    
    try:
        # Initialize GitHub MCP
        print(f"{Colors.BLUE}🔧 Initializing GitHub MCP client...{Colors.END}")
        github_client = get_github_mcp(github_token)
        
        # Fetch repository data
        print(f"{Colors.BLUE}📡 Fetching repository data from GitHub...{Colors.END}")
        repo_data = await github_client.fetch_repository_data(
            repo_url=repo_url,
            fetch_issues=True,
            fetch_prs=True,
            fetch_commits=True,
            max_items=20
        )
        
        print(f"{Colors.GREEN}✅ Repository data fetched successfully!{Colors.END}")
        print(f"   Name: {repo_data['repository'].get('name', 'N/A')}")
        print(f"   Language: {repo_data['repository'].get('language', 'N/A')}")
        print(f"   Files: {repo_data['codebase']['total_files']}")
        print(f"   Issues: {len(repo_data['issues'])}")
        print(f"   PRs: {len(repo_data['pull_requests'])}")
        print(f"   Commits: {len(repo_data['commits'])}")
        
        # Initialize orchestrator
        print(f"\n{Colors.BLUE}🤖 Initializing Multi-Agent System...{Colors.END}")
        orchestrator = AssessmentOrchestrator()
        
        # Generate assessment
        print(f"\n{Colors.BOLD}{Colors.YELLOW}🔥 Starting Multi-Agent Analysis...{Colors.END}")
        print(f"{Colors.YELLOW}This may take 2-3 minutes. Please wait...{Colors.END}\n")
        
        result = await orchestrator.generate_assessment(
            github_repo_url=repo_url,
            difficulty=difficulty,
            time_limit=time_value,
            problem_type=problem_type,
            repo_data=repo_data  # Pass pre-fetched data
        )
        
        # Display results
        print_section("Assessment Generated Successfully!", "🎉")
        
        # Extract from correct structure
        assessment = result.get('assessment', {})
        problem = assessment.get('problem', {})
        validation = assessment.get('validation', {})
        
        print(f"{Colors.BOLD}Problem Title:{Colors.END} {problem.get('title', 'N/A')}")
        print(f"{Colors.BOLD}Difficulty:{Colors.END} {problem.get('difficulty', 'N/A')}")
        print(f"{Colors.BOLD}Estimated Time:{Colors.END} {problem.get('estimated_time', 'N/A')} minutes")
        print(f"{Colors.BOLD}Tech Stack:{Colors.END} {', '.join(problem.get('tech_stack', []))}")
        
        print(f"\n{Colors.BOLD}Description:{Colors.END}")
        print(f"{problem.get('description', 'N/A')[:300]}...")
        
        print(f"\n{Colors.BOLD}Requirements:{Colors.END} {len(problem.get('requirements', []))}")
        print(f"{Colors.BOLD}Acceptance Criteria:{Colors.END} {len(problem.get('acceptance_criteria', []))}")
        print(f"{Colors.BOLD}Starter Code Files:{Colors.END} {len(problem.get('starter_code', []))}")
        
        print(f"\n{Colors.BOLD}QA Validation Score:{Colors.END} {validation.get('overall_score', 0)}/100")
        print(f"{Colors.BOLD}Feasibility:{Colors.END} {validation.get('scores', {}).get('feasibility', 0)}/100")
        print(f"{Colors.BOLD}Quality:{Colors.END} {validation.get('scores', {}).get('quality', 0)}/100")
        print(f"{Colors.BOLD}Technical:{Colors.END} {validation.get('scores', {}).get('technical', 0)}/100")
        print(f"{Colors.BOLD}Educational:{Colors.END} {validation.get('scores', {}).get('educational', 0)}/100")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"assessment_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n{Colors.GREEN}✅ Assessment saved to: {output_file}{Colors.END}")
        
        # Performance metrics
        metadata = assessment.get('metadata', {})
        if 'performance' in metadata:
            perf = metadata['performance']
            print(f"\n{Colors.BOLD}Performance Metrics:{Colors.END}")
            total_dur = perf.get('total_duration', 0)
            scan_dur = perf.get('scan', 0)
            analysis_dur = perf.get('analysis', 0)
            creation_dur = perf.get('creation', 0)
            validation_dur = perf.get('validation', 0)
            
            # Ensure all are floats
            print(f"  Total Time: {float(total_dur):.2f}s")
            print(f"  Scan: {float(scan_dur):.2f}s")
            print(f"  Analysis: {float(analysis_dur):.2f}s")
            print(f"  Creation: {float(creation_dur):.2f}s")
            print(f"  Validation: {float(validation_dur):.2f}s")
        
        # Save detailed logs
        log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"DETAILED_RUN_{log_timestamp}.txt"
        
        with open(log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("ACTUALCODE - DETAILED GENERATION LOG\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Repository: {repo_url}\n")
            f.write(f"Difficulty: {difficulty}\n")
            f.write(f"Time Limit: {time_value} minutes\n\n")
            
            # Repository Data
            f.write("="*80 + "\n")
            f.write("REPOSITORY DATA\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(repo_data, indent=2) + "\n\n")
            
            # Analysis Report
            if 'debug' in result and 'analysis_report' in result['debug']:
                f.write("="*80 + "\n")
                f.write("ANALYSIS REPORT (3 LOOPS)\n")
                f.write("="*80 + "\n")
                f.write(json.dumps(result['debug']['analysis_report'], indent=2) + "\n\n")
            
            # Generated Problem
            f.write("="*80 + "\n")
            f.write("GENERATED PROBLEM\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(problem, indent=2) + "\n\n")
            
            # QA Validation
            f.write("="*80 + "\n")
            f.write("QA VALIDATION\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(validation, indent=2) + "\n\n")
            
            # Full Result
            f.write("="*80 + "\n")
            f.write("COMPLETE RESULT\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(result, indent=2) + "\n")
        
        print(f"{Colors.GREEN}✅ Detailed logs saved to: {log_file}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎊 Assessment generation complete!{Colors.END}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {type(e).__name__}: {str(e)}{Colors.END}")
        import traceback
        print(f"\n{Colors.RED}Traceback:{Colors.END}")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
