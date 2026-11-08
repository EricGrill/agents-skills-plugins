#!/bin/bash
# Quick test with a simple repository

cd /Users/muratcankoylan/ActualCode/hackathon_code

export GITHUB_TOKEN=your_github_token_here
export GOOGLE_CLOUD_PROJECT=true-ability-473715-b4
export GOOGLE_APPLICATION_CREDENTIALS=/Users/muratcankoylan/ActualCode/true-ability-473715-b4-22e5d8ca9981.json
export GOOGLE_CLOUD_REGION=us-central1

source venv/bin/activate

# Create test input
echo "sindresorhus/is
2
1
2
y" | python cli_runner.py 2>&1 | tee test_output.log

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Check the files:"
echo "  1. assessment_*.json - Complete assessment"
echo "  2. DETAILED_RUN_*.txt - Full logs"
echo "  3. test_output.log - Terminal output"
echo "═══════════════════════════════════════════════════════════════════════════"
