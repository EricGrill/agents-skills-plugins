import asyncio
import os
import logging
import sys
from anthropic import Anthropic
import aiohttp
from dotenv import load_dotenv

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import (
    ANTHROPIC_API_KEY, 
    DEBUG, 
    LOG_FORMAT,
    INPUT_DIR,
    RAW_DIR,
    SECTIONS_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    CLAUDE_MODEL
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "setup_test.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_directories():
    """Test if all required directories exist and are writable"""
    logger.info("Testing directory structure...")
    directories = [INPUT_DIR, RAW_DIR, SECTIONS_DIR, REPORTS_DIR, LOGS_DIR]
    
    for directory in directories:
        if not os.path.exists(directory):
            logger.error(f"Directory missing: {directory}")
            return False
        
        # Test write permissions
        test_file = os.path.join(directory, ".test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"Directory OK: {directory}")
        except Exception as e:
            logger.error(f"Cannot write to directory {directory}: {str(e)}")
            return False
    
    return True

async def test_claude():
    """Test Claude API connection"""
    logger.info("Testing Claude API connection...")
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        
        # Access the response content
        if response.content and len(response.content) > 0:
            logger.info(f"Claude response: {response.content[0].text}")
            logger.info("Claude API test successful!")
            return True
        else:
            logger.error("No content in Claude response")
            return False
    except Exception as e:
        logger.error(f"Claude API test failed: {str(e)}")
        return False

async def test_web_access():
    """Test web access to case study URLs"""
    logger.info("Testing web access...")
    test_url = "https://aws.amazon.com/solutions/case-studies/airbnb-case-study/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    logger.info("Web access test successful!")
                    return True
                else:
                    logger.error(f"Web access test failed with status: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Web access test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    load_dotenv()
    
    # Test environment variables
    logger.info("\nChecking environment variables...")
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return
    
    logger.info("Environment variables loaded successfully!")
    
    # Run tests
    tests = [
        ("Directory Structure", test_directories()),
        ("Claude API", test_claude()),
        ("Web Access", test_web_access())
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\nRunning test: {test_name}")
        result = await test_coro
        results.append((test_name, result))
        
    # Print summary
    print("\nTest Summary:")
    print("-" * 40)
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Exit with appropriate status code
    if all(result for _, result in results):
        logger.info("All tests passed successfully!")
        sys.exit(0)
    else:
        logger.error("Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())