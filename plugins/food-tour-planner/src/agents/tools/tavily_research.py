"""Tavily research tool for neighborhood analysis."""

from typing import Dict, Any
from langchain_core.tools import tool


def create_tavily_tools(api_key: str):
    """Create Tavily research tools."""
    from tavily import TavilyClient
    
    tavily_client = TavilyClient(api_key=api_key)
    
    @tool
    def research_neighborhood(location_name: str, query_focus: str = "food and dining") -> Dict[str, Any]:
        """
        Research a neighborhood or location to understand its character, history, and attractions.
        
        Args:
            location_name: Name of the neighborhood or location (e.g., "Kensington Market Toronto")
            query_focus: Focus of the research (e.g., "food and dining", "nightlife", "culture")
        
        Returns:
            Research findings about the neighborhood
        """
        try:
            query = f"{location_name} {query_focus} guide attractions what to know"
            result = tavily_client.search(query, max_results=5)
            
            return {
                'location': location_name,
                'focus': query_focus,
                'summary': result.get('answer', ''),
                'sources': [
                    {
                        'title': r.get('title'),
                        'url': r.get('url'),
                        'content': r.get('content', '')[:500]
                    }
                    for r in result.get('results', [])[:3]
                ]
            }
        except Exception as e:
            return {'error': f'Research failed: {str(e)}'}
    
    @tool
    def research_food_trends(location_name: str) -> Dict[str, Any]:
        """
        Research current food trends, popular dishes, and culinary scene in a location.
        
        Args:
            location_name: Name of the location
        
        Returns:
            Information about food trends and popular dishes
        """
        try:
            query = f"{location_name} food trends popular dishes local cuisine must try 2024"
            result = tavily_client.search(query, max_results=5)
            
            return {
                'location': location_name,
                'findings': result.get('answer', ''),
                'sources': [
                    {'title': r.get('title'), 'url': r.get('url')}
                    for r in result.get('results', [])[:3]
                ]
            }
        except Exception as e:
            return {'error': f'Research failed: {str(e)}'}
    
    return [research_neighborhood, research_food_trends]

