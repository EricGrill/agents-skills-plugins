# ⚡ Quick Reference Guide

Essential commands, code snippets, and troubleshooting for rapid development.

---

## 🚀 Essential Commands

### Google Cloud

```bash
# Set project
export PROJECT_ID="actualcode-hackathon"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com run.googleapis.com sqladmin.googleapis.com storage.googleapis.com

# Deploy agents
gcloud ai agents deploy --config=agent_config.yaml --region=us-central1

# Deploy frontend
gcloud run deploy actualcode-frontend --source=. --region=us-central1

# View logs
gcloud logging tail "resource.type=cloud_run_revision"
```

### Development

```bash
# Activate Python venv
source venv/bin/activate

# Start Next.js dev server
npm run dev

# Run orchestrator
python orchestrator.py

# Run tests
pytest tests/ -v

# Run specific agent
python agents/scanner_agent.py
```

### Database

```bash
# Generate Prisma client
npx prisma generate

# Push schema to database
npx prisma db push

# Open Prisma Studio
npx prisma studio

# Reset database (WARNING: deletes data)
npx prisma db push --force-reset
```

---

## 📝 Code Snippets

### 1. Basic ADK Agent

```python
from adk import LlmAgent

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    system_instruction="You are...",
    a2a_capabilities={
        "exposes": ["capability_name"],
        "consumes": ["other_capability"],
        "protocol_version": "1.0"
    }
)

# Run agent
result = await agent.run("Your prompt here")
```

### 2. GitHub MCP Setup

```python
from adk.tools import MCPTool
import os

github_mcp = MCPTool(
    name="github",
    server_config={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
    }
)

# Use in agent
agent = LlmAgent(
    name="scanner",
    model="gemini-2.5-flash",
    tools=[github_mcp]
)
```

### 3. A2A Message

```python
from utils.a2a_protocol import A2AMessage, a2a_protocol

# Send message
message = await a2a_protocol.send_message(
    sender_id="agent_1",
    sender_type="analyzer",
    recipient_id="agent_2",
    data={"key": "value"},
    conversation_id="conv_123"
)

# Broadcast to all agents
await a2a_protocol.broadcast_message(
    sender_id="orchestrator",
    sender_type="coordinator",
    data={"results": "..."},
    conversation_id="conv_123"
)
```

### 4. Parallel Agents

```python
import asyncio

# Run agents in parallel
tasks = [
    code_analyzer.analyze(data),
    pr_analyzer.analyze(data),
    issue_analyzer.analyze(data),
    dependency_analyzer.analyze(data)
]

results = await asyncio.gather(*tasks)
```

### 5. Performance Monitoring

```python
from utils.monitoring import AgentLogger, PerformanceMonitor

# Logger
logger = AgentLogger("my_agent")
logger.info("Processing started")
logger.error("Error occurred", error_details="...")

# Performance tracking
perf = PerformanceMonitor()
perf.start_timer("operation")
# ... do work ...
perf.end_timer("operation")
duration = perf.get_duration("operation")
```

### 6. Error Handling with Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_retry():
    # Your code here
    return await agent.run(prompt)
```

---

## 🎯 Agent Prompts

### Scanner Agent

```python
system_instruction = """You are a GitHub repository scanner.

Retrieve:
1. Repository metadata (name, description, stars, language)
2. File structure (directories and key files)
3. Last 20 issues
4. Last 20 pull requests
5. Last 50 commits
6. README content
7. Dependencies from package.json/requirements.txt

Use GitHub MCP tools. Output structured JSON."""
```

### Code Analyzer

```python
system_instruction = """You are a senior software architect.

Analyze the codebase for:
1. Architectural patterns (MVC, microservices, etc.)
2. Code complexity (low/medium/high)
3. Code quality indicators
4. Feature opportunities for coding challenges

Focus on REALISTIC, IMPLEMENTABLE problems.
Output JSON with architecture, complexity, quality, and opportunities."""
```

### Problem Creator

```python
system_instruction = """You are a technical interviewer.

Create REALISTIC coding assessments that:
- Are completable in 2-4 hours
- Match the repository's tech stack
- Are self-contained (no private repo access)
- Have clear requirements and acceptance criteria
- Include helpful starter code

Output JSON with title, description, requirements, 
acceptance_criteria, starter_code, and hints."""
```

### QA Validator

```python
system_instruction = """You are a strict QA reviewer.

Validate assessments on:
1. Feasibility (can be completed in time limit)
2. Quality (clear, testable requirements)
3. Technical accuracy (correct tech stack)
4. Educational value (tests relevant skills)

Score each category 0-100.
If overall < 85, REJECT with specific improvements.
Output JSON with scores, issues, and suggestions."""
```

---

## 🔧 Next.js API Route

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { githubRepoUrl, difficulty, problemType } = await req.json();
  
  // Validate
  if (!githubRepoUrl) {
    return NextResponse.json({ error: 'URL required' }, { status: 400 });
  }
  
  // Call Python orchestrator or Agent Engine
  // Return results
  
  return NextResponse.json({ success: true, data: result });
}
```

---

## 🗄️ Database Schema Snippets

