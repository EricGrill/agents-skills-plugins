"""Main DeepAgent for food tour planning."""

import os
from typing import Dict, Any, List, Optional
from deepagents import create_deep_agent
from .tools.places_lightweight import PlacesLightweightTools
from .tools.tavily_research import create_tavily_tools
from .tools.dashboard_generator import create_dashboard_tool


class FoodTourDeepAgent:
    """Main agent for intelligent food tour planning."""
    
    def __init__(
        self,
        google_maps_api_key: str,
        tavily_api_key: str,
        anthropic_api_key: str,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        self.google_maps_key = google_maps_api_key
        self.tavily_key = tavily_api_key
        self.model = model
        
        # Set API keys in environment
        os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
        os.environ['TAVILY_API_KEY'] = tavily_api_key
        
        # Initialize tool providers
        self.places_tools = PlacesLightweightTools(google_maps_api_key)
        self.tavily_tools = create_tavily_tools(tavily_api_key)
        self.dashboard_tools = create_dashboard_tool()
        
        # Create the main agent
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the Deep Agent with subagents and tools."""
        
        # Main agent system prompt
        system_prompt = """You are an intelligent food tour planning assistant.

Your mission is to create personalized, engaging food tour experiences based on user requests.

When a user provides a location and request (e.g., "I want a fun evening in Kensington Market"),
you should:

1. **PLAN** the task using the write_todos tool to break down what needs to be done
2. **DELEGATE TO SUBAGENTS** for specialized tasks:
   - Use 'neighborhood-researcher' subagent for research about the area's culture and history
   - Use 'restaurant-finder' subagent ONLY for complex queries and reasoning about establishments
   - Use 'dashboard-creator' subagent to generate the final HTML dashboard
3. **CALL TOOLS DIRECTLY** when you need raw data:
   - Call search_restaurants_nearby() YOURSELF to get detailed establishment data with reviews, photos, ratings
   - Call geocode_location() YOURSELF if you need to convert addresses to coordinates
   - These tools return structured JSON - preserve this data for the dashboard!
4. **CREATE THE DASHBOARD** by passing the FULL structured data from tool calls to dashboard-creator

CRITICAL: When calling dashboard-creator, pass the complete establishment objects from search_restaurants_nearby(),
including: name, rating, total_reviews, address, photos, reviews, phone, website, price_level, is_open.
DO NOT manually recreate the objects - pass them as-is from the API response.

Always consider:
- The user's intent (fun evening, romantic dinner, quick lunch, etc.)
- Neighborhood character and what makes it special
- Balance between popular spots and hidden gems
- Practical details (opening hours, price levels)
- Creating a cohesive narrative that tells the story of the neighborhood

Keep your responses concise and focused. Let the tools do the heavy lifting."""

        # Subagent for restaurant finding
        restaurant_subagent = {
            "name": "restaurant-finder",
            "description": "Specialized agent for finding and evaluating restaurants, cafes, and food establishments",
            "system_prompt": """You are a restaurant finding specialist. Your job is to:
1. Search for relevant food establishments based on coordinates and user preferences
2. Evaluate the results based on ratings, reviews, and relevance
3. Return a curated list with the most relevant options

Focus on quality over quantity. Provide context about why each place is recommended.""",
            "tools": self.places_tools.get_tools(),
            "model": self.model
        }
        
        # Subagent for neighborhood research
        research_subagent = {
            "name": "neighborhood-researcher",
            "description": "Specialized agent for researching neighborhoods, food trends, and local culture",
            "system_prompt": """You are a neighborhood research specialist. Your job is to:
1. Research the neighborhood's history, character, and food scene
2. Identify current food trends and popular dishes in the area
3. Provide context that helps understand why certain establishments are special

Provide rich, engaging insights that bring the neighborhood to life.""",
            "tools": self.tavily_tools,
            "model": self.model
        }
        
        # Subagent for dashboard creation
        dashboard_subagent = {
            "name": "dashboard-creator",
            "description": "Specialized agent for creating beautiful HTML dashboards with tour recommendations",
            "system_prompt": """You are a dashboard creation specialist. Your job is to:
1. Take all the gathered information (establishments, research, recommendations)
2. Organize it into a coherent, engaging format
3. Generate a beautiful HTML dashboard using the create_food_tour_dashboard tool

IMPORTANT: When calling create_food_tour_dashboard, you must pass:
- title: String - creative title for the tour
- neighborhood_info: Dict with 'name' and 'description' keys (description should be substantive, not empty)
- establishments: Array of complete establishment objects (DO NOT modify or recreate them)
- recommendations: String - your tour narrative with personalized suggestions
- research_findings: Dict with 'summary' and optional 'sources' array

The establishments array should contain the EXACT objects received, with all fields:
name, rating, total_reviews, address, location, price_level, types, website, phone, is_open, photos, reviews

Make sure the dashboard tells a story and makes the user excited about their food tour.""",
            "tools": self.dashboard_tools,
            "model": self.model
        }
        
        # Create the Deep Agent
        agent = create_deep_agent(
            model=self.model,
            subagents=[restaurant_subagent, research_subagent, dashboard_subagent],
            tools=self.places_tools.get_tools(),  # Give main agent direct access to Places tools
            system_prompt=system_prompt
        )
        
        return agent
    
    async def plan_food_tour(
        self,
        location_name: str,
        coordinates: Dict[str, float],
        user_prompt: str,
        stream_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Plan a food tour based on user request.
        
        Args:
            location_name: Name of the location/neighborhood
            coordinates: Dict with 'lat' and 'lng'
            user_prompt: User's request (e.g., "I want a fun evening here")
            stream_callback: Optional callback for streaming responses
        
        Returns:
            Planning results including dashboard path
        """
        # Construct the agent input
        user_message = f"""
Location: {location_name}
Coordinates: {coordinates['lat']}, {coordinates['lng']}

User Request: {user_prompt}

Please plan a food tour for this request. Follow these steps:

1. Use write_todos to plan your approach

2. Delegate to 'neighborhood-researcher' subagent to research the area
   - Ask for a comprehensive description of the neighborhood's character, history, and food scene
   - Save this description to use in the dashboard

3. Call search_restaurants_nearby() DIRECTLY (as main agent, not through subagent):
   - Use coordinates: lat={coordinates['lat']}, lng={coordinates['lng']}
   - This returns complete objects with ALL fields intact
   - DO NOT modify or recreate these objects
   - Keep ALL fields: name, rating, total_reviews, address, location, price_level, types, 
     website, phone, is_open, photos (with URLs), reviews (with text)

4. Create personalized tour recommendations based on the research and establishments

5. Delegate to 'dashboard-creator' subagent and pass:
   - title: A creative, engaging title for the tour
   - neighborhood_info: {{'name': '{location_name}', 'description': '<full description from research>'}}
   - establishments: The COMPLETE array from search_restaurants_nearby() with ALL fields
   - recommendations: Your curated tour narrative
   - research_findings: {{'summary': '<key insights>', 'sources': []}}

CRITICAL: 
- Pass the EXACT establishment objects from search_restaurants_nearby() to dashboard-creator
- Include the full neighborhood description (not just the name)
- Each establishment MUST have: photos array, reviews array, total_reviews number, all metadata

Be creative and personalize the experience based on the user's request!
"""
        
        print(f"\n{'='*80}")
        print(f"🎯 SENDING TO MAIN AGENT")
        print(f"{'='*80}")
        print(user_message)
        print(f"{'='*80}\n")
        
        # Run the agent
        if stream_callback:
            # Streaming mode
            result = {'messages': [], 'dashboard_path': None}
            async for chunk in self.agent.astream(
                {"messages": [{"role": "user", "content": user_message}]},
                stream_mode="values"
            ):
                if "messages" in chunk:
                    last_message = chunk["messages"][-1]
                    stream_callback(last_message)
                    result['messages'] = chunk["messages"]
            return result
        else:
            # Non-streaming mode
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": user_message}]}
            )
            return {
                'messages': response.get('messages', []),
                'dashboard_path': None
            }


def create_food_tour_agent(
    google_maps_api_key: str,
    tavily_api_key: str,
    anthropic_api_key: str,
    model: str = "claude-sonnet-4-5-20250929"
) -> FoodTourDeepAgent:
    """
    Factory function to create a Food Tour Deep Agent.
    
    Args:
        google_maps_api_key: Google Maps API key
        tavily_api_key: Tavily API key for research
        anthropic_api_key: Anthropic API key for Claude
        model: Model to use (default: gpt-4o)
    
    Returns:
        Configured FoodTourDeepAgent instance
    """
    return FoodTourDeepAgent(
        google_maps_api_key=google_maps_api_key,
        tavily_api_key=tavily_api_key,
        anthropic_api_key=anthropic_api_key,
        model=model
    )

