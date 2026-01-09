#!/bin/bash
# Complete setup verification for ActualCode

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                   ActualCode Setup Verification                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Virtual Environment
echo "1. Checking Virtual Environment..."
if [ -d "venv" ]; then
    echo -e "   ${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "   ${RED}❌ Virtual environment not found${NC}"
    echo "      Run: python -m venv venv"
    ((ERRORS++))
fi

# Check 2: GitHub Token
echo ""
echo "2. Checking GitHub Token..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "   ${RED}❌ GITHUB_TOKEN not set${NC}"
    echo "      Run: export GITHUB_TOKEN='your_token_here'"
    echo "      Get token: https://github.com/settings/tokens"
    ((ERRORS++))
else
    echo -e "   ${GREEN}✅ GITHUB_TOKEN is set${NC}"
    echo "      Length: ${#GITHUB_TOKEN} characters"
fi

# Check 3: Google Cloud Project
echo ""
echo "3. Checking Google Cloud Configuration..."
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "   ${YELLOW}⚠️  GOOGLE_CLOUD_PROJECT not set (may use defaults)${NC}"
else
    echo -e "   ${GREEN}✅ GOOGLE_CLOUD_PROJECT: $GOOGLE_CLOUD_PROJECT${NC}"
fi

# Check 4: Google Credentials
echo ""
echo "4. Checking Google Cloud Credentials..."
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "   ${YELLOW}⚠️  GOOGLE_APPLICATION_CREDENTIALS not set${NC}"
else
    if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo -e "   ${GREEN}✅ Credentials file exists${NC}"
        echo "      Path: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo -e "   ${RED}❌ Credentials file not found${NC}"
        echo "      Path: $GOOGLE_APPLICATION_CREDENTIALS"
        ((ERRORS++))
    fi
fi

# Check 5: Required Python packages
echo ""
echo "5. Checking Python Dependencies..."
if [ -f "venv/bin/pip" ]; then
    # Check for aiohttp
    if venv/bin/pip show aiohttp > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ aiohttp installed${NC}"
    else
        echo -e "   ${RED}❌ aiohttp not installed${NC}"
        echo "      Run: source venv/bin/activate && pip install aiohttp"
        ((ERRORS++))
    fi
    
    # Check for google-cloud-aiplatform
    if venv/bin/pip show google-cloud-aiplatform > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ google-cloud-aiplatform installed${NC}"
    else
        echo -e "   ${RED}❌ google-cloud-aiplatform not installed${NC}"
        ((ERRORS++))
    fi
else
    echo -e "   ${YELLOW}⚠️  Cannot check (venv/bin/pip not found)${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "You're ready to run ActualCode:"
    echo "  source venv/bin/activate"
    echo "  python test_github_connection.py  # Test GitHub connection"
    echo "  python cli_runner.py              # Run the CLI"
else
    echo -e "${RED}❌ $ERRORS issue(s) found${NC}"
    echo ""
    echo "Please fix the issues above before running ActualCode."
    echo "See SETUP_GITHUB.md for detailed instructions."
fi
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

exit $ERRORS
