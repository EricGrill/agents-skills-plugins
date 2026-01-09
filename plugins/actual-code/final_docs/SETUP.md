# 🚀 Complete Setup Guide

This guide will take you from zero to a working multi-agent system. Follow the steps in order.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Google Cloud Setup](#google-cloud-setup)
4. [GitHub Configuration](#github-configuration)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **macOS, Linux, or Windows** (macOS darwin 24.6.0 confirmed working)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Python 3.11+** - For Google ADK agents
- **PostgreSQL 15+** - For database
- **Git** - For version control

### Accounts Required
- **Google Cloud Account** with billing enabled
- **GitHub Account** with admin access to repositories

### Verification

```bash
# Check Node.js version
node --version  # Should be >= 20.0.0

# Check Python version
python3 --version  # Should be >= 3.11

# Check PostgreSQL
psql --version  # Should be >= 15

# Check git
git --version
```

---

## Environment Setup

### Step 1: Navigate to Project

```bash
cd /Users/muratcankoylan/ActualCode/actualy_code
```

### Step 2: Install Node.js Dependencies

```bash
# Install all Node.js packages
npm install

# Verify installation
npm list --depth=0
```

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation
which python  # Should point to venv/bin/python
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Google ADK and dependencies
pip install google-adk

# Install Google Cloud libraries
pip install google-cloud-aiplatform google-auth google-cloud-logging google-cloud-storage

# Install utility libraries
pip install python-dotenv pydantic tenacity asyncio

# Install testing libraries
pip install pytest pytest-asyncio

# Create requirements.txt
pip freeze > requirements.txt
```

### Step 5: Create Environment File

```bash
# Create .env file
cat > .env << 'EOF'
# Google Cloud
GOOGLE_CLOUD_PROJECT=ActualCode
GOOGLE_GENAI_USE_VERTEXAI="True"
GOOGLE_CLOUD_REGION=us-central1

# GitHub
GITHUB_TOKEN=ghp_your_token_here
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/assessment_platform

# Next.js Authentication
NEXTAUTH_SECRET=your-secret-key-change-this
NEXTAUTH_URL=http://localhost:3000

# Agent Engine (will be updated after deployment)
AGENT_ENGINE_URL=

# Environment
NODE_ENV=development
EOF

# Add to .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## Google Cloud Setup

### Step 1: Install Google Cloud SDK

```bash
# Install gcloud CLI (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Authenticate
gcloud auth login
gcloud auth application-default login
```

### Step 2: Create Google Cloud Project

```bash
# Set project variables
export PROJECT_ID="actualcode-hackathon"
export PROJECT_NAME="ActualCode Hackathon"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"

# Set as current project
gcloud config set project $PROJECT_ID
```

### Step 3: Link Billing Account

```bash
# List billing accounts
gcloud billing accounts list

# Link billing (replace with your billing account ID)
export BILLING_ACCOUNT_ID="your-billing-account-id"
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
```

### Step 4: Enable Required APIs

```bash
# Enable all required Google Cloud APIs
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  cloudbuild.googleapis.com

# Verify enabled APIs
gcloud services list --enabled
```

### Step 5: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create actualcode-sa \
  --display-name="ActualCode Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:actualcode-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:actualcode-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:actualcode-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create \
  ~/actualcode-sa-key.json \
  --iam-account=actualcode-sa@$PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/actualcode-sa-key.json"

# Update .env file with the path
echo "GOOGLE_APPLICATION_CREDENTIALS=$HOME/actualcode-sa-key.json" >> .env
```

---

## GitHub Configuration

### Step 1: Create GitHub Personal Access Token

**Manual Steps:**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `ActualCode Hackathon`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read user profile data)
5. Click "Generate token"
6. **Copy the token immediately** (it won't be shown again)

```bash
# Add to .env file
# Replace ghp_your_token_here with your actual token
```

### Step 2: Create GitHub OAuth App (for NextAuth)

**Manual Steps:**

1. Go to https://github.com/settings/developers
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in the details:
   - **Application name**: `Assessment Platform`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Click "Register application"
5. Copy **Client ID**
6. Click "Generate a new client secret" and copy **Client Secret**

```bash
# Update .env file with OAuth credentials
# GITHUB_CLIENT_ID=your_client_id
# GITHUB_CLIENT_SECRET=your_client_secret
```

### Step 3: Generate NextAuth Secret

```bash
# Generate a secure secret for NextAuth
openssl rand -base64 32

# Add to .env file as NEXTAUTH_SECRET
```

---

## Database Setup

### Step 1: Start PostgreSQL

```bash
# On macOS (with Homebrew)
brew services start postgresql@15

# On Ubuntu/Debian
sudo systemctl start postgresql

# On Windows
# Start PostgreSQL from Services or pg_ctl
```

### Step 2: Create Database

```bash
# Create database
createdb assessment_platform

# Test connection
psql -d assessment_platform -c "SELECT 1;"
```

### Step 3: Update Database URL in .env

```bash
# Update .env with your database credentials
# DATABASE_URL="postgresql://username:password@localhost:5432/assessment_platform"

# For local development, username is often your system username
# DATABASE_URL="postgresql://$(whoami)@localhost:5432/assessment_platform"
```

### Step 4: Initialize Prisma

```bash
# Generate Prisma client
npx prisma generate

# Push schema to database
npx prisma db push

# (Optional) Open Prisma Studio to view database
npx prisma studio
```

---

## Running the Application

### Development Mode

```bash
# Activate Python virtual environment (if not already active)
source venv/bin/activate

# Start Next.js development server
npm run dev

# Application will be available at:
# - Local: http://localhost:3000
# - Network: http://YOUR_IP:3000
```

### Test Agent Locally (Optional)

```bash
# Test individual agent (after implementing)
python agents/scanner_agent.py

# Test orchestrator
python orchestrator.py

# Run Python tests
pytest tests/ -v
```

---

## Troubleshooting

### Common Issues

#### **Node.js Version Errors**

```bash
# Install Node.js 20 using nvm
nvm install 20
nvm use 20

# Verify version
node --version
```

#### **Python Virtual Environment Issues**

```bash
# Make sure you're in the right directory
cd /Users/muratcankoylan/ActualCode/actualy_code

# Deactivate if active
deactivate 2>/dev/null || true

# Remove old venv
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# Verify
which python  # Should show venv path
```

#### **Google ADK Not Installing**

```bash
# Update pip first
pip install --upgrade pip

# Try with verbose output
pip install google-adk -v

# If fails, check Python version
python --version  # Should be 3.11+
```

#### **Database Connection Fails**

```bash
# Test PostgreSQL is running
pg_isready

# Test connection
psql -d assessment_platform -c "SELECT 1;"

# Reset database (WARNING: deletes all data)
npx prisma db push --force-reset
```

#### **GitHub OAuth "Invalid redirect URI"**

- Make sure callback URL is **exactly**: `http://localhost:3000/api/auth/callback/github`
- Check for typos in GitHub OAuth App settings
- Ensure no trailing slashes

#### **"Invalid client secret" Error**

- Regenerate client secret in GitHub OAuth App settings
- Update `.env` file with new secret
- Restart development server

#### **Google Cloud Permission Issues**

```bash
# Verify service account has correct roles
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:actualcode-sa@*"

# Re-authenticate if needed
gcloud auth application-default login
```

#### **Port 3000 Already in Use**

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=3001 npm run dev
```

---

## Verification Checklist

Before proceeding to implementation, verify:

- [ ] Node.js 20+ installed and verified
- [ ] Python 3.11+ virtual environment created and active
- [ ] All Python dependencies installed (google-adk, etc.)
- [ ] All Node.js dependencies installed
- [ ] Google Cloud project created
- [ ] All Google Cloud APIs enabled
- [ ] Service account created with key downloaded
- [ ] GitHub Personal Access Token created
- [ ] GitHub OAuth App created (Client ID & Secret)
- [ ] PostgreSQL installed and running
- [ ] Database created and Prisma schema pushed
- [ ] `.env` file created with all credentials
- [ ] Development server starts without errors

---

## Next Steps

Once setup is complete:

1. **Test the Application**: Visit http://localhost:3000
2. **Read Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
3. **Start Implementation**: Follow [IMPLEMENTATION.md](./IMPLEMENTATION.md) step-by-step
4. **Use Quick Reference**: Keep [REFERENCE.md](./REFERENCE.md) handy for code snippets

---

## Environment Variables Reference

Complete `.env` file template:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=actualcode-hackathon
GOOGLE_APPLICATION_CREDENTIALS=/path/to/actualcode-sa-key.json
GOOGLE_CLOUD_REGION=us-central1

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_CLIENT_ID=1234567890abcdef1234
GITHUB_CLIENT_SECRET=abcdef1234567890abcdef1234567890abcdef12

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/assessment_platform

# Next.js
NEXTAUTH_SECRET=your-generated-secret-from-openssl
NEXTAUTH_URL=http://localhost:3000

# Agent Engine (populated after deployment)
AGENT_ENGINE_URL=

# Environment
NODE_ENV=development
```

---

## Support

If you encounter issues not covered here:

1. Check the **Troubleshooting** section above
2. Review [REFERENCE.md](./REFERENCE.md) for common solutions
3. Check Google Cloud Console for service status
4. Verify all environment variables are set correctly
5. Ensure all services (PostgreSQL, Google Cloud APIs) are running

---

**Setup Complete!** 🎉

You're now ready to start implementing the multi-agent system. Head to [IMPLEMENTATION.md](./IMPLEMENTATION.md) for step-by-step instructions.
