import logging
import json
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, Optional
from src.config import RAW_DIR, FIRECRAWL_API_KEY

logger = logging.getLogger(__name__)

class WebLoader:
    def __init__(self):
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }

    async def extract_case_study(self, url: str) -> Optional[Dict]:
        """Extract and process case study content using Firecrawl"""
        logger.info(f"Starting Firecrawl extraction for {url}")
        
        try:
            # Configure Firecrawl extraction parameters
            params = {
                "url": url,
                "onlyMainContent": True,
                "formats": ["markdown"],
                "timeout": 30000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/scrape",
                    headers=self.headers,
                    json=params,
                    verify_ssl=False
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Firecrawl scrape failed: {response.status} - {error_text}")
                        return None

                    data = await response.json()
                    
                    if not data.get('success') or not data.get('data'):
                        logger.error(f"No content returned from Firecrawl for {url}")
                        return None

                    # Extract content from Firecrawl response
                    content_data = data['data']
                    metadata = content_data.get('metadata', {})
                    
                    # Structure the content
                    structured_data = {
                        "title": metadata.get('title', ''),
                        "content": content_data.get('markdown', ''),
                        "url": url,
                        "metadata": metadata
                    }
                    
                    return structured_data

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None

    async def save_raw_content(self, case_id: int, content: Dict):
        """Save raw content to file"""
        try:
            # Create case directory
            case_dir = Path(RAW_DIR) / f"case_{case_id}"
            case_dir.mkdir(exist_ok=True)
            
            # Save raw content
            with open(case_dir / "raw_content.txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {content.get('title', '')}\n")
                f.write(f"URL: {content.get('url', '')}\n\n")
                f.write("Content:\n")
                f.write(content.get('content', ''))
                
            # Save metadata
            with open(case_dir / "metadata.json", "w", encoding="utf-8") as f:
                metadata = {
                    "title": content.get('title'),
                    "url": content.get('url'),
                    "extraction_timestamp": str(asyncio.get_event_loop().time()),
                    "metadata": content.get('metadata', {})
                }
                json.dump(metadata, f, indent=2)
                
            # Save structured content
            with open(case_dir / "structured_content.json", "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving raw content for case {case_id}: {str(e)}")
            return False
