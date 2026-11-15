"""Dashboard generator tool - creates HTML reports."""

import os
import json
from typing import Dict, Any
from langchain_core.tools import tool


def create_dashboard_tool(output_dir: str = "dashboards"):
    """Create dashboard generation tool."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    @tool
    def create_food_tour_dashboard(
        title: str,
        neighborhood_info: Dict[str, Any],
        establishments: list,
        recommendations: str,
        research_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an HTML dashboard for a food tour plan.
        
        Args:
            title: Title of the food tour
            neighborhood_info: Information about the neighborhood
            establishments: List of recommended establishments
            recommendations: Summary recommendations
            research_findings: Research data about the area
        
        Returns:
            Path to generated dashboard and success status
        """
        try:
            # Log the data being received
            print(f"\n{'='*70}")
            print(f"📊 DASHBOARD GENERATOR - Data Received:")
            print(f"{'='*70}")
            print(f"Title: {title}")
            print(f"Neighborhood Info: {neighborhood_info}")
            print(f"Establishments count: {len(establishments)}")
            for i, est in enumerate(establishments[:2]):
                print(f"\nEstablishment {i+1}:")
                print(f"  Name: {est.get('name')}")
                print(f"  Rating: {est.get('rating')}")
                print(f"  Total Reviews: {est.get('total_reviews')}")
                print(f"  Address: {est.get('address')}")
                print(f"  Photos: {len(est.get('photos', []))} photos")
                print(f"  Reviews: {len(est.get('reviews', []))} reviews")
                print(f"  Website: {est.get('website')}")
                print(f"  Types: {est.get('types')}")
            print(f"{'='*70}\n")
            
            # Build establishments HTML
            establishments_html = ""
            for est in establishments:
                # Meta badges
                meta_badges = [
                    f'<span class="meta-badge">⭐ {est.get("rating", "N/A")} ({est.get("total_reviews", 0)} reviews)</span>'
                ]
                if est.get('price_level'):
                    meta_badges.append(f'<span class="meta-badge">💰 {est.get("price_level")}</span>')
                if est.get('is_open') is not None:
                    status_icon = "🟢 Open" if est.get('is_open') else "🔴 Closed"
                    meta_badges.append(f'<span class="meta-badge">{status_icon}</span>')
                meta_html = "".join(meta_badges)

                # Address & links
                address_html = f'<p class="establishment-address">📍 {est.get("address", "N/A")}</p>'
                link_items = []
                if est.get('website'):
                    link_items.append(f'<a href="{est.get("website")}" target="_blank">Visit website ↗</a>')
                if est.get('phone'):
                    link_items.append(f'<span>📞 {est.get("phone")}</span>')
                links_html = ''
                if link_items:
                    links_html = '<div class="establishment-links">' + ' · '.join(link_items) + '</div>'

                # Tags
                tags_html = ''
                if est.get('types'):
                    display_tags = [t.replace('_', ' ') for t in est.get('types', [])[:3]]
                    tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in display_tags])

                # Build photos
                photos_html = ""
                if est.get('photos'):
                    photo_items = "".join([f'<div class="photo"><img src="{p.get("url")}" alt="{est.get("name")}"></div>' for p in est.get('photos', [])])
                    photos_html = f'<div class="photos">{photo_items}</div>'

                # Build reviews
                reviews_html = ""
                if est.get('reviews'):
                    review_items = ""
                    for review in est.get('reviews', []):
                        stars = "⭐" * review.get('rating', 0)
                        review_items += f'''<div class="review">
                            <div class="review-header">
                                <span>{review.get('author', 'Anonymous')}</span>
                                <span class="rating">{stars}</span>
                            </div>
                            <p class="review-text">{review.get('text', '')}</p>
                            <p class="review-meta">{review.get('time', '')}</p>
                        </div>'''
                    reviews_html = f'<div class="reviews"><h4>Recent Voices</h4>{review_items}</div>'

                establishments_html += f'''
            <div class="establishment">
                <div class="establishment-header">
                    <div class="establishment-body">
                        <h3>{est.get('name', 'Unknown')}</h3>
                        <div class="establishment-meta">{meta_html}</div>
                        {address_html}
                        {links_html}
                    </div>
                    <div class="establishment-tags">{tags_html}</div>
                </div>
                {photos_html}
                {reviews_html}
            </div>
            '''
            
            # Build research sources HTML
            sources_html = ""
            if research_findings.get('sources'):
                for source in research_findings.get('sources', []):
                    summary = source.get('content', '')[:220]
                    if summary and len(source.get('content', '')) > 220:
                        summary += '…'
                    sources_html += f'''<div class="source">
                    <a href="{source.get('url')}" target="_blank">{source.get('title')}</a>
                    <p>{summary}</p>
                </div>'''
            
            research_section = ""
            if sources_html or research_findings.get('summary'):
                research_section = f'''<div class="section">
            <h2><span class="icon">🔍</span>Deep Dives & Culture Notes</h2>
            <p class="section-summary">{research_findings.get('summary', '')}</p>
            <div class="research-sources">{sources_html}</div>
        </div>'''
            
            # Process recommendations to convert markdown to HTML
            def markdown_to_html(text):
                """Simple markdown to HTML converter for better readability."""
                import re
                
                # Convert **bold** to <strong>
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                
                # Convert bullet points and structure
                lines = text.split('\n')
                html_parts = []
                in_list = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if in_list:
                            html_parts.append('</ul>')
                            in_list = False
                        html_parts.append('<br>')
                        continue
                    
                    # Headers
                    if line.startswith('###'):
                        if in_list:
                            html_parts.append('</ul>')
                            in_list = False
                        html_parts.append(f'<h4>{line.replace("###", "").strip()}</h4>')
                    elif line.startswith('##'):
                        if in_list:
                            html_parts.append('</ul>')
                            in_list = False
                        html_parts.append(f'<h3>{line.replace("##", "").strip()}</h3>')
                    # Emoji-based time blocks (🌅, ☕, 🥐, etc.)
                    elif re.match(r'^[🌅☕🥐🌮🥙🍜🍕🍝🍔🍣🍱🥘🍲🍛🍳🥞🧇]', line):
                        if in_list:
                            html_parts.append('</ul>')
                            in_list = False
                        html_parts.append(f'<div class="tour-block">{line}</div>')
                    # Bullet points
                    elif line.startswith('- ') or line.startswith('* '):
                        if not in_list:
                            html_parts.append('<ul>')
                            in_list = True
                        html_parts.append(f'<li>{line[2:].strip()}</li>')
                    # Regular paragraphs
                    else:
                        if in_list:
                            html_parts.append('</ul>')
                            in_list = False
                        html_parts.append(f'<p>{line}</p>')
                
                if in_list:
                    html_parts.append('</ul>')
                
                return '\n'.join(html_parts)
            
            recommendations_html = markdown_to_html(recommendations)
            
            # Generate complete HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
            color: #0f172a;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 60px 30px 120px;
        }}
        .header {{
            background: rgba(255,255,255,0.92);
            border-radius: 28px;
            padding: 48px 56px;
            border: 1px solid rgba(148,163,184,0.18);
            box-shadow: 0 40px 80px rgba(15,23,42,0.10);
            backdrop-filter: blur(18px);
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 48px;
            font-weight: 700;
            color: #0f172a;
        }}
        .header .subtitle {{
            font-size: 18px;
            color: #475569;
            margin-top: 12px;
            letter-spacing: 0.01em;
        }}
        .section {{
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            padding: 36px 40px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 24px 48px rgba(15,23,42,0.08);
            margin-bottom: 32px;
        }}
        .section h2 {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 24px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 24px;
        }}
        .section h2 span.icon {{
            width: 40px;
            height: 40px;
            border-radius: 14px;
            background: #eef2ff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #4338ca;
        }}
        .section-summary {{
            font-size: 16px;
            line-height: 1.7;
            color: #475569;
        }}
        .neighborhood-info {{
            background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 100%);
            border-radius: 20px;
            border: 1px solid rgba(148,163,184,0.25);
            padding: 28px;
            color: #1e293b;
            line-height: 1.7;
            font-size: 16px;
        }}
        .establishment {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 18px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .establishment:hover {{
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(15,23,42,0.10);
        }}
        .establishment-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
            flex-wrap: wrap;
        }}
        .establishment-body {{
            flex: 1 1 280px;
        }}
        .establishment h3 {{
            font-size: 22px;
            font-weight: 600;
            color: #0f172a;
        }}
        .establishment-meta {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 16px 0 10px;
        }}
        .meta-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #f1f5f9;
            color: #334155;
            border-radius: 999px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 500;
        }}
        .establishment-address {{
            font-size: 15px;
            color: #475569;
            margin: 4px 0 0;
        }}
        .establishment-links {{
            margin-top: 12px;
            font-size: 15px;
            display: flex;
            gap: 18px;
            flex-wrap: wrap;
            color: #2563eb;
        }}
        .establishment-links a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }}
        .establishment-links a:hover {{
            text-decoration: underline;
        }}
        .establishment-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tag {{
            background: #eef2ff;
            color: #4338ca;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .photos {{
            margin-top: 24px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }}
        .photo img {{
            width: 100%;
            height: 160px;
            object-fit: cover;
            border-radius: 14px;
        }}
        .reviews {{
            margin-top: 24px;
            border-top: 1px solid #e2e8f0;
            padding-top: 24px;
        }}
        .reviews h4 {{
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
        }}
        .review {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .review-header {{
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            color: #1e293b;
        }}
        .review-text {{
            font-size: 14px;
            color: #475569;
            line-height: 1.6;
        }}
        .review-meta {{
            font-size: 12px;
            color: #94a3b8;
            letter-spacing: 0.04em;
        }}
        .rating {{
            color: #f59e0b;
            font-size: 16px;
        }}
        .recommendations {{
            border-radius: 20px;
            background: linear-gradient(135deg, #111c44 0%, #1f2937 100%);
            color: #f8fafc;
            padding: 32px 36px;
            font-size: 16px;
            line-height: 1.8;
            border: 1px solid rgba(148,163,184,0.2);
            box-shadow: 0 30px 60px rgba(15,23,42,0.35);
        }}
        .recommendations h3 {{
            margin-top: 20px;
            margin-bottom: 16px;
            font-size: 22px;
            font-weight: 600;
            color: #f8fafc;
        }}
        .recommendations h4 {{
            margin-top: 16px;
            margin-bottom: 12px;
            font-size: 18px;
            font-weight: 600;
            color: #e0e7ff;
        }}
        .recommendations p {{
            margin-bottom: 14px;
            color: #e2e8f0;
        }}
        .recommendations ul {{
            margin: 16px 0 0 0;
            padding-left: 18px;
        }}
        .recommendations li {{
            margin-bottom: 12px;
            color: #e2e8f0;
        }}
        .recommendations strong {{
            color: #fbbf24;
            font-weight: 600;
        }}
        .tour-block {{
            background: rgba(255,255,255,0.08);
            border-left: 4px solid #fbbf24;
            border-radius: 12px;
            padding: 20px 24px;
            margin: 16px 0;
            font-size: 16px;
            line-height: 1.7;
        }}
        .tour-block strong {{
            color: #fcd34d;
        }}
        .research-sources {{
            margin-top: 28px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }}
        .source {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 20px;
            line-height: 1.6;
            color: #1e293b;
        }}
        .source a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }}
        .source a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 60px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
        }}
        .footer strong {{
            color: #1e293b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">AI-crafted food tour intelligence</div>
        </div>

        <div class="section">
            <h2><span class="icon">📍</span>About the Neighborhood</h2>
            <div class="neighborhood-info">
                <p><strong>Location:</strong> {neighborhood_info.get('name', 'N/A')}</p>
                <p style="margin-top: 10px;">{neighborhood_info.get('description', 'No description available')}</p>
            </div>
        </div>

        <div class="section">
            <h2><span class="icon">🍽️</span>Recommended Establishments</h2>
            {establishments_html}
        </div>

        <div class="section">
            <h2><span class="icon">💡</span>Tour Recommendations</h2>
            <div class="recommendations">{recommendations_html}</div>
        </div>

        {research_section}

        <div class="footer">
            <p>Generated by DeepAgent Food Tour Scanner</p>
            <p style="margin-top: 10px;">🧠 Using LangChain, Google Maps API, and Tavily Research</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Save file
            filename = f"{title.replace(' ', '_').lower()}.html"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f'Dashboard created successfully at {filepath}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Dashboard creation failed: {str(e)}'
            }
    
    return [create_food_tour_dashboard]

