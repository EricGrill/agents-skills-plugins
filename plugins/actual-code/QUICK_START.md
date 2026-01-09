# 🚀 Quick Start - 5 Minute Setup

Get ActualCode running with real GitHub repositories in 5 minutes!

## Step 1: Get GitHub Token (2 minutes)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "ActualCode CLI"
4. Select scopes:
   - ✅ `repo` (for private repos) OR
   - ✅ `public_repo` (for public repos only)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

```bash
# Set the token in your terminal
export GITHUB_TOKEN='ghp_your_token_here'
```

## Step 2: Verify Setup (1 minute)

```bash
cd /Users/muratcankoylan/ActualCode/hackathon_code

# Test GitHub token
./test_github_token.sh

# Expected output:
# ✅ GITHUB_TOKEN is set
# ✅ GitHub API access successful!
```

## Step 3: Activate Environment (30 seconds)

```bash
# Activate Python virtual environment
source venv/bin/activate

# Verify Google Cloud (should already be set)
echo $GOOGLE_CLOUD_PROJECT
# Should show: true-ability-473715-b4
```

## Step 4: Run the CLI (30 seconds)

```bash
python cli_runner.py
```

## Step 5: Generate Assessment (2-3 minutes)

Follow the prompts:

```
1. Repository URL: sindresorhus/is
2. Difficulty: medium (press Enter)
3. Problem Type: feature (press Enter)
4. Time Limit: 180 minutes (press Enter)
5. Confirm: y (press Enter)
```

Wait 2-3 minutes and you're done!

## 🎯 Example Session

```bash
$ export GITHUB_TOKEN='ghp_xxxxxxxxxxxxx'
$ cd /Users/muratcankoylan/ActualCode/hackathon_code
$ source venv/bin/activate
$ python cli_runner.py

# Interactive prompts appear...
GitHub Repository URL: expressjs/express
[Select options...]
Proceed? y

# Generation starts...
🔧 Initializing GitHub MCP client...
📡 Fetching repository data from GitHub...
✅ Repository data fetched successfully!
   Name: express
   Language: JavaScript
   Files: 234
   Issues: 20
   PRs: 20
   Commits: 50

🤖 Initializing Multi-Agent System...
🔥 Starting Multi-Agent Analysis...

# 2-3 minutes later...
🎉 Assessment Generated Successfully!

Problem Title: Implement Advanced Middleware System
Difficulty: medium
Estimated Time: 180 minutes
Tech Stack: JavaScript, Express, Node.js

✅ Assessment saved to: assessment_20250930_153045.json
```

## ✅ Verify Output

```bash
# List generated files
ls -lh assessment_*.json

# View the problem title
cat assessment_*.json | head -20

# Pretty print (if you have jq)
cat assessment_*.json | jq '.problem.title'
```

## 🎊 You're Done!

You now have:
- ✅ Real GitHub integration working
- ✅ Multi-agent AI pipeline running
- ✅ Generated coding assessment
- ✅ Complete JSON output file

## 🔍 Troubleshooting

### "GitHub token not found"
```bash
# Make sure you exported it
export GITHUB_TOKEN='ghp_your_token_here'

# Verify it's set
echo $GITHUB_TOKEN
```

### "Permission denied" Google Cloud
```bash
# Check your service account key path
echo $GOOGLE_APPLICATION_CREDENTIALS
# Should point to: /path/to/true-ability-473715-b4-22e5d8ca9981.json
```

### "Module not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify it's activated (should see (venv) in prompt)
which python
# Should show: /Users/muratcankoylan/ActualCode/hackathon_code/venv/bin/python
```

## 📚 Next Steps

- Read [CLI_GUIDE.md](CLI_GUIDE.md) for detailed usage
- Read [PRODUCTION_READY.md](PRODUCTION_READY.md) for architecture
- Try different repositories
- Experiment with difficulty levels

**Happy Coding! 🎉**
