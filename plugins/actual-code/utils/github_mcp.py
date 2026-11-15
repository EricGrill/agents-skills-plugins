"""GitHub MCP Integration Module

Integrates with GitHub's Model Context Protocol server to fetch real repository data.
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class GitHubMCP:
    """GitHub Model Context Protocol client for fetching repository data"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub MCP client
        
        Args:
            github_token: GitHub Personal Access Token. If None, reads from env.
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        
        if not self.github_token:
            raise ValueError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable "
                "or pass it to the constructor."
            )
        
        self.mcp_process = None
        logger.info("GitHub MCP client initialized")
    
    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """
        Parse GitHub repository URL to extract owner and repo name
        
        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
            
        Returns:
            Tuple of (owner, repo_name)
        """
        # Handle different URL formats
        # https://github.com/owner/repo
        # github.com/owner/repo
        # owner/repo
        
        url = repo_url.strip().rstrip('/')
        
        if url.startswith('http'):
            # Extract from full URL
            parts = url.split('github.com/')[-1].split('/')
        elif 'github.com/' in url:
            parts = url.split('github.com/')[-1].split('/')
        else:
            # Assume format is owner/repo
            parts = url.split('/')
        
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    async def fetch_repository_data(
        self,
        repo_url: str,
        fetch_issues: bool = True,
        fetch_prs: bool = True,
        fetch_commits: bool = True,
        max_items: int = 20
    ) -> Dict[str, Any]:
        """
        Fetch comprehensive repository data from GitHub
        
        Args:
            repo_url: GitHub repository URL
            fetch_issues: Whether to fetch issues
            fetch_prs: Whether to fetch pull requests
            fetch_commits: Whether to fetch commits
            max_items: Maximum number of items to fetch for lists
            
        Returns:
            Dictionary containing all repository data
        """
        owner, repo = self._parse_repo_url(repo_url)
        
        logger.info(f"Fetching data for {owner}/{repo}")
        
        try:
            # Fetch repository metadata
            repo_data = await self._fetch_repo_metadata(owner, repo)
            
            # Fetch file structure
            file_tree = await self._fetch_file_tree(owner, repo)
            
            # Fetch README
            readme = await self._fetch_readme(owner, repo)
            
            # Fetch dependencies
            dependencies = await self._fetch_dependencies(owner, repo)
            
            # Optionally fetch issues, PRs, commits
            issues = []
            pull_requests = []
            commits = []
            
            if fetch_issues:
                issues = await self._fetch_issues(owner, repo, max_items)
            
            if fetch_prs:
                pull_requests = await self._fetch_pull_requests(owner, repo, max_items)
            
            if fetch_commits:
                commits = await self._fetch_commits(owner, repo, max_items)
            
            return {
                "repository": repo_data,
                "codebase": {
                    "file_tree": file_tree,
                    "total_files": len(file_tree) if isinstance(file_tree, list) else 0
                },
                "readme": readme,
                "dependencies": dependencies,
                "issues": issues,
                "pull_requests": pull_requests,
                "commits": commits,
                "metadata": {
                    "owner": owner,
                    "repo_name": repo,
                    "full_name": f"{owner}/{repo}",
                    "url": f"https://github.com/{owner}/{repo}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching repository data: {e}")
            raise
    
    async def _fetch_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch basic repository metadata using GitHub API"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": data.get("name"),
                        "full_name": data.get("full_name"),
                        "description": data.get("description"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "open_issues": data.get("open_issues_count", 0),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "topics": data.get("topics", []),
                        "default_branch": data.get("default_branch", "main")
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to fetch repo metadata: {response.status} - {error_text[:200]}")
                    return {}
    
    async def _fetch_file_tree(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch file tree using GitHub API"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    tree = data.get("tree", [])
                    # Return simplified file list
                    return [
                        {
                            "path": item["path"],
                            "type": item["type"],
                            "size": item.get("size", 0)
                        }
                        for item in tree[:500]  # Limit to 500 files
                    ]
                else:
                    logger.error(f"Failed to fetch file tree: {response.status}")
                    return []
    
    async def _fetch_readme(self, owner: str, repo: str) -> str:
        """Fetch README content"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.raw",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"README not found or inaccessible: {response.status}")
                    return ""
    
    async def _fetch_dependencies(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch dependencies from common dependency files"""
        import aiohttp
        
        dependencies = []
        
        # Common dependency files to check
        dep_files = [
            "package.json",  # Node.js
            "requirements.txt",  # Python
            "Gemfile",  # Ruby
            "pom.xml",  # Java Maven
            "build.gradle",  # Java Gradle
            "go.mod",  # Go
            "Cargo.toml"  # Rust
        ]
        
        async with aiohttp.ClientSession() as session:
            for file in dep_files:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file}"
                headers = {
                    "Authorization": f"Bearer {self.github_token}",
                    "Accept": "application/vnd.github.raw",
                    "User-Agent": "ActualCode-CLI/1.0",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                
                try:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            dependencies.append({
                                "file": file,
                                "content": content[:1000]  # First 1000 chars
                            })
                except Exception as e:
                    logger.debug(f"Could not fetch {file}: {e}")
        
        return dependencies
    
    async def _fetch_issues(self, owner: str, repo: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch recent issues"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        params = {
            "state": "all",
            "per_page": max_items,
            "sort": "updated"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "number": issue["number"],
                            "title": issue["title"],
                            "body": (issue.get("body") or "")[:500],  # Handle None
                            "state": issue["state"],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])]
                        }
                        for issue in data
                        if "pull_request" not in issue  # Filter out PRs
                    ]
                else:
                    logger.error(f"Failed to fetch issues: {response.status}")
                    return []
    
    async def _fetch_pull_requests(self, owner: str, repo: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch recent pull requests"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        params = {
            "state": "all",
            "per_page": max_items,
            "sort": "updated"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "number": pr["number"],
                            "title": pr["title"],
                            "body": (pr.get("body") or "")[:500],  # Handle None
                            "state": pr["state"],
                            "created_at": pr["created_at"],
                            "updated_at": pr["updated_at"],
                            "merged_at": pr.get("merged_at")
                        }
                        for pr in data
                    ]
                else:
                    logger.error(f"Failed to fetch pull requests: {response.status}")
                    return []
    
    async def _fetch_commits(self, owner: str, repo: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch recent commits"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ActualCode-CLI/1.0",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        params = {
            "per_page": min(max_items, 100)  # GitHub API max is 100
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "sha": commit["sha"][:8],
                            "message": (commit["commit"]["message"] or "").split('\n')[0][:100],
                            "author": commit["commit"]["author"]["name"],
                            "date": commit["commit"]["author"]["date"]
                        }
                        for commit in data
                    ]
                else:
                    logger.error(f"Failed to fetch commits: {response.status}")
                    return []


# Create singleton instance
github_mcp = None

def get_github_mcp(github_token: Optional[str] = None) -> GitHubMCP:
    """Get or create GitHub MCP instance"""
    global github_mcp
    if github_mcp is None:
        github_mcp = GitHubMCP(github_token)
    return github_mcp
