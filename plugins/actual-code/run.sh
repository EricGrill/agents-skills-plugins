#!/bin/bash
# ActualCode - Quick Run Script
# Sets all environment variables and runs the CLI

cd "$(dirname "$0")"

echo "🚀 Starting ActualCode CLI..."
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded Google Cloud credentials from .env"
else
    echo "⚠️  .env file not found (Google Cloud credentials may not be set)"
fi

# Check GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo ""
    echo "❌ GITHUB_TOKEN not set!"
    echo ""
    echo "Please run:"
    echo "  export GITHUB_TOKEN='your_token_here'"
    echo ""
    echo "Or set it now and run this script again:"
    read -p "Enter GitHub Token (or press Enter to exit): " token
    if [ -n "$token" ]; then
        export GITHUB_TOKEN="$token"
    else
        exit 1
    fi
fi

echo "✅ GitHub token configured"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "                  Ready to Generate Assessment                  "
echo "════════════════════════════════════════════════════════════════"
echo ""

# Run the CLI
python cli_runner.py