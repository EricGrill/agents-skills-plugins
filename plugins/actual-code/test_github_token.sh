#!/bin/bash
# Quick test to verify GitHub token works

echo "Testing GitHub token..."

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set!"
    echo "Please run: export GITHUB_TOKEN='your_token_here'"
    exit 1
fi

echo "✅ GITHUB_TOKEN is set"
echo "Testing API access..."

# Test with a simple API call
response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user)

if echo "$response" | grep -q "login"; then
    login=$(echo "$response" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
    echo "✅ GitHub API access successful!"
    echo "   Authenticated as: $login"
else
    echo "❌ GitHub API access failed"
    echo "   Response: $response"
    exit 1
fi

echo ""
echo "Ready to use ActualCode CLI!"
