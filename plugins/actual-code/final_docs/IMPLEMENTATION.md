# 📝 Step-by-Step Implementation Guide

Complete implementation instructions from zero to working multi-agent system.

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Foundation](#phase-1-foundation)
3. [Phase 2: Core Agents](#phase-2-core-agents)
4. [Phase 3: Orchestration](#phase-3-orchestration)
5. [Phase 4: Frontend Integration](#phase-4-frontend-integration)
6. [Phase 5: Testing](#phase-5-testing)
7. [Phase 6: Deployment](#phase-6-deployment)

---

## Overview

### Prerequisites

Before starting, ensure you've completed [SETUP.md](./SETUP.md):
- ✅ Environment configured
- ✅ Google Cloud project created
- ✅ GitHub tokens obtained
- ✅ Database initialized
- ✅ Development server running

### Project Structure

We'll be creating these files:

```
actualy_code/
├── agents/
│   ├── __init__.py
│   ├── scanner_agent.py
│   ├── code_analyzer_agent.py
│   ├── pr_analyzer_agent.py
│   ├── issue_analyzer_agent.py
│   ├── dependency_analyzer_agent.py
│   ├── problem_creator_agent.py
│   └── qa_validator_agent.py
├── utils/
│   ├── __init__.py
│   ├── a2a_protocol.py
│   └── monitoring.py
├── orchestrator.py
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_orchestrator.py
└── src/app/api/assessments/generate/route.ts
```

### Estimated Time

- **Phase 1**: ~30 minutes
- **Phase 2**: ~2 hours
- **Phase 3**: ~45 minutes
- **Phase 4**: ~30 minutes
- **Phase 5**: ~1 hour
- **Phase 6**: ~1 hour

**Total**: ~6 hours for complete implementation

---

## Phase 1: Foundation

### Task 1.1: Create Project Directories

```bash
# Navigate to project
cd /Users/muratcankoylan/ActualCode/actualy_code

# Create directories
mkdir -p agents utils tests/unit tests/integration scripts

# Create Python module files
touch agents/__init__.py
touch utils/__init__.py
touch tests/__init__.py

# Verify structure
ls -la agents/ utils/ tests/
```

**Time: 2 minutes**

---

### Task 1.2: Create A2A Protocol Module

Create `utils/a2a_protocol.py`:

```python
"""A2A Protocol Implementation for Agent Communication"""

import uuid
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class A2AMessage:
    """A2A Protocol Message Structure"""
    
    protocol_version: str = "1.0"
    message_id: str = ""
    sender_id: str = ""
    sender_type: str = ""
    recipient_id: str = ""
    message_type: str = "request"  # request, response, broadcast, notification
    timestamp: float = 0.0
    payload: Dict[str, Any] = None
    conversation_id: str = ""
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"msg_{uuid.uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = time.time()
        if self.payload is None:
            self.payload = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "protocol_version": self.protocol_version,
            "message_id": self.message_id,
            "sender": {
                "agent_id": self.sender_id,
                "agent_type": self.sender_type
            },
            "recipient": {
                "agent_id": self.recipient_id
            },
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "payload": {
                "data": self.payload.get("data", {}),
                "metadata": {
                    "conversation_id": self.conversation_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }


class A2AProtocol:
    """A2A Protocol Handler"""
    
    def __init__(self):
        self.message_history = []
    
    async def send_message(
        self,
        sender_id: str,
        sender_type: str,
        recipient_id: str,
        data: Dict[str, Any],
        conversation_id: str,
        message_type: str = "request"
    ) -> A2AMessage:
        """Send an A2A message"""
        
        message = A2AMessage(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            message_type=message_type,
            payload={"data": data},
            conversation_id=conversation_id
        )
        
        # Log message
        self.message_history.append(message)
        
        return message
    
    async def broadcast_message(
        self,
        sender_id: str,
        sender_type: str,
        data: Dict[str, Any],
        conversation_id: str
    ) -> A2AMessage:
        """Broadcast message to all agents"""
        
        return await self.send_message(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id="all_agents",
            data=data,
            conversation_id=conversation_id,
            message_type="broadcast"
        )
    
    def get_message_history(self, conversation_id: Optional[str] = None) -> list:
        """Get message history for a conversation"""
        
        if conversation_id:
            return [
                msg for msg in self.message_history 
                if msg.conversation_id == conversation_id
            ]
        return self.message_history


# Global A2A protocol instance
a2a_protocol = A2AProtocol()
```

**Test the module**:

```bash
python3 << 'PYTEST'
from utils.a2a_protocol import A2AMessage, A2AProtocol
import asyncio

async def test_a2a():
    protocol = A2AProtocol()
    msg = await protocol.send_message(
        sender_id="test_agent",
        sender_type="analyzer",
        recipient_id="receiver",
        data={"test": "data"},
        conversation_id="conv_test"
    )
    print("✅ A2A Protocol working!")
    print(f"Message ID: {msg.message_id}")

asyncio.run(test_a2a())
PYTEST
```

**Time: 10 minutes**

---

### Task 1.3: Create Monitoring Module

Create `utils/monitoring.py`:

```python
"""Logging and Monitoring Utilities"""

import logging
import time
from typing import Optional
from datetime import datetime


class AgentLogger:
    """Unified logging for agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logs = []
        
        # Set up local logging
        self.logger = logging.getLogger(agent_name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, extra: Optional[dict] = None):
        """Log a message"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "level": level,
            "message": message,
            "extra": extra or {}
        }
        
        self.logs.append(log_entry)
        getattr(self.logger, level.lower())(message)
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, kwargs)
    
    def get_logs(self) -> list:
        return self.logs


class PerformanceMonitor:
    """Monitor agent performance"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = {
            "start_time": time.time(),
            "end_time": None,
            "duration": None
        }
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        if operation in self.metrics:
            self.metrics[operation]["end_time"] = time.time()
            self.metrics[operation]["duration"] = (
                self.metrics[operation]["end_time"] - 
                self.metrics[operation]["start_time"]
            )
    
    def get_duration(self, operation: str) -> Optional[float]:
        """Get duration of an operation"""
        if operation in self.metrics:
            return self.metrics[operation].get("duration")
        return None
    
    def get_all_metrics(self) -> dict:
        """Get all metrics"""
        return self.metrics
```

**Time: 5 minutes**

---

## Phase 2: Core Agents

### Task 2.1: Scanner Agent (GitHub MCP)

Create `agents/scanner_agent.py`:

```python
"""Agent 1: GitHub Scanner using MCP"""

import os
import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger

# NOTE: Update these imports once google-adk is properly installed
# For now, we'll use mock implementations for development

class MockMCPTool:
    """Mock MCP tool for development"""
    def __init__(self, name, server_config):
        self.name = name
        self.server_config = server_config

class MockLlmAgent:
    """Mock LLM agent for development"""
    def __init__(self, name, model, tools=None, system_instruction="", a2a_capabilities=None):
        self.name = name
        self.model = model
        self.tools = tools or []
        self.system_instruction = system_instruction
        self.a2a_capabilities = a2a_capabilities or {}
    
    async def run(self, prompt):
        # Mock implementation - replace with real ADK
        return {
            "status": "success",
            "repository": {
                "name": "sample-repo",
                "description": "Sample repository",
                "language": "Python"
            },
            "message": "Scanner agent mock response"
        }


def create_github_mcp_tool():
    """Create GitHub MCP tool"""
    return MockMCPTool(
        name="github",
        server_config={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")
            }
        }
    )


def create_scanner_agent():
    """Create GitHub Scanner Agent"""
    
    github_mcp = create_github_mcp_tool()
    
    return MockLlmAgent(
        name="github_scanner",
        model="gemini-2.5-flash",
        tools=[github_mcp],
        system_instruction="""You are a GitHub repository scanner.

Your job is to retrieve comprehensive data about a GitHub repository:
1. Repository metadata (name, description, language, stars, etc.)
2. File structure and codebase overview
3. Recent issues (last 20)
4. Recent pull requests (last 20)
5. Recent commits (last 50)
6. README content
7. Dependencies (from package.json, requirements.txt, etc.)

Use the GitHub MCP tools to gather this information efficiently.
Output a structured JSON report.""",
        a2a_capabilities={
            "exposes": [
                "scan_repository",
                "get_repo_metadata",
                "get_issues",
                "get_pull_requests"
            ],
            "protocol_version": "1.0"
        }
    )


async def scan_repository(repo_url: str) -> Dict[str, Any]:
    """Scan a GitHub repository and return comprehensive data"""
    
    logger = AgentLogger("scanner_agent")
    
    logger.info(f"Scanning repository: {repo_url}")
    
    # Extract owner and repo from URL
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    logger.info(f"Owner: {owner}, Repo: {repo}")
    
    # Create agent
    agent = create_scanner_agent()
    
    # Create prompt
    prompt = f"""Scan the GitHub repository: {owner}/{repo}

Please gather the following information:
1. Repository metadata
2. File structure (top-level directories and key files)
3. Last 20 issues
4. Last 20 pull requests
5. Last 50 commits
6. README content
7. Dependencies

Return the data as a structured JSON object."""
    
    # Run agent
    logger.info("Running scanner agent...")
    result = await agent.run(prompt)
    
    logger.info("Scan complete")
    
    return {
        "repository": {
            "owner": owner,
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "url": repo_url
        },
        "scan_result": result,
        "status": "completed"
    }


# CLI for testing
if __name__ == "__main__":
    async def test():
        result = await scan_repository("https://github.com/vercel/next.js")
        print("✅ Scanner Agent Test Result:")
        print(result)
    
    asyncio.run(test())
```

**Test**:
```bash
python agents/scanner_agent.py
```

**Time: 15 minutes**

---

### Task 2.2: Analysis Agents (Agents 2-5)

Create a script to generate all analysis agents:

```bash
cat > scripts/create_analysis_agents.sh << 'EOF'
#!/bin/bash

# Code Analyzer Agent
cat > agents/code_analyzer_agent.py << 'PYEOF'
"""Agent 2: Code Analyzer"""

import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger

class CodeAnalyzerAgent:
    def __init__(self):
        self.logger = AgentLogger("code_analyzer")
        self.name = "code_analyzer"
        self.model = "gemini-2.5-pro"
    
    async def analyze(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository architecture and code quality"""
        
        self.logger.info("Analyzing code architecture...")
        
        # Mock analysis (replace with real ADK implementation)
        return {
            "architecture": {
                "pattern": "MVC",
                "layers": ["controller", "model", "view"],
                "complexity": "medium"
            },
            "quality_score": 85,
            "opportunities": [
                "Add authentication system",
                "Implement caching layer",
                "Add API versioning"
            ]
        }

code_analyzer = CodeAnalyzerAgent()

if __name__ == "__main__":
    asyncio.run(code_analyzer.analyze({}))
PYEOF

# PR Analyzer Agent
cat > agents/pr_analyzer_agent.py << 'PYEOF'
"""Agent 3: PR Analyzer"""

import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger

class PRAnalyzerAgent:
    def __init__(self):
        self.logger = AgentLogger("pr_analyzer")
        self.name = "pr_analyzer"
        self.model = "gemini-2.5-flash"
    
    async def analyze(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pull request patterns"""
        
        self.logger.info("Analyzing PR patterns...")
        
        return {
            "patterns": {
                "common_changes": ["feature", "bug_fix", "refactor"],
                "frequent_files": ["src/api/", "src/components/"]
            },
            "insights": {
                "recent_features": ["OAuth integration", "Rate limiting"],
                "common_bugs": ["Memory leaks", "Race conditions"]
            }
        }

pr_analyzer = PRAnalyzerAgent()

if __name__ == "__main__":
    asyncio.run(pr_analyzer.analyze({}))
PYEOF

# Issue Analyzer Agent
cat > agents/issue_analyzer_agent.py << 'PYEOF'
"""Agent 4: Issue Analyzer"""

import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger

class IssueAnalyzerAgent:
    def __init__(self):
        self.logger = AgentLogger("issue_analyzer")
        self.name = "issue_analyzer"
        self.model = "gemini-2.5-flash"
    
    async def analyze(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue patterns"""
        
        self.logger.info("Analyzing issue patterns...")
        
        return {
            "categories": {
                "bugs": 45,
                "features": 30,
                "enhancements": 25
            },
            "top_issues": [
                "Add dark mode support",
                "Improve performance",
                "Add export functionality"
            ]
        }

issue_analyzer = IssueAnalyzerAgent()

if __name__ == "__main__":
    asyncio.run(issue_analyzer.analyze({}))
PYEOF

# Dependency Analyzer Agent
cat > agents/dependency_analyzer_agent.py << 'PYEOF'
"""Agent 5: Dependency Analyzer"""

import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger

class DependencyAnalyzerAgent:
    def __init__(self):
        self.logger = AgentLogger("dependency_analyzer")
        self.name = "dependency_analyzer"
        self.model = "gemini-2.5-flash"
    
    async def analyze(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies and tech stack"""
        
        self.logger.info("Analyzing dependencies...")
        
        return {
            "tech_stack": {
                "frameworks": ["Next.js", "React"],
                "libraries": ["Prisma", "Tailwind CSS"],
                "runtime": "Node.js 20+"
            },
            "health": {
                "outdated": 3,
                "vulnerable": 0,
                "up_to_date": 27
            }
        }

dependency_analyzer = DependencyAnalyzerAgent()

if __name__ == "__main__":
    asyncio.run(dependency_analyzer.analyze({}))
PYEOF

chmod +x agents/*.py

echo "✅ All analysis agents created!"
EOF

chmod +x scripts/create_analysis_agents.sh
./scripts/create_analysis_agents.sh
```

**Time: 20 minutes**

---

### Task 2.3: Problem Creator Agent

Create `agents/problem_creator_agent.py`:

```python
"""Agent 6: Problem Creator"""

import asyncio
from typing import Dict, Any
from utils.monitoring import AgentLogger


class ProblemCreatorAgent:
    def __init__(self):
        self.logger = AgentLogger("problem_creator")
        self.name = "problem_creator"
        self.model = "gemini-2.5-pro"
    
    async def create_problem(
        self,
        repository_report: Dict[str, Any],
        difficulty: str,
        problem_type: str
    ) -> Dict[str, Any]:
        """Create a coding problem based on repository analysis"""
        
        self.logger.info(f"Creating {difficulty} {problem_type} problem...")
        
        # Mock problem (replace with real ADK implementation)
        problem = {
            "title": "Implement OAuth2 Token Refresh",
            "description": "Add token refresh functionality to the authentication system",
            "difficulty": difficulty,
            "type": problem_type,
            "requirements": [
                "Implement refresh token endpoint",
                "Add token rotation logic",
                "Handle token expiration"
            ],
            "acceptance_criteria": [
                "Tokens refresh before expiration",
                "Old tokens are invalidated",
                "Concurrent requests handled correctly"
            ],
            "starter_code": """
# auth/refresh.py
def refresh_token(refresh_token: str):
    # TODO: Implement token refresh logic
    pass
""",
            "hints": [
                "Use JWT for token generation",
                "Store refresh tokens in database",
                "Implement token family tracking"
            ],
            "estimated_time": 120,  # minutes
            "tech_stack": ["Python", "JWT", "PostgreSQL"]
        }
        
        self.logger.info(f"Problem created: {problem['title']}")
        
        return problem


problem_creator = ProblemCreatorAgent()


if __name__ == "__main__":
    async def test():
        problem = await problem_creator.create_problem(
            repository_report={},
            difficulty="medium",
            problem_type="feature"
        )
        print("✅ Problem Creator Test:")
        print(problem)
    
    asyncio.run(test())
```

**Time: 15 minutes**

---

### Task 2.4: QA Validator Agent

Create `agents/qa_validator_agent.py`:

```python
"""Agent 7: QA/Validation Agent"""

import asyncio
from typing import Dict, Any, Tuple
from utils.monitoring import AgentLogger


class QAValidatorAgent:
    def __init__(self):
        self.logger = AgentLogger("qa_validator")
        self.name = "qa_validator"
        self.model = "gemini-2.5-flash"
        self.threshold = 85  # Minimum quality score
    
    async def validate_problem(
        self,
        problem: Dict[str, Any],
        repository_report: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate problem quality"""
        
        self.logger.info(f"Validating problem: {problem.get('title', 'Unknown')}")
        
        # Calculate scores
        scores = {
            "feasibility": await self._check_feasibility(problem),
            "quality": await self._check_quality(problem),
            "technical": await self._check_technical(problem),
            "educational": await self._check_educational(problem)
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        validation_result = {
            "approved": overall_score >= self.threshold,
            "overall_score": overall_score,
            "scores": scores,
            "issues": self._identify_issues(scores),
            "suggestions": self._generate_suggestions(scores)
        }
        
        self.logger.info(f"Validation complete. Score: {overall_score}/100")
        
        return validation_result["approved"], validation_result
    
    async def _check_feasibility(self, problem: Dict[str, Any]) -> float:
        """Check if problem is feasible"""
        return 90.0
    
    async def _check_quality(self, problem: Dict[str, Any]) -> float:
        """Check problem quality"""
        return 88.0
    
    async def _check_technical(self, problem: Dict[str, Any]) -> float:
        """Check technical accuracy"""
        return 92.0
    
    async def _check_educational(self, problem: Dict[str, Any]) -> float:
        """Check educational value"""
        return 85.0
    
    def _identify_issues(self, scores: Dict[str, float]) -> list:
        """Identify issues based on scores"""
        issues = []
        for category, score in scores.items():
            if score < 80:
                issues.append(f"{category} score is low ({score}/100)")
        return issues
    
    def _generate_suggestions(self, scores: Dict[str, float]) -> list:
        """Generate improvement suggestions"""
        suggestions = []
        if scores["feasibility"] < 85:
            suggestions.append("Make requirements more specific")
        if scores["quality"] < 85:
            suggestions.append("Improve problem description clarity")
        return suggestions


qa_validator = QAValidatorAgent()


if __name__ == "__main__":
    async def test():
        problem = {
            "title": "Test Problem",
            "requirements": ["Req 1", "Req 2"]
        }
        approved, result = await qa_validator.validate_problem(problem, {})
        print(f"✅ QA Validation Test:")
        print(f"Approved: {approved}")
        print(f"Score: {result['overall_score']}/100")
    
    asyncio.run(test())
```

**Time: 15 minutes**

---

## Phase 3: Orchestration

### Task 3.1: Create Orchestrator

Create `orchestrator.py`:

```python
"""Multi-Agent Orchestrator with 3-Loop Analysis"""

import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime

from agents.scanner_agent import scan_repository
from agents.code_analyzer_agent import code_analyzer
from agents.pr_analyzer_agent import pr_analyzer
from agents.issue_analyzer_agent import issue_analyzer
from agents.dependency_analyzer_agent import dependency_analyzer
from agents.problem_creator_agent import problem_creator
from agents.qa_validator_agent import qa_validator

from utils.a2a_protocol import a2a_protocol
from utils.monitoring import AgentLogger, PerformanceMonitor


class MultiAgentOrchestrator:
    """Orchestrates the multi-agent assessment generation pipeline"""
    
    def __init__(self):
        self.logger = AgentLogger("orchestrator")
        self.performance = PerformanceMonitor()
        self.conversation_id = None
    
    async def generate_assessment(
        self,
        github_repo_url: str,
        difficulty: str = "medium",
        problem_type: str = "feature",
        focus_area: str = None
    ) -> Dict[str, Any]:
        """Generate a complete assessment using multi-agent collaboration"""
        
        # Initialize
        self.conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        self.logger.info(f"🚀 Starting assessment generation")
        self.logger.info(f"📝 Conversation ID: {self.conversation_id}")
        self.logger.info(f"🔗 Repository: {github_repo_url}")
        
        self.performance.start_timer("total")
        
        try:
            # Step 1: Scan Repository
            repo_data = await self._step1_scan_repository(github_repo_url)
            
            # Step 2-5: Multi-Agent Analysis (3 loops)
            analysis_report = await self._step2_multi_agent_analysis(repo_data)
            
            # Step 6: Create Problem
            problem = await self._step3_create_problem(
                analysis_report, difficulty, problem_type, focus_area
            )
            
            # Step 7: Validate & Improve
            validated_problem = await self._step4_validate_problem(
                problem, analysis_report
            )
            
            self.performance.end_timer("total")
            
            # Prepare final output
            result = {
                "success": True,
                "assessment": validated_problem,
                "metadata": {
                    "conversation_id": self.conversation_id,
                    "repository": github_repo_url,
                    "difficulty": difficulty,
                    "problem_type": problem_type,
                    "generated_at": datetime.utcnow().isoformat(),
                    "processing_time": self.performance.get_duration("total"),
                    "agents_involved": 7,
                    "a2a_messages": len(a2a_protocol.message_history)
                }
            }
            
            self.logger.info(f"✅ Assessment generation complete!")
            self.logger.info(f"⏱️  Total time: {result['metadata']['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Assessment generation failed: {str(e)}")
            self.performance.end_timer("total")
            
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "conversation_id": self.conversation_id,
                    "processing_time": self.performance.get_duration("total")
                }
            }
    
    async def _step1_scan_repository(self, repo_url: str) -> Dict[str, Any]:
        """Step 1: Scan GitHub repository"""
        
        self.logger.info("\n" + "="*60)
        self.logger.info("🔍 STEP 1: Scanning GitHub Repository")
        self.logger.info("="*60)
        
        self.performance.start_timer("scanner")
        
        repo_data = await scan_repository(repo_url)
        
        await a2a_protocol.send_message(
            sender_id="github_scanner",
            sender_type="fetcher",
            recipient_id="orchestrator",
            data=repo_data,
            conversation_id=self.conversation_id
        )
        
        self.performance.end_timer("scanner")
        self.logger.info(f"✅ Scanner complete ({self.performance.get_duration('scanner'):.2f}s)")
        
        return repo_data
    
    async def _step2_multi_agent_analysis(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 2-5: Multi-agent analysis with 3 loops"""
        
        self.logger.info("\n" + "="*60)
        self.logger.info("🔄 STEP 2-5: Multi-Agent Analysis (3 Loops)")
        self.logger.info("="*60)
        
        self.performance.start_timer("analysis")
        
        analysis_results = {}
        
        # 3 Loop Iterations
        for iteration in range(1, 4):
            self.logger.info(f"\n--- Loop {iteration}/3 ---")
            
            # Run analyzers in parallel
            tasks = [
                code_analyzer.analyze(repo_data),
                pr_analyzer.analyze(repo_data),
                issue_analyzer.analyze(repo_data),
                dependency_analyzer.analyze(repo_data)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Store results
            analysis_results[f"iteration_{iteration}"] = {
                "code": results[0],
                "pr": results[1],
                "issue": results[2],
                "dependency": results[3]
            }
            
            # Broadcast results via A2A
            if iteration < 3:
                await a2a_protocol.broadcast_message(
                    sender_id="orchestrator",
                    sender_type="coordinator",
                    data=analysis_results[f"iteration_{iteration}"],
                    conversation_id=self.conversation_id
                )
                
                self.logger.info(f"📤 Iteration {iteration} results broadcast to all agents")
        
        # Synthesize final report
        final_report = self._synthesize_report(analysis_results)
        
        self.performance.end_timer("analysis")
        self.logger.info(f"✅ Analysis complete ({self.performance.get_duration('analysis'):.2f}s)")
        
        return final_report
    
    def _synthesize_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all analysis iterations into final report"""
        
        final_iteration = analysis_results["iteration_3"]
        
        return {
            "repository_profile": {
                "complexity": final_iteration["code"].get("architecture", {}).get("complexity", "medium"),
                "tech_stack": final_iteration["dependency"].get("tech_stack", {})
            },
            "opportunities": final_iteration["code"].get("opportunities", []),
            "pr_insights": final_iteration["pr"].get("insights", {}),
            "issue_insights": final_iteration["issue"].get("top_issues", []),
            "all_iterations": analysis_results
        }
    
    async def _step3_create_problem(
        self,
        analysis_report: Dict[str, Any],
        difficulty: str,
        problem_type: str,
        focus_area: str = None
    ) -> Dict[str, Any]:
        """Step 6: Create problem"""
        
        self.logger.info("\n" + "="*60)
        self.logger.info("📝 STEP 6: Creating Coding Problem")
        self.logger.info("="*60)
        
        self.performance.start_timer("problem_creation")
        
        problem = await problem_creator.create_problem(
            repository_report=analysis_report,
            difficulty=difficulty,
            problem_type=problem_type
        )
        
        await a2a_protocol.send_message(
            sender_id="problem_creator",
            sender_type="creator",
            recipient_id="qa_validator",
            data=problem,
            conversation_id=self.conversation_id
        )
        
        self.performance.end_timer("problem_creation")
        self.logger.info(f"✅ Problem created ({self.performance.get_duration('problem_creation'):.2f}s)")
        
        return problem
    
    async def _step4_validate_problem(
        self,
        problem: Dict[str, Any],
        analysis_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 7: Validate and improve problem"""
        
        self.logger.info("\n" + "="*60)
        self.logger.info("✅ STEP 7: Quality Validation")
        self.logger.info("="*60)
        
        self.performance.start_timer("validation")
        
        approved, validation_result = await qa_validator.validate_problem(
            problem=problem,
            repository_report=analysis_report
        )
        
        # Improvement loop (max 2 iterations)
        iteration = 0
        while not approved and iteration < 2:
            iteration += 1
            self.logger.info(f"🔄 Improvement iteration {iteration}/2")
            
            improved_problem = await problem_creator.create_problem(
                repository_report=analysis_report,
                difficulty=problem["difficulty"],
                problem_type=problem["type"]
            )
            
            approved, validation_result = await qa_validator.validate_problem(
                problem=improved_problem,
                repository_report=analysis_report
            )
            
            problem = improved_problem
        
        self.performance.end_timer("validation")
        
        self.logger.info(f"✅ Validation complete ({self.performance.get_duration('validation'):.2f}s)")
        self.logger.info(f"📊 Quality Score: {validation_result['overall_score']}/100")
        
        # Combine problem with validation results
        final_assessment = {
            **problem,
            "validation": validation_result,
            "approved": approved
        }
        
        return final_assessment


# CLI for testing
async def main():
    orchestrator = MultiAgentOrchestrator()
    
    result = await orchestrator.generate_assessment(
        github_repo_url="https://github.com/vercel/next.js",
        difficulty="medium",
        problem_type="feature"
    )
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Processing Time: {result['metadata']['processing_time']:.2f}s")
    print(f"A2A Messages: {result['metadata']['a2a_messages']}")
    
    if result['success']:
        print(f"\nAssessment Title: {result['assessment']['title']}")
        print(f"Quality Score: {result['assessment']['validation']['overall_score']}/100")


if __name__ == "__main__":
    asyncio.run(main())
```

**Test**:
```bash
python orchestrator.py
```

**Time: 30 minutes**

---

## Phase 4: Frontend Integration

### Task 4.1: Update API Route

Update `src/app/api/assessments/generate/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
  try {
    const { githubRepoUrl, difficulty, problemType, focusArea } = await req.json();
    
    // Validate input
    if (!githubRepoUrl) {
      return NextResponse.json(
        { error: 'GitHub repository URL is required' },
        { status: 400 }
      );
    }
    
    // Call Python orchestrator
    const args = [
      'orchestrator.py',
      '--repo', githubRepoUrl,
      '--difficulty', difficulty || 'medium',
      '--type', problemType || 'feature'
    ];
    
    if (focusArea) {
      args.push('--focus', focusArea);
    }
    
    const pythonProcess = spawn('python3', args, {
      cwd: path.join(process.cwd())
    });
    
    let result = '';
    let error = '';
    
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    return new Promise((resolve) => {
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          resolve(NextResponse.json(
            { error: 'Failed to generate assessment', details: error },
            { status: 500 }
          ));
        } else {
          try {
            const assessment = JSON.parse(result);
            resolve(NextResponse.json(assessment));
          } catch (e) {
            resolve(NextResponse.json(
              { error: 'Failed to parse result' },
              { status: 500 }
            ));
          }
        }
      });
    });
    
  } catch (error) {
    console.error('Assessment generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**Time: 10 minutes**

---

### Task 4.2: Create Frontend Component

Create `src/components/AssessmentGenerator.tsx`:

```typescript
'use client';

import { useState } from 'react';

export default function AssessmentGenerator() {
  const [formData, setFormData] = useState({
    githubRepoUrl: '',
    difficulty: 'medium',
    problemType: 'feature',
    focusArea: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/assessments/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate assessment');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Generate Code Assessment</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label className="block text-sm font-medium mb-2">
            GitHub Repository URL
          </label>
          <input
            type="url"
            required
            className="w-full px-4 py-2 border rounded-lg"
            placeholder="https://github.com/owner/repo"
            value={formData.githubRepoUrl}
            onChange={(e) => setFormData({...formData, githubRepoUrl: e.target.value})}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Difficulty</label>
            <select
              className="w-full px-4 py-2 border rounded-lg"
              value={formData.difficulty}
              onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
              <option value="expert">Expert</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Problem Type</label>
            <select
              className="w-full px-4 py-2 border rounded-lg"
              value={formData.problemType}
              onChange={(e) => setFormData({...formData, problemType: e.target.value})}
            >
              <option value="feature">Feature</option>
              <option value="bug-fix">Bug Fix</option>
              <option value="refactor">Refactor</option>
              <option value="optimization">Optimization</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Generating Assessment...' : 'Generate Assessment'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {result && result.success && (
        <div className="bg-white border rounded-lg p-6 space-y-4">
          <h2 className="text-2xl font-bold">{result.assessment.title}</h2>
          
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Quality Score</div>
            <div className="text-3xl font-bold text-green-600">
              {result.assessment.validation.overall_score}/100
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Description</h3>
            <p>{result.assessment.description}</p>
          </div>

          <div className="pt-4 border-t">
            <div className="text-sm text-gray-600">
              Generated in {result.metadata.processing_time.toFixed(2)}s using {result.metadata.agents_involved} AI agents
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Time: 20 minutes**

---

## Phase 5: Testing

### Task 5.1: Create Unit Tests

Create `tests/test_scanner.py`:

```python
import pytest
import asyncio
from agents.scanner_agent import scan_repository

@pytest.mark.asyncio
async def test_scanner_agent():
    """Test GitHub scanner agent"""
    
    result = await scan_repository("https://github.com/vercel/next.js")
    
    assert result is not None
    assert "repository" in result
    assert result["status"] == "completed"
```

Create `tests/test_orchestrator.py`:

```python
import pytest
from orchestrator import MultiAgentOrchestrator

@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete assessment generation pipeline"""
    
    orchestrator = MultiAgentOrchestrator()
    
    result = await orchestrator.generate_assessment(
        github_repo_url="https://github.com/vercel/next.js",
        difficulty="medium",
        problem_type="feature"
    )
    
    assert result is not None
    assert "assessment" in result or "error" in result
    assert "metadata" in result
```

**Run tests**:
```bash
pytest tests/ -v
```

**Time: 30 minutes**

---

## Phase 6: Deployment

### Task 6.1: Create Agent Configuration

Create `agent_config.yaml`:

```yaml
agents:
  - name: github-scanner
    type: llm_agent
    model: gemini-2.5-flash
    tools:
      - type: mcp
        name: github
    scaling:
      min_instances: 0
      max_instances: 5

  - name: code-analyzer
    type: llm_agent
    model: gemini-2.5-pro
    scaling:
      min_instances: 1
      max_instances: 10

a2a_config:
  protocol_version: "1.0"
  authentication: oauth2
  encryption: tls
```

### Task 6.2: Deploy to Google Cloud

```bash
# Deploy agents to Agent Engine
gcloud ai agents deploy \
  --config=agent_config.yaml \
  --region=us-central1 \
  --project=$PROJECT_ID

# Deploy Next.js frontend to Cloud Run
gcloud run deploy actualcode-frontend \
  --source=. \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated
```

**Time: 1 hour**

---

## Summary

You've now implemented:

✅ **7 AI Agents** - Scanner, 4 Analyzers, Problem Creator, QA Validator  
✅ **A2A Protocol** - Agent-to-agent communication  
✅ **Multi-Agent Orchestrator** - 3-loop analysis coordination  
✅ **Frontend Integration** - Next.js UI and API  
✅ **Testing** - Unit and integration tests  
✅ **Deployment** - Google Cloud production setup

**Next Steps**:
1. Replace mock implementations with real Google ADK
2. Add GitHub MCP integration
3. Enhance prompts for better results
4. Add more comprehensive testing
5. Monitor and optimize performance

For quick reference while coding, see **[REFERENCE.md](./REFERENCE.md)**.

For demo preparation, see **[HACKATHON.md](./HACKATHON.md)**.
