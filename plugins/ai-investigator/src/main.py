import pandas as pd
import asyncio
import logging
from pathlib import Path
from typing import Dict, List
import json
from src.config import (
    INPUT_DIR, 
    RAW_DIR, 
    LOGS_DIR,
    LOG_FORMAT,
    SECTIONS_DIR,
    REPORTS_DIR
)
from src.scrapers.web_loader import WebLoader
from src.processors.claude_processor import ClaudeProcessor
from src.scrapers.website_crawler import WebsiteCrawler
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(Path(LOGS_DIR) / "processing_log.json"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()

async def load_urls_from_csv() -> List[str]:
    """Load URLs from CSV file"""
    try:
        # Try both possible filenames
        csv_path = Path(INPUT_DIR) / "ai case studies - Sheet1.csv"
        if not csv_path.exists():
            csv_path = Path(INPUT_DIR) / "urls.csv"
            
        if not csv_path.exists():
            logger.error(f"No CSV file found in {INPUT_DIR}")
            return []
            
        # Read the CSV file
        df = pd.read_csv(csv_path)
        first_column = df.columns[0]
        if first_column != 'url':
            df = df.rename(columns={first_column: 'url'})
        
        urls = df['url'].tolist()
        logger.info(f"Loaded {len(urls)} URLs from CSV")
        return urls
        
    except Exception as e:
        logger.error(f"Error loading URLs from CSV: {str(e)}")
        return []

async def process_case_study(web_loader: WebLoader, claude_processor: ClaudeProcessor, url: str, index: int, progress=None):
    """Process a single case study"""
    console.rule(f"Processing Case Study #{index + 1}")
    console.print(f"URL: {url}", style="blue")
    
    try:
        # Step 1: Extract content
        if progress:
            progress.update(progress.task_ids[0], description="📥 Extracting content...")
        content = await web_loader.extract_case_study(url)
        
        if not content:
            console.print("❌ Failed to extract content", style="red")
            return
            
        if progress:
            progress.update(progress.task_ids[0], description="💾 Saving raw content...")
        await web_loader.save_raw_content(index, content)
        
        # Step 2: Analyze relevance
        if progress:
            progress.update(progress.task_ids[0], description="🔍 Analyzing enterprise AI relevance...")
        analysis = await claude_processor.analyze_enterprise_relevance(content['content'])
        
        if analysis.get('is_enterprise_ai'):
            console.print("\n✅ Qualified as Enterprise AI Case Study", style="green")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Attribute", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("Company", analysis.get('company_details', {}).get('name', 'Unknown'))
            table.add_row("Industry", analysis.get('company_details', {}).get('industry', 'Unknown'))
            table.add_row("Technologies", ', '.join(analysis.get('ai_implementation', {}).get('technologies', [])))
            table.add_row("Confidence", f"{analysis.get('confidence_score', 0.0):.2f}")
            
            console.print(table)
            
            # Step 3: Generate reports
            if progress:
                progress.update(progress.task_ids[0], description="📝 Generating executive report...")
            executive_report = await claude_processor.generate_executive_report(
                content['content'], 
                analysis
            )
            
            if executive_report:
                if progress:
                    progress.update(progress.task_ids[0], description="💾 Saving reports...")
                if await claude_processor.save_reports(index, content, analysis, executive_report):
                    console.print("\nReports saved:", style="green")
                    console.print(f"📄 Individual report: reports/individual/case_{index}.md")
                    console.print(f"📊 Updated cross-case analysis: reports/cross_case_analysis/cross_case_analysis.json")
                    console.print(f"📈 Updated executive dashboard: reports/executive_dashboard/executive_dashboard.json")
                else:
                    console.print("❌ Failed to save some reports", style="red")
            else:
                console.print("❌ Failed to generate executive report", style="red")
        
        else:
            console.print("\n⚠️ Not an Enterprise AI Case Study", style="yellow")
            console.print(f"Reason: {analysis.get('disqualification_reason')}")
        
        # Wait before next case study
        await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"Error processing case study #{index + 1}: {str(e)}")
        console.print(f"❌ Error: {str(e)}", style="red")

async def process_website(website_url: str, web_loader: WebLoader, claude_processor: ClaudeProcessor, website_crawler: WebsiteCrawler):
    """Process an entire website for case studies"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Crawling website...", total=None)
            
            # Find case studies
            case_studies = await website_crawler.find_case_study_links(website_url, claude_processor)
            
            if not case_studies:
                console.print("❌ No case studies found on website", style="red")
                return
            
            # Display found case studies
            console.print(f"\n📊 Found {len(case_studies)} potential case studies:", style="green")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", justify="right")
            table.add_column("Title", style="yellow")
            table.add_column("URL", style="blue")
            
            for i, case in enumerate(case_studies, 1):
                table.add_row(
                    str(i),
                    case['title'],
                    case['url']
                )
            
            console.print(table)
            
            # Process each case study
            console.print("\n🔄 Starting analysis of case studies...", style="cyan")
            for index, case in enumerate(case_studies):
                await process_case_study(web_loader, claude_processor, case['url'], index, progress)
                
    except Exception as e:
        logger.error(f"Error processing website {website_url}: {str(e)}")
        console.print(f"❌ Error: {str(e)}", style="red")

async def main():
    """Main entry point for the case study analyzer"""
    try:
        # Initialize components
        web_loader = WebLoader()
        website_crawler = WebsiteCrawler()
        claude_processor = ClaudeProcessor()
        
        # Show welcome message
        console.print("\n=== AI Enterprise Case Study Analyzer ===", style="bold green")
        console.print("\nChoose analysis mode:", style="yellow")
        console.print("1. Analyze specific case study URLs from CSV")
        console.print("2. Analyze case studies from a company website")
        
        mode = console.input("\nEnter mode (1 or 2): ").strip()
        
        if mode == "1":
            urls = await load_urls_from_csv()
            if not urls:
                console.print("❌ No URLs found in CSV file", style="red")
                return
                
            console.print(f"\n📊 Found {len(urls)} URLs to analyze", style="green")
            for index, url in enumerate(urls):
                await process_case_study(web_loader, claude_processor, url, index)
                
        elif mode == "2":
            website_url = console.input("\nEnter company website URL: ").strip()
            await process_website(website_url, web_loader, claude_processor, website_crawler)
            
        else:
            console.print("❌ Invalid mode selected", style="red")
            return

        console.print("\n✅ Analysis complete!", style="bold green")

    except KeyboardInterrupt:
        console.print("\n\n⚠️ Process interrupted by user", style="yellow")
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        console.print(f"\n❌ Error: {str(e)}", style="red")

if __name__ == "__main__":
    asyncio.run(main())
