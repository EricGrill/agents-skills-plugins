"""Agent 1: GitHub Scanner

Retrieves comprehensive repository data using GitHub API via github_mcp utility.
"""

import json
import os
from typing import Dict, Any, Optional
from agents.base_agent import BaseGeminiAgent
from utils.a2a_protocol import a2a_protocol
from utils.github_mcp import get_github_mcp


class ScannerAgent(BaseGeminiAgent):
    """Scans GitHub repositories for comprehensive data using GitHub API"""
    
    def __init__(self, use_real_data: bool = True):
        system_instruction = """You are a GitHub repository analyst.

You analyze GitHub repository data and ensure it's properly structured and complete.
Your role is to organize and format the data for downstream agents."""
        
        super().__init__(
            name="github_scanner",
            model="gemini-2.5-flash",
            system_instruction=system_instruction,
            temperature=0.1,
            max_output_tokens=2048
        )
        
        self.use_real_data = use_real_data
        self.github_client = None
        
        # Initialize GitHub client if using real data
        if use_real_data:
            try:
                self.github_client = get_github_mcp()
                self.logger.info("GitHub MCP client initialized")
            except ValueError as e:
                self.logger.warning(f"Could not initialize GitHub client: {e}. Falling back to mock data.")
                self.use_real_data = False
    
    async def scan_repository(
        self,
        repo_url: str,
        depth: str = "shallow",
        conversation_id: str = None,
        pre_fetched_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Scan a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            depth: Scan depth ('shallow' or 'deep')
            conversation_id: Optional conversation ID for A2A tracking
            
        Returns:
            Repository data dictionary
        """
        
        self.logger.info(
            "Scanning repository",
            repo_url=repo_url,
            depth=depth,
            use_real_data=self.use_real_data,
            conversation_id=conversation_id
        )
        
        # Send A2A notification
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="scanner",
                recipient_id="orchestrator",
                data={"status": "scanning", "repo_url": repo_url},
                conversation_id=conversation_id,
                message_type="notification"
            )
        
        # Use pre-fetched data if provided
        if pre_fetched_data:
            self.logger.info("Using pre-fetched repository data")
            repo_data = pre_fetched_data
        # Use real GitHub data if configured
        elif self.use_real_data and self.github_client:
            self.logger.info("Fetching real repository data from GitHub")
            try:
                repo_data = await self.github_client.fetch_repository_data(
                    repo_url=repo_url,
                    fetch_issues=True,
                    fetch_prs=True,
                    fetch_commits=True,
                    max_items=20
                )
            except Exception as e:
                self.logger.error(f"Failed to fetch real data: {e}. Using mock data.")
                repo_data = self._get_mock_repository_data(repo_url)
        # Fall back to mock data
        else:
            self.logger.info("Using mock repository data")
            repo_data = self._get_mock_repository_data(repo_url)
        
        self.logger.info(
            "Repository scan complete",
            repo_name=repo_data.get('repository', {}).get('name', 'Unknown'),
            total_files=repo_data.get('codebase', {}).get('total_files', 0),
            data_source="prefetched" if pre_fetched_data else ("real" if self.use_real_data else "mock")
        )
        
        # Send A2A response
        if conversation_id:
            await a2a_protocol.send_message(
                sender_id=self.name,
                sender_type="scanner",
                recipient_id="orchestrator",
                data={
                    "status": "completed",
                    "repository": repo_data.get('repository', {}),
                    "files_scanned": repo_data.get('codebase', {}).get('total_files', 0),
                    "data_source": "prefetched" if pre_fetched_data else ("real" if self.use_real_data else "mock")
                },
                conversation_id=conversation_id,
                message_type="response"
            )
        
        return repo_data
    
    def _get_mock_repository_data(self, repo_url: str) -> Dict[str, Any]:
        """Generate comprehensive mock repository data
        
        This simulates what GitHub MCP would return.
        """
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1]
        owner = repo_url.rstrip('/').split('/')[-2] if '/' in repo_url else "owner"
        
        return {
            "repository": {
                "name": repo_name,
                "full_name": f"{owner}/{repo_name}",
                "description": f"A modern web application built with React and Node.js",
                "language": "JavaScript",
                "stars": 1234,
                "forks": 456,
                "url": repo_url,
                "default_branch": "main"
            },
            "codebase": {
                "file_tree": [
                    {"path": "src/", "type": "directory"},
                    {"path": "src/components/", "type": "directory"},
                    {"path": "src/components/App.jsx", "type": "file", "language": "JavaScript"},
                    {"path": "src/components/Header.jsx", "type": "file", "language": "JavaScript"},
                    {"path": "src/api/", "type": "directory"},
                    {"path": "src/api/users.js", "type": "file", "language": "JavaScript"},
                    {"path": "src/utils/", "type": "directory"},
                    {"path": "src/utils/helpers.js", "type": "file", "language": "JavaScript"},
                    {"path": "server/", "type": "directory"},
                    {"path": "server/index.js", "type": "file", "language": "JavaScript"},
                    {"path": "server/routes/", "type": "directory"},
                    {"path": "server/models/", "type": "directory"},
                    {"path": "tests/", "type": "directory"},
                    {"path": "tests/unit/", "type": "directory"},
                    {"path": "tests/integration/", "type": "directory"},
                    {"path": "package.json", "type": "file"},
                    {"path": "README.md", "type": "file"},
                    {"path": ".gitignore", "type": "file"}
                ],
                "total_files": 45,
                "language_distribution": {
                    "JavaScript": 75,
                    "JSX": 15,
                    "CSS": 8,
                    "Markdown": 2
                }
            },
            "pullRequests": [
                {
                    "id": 1,
                    "title": "Add user authentication",
                    "description": "Implements JWT-based authentication",
                    "author": "developer1",
                    "state": "merged",
                    "files_changed": ["src/api/auth.js", "server/middleware/auth.js"]
                },
                {
                    "id": 2,
                    "title": "Fix memory leak in data fetching",
                    "description": "Resolves issue with unmounted components",
                    "author": "developer2",
                    "state": "merged",
                    "files_changed": ["src/hooks/useData.js"]
                },
                {
                    "id": 3,
                    "title": "Add caching layer",
                    "description": "Implements Redis caching for API responses",
                    "author": "developer1",
                    "state": "open",
                    "files_changed": ["server/cache.js", "server/routes/api.js"]
                }
            ],
            "issues": [
                {
                    "id": 101,
                    "title": "Add remedy history/favorites feature",
                    "description": "Users want to save and revisit their past remedy searches using localStorage",
                    "labels": ["enhancement", "feature"],
                    "state": "open",
                    "comments": 8
                },
                {
                    "id": 102,
                    "title": "Typing animation stutters on mobile",
                    "description": "The remedy typing effect lags on mobile devices, especially with longer responses",
                    "labels": ["performance", "bug", "mobile"],
                    "state": "open",
                    "comments": 5
                },
                {
                    "id": 103,
                    "title": "Add multilingual support for remedies",
                    "description": "Support Hindi, Sanskrit, and other Indian languages for remedy descriptions",
                    "labels": ["feature", "i18n"],
                    "state": "open",
                    "comments": 12
                }
            ],
            "commits": [
                {"sha": "a1b2c3d", "message": "Initial commit - Basic remedy generator", "author": "developer1", "date": "2024-01-15"},
                {"sha": "e4f5g6h", "message": "Add Google Gemini AI integration", "author": "developer1", "date": "2024-01-20"},
                {"sha": "i7j8k9l", "message": "Implement typing animation effect", "author": "developer2", "date": "2024-02-01"},
                {"sha": "m1n2o3p", "message": "Add animated herb icons", "author": "developer2", "date": "2024-02-10"},
                {"sha": "q4r5s6t", "message": "Improve CSS styling and responsiveness", "author": "developer1", "date": "2024-02-15"}
            ],
            "readme": file_contents.get('README.md', '# Ayurvedic-Remedy\n\nAI-powered Ayurvedic remedy generator'),
            "dependencies": [
                {"name": "@google/generative-ai", "version": "latest", "type": "production", "description": "Google Gemini AI SDK"},
                {"name": "dotenv", "version": "16.0.0", "type": "production", "description": "Environment variable management"}
            ],
            "tech_stack": {
                "frontend": ["Vanilla JavaScript", "HTML5", "CSS3"],
                "ai": ["Google Gemini Pro API"],
                "features": ["Typing animation", "Animated icons", "Responsive design"]
            }
        }


# Create singleton instance (will use real data if GITHUB_TOKEN is set)
scanner = ScannerAgent(use_real_data=True)
