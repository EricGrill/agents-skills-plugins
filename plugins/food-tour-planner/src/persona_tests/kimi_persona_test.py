"""
Test Tavily research output with Kimi K2 Thinking persona transformation.

This script:
1. Uses Tavily to research Kensington Market Toronto
2. Gets baseline output from current model
3. Sends Tavily output to Kimi K2 Thinking via OpenRouter
4. Transforms it to "friend who's lived here 15 years" persona
5. Compares outputs
"""

import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()

# Initialize clients
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

# OpenRouter with Kimi K2 Thinking
kimi_model = ChatOpenAI(
    model="moonshotai/kimi-k2-thinking",
    temperature=0.7,
    model_kwargs={"max_tokens": 16000},  # Set max_tokens via model_kwargs for OpenRouter
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://github.com/muratcankoylan/DeepAgent_Food_Tour",
        "X-Title": "DeepAgent Food Tours"
    }
)

# Current model (Claude)
claude_model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
)


def research_neighborhood(neighborhood, city):
    """Use Tavily to research a specific neighborhood."""
    print("\n" + "="*80)
    print(f"🔍 RESEARCHING {neighborhood.upper()} WITH TAVILY")
    print("="*80 + "\n")
    
    query = f"""
    Research {neighborhood} in {city}. Focus on:
    - Neighborhood character and unique identity
    - Historical background and evolution
    - Multicultural food scene
    - Key cultural communities
    - Local food establishments and what makes them special
    - Insider tips and hidden gems
    - Best times to visit and what to avoid
    """
    
    print(f"Query: {query}")
    print("Calling Tavily API...\n")
    
    try:
        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        
        print(f"DEBUG: Tavily response keys: {results.keys()}")
        print(f"DEBUG: Has answer: {'answer' in results}")
        print(f"DEBUG: Answer value: {results.get('answer')}\n")
        
    except Exception as e:
        print(f"❌ Tavily API error: {str(e)}\n")
        return f"# {neighborhood} {city} Research\n\n## Error:\nTavily search failed: {str(e)}"
    
    # Compile research
    research_text = f"# {neighborhood} {city} Research\n\n"
    
    # Add answer if available
    answer = results.get('answer')
    if answer:
        research_text += f"## Tavily Summary:\n{answer}\n\n"
    
    research_text += f"## Sources:\n"
    
    for i, source in enumerate(results.get('results', []), 1):
        research_text += f"\n### Source {i}: {source.get('title', 'Untitled')}\n"
        research_text += f"URL: {source.get('url', 'N/A')}\n"
        research_text += f"{source.get('content', 'No content')}\n"
    
    print(f"✅ Tavily research completed for {neighborhood}")
    print(f"   - Got {len(results.get('results', []))} sources")
    print(f"   - Answer: {'Yes' if answer else 'No'}")
    print(f"   - Total content: ~{len(research_text)} characters\n")
    
    return research_text


def get_baseline_output(research_text, neighborhood):
    """Get baseline output using current Claude model."""
    print("\n" + "="*80)
    print("📝 BASELINE: CLAUDE WITH STANDARD PROMPT")
    print("="*80 + "\n")
    
    prompt = f"""Based on this research about {neighborhood}, write a comprehensive 
description of the neighborhood's character, history, and food scene for a food tour dashboard.

Research:
{research_text}

Write an engaging, informative description that captures what makes this neighborhood special."""
    
    response = claude_model.invoke(prompt)
    output = response.content
    
    print(f"✅ Claude output generated ({len(output)} characters)\n")
    print("--- CLAUDE OUTPUT ---")
    print(output)
    print("\n" + "="*80 + "\n")
    return output


