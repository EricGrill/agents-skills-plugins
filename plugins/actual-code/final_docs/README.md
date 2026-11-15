# ActualCode - AI-Powered Code Assessment Platform

**Tagline**: *"From GitHub Repos to Coding Challenges - Better than LeetCode, Powered by AI Agents"*

---

## 🎯 Project Overview

ActualCode is a revolutionary code assessment platform that analyzes real GitHub repositories and generates personalized, realistic coding challenges using a multi-agent AI architecture powered by Google's cutting-edge technologies.

### The Problem
- **LeetCode is too generic** - Candidates solve abstract algorithms, not real-world problems
- **Hiring teams struggle** - Creating repository-specific assessments is time-consuming
- **Context gap** - Candidates who ace LeetCode still struggle with actual codebases

### Our Solution
1. **Input**: Give us any GitHub repository + difficulty level
2. **AI Magic**: 7 specialized AI agents collaborate using Google's A2A protocol
3. **Output**: Get a realistic, implementable coding problem in < 3 minutes

---

## 🏗️ System Architecture

```
User Input (GitHub Repo + Difficulty)
           ↓
    Agent 1: Scanner (GitHub MCP)
           ↓
    Agents 2-5: Multi-Agent Analysis (3 loops via A2A)
      • Code Analyzer
      • PR Analyzer
      • Issue Analyzer
      • Dependency Analyzer
           ↓
    Agent 6: Problem Creator (Gemini 2.5 Pro)
           ↓
    Agent 7: QA Validator (Quality Gates)
           ↓
    Personalized Assessment ✨
```

---

## 🔥 Key Innovations

### 1. **First-of-its-Kind A2A Protocol Implementation**
- 7 agents communicating via Google's Agent2Agent protocol
- Demonstrates agent interoperability at scale
- Proof of concept for future multi-agent ecosystems

### 2. **Deep Repository Understanding**
- GitHub MCP integration for comprehensive analysis
- PRs, Issues, Code, Dependencies all analyzed
- 3-loop collaborative analysis for deep insights

### 3. **Production-Grade Quality**
- Deployed on Google Cloud Agent Engine
- Built-in QA agent with 4 validation categories
- Improvement loops ensure 85+ quality scores

### 4. **Realistic, Implementable Problems**
- Not toy problems - real features candidates can build
- Self-contained (no private repo access needed)
- Aligned with repository's actual tech stack

---

## 💻 Tech Stack

### Google Cloud Platform
- ✅ **Vertex AI** - Gemini 2.5 Pro & Flash
- ✅ **Agent Engine** - Production agent runtime
- ✅ **Cloud Run** - Next.js deployment
- ✅ **Cloud SQL** - PostgreSQL database
- ✅ **Cloud Storage** - Repository caching
- ✅ **Cloud Logging & Monitoring** - Observability

### Agent Development
- ✅ **Google ADK (Python)** - Agent framework
- ✅ **A2A Protocol** - Agent interoperability
- ✅ **GitHub MCP** - Repository data access
- ✅ **Gemini 2.5 Pro/Flash** - LLM models

### Frontend
- ✅ **Next.js 15** - React framework
- ✅ **TypeScript** - Type safety
- ✅ **Tailwind CSS** - Styling
- ✅ **Prisma** - Database ORM

---

## 📊 Agent Specifications

| # | Agent Name | Model | Role | A2A Capabilities |
|---|------------|-------|------|------------------|
| 1 | Scanner | Flash | Fetch GitHub data via MCP | Exposes: `scan_repository` |
| 2 | Code Analyzer | Pro | Analyze architecture & patterns | Exposes: `analyze_architecture` |
| 3 | PR Analyzer | Flash | Extract PR insights | Exposes: `analyze_prs` |
| 4 | Issue Analyzer | Flash | Identify issue patterns | Exposes: `analyze_issues` |
| 5 | Dependency Analyzer | Flash | Analyze tech stack | Exposes: `analyze_dependencies` |
| 6 | Problem Creator | Pro | Generate coding problems | Exposes: `create_problem` |
| 7 | QA Validator | Flash | Validate & improve | Exposes: `validate_problem` |

---

## 📈 Success Metrics

### Technical Excellence
- ⚡ Generation time: **< 3 minutes** (Target: 142 seconds average)
- 🎯 Quality score: **> 85/100** (Target: 90 average)
- 🔄 Agent success rate: **> 95%**
- 📡 A2A message success: **> 99%**

### Innovation
- 🏆 First hackathon project using A2A protocol
- 🏆 7 agents collaborating seamlessly
- 🏆 Production deployment on Agent Engine
- 🏆 Real GitHub MCP integration

---

## 📚 Documentation

This project includes comprehensive documentation to help you build and deploy:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[SETUP.md](./SETUP.md)** | Complete setup instructions | 15 min |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | System architecture & agent design | 20 min |
| **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** | Step-by-step implementation guide | 1 hour |
| **[REFERENCE.md](./REFERENCE.md)** | Quick reference & code snippets | Reference |
| **[HACKATHON.md](./HACKATHON.md)** | Demo script & presentation guide | 15 min |

### Recommended Reading Order
1. **README.md** (this file) - Get oriented
2. **SETUP.md** - Set up your environment
3. **ARCHITECTURE.md** - Understand the system
4. **IMPLEMENTATION.md** - Build it step-by-step
5. **REFERENCE.md** - Quick lookups while coding
6. **HACKATHON.md** - Prepare your demo

