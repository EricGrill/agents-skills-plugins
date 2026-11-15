"""Python API server to bridge DeepAgent with Node.js scan manager."""

import os
import asyncio
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Fix path to import from local agents folder
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import our local agents module
from src.agents.food_tour_agent import create_food_tour_agent

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the DeepAgent
agent = None

def init_agent():
    """Initialize the Food Tour Deep Agent."""
    global agent
    try:
        agent = create_food_tour_agent(
            google_maps_api_key=os.getenv('GOOGLE_MAPS_API_KEY'),
            tavily_api_key=os.getenv('TAVILY_API_KEY'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        print("✅ Food Tour DeepAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize DeepAgent: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'agent_ready': agent is not None
    })

@app.route('/plan-tour', methods=['POST'])
def plan_tour():
    """
    Plan a food tour using DeepAgent.
    
    Expected JSON payload:
    {
        "location_name": "Kensington Market, Toronto",
        "coordinates": {"lat": 43.6549, "lng": -79.4003},
        "user_prompt": "I want a fun evening...",
        "search_points": [{"lat": ..., "lng": ...}, ...]
    }
    """
    try:
        data = request.json
        print(f"\n{'='*80}")
        print(f"📥 NEW FOOD TOUR REQUEST")
        print(f"{'='*80}")
        print(f"Location: {data.get('location_name')}")
        print(f"Coordinates: {data.get('coordinates')}")
        print(f"User Prompt: {data.get('user_prompt')}")
        print(f"Search Points: {len(data.get('search_points', []))} points")
        print(f"{'='*80}\n")
        
        location_name = data.get('location_name')
        coordinates = data.get('coordinates')
        user_prompt = data.get('user_prompt')
        search_points = data.get('search_points', [])
        
        if not all([location_name, coordinates, user_prompt]):
            print("❌ Missing required fields")
            return jsonify({
                'success': False,
                'error': 'Missing required fields: location_name, coordinates, or user_prompt'
            }), 400
        
        print(f"📍 Validating request data...")
        print(f"   ✓ Location: {location_name}")
        print(f"   ✓ Coordinates: lat={coordinates['lat']}, lng={coordinates['lng']}")
        print(f"   ✓ Prompt: {user_prompt[:100]}...")
        print(f"\n🚀 Initializing DeepAgent execution...\n")
        
        # Run the agent asynchronously
        async def run_agent():
            messages = []
            current_agent = "Main Agent"
            message_count = 0
            
            def capture_message(message):
                """Capture streaming messages with agent tracking."""
                nonlocal current_agent, message_count
                message_count += 1
                
                print(f"\n{'='*80}")
                print(f"MESSAGE #{message_count}")
                print(f"{'='*80}")
                
                # Print full message structure for debugging
                print(f"Message Type: {type(message).__name__}")
                print(f"Has content: {hasattr(message, 'content')}")
                
                if hasattr(message, 'role'):
                    print(f"Role: {message.role}")
                
                # Handle different message types
                if hasattr(message, 'content'):
                    content = message.content
                    
                    # Handle list content (tool calls)
                    if isinstance(content, list):
                        print(f"\n📋 Content is a list with {len(content)} items:")
                        for i, item in enumerate(content):
                            print(f"\n  Item {i+1}: {type(item).__name__}")
                            if hasattr(item, 'text'):
                                print(f"  Text: {item.text}")
                            elif hasattr(item, 'name'):
                                print(f"  Tool Call: {item.name}")
                                if hasattr(item, 'input'):
                                    import json
                                    print(f"  Input: {json.dumps(item.input, indent=2)[:500]}")
                            else:
                                print(f"  {str(item)[:300]}")
                    else:
                        # String content
                        content_str = str(content)
                        print(f"\n📝 Content ({len(content_str)} chars):")
                        print(f"{content_str[:500]}{'...' if len(content_str) > 500 else ''}")
                        
                        # Detect agent context
                        if 'restaurant-finder' in content_str.lower():
                            current_agent = "🍽️ Restaurant Finder"
                        elif 'neighborhood-researcher' in content_str.lower():
                            current_agent = "🔍 Neighborhood Researcher"
                        elif 'dashboard-creator' in content_str.lower():
                            current_agent = "📊 Dashboard Creator"
                
                # Handle tool calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"\n🔧 Tool Calls ({len(message.tool_calls)}):")
                    for tc in message.tool_calls:
                        print(f"  - {tc.get('name', 'unknown')}")
                        if 'args' in tc:
                            import json
                            print(f"    Args: {json.dumps(tc['args'], indent=4)[:500]}")
                
                # Handle additional message properties
                if hasattr(message, 'additional_kwargs') and message.additional_kwargs:
                    print(f"\n🔍 Additional Info:")
                    for key, value in message.additional_kwargs.items():
                        print(f"  {key}: {str(value)[:200]}")
                
                print(f"\n🏷️ Current Agent Context: {current_agent}")
                print(f"{'='*80}\n")
                
                messages.append({
                    'role': str(getattr(message, 'role', 'assistant')),
                    'content': str(content) if hasattr(message, 'content') else '',
                    'agent': current_agent
                })
            
            result = await agent.plan_food_tour(
                location_name=location_name,
                coordinates=coordinates,
                user_prompt=user_prompt,
                stream_callback=capture_message
            )
            
            return {
                'messages': messages,
                'dashboard_path': result.get('dashboard_path')
            }
        
        # Run the async function
        print("⚙️ Starting async execution...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_agent())
        loop.close()
        print("✅ Agent completed successfully!")
        
        return jsonify({
            'success': True,
            'result': result,
            'dashboard_url': 'http://localhost:3002'
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ ERROR in /plan-tour:")
        print(error_trace)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint."""
    return jsonify({
        'message': 'DeepAgent API is running',
        'agent_initialized': agent is not None
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧠 Food Tour DeepAgent API Server")
    print("="*70)
    
    # Initialize agent
    init_agent()
    
    port = int(os.getenv('DEEPAGENT_PORT', 5001))
    
    print(f"\n🚀 Starting server on http://localhost:{port}")
    print(f"📍 Endpoints:")
    print(f"   - POST /plan-tour  : Plan a food tour")
    print(f"   - GET  /health     : Health check")
    print(f"   - GET  /test       : Simple test")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