def transform_with_kimi_persona(research_text, neighborhood):
    """Transform Tavily research using Kimi K2 with friend persona."""
    print("\n" + "="*80)
    print("🎭 KIMI K2 THINKING: FRIEND WHO'S LIVED HERE 15 YEARS")
    print("="*80 + "\n")
    
    prompt = f"""You're writing about {neighborhood} for a food tour guide.

**IMPORTANT TONE:**
- You are not a tour guide. More like the friend who's lived here 15 years and tells you the truth about where to eat.
- Respects places that grind it out over corporations.
- Conversational but not performative.
- Think: Anthony Bourdain doing walking tours, not Rick Steves. 
- Write like a friend who's lived here 15 years and tells you the truth about where to eat
- Be honest, direct, and opinionated
- Share insider knowledge and real talk
- Skip the marketing BS

Based on this research, write a description of {neighborhood} that tells people 
what they actually need to know:

{research_text}

Remember: You're the friend who knows all the spots, not a cheerful tour guide. 
Give me the real story. Write a complete response (at least 300 words)."""
    
    try:
        response = kimi_model.invoke(prompt)
        
        # Debug response metadata
        if hasattr(response, 'response_metadata'):
            print(f"DEBUG: Response metadata: {response.response_metadata}")
        if hasattr(response, 'usage_metadata'):
            print(f"DEBUG: Usage metadata: {response.usage_metadata}")
        
        # Handle different response formats
        if hasattr(response, 'content'):
            output = response.content
        elif hasattr(response, 'text'):
            output = response.text
        elif isinstance(response, dict) and 'content' in response:
            output = response['content']
        elif isinstance(response, dict) and 'text' in response:
            output = response['text']
        else:
            output = str(response)
        
        print(f"✅ Kimi K2 Thinking output generated ({len(output)} characters)")
        print(f"   Output ends with: ...{output[-100:]}")
        print("--- KIMI K2 OUTPUT ---")
        print(output)
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        output = f"Error calling Kimi K2: {str(e)}\n\nFull error:\n{repr(e)}"
        print(f"❌ Error: {str(e)}\n")
    
    return output


def save_comparison(research_text, baseline_output, kimi_output, neighborhood, city):
    """Save comparison to file."""
    safe_filename = f"{neighborhood.lower().replace(' ', '_')}_{city.lower().replace(' ', '_')}_comparison.md"
    output_path = f"src/persona_tests/{safe_filename}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {neighborhood} {city} Persona Comparison\n\n")
        f.write("## Original Tavily Research\n\n")
        f.write(research_text)
        f.write("\n\n" + "="*80 + "\n\n")
        f.write("## Baseline Output (Claude - Standard Prompt)\n\n")
        f.write(baseline_output)
        f.write("\n\n" + "="*80 + "\n\n")
        f.write("## Kimi K2 Thinking (Friend Persona)\n\n")
        f.write(kimi_output)
        f.write("\n\n" + "="*80 + "\n\n")
        f.write("## Analysis\n\n")
        f.write(f"- Neighborhood: {neighborhood}, {city}\n")
        f.write(f"- Tavily Research: {len(research_text)} characters\n")
        f.write(f"- Claude Baseline: {len(baseline_output)} characters\n")
        f.write(f"- Kimi K2 Persona: {len(kimi_output)} characters\n\n")
        f.write("### Key Differences\n")
        f.write("- **Tone**: Compare warmth vs directness\n")
        f.write("- **Information density**: What details each chose to emphasize\n")
        f.write("- **Voice**: Tour guide vs experienced friend\n")
    
    print(f"\n💾 Comparison saved to: {output_path}")


def main():
    """Run the full persona test."""
    import sys
    
    # Parse command line arguments
    if len(sys.argv) >= 3:
        neighborhood = sys.argv[1]
        city = sys.argv[2]
    else:
        neighborhood = "Kensington Market"
        city = "Toronto"
    
    print("\n" + "="*80)
    print(f"🧪 {neighborhood.upper()} PERSONA TEST")
    print("="*80)
    print(f"\nNeighborhood: {neighborhood}")
    print(f"City: {city}")
    print("\nComparing:")
    print("1. Baseline (Claude with standard prompt)")
    print("2. Kimi K2 Thinking (friend persona via OpenRouter)")
    print("")
    
    try:
        # Step 1: Get Tavily research
        research_text = research_neighborhood(neighborhood, city)
        
        # Step 2: Get baseline with Claude
        baseline_output = get_baseline_output(research_text, neighborhood)
        
        # Step 3: Transform with Kimi K2
        kimi_output = transform_with_kimi_persona(research_text, neighborhood)
        
        # Step 4: Save comparison
        save_comparison(research_text, baseline_output, kimi_output, neighborhood, city)
        
        safe_filename = f"{neighborhood.lower().replace(' ', '_')}_{city.lower().replace(' ', '_')}_comparison.md"
        output_file = f"src/persona_tests/{safe_filename}"
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80)
        print(f"\nView the comparison at:")
        print(f"{output_file}")
        print("")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

