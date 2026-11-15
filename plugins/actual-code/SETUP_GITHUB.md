# 🔑 GitHub Token Setup

## Why You Need a GitHub Token

The ActualCode CLI fetches real repository data from GitHub's API. To do this, you need a **Personal Access Token** for authentication.

## Step 1: Create GitHub Token (2 minutes)

### Option A: Using GitHub Website (Recommended)

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click "Generate new token" → "Generate new token (classic)"
   
3. **Configure Token**
   - **Note**: `ActualCode CLI`
   - **Expiration**: Choose duration (90 days recommended)
   - **Scopes**: Select:
     - ✅ `public_repo` (for public repositories only)
     - OR ✅ `repo` (if you want to analyze private repos too)

4. **Generate and Copy**
   - Click "Generate token"
   - **IMPORTANT**: Copy the token immediately (you won't see it again!)
     - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Option B: Using GitHub CLI (if installed)

```bash
gh auth login
gh auth token
```

## Step 2: Set Token in Terminal

### For Current Session (Temporary)

```bash
export GITHUB_TOKEN='ghp_your_token_here'
```

**Note**: Replace `ghp_your_token_here` with your actual token!

### For Permanent Setup (Recommended)

Add to your shell configuration file:

**For Bash (~/.bashrc or ~/.bash_profile):**
```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bash_profile
source ~/.bash_profile
```

**For Zsh (~/.zshrc):**
```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

## Step 3: Verify Setup

### Test 1: Check Environment Variable

```bash
echo $GITHUB_TOKEN
```

**Expected**: Should show your token (starts with `ghp_`)

### Test 2: Test GitHub API Access

```bash
cd /Users/muratcankoylan/ActualCode/hackathon_code
source venv/bin/activate
./test_github_token.sh
```

**Expected output:**
```
✅ GITHUB_TOKEN is set
Testing API access...
✅ GitHub API access successful!
   Authenticated as: your-username
Ready to use ActualCode CLI!
```

### Test 3: Test Full GitHub Connection

```bash
python test_github_connection.py
```

**Expected output:**
```
Testing GitHub Connection...
✅ GitHub token found
🔧 Initializing GitHub MCP client...
✅ Client initialized
📡 Testing with repository: sindresorhus/is
✅ SUCCESS! Repository data fetched:
   Name: is
   Language: JavaScript
   Stars: 1600+
   Files: 50+
🎉 GitHub connection test PASSED!
```

## Step 4: Run ActualCode CLI

Once all tests pass:

```bash
python cli_runner.py
```

## 🛠️ Troubleshooting

### "GITHUB_TOKEN not set"

```bash
# Make sure you exported it
export GITHUB_TOKEN='ghp_your_actual_token_here'

# Verify it's set
echo $GITHUB_TOKEN

# Should show your token
```

### "Bad credentials" or "401 Unauthorized"

Your token might be:
- ❌ Incorrect - Double check you copied it correctly
- ❌ Expired - Generate a new token
- ❌ Missing scopes - Regenerate with `public_repo` or `repo` scope

### "403 API rate limit exceeded"

GitHub has rate limits:
- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour

Wait an hour or use a different token.

### Token Doesn't Persist

You need to add it to your shell config file:

```bash
# Check which shell you're using
echo $SHELL

# If /bin/zsh
echo 'export GITHUB_TOKEN="ghp_your_token"' >> ~/.zshrc
source ~/.zshrc

# If /bin/bash
echo 'export GITHUB_TOKEN="ghp_your_token"' >> ~/.bash_profile
source ~/.bash_profile
```

## 🔐 Security Best Practices

1. **Never commit tokens to Git**
   - Tokens are in `.gitignore` (environment variables only)
   
2. **Use minimal scopes**
   - For public repos only: `public_repo`
   - For private repos: `repo`

3. **Set expiration**
   - Recommended: 90 days
   - Regenerate regularly

4. **Revoke if compromised**
   - Go to https://github.com/settings/tokens
   - Delete the token immediately

## 📝 Quick Reference

```bash
# Set token (replace with your actual token)
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Verify
echo $GITHUB_TOKEN

# Test
./test_github_token.sh

# Run CLI
python cli_runner.py
```

## ✅ Checklist

- [ ] Created GitHub Personal Access Token
- [ ] Copied token to clipboard
- [ ] Set `GITHUB_TOKEN` environment variable
- [ ] Verified with `echo $GITHUB_TOKEN`
- [ ] Ran `./test_github_token.sh` successfully
- [ ] Ran `python test_github_connection.py` successfully
- [ ] Ready to run `python cli_runner.py`!

---

**Next**: Once setup is complete, see [QUICK_START.md](QUICK_START.md) for usage!
