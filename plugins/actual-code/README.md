# 🎯 ActualCode - AI-Powered Code Assessment Generator

[![Watch this video](https://img.youtube.com/vi/jnIFJ8-syio/0.jpg)](https://www.youtube.com/watch?v=jnIFJ8-syio)

Technical details: https://github.com/muratcankoylan/actual_code/blob/main/ActualCode-TechnicalDeepDiveforJury.md

**Transform GitHub repositories into realistic coding challenges using multi-agent AI**

[![Built with Google Gemini](https://img.shields.io/badge/Built%20with-Google%20Gemini-4285F4?logo=google)](https://cloud.google.com/vertex-ai)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![A2A Protocol](https://img.shields.io/badge/Protocol-A2A-FF6B6B)](https://github.com/google/adk)

---

## 🌟 Overview

ActualCode is a code assessment platform that analyzes **real GitHub repositories** and generates **personalized, realistic coding challenges** using a **7-agent AI architecture** powered by Google's Gemini models and the A2A (Agent-to-Agent) protocol.

### The Problem We Solve

- **LeetCode is too generic** - Candidates solve abstract algorithms, not real-world problems
- **Hiring is time-consuming** - Creating repository-specific assessments takes hours
- **Context gap** - Candidates who ace LeetCode still struggle with actual codebases

### Our Solution

1. **Input**: Any GitHub repository URL + difficulty level
2. **AI Magic**: 7 specialized AI agents collaborate using A2A protocol
3. **Output**: Realistic, implementable coding problem in **~2 minutes**

---

## 🏗️ Architecture

```
User Input (GitHub Repo)
        ↓
   Agent 1: Scanner (GitHub API)
        ↓
   Agents 2-5: Parallel Analysis
     • Code Analyzer (Gemini 2.5 Pro)
     • PR Analyzer (Gemini 2.5 Flash)
     • Issue Analyzer (Gemini 2.5 Flash)
     • Dependency Analyzer (Gemini 2.5 Flash)
        ↓
   Agent 6: Problem Creator (Gemini 2.5 Pro)
        ↓
   Agent 7: QA Validator (Gemini 2.5 Flash)
        ↓
   Personalized Assessment ✨
```

### Multi-Agent System Features

- **7 Specialized Agents** - Each with unique expertise
- **A2A Protocol** - Google's Agent-to-Agent communication
- **Single-Pass Analysis** - Optimized for speed (2 min vs 4+ min)
- **QA Validation** - Automated quality scoring with feedback
- **Repository-Specific** - Problems tailored to actual codebase

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **GitHub Personal Access Token** - [Get here](https://github.com/settings/tokens)
3. **Google Cloud Account** - With Vertex AI enabled
4. **Service Account Key** - For Google Cloud authentication

### Installation

```bash
# Clone the repository
git clone https://github.com/muratcankoylan/actual_code.git
cd actual_code

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Create a `.env` file with:

```bash
# GitHub Token
GITHUB_TOKEN=your_github_personal_access_token

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

### Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the CLI
python cli_runner.py
```

Follow the interactive prompts to generate your first assessment!

---

## 📖 Usage

### Interactive CLI

```bash
$ python cli_runner.py

GitHub Repository URL: facebook/react
Select Difficulty: [2] medium
Select Problem Type: [1] feature
Time Limit: [3] 180 minutes
Proceed? y

[AI agents analyze the repository...]

✅ Assessment Generated Successfully!
Problem Title: Implement Error Boundary with Recovery
Tech Stack: JavaScript, React, TypeScript
QA Score: 85/100

✅ Assessment saved to: assessment_20250930_153045.json
✅ Detailed logs saved to: DETAILED_RUN_20250930_153045.txt
```

### Output Files

1. **`assessment_{timestamp}.json`** - Complete assessment with:
   - Problem statement
   - Requirements & acceptance criteria
   - Starter code
   - Hints
   - Evaluation rubric
   - QA validation scores

2. **`DETAILED_RUN_{timestamp}.txt`** - Complete logs with:
   - Repository data (all files)
   - Agent analysis details
   - Problem generation process
   - QA validation feedback

---

## 🎯 Features

### Real GitHub Integration

- ✅ Fetches actual repository data via GitHub API
- ✅ Analyzes real code structure, PRs, issues
- ✅ Uses actual tech stack and dependencies
- ✅ References real codebase patterns

### Multi-Agent AI Pipeline

- ✅ **7 Specialized Agents** working in concert
- ✅ **A2A Protocol** for agent communication
- ✅ **Parallel Processing** for speed
- ✅ **Single-Pass Analysis** (optimized)
- ✅ **QA Validation** with automated scoring

### Repository-Specific Problems

- ✅ Problems match the input repository's tech stack
- ✅ Addresses actual weaknesses in the codebase
- ✅ Uses repository's architecture patterns
- ✅ Realistic and implementable within time limit

### Quality Assurance

- ✅ 4-dimension validation (Feasibility, Quality, Technical, Educational)
- ✅ Automated scoring (0-100)
- ✅ Specific feedback for improvement
- ✅ Single-pass validation with refinement

---

## 🧪 Example

### Input

```
Repository: https://github.com/expressjs/express
Difficulty: medium
Type: feature
Time: 180 minutes
```

### Output

```json
{
  "problem": {
    "title": "Implement Advanced Middleware Error Handling",
    "description": "Add comprehensive error handling middleware to Express...",
    "tech_stack": ["JavaScript", "Express", "Node.js"],
    "requirements": [
      "Create custom error classes",
      "Implement middleware chain",
      "Add error logging",
      ...
    ],
    "acceptance_criteria": [...],
    "starter_code": [...],
    "hints": [...],
    "estimated_time": 180,
    "difficulty": "medium",
    "evaluation_rubric": [...]
  },
  "validation": {
    "overall_score": 85,
    "scores": {
      "feasibility": 90,
      "quality": 85,
      "technical": 82,
      "educational": 83
    }
  }
}
```

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[CLI_GUIDE.md](CLI_GUIDE.md)** - Complete CLI documentation
- **[PRODUCTION_READY.md](PRODUCTION_READY.md)** - Architecture details
- **[SETUP_GITHUB.md](SETUP_GITHUB.md)** - GitHub token setup
- **[ALL_ISSUES_RESOLVED.md](ALL_ISSUES_RESOLVED.md)** - Development changelog
- **[final_docs/](final_docs/)** - Complete technical documentation

---

## 🏗️ Technical Stack

### AI & Cloud

- **Google Vertex AI** - AI platform
- **Gemini 2.5 Pro** - Code analysis & problem creation
- **Gemini 2.5 Flash** - PR/Issue/Dependency analysis & QA validation
- **Google ADK** - Agent Development Kit
- **A2A Protocol** - Agent-to-Agent communication

### Backend

- **Python 3.11+** - Core language
- **aiohttp** - Async HTTP for GitHub API
- **structlog** - Structured logging

### Integration

- **GitHub API** - Repository data fetching
- **Vertex AI API** - AI model access

---

## 📊 Performance

- **Repository Fetch**: 5-15 seconds
- **Agent Analysis**: ~60 seconds (single-pass)
- **Problem Creation**: 30-45 seconds
- **QA Validation**: 10-15 seconds
- **Refinement**: 20-35 seconds

**Total**: **~2 minutes** (optimized from 4+ minutes)

---

## 🔧 Project Structure

```
hackathon_code/
├── cli_runner.py              # Interactive CLI interface
├── orchestrator.py            # Multi-agent coordinator
├── agents/                    # 7 AI agents
│   ├── scanner_agent.py       # GitHub repository scanner
│   ├── code_analyzer_agent.py # Code architecture analyzer
│   ├── pr_analyzer_agent.py   # Pull request analyzer
│   ├── issue_analyzer_agent.py# Issue tracker analyzer
│   ├── dependency_analyzer_agent.py # Tech stack analyzer
│   ├── problem_creator_agent.py # Problem generator
│   └── qa_validator_agent.py  # Quality validator
├── utils/                     # Utilities
│   ├── github_mcp.py          # GitHub API integration
│   ├── a2a_protocol.py        # A2A protocol implementation
│   ├── monitoring.py          # Performance monitoring
│   └── json_parser.py         # Robust JSON parsing
├── final_docs/                # Complete documentation
└── requirements.txt           # Python dependencies
```

---

## 🎨 Key Innovations

### 1. Multi-Agent A2A Protocol

First production implementation of Google's A2A protocol with 7 specialized agents communicating seamlessly.

### 2. Repository-Specific Problems

Unlike generic platforms, problems are tailored to:
- Actual tech stack used
- Real code patterns found
- Specific weaknesses identified
- Genuine opportunities discovered

### 3. Single-Pass Optimization

Optimized from 3-loop analysis to single-pass:
- **2x faster** generation
- **66% fewer API calls**
- Same quality output

### 4. Quality Assurance

Built-in QA agent validates on 4 dimensions:
- Feasibility (time, context, dependencies)
- Quality (clarity, testability)
- Technical (stack match, patterns)
- Educational (skill assessment value)

---

## 🛠️ Development

### Running Tests

```bash
# Test GitHub connection
python test_github_connection.py

# Test with your repository
python test_my_repo.py

# Verify setup
./verify_setup.sh
```

### Key Scripts

- `cli_runner.py` - Main CLI application
- `test_github_connection.py` - GitHub API tester
- `test_my_repo.py` - Repository-specific tester
- `verify_setup.sh` - Environment checker

---

## 🔐 Security

- ✅ No tokens in code or repository
- ✅ Environment variables for secrets
- ✅ .gitignore for sensitive files
- ✅ Service account keys excluded
- ✅ API rate limiting handled

---

## 📝 Contributing

This project was built for the Google AI Hackathon showcasing:
- Google Gemini 2.5 Pro/Flash
- Vertex AI integration
- A2A Protocol implementation
- Multi-agent architecture

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Google Vertex AI** - For powerful AI models
- **Google ADK** - For agent development framework
- **A2A Protocol** - For agent interoperability

---

## 📞 Contact

**Murat Can Koylan**
- GitHub: [@muratcankoylan](https://github.com/muratcankoylan)
- Repository: [actual_code](https://github.com/muratcankoylan/actual_code)

---

## 🚀 Get Started Now!

```bash
git clone https://github.com/muratcankoylan/actual_code.git
cd actual_code
pip install -r requirements.txt
python cli_runner.py
```

**Generate your first AI-powered coding assessment in 2 minutes!** 🎉
