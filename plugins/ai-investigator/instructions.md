# AI Enterprise Case Study Analyzer

Build a Python application using Claude 3.5 Sonnet API to analyze and generate structured reports on enterprise AI adoption case studies.

## NEW FEATURE: Company Website Case Study Extraction

The system should now support analyzing case studies not only from direct URLs but also by crawling company websites to find and extract case study links for analysis.
Users must be prompted to choose between analyzing a provided case study URL or analyzing a company website for case studies.

###INPUT REQUIREMENTS

- CSV file containing URLs of potential AI case studies OR a company website URL.
- The system should analyze and filter for enterprise-specific AI implementation cases.
- Whenever an enterprise AI case study is detected, it should be saved for further processing.

### ANALYSIS CRITERIA

- Must involve established companies (not startups).
- Focus on business AI implementation.
- Clear business outcomes and metrics.
- Enterprise-scale deployment.

### CONTENT REQUIREMENTS

- AI/ML technology implementation details.
- Enterprise integration aspects.
- Business process transformation.
- ROI or business impact metrics.
- Change management approach.

### PROCESSING WORKFLOW

#### PHASE 1: Case Study Collection & Filtering

- User Input Selection:
  - Prompt the user to choose between:
    - Analyzing a case study from a provided URL.
    - Analyzing a company website to find case study links.
- Case Study URL Analysis:
  - Scrape content from the provided URL using web_loader.
  - Analyze with Claude to determine if it qualifies as an enterprise AI case study.
  - Filter out non-enterprise or non-AI cases.
  - Save qualified content for further processing.

#### PHASE 2: Company Website Analysis (New Feature)

- Scrape the company website to find case study links.
- Create a structured table listing found case study URLs.
- Analyze each extracted URL using the current system.
- Inform the user of case studies found and analyzed.

#### PHASE 3: Detailed Analysis

- For each qualified case study:

  - Extract and analyze six key sections:
    - Company Context & AI Strategy.
    - Business Challenge & Opportunity.
    - AI Solution Architecture.
    - Implementation & Integration.
    - Change Management & Adoption.
    - Business Impact & Lessons.

- Generate structured insights:
  - AI technologies used.
    - Integration patterns.
    - Success metrics.
    - Implementation challenges.
    - Best practices identified.

#### PHASE 4: Report Generation

- Generate three types of reports:
  - Individual Case Study Reports (PDF).
  - Cross-Case Analysis Report (PDF).
  - Executive Insights Dashboard (JSON).

### TECHNICAL SPECIFICATIONS

- Claude Configuration:
  - Model: claude-3-5-sonnet-20241022.
  - Temperature: 0.2.
  - Output Context Window: 8192 tokens.

#### PROCESSING PIPELINE

- Web Content Extraction.
- Enterprise AI Case Validation.
- Structured Analysis.
Report Generation.
  - Cross-Case Pattern Analysis.

### OUTPUT REQUIREMENTS

Each qualified case study generates:

- Validation Report:
  - Enterprise AI qualification criteria met.
  - Data quality assessment.
  - Content completeness check.
- Detailed Analysis Report:
  - Executive Summary.
  - AI Strategy Analysis.
  - Technical Implementation Details.
Business Impact Assessment.
  - Key Success Factors.
  - Lessons Learned.
- Cross-Case Insights:
  - Common patterns.
Success factors.
Implementation challenges.
Technology trends.
  - ROI patterns.

### ERROR HANDLING & LOGGING

- Track and log:
  - Case study qualification decisions.
  - Content extraction issues.
  - Analysis completeness.
Pattern detection confidence.
  - Processing errors and retries.

### VALIDATION CRITERIA

- Enterprise AI Case Validation:
  - Company size/maturity check.
  - AI implementation scope.
  - Business process integration.
  - Measurable outcomes.
  - Enterprise-scale considerations.
- Report Quality Validation:
  - Content completeness.
  - Technical accuracy.
  - Business impact quantification.
Implementation detail sufficiency.
  - Cross-reference verification.

### USAGE WORKFLOW

- User Input Phase
Prompt: Choose to either:
Analyze a provided case study URL.
  - Analyze a company website to find and analyze case studies.

- Case Study URL Workflow:
  - Extract content using firecrawl or web_loader.
  - Send text to Claude for analysis.
Print terminal feedback:
  - If the content qualifies, generate and save the report.
  - If not, print the reason and move to the next URL.

- Company Website Workflow:
  - Scrape the provided website URL.
  - Locate case study links and compile them into a structured table.
  - Print the found links and analyze them using the current case study process.
  - Inform the user of progress via terminal.

- Output Saving:
  - Save the individual case study report in reports/individual.
  - Save cross-case analysis in reports/cross_case_analysis.
  - Save the executive dashboard data in reports/executive_dashboard.json.


  ---

  ### IMPORTANT

  - We should use Firecrawl for scraping the website content and maps. @docs: https://docs.firecrawl.com/
@firecrawl python @firecrawl scrape  @Firecrawl crawl @Firecrawl intro @Firecrawl crawl get @firecrawl langchain @Firecrawl map @Firecrawl scrape 