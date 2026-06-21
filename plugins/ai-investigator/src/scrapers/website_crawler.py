import ast
import logging
import re
from typing import List, Dict, Optional
from src.processors.claude_processor import ClaudeProcessor
from src.config import FIRECRAWL_API_KEY
from firecrawl import FirecrawlApp

logger = logging.getLogger(__name__)

class WebsiteCrawler:
    def __init__(self):
        self.app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        self.claude_processor = None

    async def find_case_study_links(self, website_url: str, claude_processor: ClaudeProcessor) -> List[Dict[str, str]]:
        """Find case study links using Firecrawl's map endpoint and Claude's analysis"""
        self.claude_processor = claude_processor
        
        # Normalize the URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
            
        print(f"\nStarting crawl of {website_url}")
        print("This may take a few minutes...")

        try:
            # Step 1: Use Firecrawl's map endpoint to get ALL website links
            map_result = self.app.map_url(website_url, params={
                'includeSubdomains': True
            })
            
            if not map_result or 'links' not in map_result:
                logger.error("No links found in website map")
                return []

            all_links = map_result['links']
            print(f"\nFound {len(all_links)} total links")
            print("\nAll mapped links:")
            for i, link in enumerate(all_links):
                print(f"{i}. {link}")
            
            # Step 2: Let Claude analyze ALL links and identify case studies
            case_studies = await self._identify_case_studies(all_links)
            return case_studies

        except Exception as e:
            logger.error(f"Error crawling website {website_url}: {str(e)}")
            return []

    async def _identify_case_studies(self, links: List[str]) -> List[Dict[str, str]]:
        """Use Claude to identify which links are likely case studies"""
        prompt = """You are an expert at identifying case study, customer story, and success story content on company websites.

Carefully analyze the provided URLs and determine which ones are likely to lead to case studies, customer stories, success stories, or similar content.

Look for the following key patterns in the URLs:

1. Direct case study URLs:
   - /case-studies/
   - /case-studies/[specific-company-name]
   - /case-studies/how-[company-name]-used-[product]

2. Customer story URLs:
   - /customer-stories/
   - /customer-stories/[company-name]
   - /customers/[company-name]

3. Success story URLs:
   - /success-stories/
   - /success/[company-name]

4. Implementation/use case URLs:
   - URLs containing "how-[company-name]-used" or "how-to-use"
   - URLs describing specific product implementations or use cases

5. Customer example URLs:
   - URLs with [company-name] followed by implementation details
   - URLs describing specific customer use cases

Additionally, be aware of blog or news-related URLs that may contain case study content:

6. Blog/news URLs:
   - URLs containing "blog", "blogs", "news", or "newsroom"
   - URLs with brand names in the path

Analyze the provided list of URLs carefully and thoroughly. Identify ALL URLs that match the patterns above or appear to be case studies, customer stories, or similar content.

Return a JSON list of the indices of all URLs that you believe will lead to case study-related content. Do not include any other text.

Example: [0, 2, 5]

URLs to analyze:
{urls}
        """

        # Prepare URLs for Claude
        urls_data = []
        for i, url in enumerate(links):
            urls_data.append(f"{i}. {url}")

        print("\nClaude API Request:")
        print("Prompt:")
        print(prompt.format(urls='\n'.join(urls_data)))

        # Get Claude's analysis
        response = await self.claude_processor.analyze_links(
            prompt.format(urls='\n'.join(urls_data))
        )

        print("\nClaude API Response:")
        print(response)

        try:
            # Safely parse the list of indices from the LLM response.
            # Never use eval(): the response is derived from scraped web pages
            # and could contain arbitrary code.
            case_study_indices = self._parse_indices(response)

            # Get the identified case study URLs
            case_studies = []
            for i in case_study_indices:
                if i < len(links):
                    case_studies.append({
                        'url': links[i],
                        'title': self._extract_title_from_url(links[i])
                    })
            
            return case_studies
            
        except Exception as e:
            logger.error(f"Error processing Claude's response: {str(e)}")
            return []

    def _parse_indices(self, response: str) -> List[int]:
        """Safely parse a list of integer indices from an LLM response.

        The response is expected to be a JSON/Python list of integers, e.g.
        "[0, 2, 5]". It may be wrapped in markdown code fences or surrounded by
        extra prose. We use ast.literal_eval (never eval) and fall back to
        extracting the first bracketed substring. Returns [] on failure.
        """
        if not response:
            return []

        text = response.strip()

        # Strip surrounding markdown code fences if present.
        if text.startswith("```"):
            text = text.strip("`").strip()
            # Drop a leading language hint like "json" or "python".
            if "\n" in text:
                first_line, rest = text.split("\n", 1)
                if first_line.strip().isalpha():
                    text = rest.strip()

        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError):
            # Fall back to extracting the first [...] bracketed substring.
            match = re.search(r"\[.*?\]", text, re.DOTALL)
            if match:
                try:
                    return ast.literal_eval(match.group(0))
                except (ValueError, SyntaxError):
                    pass
            logger.warning(
                "Could not parse indices from response; defaulting to empty list. "
                f"Response was: {response!r}"
            )
            return []

    def _extract_title_from_url(self, url: str) -> str:
        """Extract a readable title from URL path"""
        try:
            # Remove protocol and domain
            path = url.split('/')[-1]
            # Convert dashes and underscores to spaces
            title = path.replace('-', ' ').replace('_', ' ').strip()
            # Capitalize words
            return title.title() if title else "Untitled Case Study"
        except Exception:
            return "Untitled Case Study"