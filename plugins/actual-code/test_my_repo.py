#!/usr/bin/env python3
"""Quick test with your specific repository"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.github_mcp import get_github_mcp


async def test():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN not set!")
        return False
    
    print("Testing with YOUR repository: muratcankoylan/AI-Investigator")
    print("=" * 80)
    
    github_client = get_github_mcp(token)
    
    repo_data = await github_client.fetch_repository_data(
        repo_url="muratcankoylan/AI-Investigator",
        fetch_issues=True,
        fetch_prs=True,
        fetch_commits=True,
        max_items=10
    )
    
    print("\n✅ SUCCESS! Your repository data:")
    print(f"   Name: {repo_data['repository'].get('name', 'N/A')}")
    print(f"   Description: {repo_data['repository'].get('description', 'N/A')}")
    print(f"   Language: {repo_data['repository'].get('language', 'N/A')}")
    print(f"   Stars: {repo_data['repository'].get('stars', 0)}")
    print(f"   Files: {repo_data['codebase']['total_files']}")
    print(f"   README: {len(repo_data.get('readme', ''))} chars")
    print(f"   Issues: {len(repo_data.get('issues', []))}")
    print(f"   PRs: {len(repo_data.get('pull_requests', []))}")
    print(f"   Commits: {len(repo_data.get('commits', []))}")
    
    if repo_data['codebase']['total_files'] > 0:
        print(f"\n📁 Sample files:")
        for f in repo_data['codebase']['file_tree'][:5]:
            print(f"     - {f['path']}")
    
    print("\n" + "=" * 80)
    print("🎉 Ready to generate assessment from YOUR repository!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
