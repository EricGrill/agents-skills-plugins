#!/usr/bin/env python3
"""Quick test to verify GitHub connection works"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.github_mcp import get_github_mcp


async def test_github_connection():
    """Test GitHub API connection"""
    
    print("Testing GitHub Connection...")
    print("=" * 80)
    
    # Check token
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN not set!")
        print("Please run: export GITHUB_TOKEN='your_token_here'")
        return False
    
    print(f"✅ GitHub token found (length: {len(token)})")
    
    try:
        # Initialize client
        print("\n🔧 Initializing GitHub MCP client...")
        github_client = get_github_mcp(token)
        print("✅ Client initialized")
        
        # Test with a small public repo
        test_repo = "sindresorhus/is"
        print(f"\n📡 Testing with repository: {test_repo}")
        
        # Fetch data
        repo_data = await github_client.fetch_repository_data(
            repo_url=test_repo,
            fetch_issues=False,
            fetch_prs=False,
            fetch_commits=False,
            max_items=5
        )
        
        # Display results
        print("\n✅ SUCCESS! Repository data fetched:")
        print(f"   Name: {repo_data['repository'].get('name', 'N/A')}")
        print(f"   Description: {repo_data['repository'].get('description', 'N/A')[:60]}...")
        print(f"   Language: {repo_data['repository'].get('language', 'N/A')}")
        print(f"   Stars: {repo_data['repository'].get('stars', 0)}")
        print(f"   Files: {repo_data['codebase']['total_files']}")
        print(f"   README length: {len(repo_data.get('readme', ''))} chars")
        
        print("\n" + "=" * 80)
        print("🎉 GitHub connection test PASSED!")
        print("You're ready to run: python cli_runner.py")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_github_connection())
    sys.exit(0 if success else 1)
