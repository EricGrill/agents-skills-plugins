# 🏗️ System Architecture

Complete architectural specification for the ActualCode multi-agent assessment platform.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Agent Specifications](#agent-specifications)
3. [A2A Protocol](#a2a-protocol)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Performance Targets](#performance-targets)

---

## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Next.js)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Input Form  │  │  Progress    │  │  Results Display     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                 API LAYER (Next.js API Routes)                   │
│                 POST /api/assessments/generate                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│            GOOGLE CLOUD AGENT ENGINE RUNTIME                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           MULTI-AGENT SYSTEM (ADK + A2A)                   │ │
│  │                                                             │ │
│  │  Agent 1: Scanner → Agents 2-5: Analysis → Agent 6:       │ │
│  │  (GitHub MCP)       (3-loop parallel)    Problem Creator   │ │
│  │                                              ↓              │ │
│  │                                          Agent 7:           │ │
│  │                                        QA Validator         │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │Vertex AI │  │ GitHub   │  │Cloud SQL │
         │ (Gemini) │  │   MCP    │  │(Postgres)│
         └──────────┘  └──────────┘  └──────────┘
```

---

## Agent Specifications

### Agent 1: GitHub Scanner

**Purpose**: Retrieve comprehensive repository data using GitHub MCP

**Model**: Gemini 2.5 Flash  
**Tools**: GitHub MCP Server

**Inputs**:
```typescript
{
  githubRepoUrl: string;
  depth: 'shallow' | 'deep';
}
```

**Outputs** (via A2A):
```typescript
{
  repository: {
    name: string;
    description: string;
    language: string;
    stars: number;
  };
  codebase: {
    fileTree: FileNode[];
    totalFiles: number;
    languageDistribution: Record<string, number>;
  };
  pullRequests: PullRequest[];  // Last 20
  issues: Issue[];              // Last 20
  commits: Commit[];            // Last 50
  readme: string;
  dependencies: Dependency[];
}
```

**A2A Capabilities**:
- Exposes: `scan_repository`, `get_issues`, `get_pull_requests`
- Protocol Version: 1.0

**Implementation**:
```python
from adk import LlmAgent
from adk.tools import MCPTool

scanner_agent = LlmAgent(
    name="github_scanner",
    model="gemini-2.5-flash",
    tools=[github_mcp],
    system_instruction="""
    Retrieve comprehensive GitHub repository data:
    1. Repository metadata
    2. File structure
    3. Recent issues (20)
    4. Recent PRs (20)
    5. Recent commits (50)
    6. README content
    7. Dependencies
    
    Output structured JSON.
    """,
    a2a_capabilities={
        "exposes": ["scan_repository"],
        "protocol_version": "1.0"
    }
)
```

---

### Agent 2: Code Analyzer

**Purpose**: Analyze codebase architecture, patterns, and complexity

**Model**: Gemini 2.5 Pro  
**Tools**: None (pure analysis)

**Inputs** (via A2A):
```typescript
{
  codebase: CodebaseStructure;
  fileContents: FileContent[];
  languageDistribution: Record<string, number>;
}
```

**Analysis Focus**:
1. **Architectural Patterns** - MVC, microservices, event-driven, etc.
2. **Code Quality** - Complexity metrics, test coverage, documentation
3. **Technical Debt** - Outdated dependencies, code smells, refactoring needs
4. **Feature Opportunities** - Missing functionality, incomplete features

**Outputs** (via A2A):
```typescript
{
  architecture: {
    pattern: string;
    layers: string[];
    complexity: 'low' | 'medium' | 'high';
  };
  codeQuality: {
    score: number; // 0-100
    strengths: string[];
    weaknesses: string[];
  };
  opportunities: {
    features: string[];
    improvements: string[];
    extensions: string[];
  };
}
```

**A2A Capabilities**:
- Exposes: `analyze_architecture`, `assess_quality`
- Consumes: `scan_repository`
- Protocol Version: 1.0

---

### Agent 3: PR Analyzer

**Purpose**: Extract patterns and insights from pull requests

**Model**: Gemini 2.5 Flash  
**Tools**: None (pure analysis)

**Analysis Focus**:
1. **Development Patterns** - Common change types, workflows
2. **Problem Areas** - Frequent changes, recurring bugs
3. **Feature Insights** - Recent additions, in-progress work

**Outputs** (via A2A):
```typescript
{
  patterns: {
    commonChangeTypes: string[];
    frequentFiles: { path: string; changeCount: number }[];
  };
  insights: {
    recentFeatures: string[];
    commonBugs: string[];
    performanceImprovements: string[];
  };
  suggestedProblems: {
    title: string;
    rationale: string;
    basedOnPRs: string[];
  }[];
}
```

---

### Agent 4: Issue Analyzer

**Purpose**: Extract problem patterns and feature requests from issues

**Model**: Gemini 2.5 Flash  
**Tools**: None (pure analysis)

**Analysis Focus**:
1. **Issue Categories** - Bugs, features, enhancements
2. **Priority Signals** - Community upvotes, maintainer responses
3. **Problem Patterns** - Common complaints, requested features

**Outputs** (via A2A):
```typescript
{
  categories: {
    bugs: { count: number; examples: string[] };
    features: { count: number; examples: string[] };
  };
  priorityIssues: Issue[];
  problemPatterns: Pattern[];
  suggestedProblems: ProblemSuggestion[];
}
```

---

### Agent 5: Dependency Analyzer

**Purpose**: Analyze dependencies, tech stack, and framework usage

**Model**: Gemini 2.5 Flash  
**Tools**: None (pure analysis)

**Analysis Focus**:
1. **Tech Stack** - Frameworks, libraries, tools
2. **Dependency Health** - Outdated packages, vulnerabilities
3. **Integration Opportunities** - Underutilized libraries, missing integrations

**Outputs** (via A2A):
```typescript
{
  techStack: {
    frameworks: string[];
    libraries: string[];
    runtime: string;
  };
  dependencyHealth: {
    outdated: string[];
    vulnerable: string[];
    wellMaintained: string[];
  };
  integrationOpportunities: Opportunity[];
}
```

---

### Multi-Agent Orchestrator (Agents 2-5 Collaboration)

**Purpose**: Coordinate analysis agents through 3 iterative loops

**Loop Mechanism**:

**Iteration 1: Independent Analysis**
```python
# All agents run in parallel
parallel_agent = Parallel(
    name="analysis_round_1",
    agents=[
        code_analyzer_agent,
        pr_analyzer_agent,
        issue_analyzer_agent,
        dependency_analyzer_agent
    ]
)
```

**Iteration 2: Cross-Validation**
- Agents receive other agents' outputs via A2A
- Validate and enrich their own analysis
- Find correlations and resolve conflicts

**Iteration 3: Consensus Building**
- Agents collaborate to build final report
- Rank problem suggestions by quality
- Synthesize comprehensive repository report

**Final Report**:
```typescript
{
  repositoryProfile: {
    architecture: string;
    complexity: string;
    techStack: string[];
  };
  synthesizedOpportunities: {
    problemSuggestions: ProblemSuggestion[];
    difficultyEstimates: Record<string, string>;
  };
  metadata: {
    analysisRounds: 3;
    agentsInvolved: string[];
    confidenceScore: number;
  };
}
```

---

### Agent 6: Problem Creator

**Purpose**: Create detailed, implementable coding problems

**Model**: Gemini 2.5 Pro  
**Tools**: None (pure generation)

**Inputs** (via A2A):
```typescript
{
  repositoryReport: ComprehensiveReport;
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  problemType: 'feature' | 'bug-fix' | 'refactor' | 'optimization';
  constraints: {
    timeLimit: number; // minutes
    focusArea?: string;
  }
}
```

**Generation Strategy**:
1. Select opportunity from synthesized suggestions
2. Define scope (solvable in time limit)
3. Create realistic business context
4. Specify clear, testable requirements
5. Design objective acceptance criteria
6. Generate helpful starter code
7. Provide hints without solutions

**Outputs** (via A2A):
```typescript
{
  problem: {
    title: string;
    description: string;
    businessContext: string;
    requirements: string[];
    acceptanceCriteria: string[];
    starterCode: StarterCodeFile[];
    hints: string[];
    estimatedTime: number;
    difficulty: string;
    techStack: string[];
    evaluationRubric: EvaluationCriterion[];
  };
  metadata: {
    basedOn: {
      issues: string[];
      prs: string[];
      codePatterns: string[];
    };
  };
}
```

**Prompt Template**:
```
Create a REALISTIC, IMPLEMENTABLE coding assessment that:
1. Aligns with repository's technology and patterns
2. Can be completed in {time_limit} minutes
3. Tests relevant skills for this codebase
4. Is self-contained (no private repo access needed)

CRITICAL REQUIREMENTS:
- Problem must be solvable in stated time
- All context provided (no repo access)
- Starter code provides structure, not solution
- Requirements are testable and objective
```

---

### Agent 7: QA/Validation Agent

**Purpose**: Validate problem quality and ensure feasibility

**Model**: Gemini 2.5 Flash (fast iteration)  
**Tools**: None (pure validation)

**Inputs** (via A2A):
```typescript
{
  problem: GeneratedProblem;
  repositoryReport: ComprehensiveReport;
}
```

**Validation Checks**:

**1. Feasibility (0-100)**
- Can be completed in time limit
- All required context provided
- No private repository access needed
- Starter code is functional
- Dependencies are accessible

**2. Quality (0-100)**
- Problem statement is clear
- Requirements are specific and testable
- Acceptance criteria are objective
- Hints are appropriate
- Business context is realistic

**3. Technical (0-100)**
- Uses repository's actual tech stack
- Patterns match repository style
- Complexity matches difficulty level
- Code examples are correct
- APIs/interfaces well-defined

**4. Educational (0-100)**
- Tests relevant skills
- Difficulty is appropriate
- Learning objectives clear
- Problem is non-trivial
- Solution approach not obvious

**Outputs** (via A2A):
```typescript
{
  validationResult: {
    isApproved: boolean;
    overallScore: number; // 0-100
    scores: {
      feasibility: number;
      quality: number;
      technical: number;
      educational: number;
    };
  };
  issues: Issue[];
  suggestions: Suggestion[];
  feedback: {
    strengths: string[];
    weaknesses: string[];
    improvements: string[];
  };
}
```

**Improvement Loop**:
```python
# If validation score < 85, iterate (max 2 times)
if validation_result.score < 85:
    improved_problem = await problem_creator.improve(
        original_problem=problem,
        validation_feedback=validation_result.feedback
    )
    final_validation = await qa_agent.validate(improved_problem)
```

---

## A2A Protocol

### Message Structure

```typescript
interface A2AMessage {
  protocol_version: "1.0";
  message_id: string;
  sender: {
    agent_id: string;
    agent_type: string;
    capabilities: string[];
  };
  recipient: {
    agent_id: string;
  };
  message_type: "request" | "response" | "broadcast" | "notification";
  timestamp: string;
  payload: {
    data: any;
    metadata: {
      conversation_id: string;
      iteration: number;
      confidence_score?: number;
    };
  };
  authentication: {
    signature: string;
    public_key: string;
  };
}
```

### Communication Patterns

**Pattern 1: Sequential Pipeline**
```
Scanner → Orchestrator → Analyzers → Creator → QA → API
```

**Pattern 2: Parallel Broadcast**
```
Orchestrator ──┬──→ Code Analyzer
               ├──→ PR Analyzer
               ├──→ Issue Analyzer
               └──→ Dependency Analyzer
                        ↓
               All send back to Orchestrator
```

**Pattern 3: Iterative Refinement**
```
Problem Creator → QA Agent
                   ↓
          [Score < 85?]
                   ↓ Yes
         Problem Creator (improve)
                   ↓
              QA Agent (re-validate)
```

### Agent Responsibilities Summary

| Agent | Model | Primary Role | A2A Exposes | A2A Consumes |
|-------|-------|--------------|-------------|--------------|
| 1. Scanner | Flash | Data collection | `scan_repository` | - |
| 2. Code Analyzer | Pro | Architecture analysis | `analyze_architecture` | `scan_repository` |
| 3. PR Analyzer | Flash | PR pattern analysis | `analyze_prs` | `scan_repository` |
| 4. Issue Analyzer | Flash | Issue pattern analysis | `analyze_issues` | `scan_repository` |
| 5. Dependency Analyzer | Flash | Tech stack analysis | `analyze_dependencies` | `scan_repository` |
| 6. Problem Creator | Pro | Problem generation | `create_problem` | All analyzer outputs |
| 7. QA Agent | Flash | Validation & improvement | `validate_problem` | `create_problem` |

---

## Data Flow

### End-to-End Flow

```
1. USER INPUT
   {
     githubRepoUrl: "https://github.com/user/repo",
     difficulty: "medium",
     problemType: "feature"
   }
   ↓
2. NEXT.JS API
   - Validate input
   - Create job record
   - POST to Agent Engine
   ↓
3. AGENT 1: Scanner
   - GitHub MCP ← → GitHub API
   - Repository Data (JSON)
   - [A2A: Send to Orchestrator]
   ↓
4. AGENTS 2-5: Analysis (3 loops)
   Loop 1: Parallel independent analysis
   Loop 2: Cross-validation & enrichment
   Loop 3: Consensus building
   - [A2A: Share results between agents]
   - Comprehensive Repository Report
   ↓
5. AGENT 6: Problem Creator
   - Input: Report + Difficulty + Type
   - Gemini 2.5 Pro generation
   - Generated Problem (JSON)
   - [A2A: Send to QA Agent]
   ↓
6. AGENT 7: QA Validator
   - Validation checks + Improvement loop
   - Validated Problem (JSON)
   - [A2A: Send to API]
   ↓
7. STORE & RETURN
   - Store in Cloud SQL
   - Cache in Cloud Storage
   - Return to Frontend
   ↓
8. FRONTEND DISPLAY
   - Render assessment for user
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Agent Framework** | Google ADK (Python) | Latest | Multi-agent orchestration |
| **Agent Protocol** | A2A Protocol | 1.0 | Agent interoperability |
| **LLM (Complex)** | Gemini 2.5 Pro | Latest | Analysis, problem creation |
| **LLM (Fast)** | Gemini 2.5 Flash | Latest | PR/Issue analysis, QA |
| **MCP** | GitHub MCP Server | Latest | Repository data |
| **Cloud Platform** | Google Cloud | - | Infrastructure |
| **Agent Runtime** | Vertex AI Agent Engine | Latest | Production deployment |
| **Database** | Cloud SQL PostgreSQL | 15+ | Data persistence |
| **Frontend** | Next.js | 15.4+ | Web interface |
| **Auth** | NextAuth.js + GitHub OAuth | Latest | Authentication |

### Google Cloud Services

- **Vertex AI**: Gemini model hosting and inference
- **Agent Engine**: Production agent runtime with A2A support
- **Cloud Run**: Containerized Next.js app hosting
- **Cloud SQL**: Managed PostgreSQL database
- **Cloud Storage**: Repository analysis cache
- **Cloud Logging**: Centralized logging
- **Cloud Trace**: Distributed tracing for A2A
- **Secret Manager**: Secure credential storage

---

## Deployment Architecture

```
┌────────────────────────────────────────────────────────┐
│          Global Load Balancer (Cloud LB)                │
└─────────────────────┬──────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
    ┌─────────┐              ┌─────────┐
    │Cloud Run│              │Cloud Run│
    │ us-east │              │ us-west │
    └────┬────┘              └────┬────┘
         │                        │
         └────────────┬───────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
    ┌─────────────┐       ┌─────────────┐
    │  Vertex AI  │       │  Cloud SQL  │
    │Agent Engine │       │ (Postgres)  │
    │             │       │             │
    │ Agents 1-7  │       │ HA + Backup │
    │  (ADK)      │       │             │
    │             │       │             │
    │  Gemini     │       │             │
    │  2.5 Pro    │       │             │
    └─────────────┘       └─────────────┘
         │                        │
         └────────────┬───────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
    ┌──────────┐             ┌──────────┐
    │  Cloud   │             │  Secret  │
    │  Storage │             │  Manager │
    └──────────┘             └──────────┘
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Total Time** | < 3 minutes | End-to-end |
| **Scanner** | < 20 seconds | Agent execution |
| **Analysis Loop (3x)** | < 90 seconds | 30s per loop |
| **Problem Creation** | < 30 seconds | Agent execution |
| **QA Validation** | < 20 seconds | Agent execution |
| **Improvement Loop** | < 40 seconds | If needed |

### Scalability

- **Parallel Execution**: Agents 2-5 run simultaneously
- **Auto-scaling**: Agent Engine scales based on load
- **Caching**: Repository data cached for 24 hours
- **Rate Limiting**: Exponential backoff for GitHub API

---

**Next**: See [IMPLEMENTATION.md](./IMPLEMENTATION.md) to build this system step-by-step.