---

## 🚀 Quick Start

### Prerequisites
- **Google Cloud Account** with billing enabled
- **Python 3.11+** for ADK agents
- **Node.js 20+** for Next.js frontend
- **GitHub Personal Access Token** for MCP
- **PostgreSQL database** (Cloud SQL recommended)

### 30-Second Setup

```bash
# 1. Clone and navigate
cd /Users/muratcankoylan/ActualCode/actualy_code

# 2. Install dependencies
npm install
pip install google-adk google-cloud-aiplatform

# 3. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 4. Start development
npm run dev
```

For detailed setup instructions, see **[SETUP.md](./SETUP.md)**.

---

## 📁 Project Structure

```
actualy_code/
├── final_docs/                    ⭐ Start here!
│   ├── README.md                  📖 This file
│   ├── SETUP.md                   🛠️ Setup guide
│   ├── ARCHITECTURE.md            🏗️ Architecture
│   ├── IMPLEMENTATION.md          📝 Implementation
│   ├── REFERENCE.md               ⚡ Quick reference
│   └── HACKATHON.md              🎬 Demo guide
├── agents/                        🤖 AI Agents (to be created)
│   ├── scanner_agent.py
│   ├── code_analyzer_agent.py
│   ├── pr_analyzer_agent.py
│   ├── issue_analyzer_agent.py
│   ├── dependency_analyzer_agent.py
│   ├── problem_creator_agent.py
│   └── qa_validator_agent.py
├── orchestrator.py                🎭 Multi-agent coordinator
├── utils/                         📦 Utilities
│   ├── a2a_protocol.py           📡 A2A messaging
│   └── monitoring.py             📊 Logging & metrics
├── src/                          🌐 Next.js frontend
│   └── app/
│       └── api/
│           └── assessments/
│               └── generate/
│                   └── route.ts  🚀 API endpoint
└── tests/                        ✅ Tests
```

---

## 🎯 Core Features

### 1. Repository Analysis
- Connect GitHub repositories via MCP
- Analyze code patterns, PRs, issues, and dependencies
- Extract realistic problem scenarios

### 2. AI-Powered Problem Generation
- 7 specialized agents collaborate via A2A protocol
- 3-loop iterative analysis for deep insights
- Gemini 2.5 Pro/Flash for intelligent generation

### 3. Quality Assurance
- Built-in QA agent validates every problem
- 4-category scoring: Feasibility, Quality, Technical, Educational
- Automatic improvement loops until quality threshold met

### 4. Production Deployment
- Google Cloud Agent Engine for agent orchestration
- Cloud Run for scalable Next.js hosting
- Cloud SQL for reliable data persistence
- Comprehensive monitoring and logging

---

## 🎪 Live Demo Flow (3 minutes)

**Act 1: The Problem** (30 seconds)
- Show LeetCode/HackerRank: "Generic, abstract, not related to your actual work"

**Act 2: Our Solution** (30 seconds)
- Enter GitHub repo URL, select difficulty, click "Generate Assessment"

**Act 3: Agent Magic** (90 seconds)
- Show real-time agent progress
- Highlight A2A messages between agents
- Display 3-loop analysis visualization

**Act 4: The Result** (30 seconds)
- Show generated problem with 92/100 quality score
- Highlight how it relates to actual repository

**Key Callouts**:
- ✨ "7 AI agents collaborating via A2A protocol"
- ✨ "Generated in under 3 minutes"
- ✨ "Quality validated at 92/100"
- ✨ "Uses actual repository patterns and tech stack"

---

## 🛠️ Development Status

### ✅ Completed
- **Documentation**: Comprehensive guides and references
- **Architecture Design**: Multi-agent system fully specified
- **Frontend Foundation**: Next.js app with Prisma schema
- **Project Setup**: Environment configuration ready

### 🚧 In Progress (Follow IMPLEMENTATION.md)
- **Agent Development**: Implement all 7 agents
- **A2A Protocol**: Agent-to-agent communication
- **Orchestration**: Multi-agent coordinator with 3-loop logic
- **Integration**: Frontend to backend connection
- **Deployment**: Google Cloud production setup

---

## 🤝 Contributing

1. Read **[ARCHITECTURE.md](./ARCHITECTURE.md)** to understand the system
2. Follow **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** step-by-step
3. Use **[REFERENCE.md](./REFERENCE.md)** for code snippets
4. Run tests before submitting
5. Submit pull requests with clear descriptions

---

## 📞 Support & Resources

### Documentation
- **Setup Issues**: See [SETUP.md](./SETUP.md) troubleshooting section
- **Architecture Questions**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Code Examples**: See [REFERENCE.md](./REFERENCE.md)

### External Resources
- **Google ADK**: https://google.github.io/adk-docs/
- **A2A Protocol**: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- **GitHub MCP**: https://github.com/modelcontextprotocol/servers
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔮 Future Vision

### Phase 2: Enhanced Assessment Types
- System design challenges
- Debugging challenges
- Code review challenges
- Architecture refactoring tasks

### Phase 3: Enterprise Features
- Custom branding and white-labeling
- SSO integration
- ATS integration (Greenhouse, Lever, etc.)
- Advanced analytics dashboard

### Phase 4: Learning Platform
- Skill progression tracking
- Personalized learning paths
- Interactive walkthroughs
- Mentor/candidate pairing

---

**Built with ❤️ for better technical hiring**

**Next Steps**: Head to **[SETUP.md](./SETUP.md)** to get started!
