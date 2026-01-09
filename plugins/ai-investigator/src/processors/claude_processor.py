from anthropic import Anthropic
import json
import logging
from typing import Dict, Optional, List
from pathlib import Path
from src.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_TEMPERATURE,
    CLAUDE_MAX_TOKENS,
    SECTIONS_DIR,
    REPORTS_INDIVIDUAL_DIR,
    REPORTS_CROSS_CASE_DIR,
    REPORTS_EXECUTIVE_DIR
)

logger = logging.getLogger(__name__)

class ClaudeProcessor:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
    async def analyze_enterprise_relevance(self, content: str) -> Dict:
        """Determine if the case study is relevant for enterprise AI analysis"""
        prompt = """You are an AI expert analyzing enterprise case studies. Review this case study and determine if it describes an enterprise AI implementation case study.

        Key criteria:
        1. Must be about an established company (not a startup)
        2. Must describe actual AI/ML implementation (not just plans or general AI discussion)
        3. Must show enterprise-scale deployment
        4. Must include clear business outcomes or metrics

        Review the following case study content and provide your analysis in JSON format.
        
        Case Study Content:
        ----------------
        {content}
        ----------------

        Respond with a JSON object in this exact format, no other text:
        {{
            "is_enterprise_ai": true or false,
            "confidence_score": number between 0 and 1,
            "company_details": {{
                "name": "company name",
                "industry": "industry name",
                "size_category": "Large Enterprise/Mid-size/Small"
            }},
            "ai_implementation": {{
                "technologies": ["technology1", "technology2"],
                "scale": "description of deployment scale",
                "business_areas": ["area1", "area2"]
            }},
            "qualification_criteria": {{
                "established_company": true or false,
                "business_focus": true or false,
                "enterprise_scale": true or false,
                "clear_outcomes": true or false
            }},
            "disqualification_reason": null or "reason if not qualified"
        }}"""
        
        try:
            # Create message with Claude
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                temperature=0.1,  # Lower temperature for more consistent JSON
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user", 
                    "content": prompt.format(content=content)
                }]
            )
            
            # Get response text
            response_text = response.content[0].text.strip()
            logger.debug(f"Raw Claude response: {response_text}")
            
            # Clean up the response text
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1]
            
            # Remove any leading/trailing whitespace and newlines
            response_text = response_text.strip()
            
            try:
                # Parse JSON
                analysis = json.loads(response_text)
                
                # Log successful analysis
                logger.info(f"Successfully analyzed content: {json.dumps(analysis, indent=2)}")
                
                # Validate required fields
                required_fields = ['is_enterprise_ai', 'confidence_score', 'company_details', 'qualification_criteria']
                if not all(field in analysis for field in required_fields):
                    logger.error(f"Missing required fields. Found: {list(analysis.keys())}")
                    raise ValueError("Missing required fields in response")
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Response text: {response_text}")
                
                # Return default response for JSON parsing errors
                return {
                    "is_enterprise_ai": False,
                    "confidence_score": 0.0,
                    "company_details": {
                        "name": "Unknown",
                        "industry": "Unknown",
                        "size_category": "Unknown"
                    },
                    "ai_implementation": {
                        "technologies": [],
                        "scale": "Unknown",
                        "business_areas": []
                    },
                    "qualification_criteria": {
                        "established_company": False,
                        "business_focus": False,
                        "enterprise_scale": False,
                        "clear_outcomes": False
                    },
                    "disqualification_reason": "Failed to parse analysis results"
                }
                
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "is_enterprise_ai": False,
                "confidence_score": 0.0,
                "company_details": {
                    "name": "Unknown",
                    "industry": "Unknown",
                    "size_category": "Unknown"
                },
                "ai_implementation": {
                    "technologies": [],
                    "scale": "Unknown",
                    "business_areas": []
                },
                "qualification_criteria": {
                    "established_company": False,
                    "business_focus": False,
                    "enterprise_scale": False,
                    "clear_outcomes": False
                },
                "disqualification_reason": f"Error analyzing content: {str(e)}"
            }
            
    async def generate_section_analysis(self, content: str, section: str) -> str:
        """Generate detailed analysis for a specific section"""
        section_prompts = {
            "company_context": """
            Analyze the company context and AI strategy. Focus on:
            - Company background and industry position
            - Strategic drivers for AI adoption
            - Initial AI maturity and capabilities
            - Strategic objectives and expected outcomes
            """,
            
            "business_challenge": """
            Analyze the business challenges and opportunities. Focus on:
            - Key business problems addressed
            - Market or operational pressures
            - Existing process limitations
            - Opportunity assessment and potential impact
            """,
            
            "solution_architecture": """
            Analyze the AI solution architecture. Focus on:
            - AI/ML technologies and frameworks used
            - System architecture and integration points
            - Data infrastructure and pipelines
            - Technical capabilities and innovations
            """,
            
            "implementation": """
            Analyze the implementation approach. Focus on:
            - Implementation methodology
            - Team structure and capabilities
            - Timeline and key milestones
            - Technical and organizational challenges
            """,
            
            "change_management": """
            Analyze the change management and adoption. Focus on:
            - Change management strategy
            - Training and skill development
            - User adoption approach
            - Organizational challenges and solutions
            """,
            
            "business_impact": """
            Analyze the business impact and lessons. Focus on:
            - Quantitative business outcomes
            - Qualitative improvements
            - ROI and success metrics
            - Key learnings and best practices
            """
        }
        
        prompt = f"""
        Analyze this enterprise AI case study and provide detailed insights for the {section} section.
        
        {section_prompts[section]}
        
        Provide your analysis in a clear, structured format with main findings and supporting details.
        Use markdown formatting for better readability.
        
        Case study content:
        {content}
        """
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                temperature=CLAUDE_TEMPERATURE,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating {section} analysis: {str(e)}")
            return None
            
    async def save_section_analysis(self, case_id: int, section: str, content: str) -> bool:
        """Save section analysis to file"""
        try:
            case_dir = Path(SECTIONS_DIR) / f"case_{case_id}"
            case_dir.mkdir(exist_ok=True)
            
            with open(case_dir / f"{section}.md", "w", encoding="utf-8") as f:
                f.write(content)
                
            return True
        except Exception as e:
            logger.error(f"Error saving {section} analysis for case {case_id}: {str(e)}")
            return False

    async def generate_executive_report(self, content: str, analysis: Dict) -> str:
        """Generate executive report for a qualified case study"""
        prompt = """Create an executive report for this enterprise AI case study.
        
        Previous Analysis:
        {analysis}
        
        Format the report in markdown with these sections:
        1. Executive Summary
        2. AI Strategy Analysis
        3. Technical Implementation Details
        4. Business Impact Assessment
        5. Key Success Factors
        6. Lessons Learned
        
        Case Study Content:
        {content}
        """
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                temperature=CLAUDE_TEMPERATURE,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user", 
                    "content": prompt.format(
                        content=content,
                        analysis=json.dumps(analysis, indent=2)
                    )
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating executive report: {str(e)}")
            return None

    async def save_reports(self, case_id: int, content: Dict, analysis: Dict, executive_report: str):
        """Save all reports for a qualified case study"""
        try:
            # Save individual case study report
            individual_report_path = Path(REPORTS_INDIVIDUAL_DIR) / f"case_{case_id}.md"
            with open(individual_report_path, "w", encoding="utf-8") as f:
                f.write(executive_report)
                
            # Update cross-case analysis
            cross_case_path = Path(REPORTS_CROSS_CASE_DIR) / "cross_case_analysis.json"
            cross_case_data = {}
            if cross_case_path.exists():
                with open(cross_case_path, "r") as f:
                    cross_case_data = json.load(f)
                    
            # Add this case study to cross-case analysis
            cross_case_data[f"case_{case_id}"] = {
                "company": analysis["company_details"],
                "technologies": analysis["ai_implementation"]["technologies"],
                "success_factors": analysis["qualification_criteria"],
                "business_impact": analysis.get("business_impact", {})
            }
            
            with open(cross_case_path, "w") as f:
                json.dump(cross_case_data, f, indent=2)
                
            # Update executive dashboard
            dashboard_path = Path(REPORTS_EXECUTIVE_DIR) / "executive_dashboard.json"
            dashboard_data = {}
            if dashboard_path.exists():
                with open(dashboard_path, "r") as f:
                    dashboard_data = json.load(f)
                    
            # Add summary to dashboard
            dashboard_data[f"case_{case_id}"] = {
                "company": analysis["company_details"]["name"],
                "industry": analysis["company_details"]["industry"],
                "confidence_score": analysis["confidence_score"],
                "implementation_scale": analysis["ai_implementation"]["scale"],
                "key_technologies": analysis["ai_implementation"]["technologies"]
            }
            
            with open(dashboard_path, "w") as f:
                json.dump(dashboard_data, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving reports for case {case_id}: {str(e)}")
            return False

    async def analyze_links(self, prompt: str) -> str:
        """Analyze links to identify case studies"""
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                temperature=0.2,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error analyzing links: {str(e)}")
            return "[]"  # Return empty list on error
