#!/bin/bash

# ActualCode Web UI Startup Script

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                      ActualCode Web UI                            ║"
echo "║              AI-Powered Assessment Generator                      ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected. Activating venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
        exit 1
    fi
fi

# Check environment variables
if [[ -z "$GITHUB_TOKEN" ]] && [[ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]]; then
    echo "❌ GitHub token not found!"
    echo "Please set GITHUB_TOKEN environment variable:"
    echo "  export GITHUB_TOKEN='your_token_here'"
    exit 1
fi

echo "✅ GitHub token configured"

if [[ -z "$GOOGLE_CLOUD_PROJECT" ]]; then
    echo "⚠️  GOOGLE_CLOUD_PROJECT not set (using defaults)"
else
    echo "✅ Google Cloud project: $GOOGLE_CLOUD_PROJECT"
fi

echo ""
echo "🚀 Starting ActualCode Web Server..."
echo ""

# Start the web server
python3 web_server.py
