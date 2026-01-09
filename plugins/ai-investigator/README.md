# AI Enterprise Case Study Analyzer

An intelligent system for analyzing enterprise AI case studies using the Claude 3.5 Sonnet API. The system supports two main modes of operation:
1. Analyzing case studies from provided URLs in a CSV file.
2. Discovering and analyzing case studies from company websites using the Firecrawl API.

<img width="946" alt="Screenshot 2024-11-05 at 4 58 41 AM" src="https://github.com/user-attachments/assets/95be2e76-12bd-4dea-bd91-1b7d309f0f6d">
<img width="1153" alt="Screenshot 2024-11-05 at 4 58 49 AM" src="https://github.com/user-attachments/assets/7b935a1b-b79e-4fb3-85c7-cb18d48601bb">
<img width="1153" alt="Screenshot 2024-11-05 at 4 58 49 AM" src="https://github.com/user-attachments/assets/1669df59-a81a-4aab-b62b-149e1480a82a">
<img width="1141" alt="Screenshot 2024-11-05 at 5 03 37 AM" src="https://github.com/user-attachments/assets/370e2f63-fd1c-4af4-ae78-130b99fe4b0b">



## Core Features

### 1. Case Study Discovery & Analysis
- **CSV Mode**: Analyze specific case study URLs provided in a CSV file.
- **Website Mode**: Automatically discover and analyze case studies from company websites using Firecrawl's map endpoint.
- Intelligent case study identification powered by Claude 3.5 Sonnet.
- Content extraction handled by Firecrawl's scrape endpoint.

### 2. Content Processing Pipeline
- **Content Extraction** (via Firecrawl API):
  - **Map endpoint** (`/v1/map`): Discovers links on the website.
  - **Scrape endpoint** (`/v1/scrape`): Extracts content in markdown format and retrieves metadata for context.
- **Case Study Identification**:
  - Uses Claude to identify potential case study links.
  - Filters content to ensure only relevant case studies are processed.
- **Content Analysis**:
  - Checks for enterprise AI qualification.
  - Performs a detailed, multi-section analysis.
  - Assesses business impact and technology stack.

### 3. Report Generation
The system creates three types of reports:

#### a. Individual Case Study Reports (`reports/individual/`)
- Executive Summary
- AI Strategy Analysis
- Technical Implementation Details
- Business Impact Assessment
- Key Success Factors
- Lessons Learned

#### b. Cross-Case Analysis (`reports/cross_case_analysis/`)
- Patterns across multiple implementations.
- Common success factors.
- Technology trends.
- ROI metrics and implementation challenges.

#### c. Executive Dashboard (`reports/executive_dashboard/`)
- Company profiles
- Technology stacks
- Success metrics and implementation scales
- Overall trends in enterprise AI adoption

## Technical Architecture

### 1. Firecrawl Integration
- **Map Endpoint** (`/v1/map`):
  ```python
  map_result = app.map_url(website_url, params={'includeSubdomains': True})
  ```
  Used for discovering all links on a website.

- **Scrape Endpoint** (`/v1/scrape`):
  ```python
  params = {
      "url": url,
      "onlyMainContent": True,
      "formats": ["markdown"],
      "timeout": 30000
  }
  ```
  Used for content extraction from specific pages.

### 2. Claude 3.5 Sonnet Integration
- **Link Analysis**: Identifies relevant case study URLs.
- **Content Analysis**: Checks for enterprise AI relevance.
- **Report Generation**: Produces comprehensive, structured analysis reports.

### 3. Data Processing Workflow
Input (CSV/Website) → Firecrawl Map → Link Analysis → Content Extraction → Claude Analysis → Report Generation

## Project Structure
```
project/
├── src/
│   ├── scrapers/
│   │   ├── website_crawler.py  # Firecrawl map integration
│   │   └── web_loader.py       # Firecrawl scrape integration
│   ├── processors/
│   │   └── claude_processor.py # Claude API integration
│   ├── config.py               # Configuration settings
│   └── main.py                 # Main application logic
├── input/                      # Input CSV files
├── raw_content/                # Extracted raw content
│   └── case_[id]/
│       ├── raw_content.txt
│       ├── structured_content.json
│       └── metadata.json
├── reports/
│   ├── individual/             # Individual reports
│   ├── cross_case_analysis/    # Cross-case analysis
│   └── executive_dashboard/    # Executive dashboard
└── logs/                       # Processing logs
```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-case-study-analyzer.git
   cd ai-case-study-analyzer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables in `.env`**:
   ```
   ANTHROPIC_API_KEY=your_claude_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   ```

## Usage

### 1. CSV Analysis Mode
- Place your CSV file in the `input/` directory with a column named `url` containing case study URLs.

### 2. Website Analysis Mode
- Provide a company website URL to:
  1. Map all website links using Firecrawl.
  2. Identify and analyze case study content using Claude.
  3. Extract content and generate comprehensive reports.

**Run the analyzer**:
```bash
python -m src.main
```

## API Integration Details

### Firecrawl API
1. **Map Endpoint**:
   - Discovers all links on a website.
   - Parameters: `includeSubdomains: true`, `ignoreSitemap: false`, `limit: 5000`.

2. **Scrape Endpoint**:
   - Extracts main content from individual pages.
   - Parameters: `onlyMainContent: true`, `formats: ["markdown"]`, `timeout: 30000`.

### Claude 3.5 Sonnet API
1. **Link Analysis**:
   - Model: `claude-3-5-sonnet-20241022`.
   - Temperature: `0.2`.
   - Max tokens: `4096`.

2. **Content Analysis**:
   - Checks for enterprise AI qualification.
   - Performs multi-section analysis and report generation.

## Output Examples

### Individual Case Study Report
```markdown
# Enterprise AI Implementation Report: [Company Name]
1. **Executive Summary**
   [Summary of implementation and outcomes]

2. **AI Strategy Analysis**
   [Detailed analysis of AI strategy]
```

### Cross-Case Analysis
```json
{
  "case_1": {
    "company": {...},
    "technologies": [...],
    "success_factors": {...},
    "business_impact": {...}
  }
}
```

## Star History

<a href="https://star-history.com/#muratcankoylan/AI-Investigator&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=muratcankoylan/AI-Investigator&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=muratcankoylan/AI-Investigator&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=muratcankoylan/AI-Investigator&type=Date" />
 </picture>
</a>

## Contributing
Contributions are welcome!

## License
This project is licensed under the MIT License.
