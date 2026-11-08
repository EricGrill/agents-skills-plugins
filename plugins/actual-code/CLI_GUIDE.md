# ActualCode CLI Guide

Interactive command-line interface for generating coding assessments from real GitHub repositories.

## 🚀 Quick Start

### 1. Set Up GitHub Token

You need a GitHub Personal Access Token to fetch repository data.

```bash
# Create token at https://github.com/settings/tokens
# Required scopes: repo (for private repos) or public_repo (for public only)

# Set environment variable
export GITHUB_TOKEN='your_github_token_here'
```

### 2. Ensure Google Cloud Credentials

Make sure your Google Cloud credentials are configured:

```bash
# Check current setup
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_APPLICATION_CREDENTIALS

# Should already be set from previous setup:
export GOOGLE_CLOUD_PROJECT='true-ability-473715-b4'
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your-service-account-key.json'
export GOOGLE_CLOUD_REGION='us-central1'
```

### 3. Activate Virtual Environment

```bash
cd /Users/muratcankoylan/ActualCode/hackathon_code
source venv/bin/activate
```

### 4. Run the CLI

```bash
python cli_runner.py
```

Or make it executable:

```bash
chmod +x cli_runner.py
./cli_runner.py
```

## 📝 Usage

The CLI will guide you through an interactive process:

### Step 1: Environment Check
- Verifies GitHub token is set
- Confirms Google Cloud configuration

### Step 2: Configuration
You'll be prompted for:

1. **GitHub Repository URL**
   - Examples:
     - `https://github.com/owner/repo`
     - `github.com/owner/repo`
     - `owner/repo`

2. **Difficulty Level**
   - easy
   - medium (default)
   - hard
   - expert

3. **Problem Type**
   - feature (default)
   - bug-fix
   - refactor
   - optimization

4. **Time Limit**
   - 60 minutes
   - 120 minutes
   - 180 minutes (default)
   - 240 minutes

### Step 3: Generation
- Fetches real repository data from GitHub
- Runs 7 AI agents in multi-agent pipeline
- Generates realistic coding assessment
- Validates quality (QA scoring)
- Refines based on feedback

### Step 4: Results
- Displays assessment summary
- Shows QA validation scores
- Saves complete JSON to file
- Shows performance metrics

## 📤 Output

The CLI generates a JSON file: `assessment_YYYYMMDD_HHMMSS.json`

Example structure:
```json
{
  "problem": {
    "title": "Implement User Authentication Feature",
    "description": "...",
    "requirements": [...],
    "acceptance_criteria": [...],
    "starter_code": [...],
    "hints": [...],
    "estimated_time": 180,
    "difficulty": "medium",
    "tech_stack": ["Python", "Flask", "SQLAlchemy"],
    "evaluation_rubric": [...]
  },
  "validation": {
    "overall_score": 85,
    "scores": {
      "feasibility": 90,
      "quality": 85,
      "technical": 80,
      "educational": 85
    },
    "issues": [...],
    "suggestions": [...]
  },
  "repository_analysis": {...},
  "performance": {
    "total_duration": 145.3,
    "scan": 12.1,
    "analysis": 85.4,
    "creation": 35.2,
    "validation": 12.6
  }
}
```

## 🎯 Example Session

```bash
$ python cli_runner.py

╔═══════════════════════════════════════════════════════════════════════════╗
║                          ACTUALCODE                                       ║
║              AI-Powered Code Assessment Generator                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Environment Check
════════════════════════════════════════════════════════════════════════════
✅ GitHub token configured
✅ Google Cloud project: true-ability-473715-b4

Configuration
════════════════════════════════════════════════════════════════════════════
GitHub Repository URL: facebook/react

Select Difficulty Level:
  1. easy
  → 2. medium
  3. hard
  4. expert
Enter choice (1-4) [2]: 

Select Problem Type:
  → 1. feature
  2. bug-fix
  3. refactor
  4. optimization
Enter choice (1-4) [1]: 

Estimated Time Limit:
  1. 60 minutes
  2. 120 minutes
  → 3. 180 minutes
  4. 240 minutes
Enter choice (1-4) [3]: 

Configuration Summary:
  Repository:  facebook/react
  Difficulty:  medium
  Type:        feature
  Time Limit:  180 minutes

Proceed with generation? (y/n) [y]: y

Generating Assessment
════════════════════════════════════════════════════════════════════════════
🔧 Initializing GitHub MCP client...
📡 Fetching repository data from GitHub...
✅ Repository data fetched successfully!
   Name: react
   Language: JavaScript
   Files: 1234
   Issues: 20
   PRs: 20
   Commits: 50

🤖 Initializing Multi-Agent System...

🔥 Starting Multi-Agent Analysis...
This may take 2-3 minutes. Please wait...

[Agent outputs follow...]

Assessment Generated Successfully!
════════════════════════════════════════════════════════════════════════════
Problem Title: Implement Error Boundary with Recovery
Difficulty: medium
Estimated Time: 180 minutes
Tech Stack: JavaScript, React, TypeScript

... [full details] ...

✅ Assessment saved to: assessment_20250930_150000.json

Performance Metrics:
  Total Time: 145.30s
  Scan: 12.10s
  Analysis: 85.40s
  Creation: 35.20s
  Validation: 12.60s

🎊 Assessment generation complete!
```

## 🛠️ Troubleshooting

### GitHub Token Issues
```bash
# Token not found
Error: GitHub token not provided

# Solution:
export GITHUB_TOKEN='ghp_your_token_here'
```

### API Rate Limits
GitHub API has rate limits:
- Authenticated: 5,000 requests/hour
- The CLI uses ~10-15 requests per repository

### Large Repositories
For repositories with 1000+ files:
- Fetching may take 10-30 seconds
- File tree is limited to 500 files
- This is normal and expected

### Google Cloud Errors
```bash
# Permission denied
Error: 403 PERMISSION_DENIED

# Solution: Verify credentials
gcloud auth application-default login
# Or ensure service account key is correct
```

## 💡 Tips

1. **Start with smaller repos** for testing
2. **Public repos work best** - no special permissions needed
3. **Active repos** (with recent PRs/issues) generate better assessments
4. **Tech-specific repos** (clear language/framework) work better than mixed codebases

## 🔗 Examples of Good Repositories

- `expressjs/express` - Node.js web framework
- `pallets/flask` - Python web framework
- `rails/rails` - Ruby web framework
- `facebook/react` - JavaScript UI library
- `vercel/next.js` - React framework

## 📞 Support

For issues or questions:
1. Check the logs in the output
2. Verify environment variables
3. Test with a small public repository first
