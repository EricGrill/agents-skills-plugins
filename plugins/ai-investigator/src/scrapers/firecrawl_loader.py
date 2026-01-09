import logging
from typing import Optional, Dict
from pathlib import Path
import json
import asyncio
from firecrawl import FirecrawlApp
from src.config import RAW_DIR, FIRECRAWL_API_KEY, MAX_RETRIES

logger = logging.getLogger(__name__)

class FirecrawlLoader:
    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        
    async def extract_case_study(self, url: str) -> Optional[Dict]:
        """Extract and process case study content using Firecrawl"""
        logger.info(f"Starting Firecrawl extraction for {url}")
        
        try:
            # Configure Firecrawl extraction parameters
            params = {
                "pageOptions": {
                    "onlyMainContent": True,
                    "waitForSelector": "body",
                    "removeSelectors": ["nav", "footer", "header", "script", "style"]
                },
                "extractorOptions": {
                    "formats": ["markdown", "html"],
                    "mode": "llm-extraction",
                    "extractionSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "company_name": {"type": "string"},
                            "industry": {"type": "string"},
                            "implementation_details": {"type": "string"},
                            "results": {"type": "string"},
                            "main_content": {"type": "string"}
                        }
                    }
                }
            }
            
            # Start crawl and get job ID
            crawl_result = await self.firecrawl.crawl_url(url, params)
            job_id = crawl_result.get('job_id')
            
            if not job_id:
                logger.error(f"No job ID returned for {url}")
                return None
                
            # Wait for crawl completion
            logger.info(f"Waiting for Firecrawl job {job_id} to complete...")
            content = await self.wait_for_completion(job_id)
            
            if not content:
                logger.error(f"Failed to get content for job {job_id}")
                return None
                
            # Extract and structure the content
            return {
                "url": url,
                "title": content.get('title', 'Untitled Case Study'),
                "content": content.get('main_content', ''),
                "structured_data": {
                    "title": content.get('title'),
                    "company_name": content.get('company_name'),
                    "industry": content.get('industry'),
                    "implementation_details": content.get('implementation_details'),
                    "results": content.get('results')
                },
                "metadata": {
                    "extraction_time": str(asyncio.get_event_loop().time()),
                    "job_id": job_id,
                    "content_length": len(content.get('main_content', ''))
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
            
    async def wait_for_completion(self, job_id: str, timeout: int = 300) -> Optional[Dict]:
        """Wait for Firecrawl job completion with timeout"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                status = await self.firecrawl.check_crawl_status(job_id)
                
                if status["status"] == "completed":
                    logger.info(f"Job {job_id} completed successfully")
                    return status["data"]
                elif status["status"] == "failed":
                    logger.error(f"Job {job_id} failed: {status.get('error')}")
                    return None
                    
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.error(f"Timeout waiting for job {job_id}")
                    return None
                    
                # Wait before next check
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error checking status for job {job_id}: {str(e)}")
                return None
                
    async def save_raw_content(self, case_id: int, content: Dict) -> bool:
        """Save raw case study content to file"""
        try:
            case_dir = Path(RAW_DIR) / f"case_{case_id}"
            case_dir.mkdir(exist_ok=True)
            
            # Save structured content
            with open(case_dir / "structured_content.json", "w", encoding="utf-8") as f:
                json.dump(content["structured_data"], f, indent=2)
            
            # Save raw content
            with open(case_dir / "raw_content.txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {content['title']}\n")
                f.write(f"URL: {content['url']}\n")
                f.write("\nContent:\n")
                f.write(content['content'])
            
            # Save metadata
            with open(case_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(content["metadata"], f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving content for case {case_id}: {str(e)}")
            return False