```prisma
// Assessment model
model Assessment {
  id                String   @id @default(uuid())
  title             String
  description       String
  requirements      String[]
  acceptanceCriteria String[]
  difficulty        String
  estimatedTime     Int
  qualityScore      Int
  
  repositoryUrl     String
  repositoryName    String
  
  createdAt         DateTime @default(now())
  
  conversationId    String
  agentsInvolved    String[]
  processingTime    Int
  
  @@index([repositoryUrl])
  @@index([difficulty])
}
```

---

## 🔍 Debugging

### View A2A Messages

```python
# In your code
from utils.a2a_protocol import a2a_protocol

# Get all messages for a conversation
messages = a2a_protocol.get_message_history("conv_123")
for msg in messages:
    print(f"{msg.sender_id} → {msg.recipient_id}: {msg.message_type}")
```

### View Cloud Logs

```bash
# Recent logs
gcloud logging read 'resource.type="cloud_run_revision"' --limit=50 --format=json

# Filter by agent
gcloud logging read 'resource.type="cloud_run_revision" AND jsonPayload.agent_name="scanner"' --limit=20

# Follow logs real-time
gcloud logging tail "resource.type=cloud_run_revision"
```

### Test Single Agent

```python
# test_agent.py
import asyncio
from agents.scanner_agent import scanner_agent

async def test():
    result = await scanner_agent.run("Scan https://github.com/vercel/next.js")
    print(result)

asyncio.run(test())
```

---

## 📦 Environment Variables

```bash
# .env file
GOOGLE_CLOUD_PROJECT=actualcode-hackathon
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_CLIENT_ID=xxxxxxxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxx
DATABASE_URL=postgresql://user:pass@host:5432/db
NEXTAUTH_SECRET=xxxxxxxxxxxxx
NEXTAUTH_URL=http://localhost:3000
AGENT_ENGINE_URL=https://your-agent-engine-url
```

---

## 🎯 Key Metrics to Monitor

```typescript
const metrics = {
  // Performance
  total_generation_time: "< 3 minutes",
  scanner_time: "< 20 seconds",
  analysis_loop_time: "< 90 seconds",
  problem_creation_time: "< 30 seconds",
  qa_validation_time: "< 20 seconds",
  
  // Quality
  quality_score: "> 85/100",
  agent_success_rate: "> 95%",
  a2a_message_success: "> 99%",
  
  // Business
  user_satisfaction: "> 4.5/5",
  problem_uniqueness: "> 80%",
  completion_rate: "> 70%"
};
```

---

## 🚨 Common Issues & Solutions

### GitHub MCP Rate Limiting

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3)
)
async def fetch_with_retry():
    return await github_mcp.call()
```

### Agent Timeout

```python
# Set timeout in agent config
agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    timeout=60  # seconds
)
```

### Large Repository Handling

```python
def sample_large_repo(files: list, max_files: int = 50) -> list:
    """Sample files from large repositories"""
    if len(files) <= max_files:
        return files
    
    # Prioritize important files
    important = [f for f in files if any(
        keyword in f.path.lower() 
        for keyword in ['readme', 'package', 'main', 'index', 'app']
    )]
    
    return important[:max_files]
```

### A2A Message Failure Fallback

```python
try:
    result = await agent.send_a2a_message(message)
except Exception as e:
    logger.warning(f"A2A failed: {e}, using direct call")
    result = await agent.direct_call(data)
```

### Port Already in Use

```bash
# Find process on port 3000
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Database Connection Issues

```bash
# Test connection
psql -d assessment_platform -c "SELECT 1;"

# Check PostgreSQL status
pg_isready

# Restart PostgreSQL
brew services restart postgresql@15  # macOS
sudo systemctl restart postgresql    # Linux
```

---

## 📚 Important Links

- **Google ADK**: https://google.github.io/adk-docs/
- **A2A Protocol**: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- **GitHub MCP**: https://github.com/modelcontextprotocol/servers
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **Agent Engine**: https://cloud.google.com/agent-engine/docs
- **Next.js**: https://nextjs.org/docs
- **Prisma**: https://www.prisma.io/docs

---

## ✅ Pre-Deployment Checklist

- [ ] All 7 agents implemented
- [ ] A2A protocol working
- [ ] GitHub MCP integration tested
- [ ] End-to-end flow works
- [ ] Frontend UI complete
- [ ] Tests passing
- [ ] Environment variables set
- [ ] Database schema deployed
- [ ] Google Cloud project configured
- [ ] Monitoring set up

---

## 🎬 Quick Demo Script

```bash
# 1. Show the problem
"LeetCode is too generic. We need personalized assessments."

# 2. Input repository
"Enter any GitHub repo: https://github.com/vercel/next.js"

# 3. Show agent execution
"Watch 7 AI agents collaborate using Google's A2A protocol"

# 4. Highlight collaboration
"Agents 2-5 run in parallel, sharing insights via A2A messages"

# 5. Show result
"In under 3 minutes, we get a realistic, repository-specific problem"

# 6. Show quality
"QA agent validated this with a 92/100 quality score"

# 7. Tech stack
"Built with Google ADK, Gemini 2.5, Agent Engine, and A2A protocol"
```

---

**Pro Tips**:
1. Start with Agent 1 (Scanner) and test thoroughly before building others
2. Use mock implementations first, then replace with real ADK
3. Test each agent individually before orchestration
4. Monitor A2A messages to debug communication issues
5. Cache repository data to avoid rate limits
6. Use performance monitoring to optimize bottlenecks

**Remember**: A2A protocol is the key differentiator. Showcase agent-to-agent communication in your demo!
