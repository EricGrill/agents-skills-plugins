# OpenRouter + Kimi K2 Thinking Integration

## Overview
Integrated OpenRouter's Kimi K2 Thinking model to test alternative writing personas with enhanced emotional intelligence and authentic voice for neighborhood descriptions.

## What Was Built
1. **Standalone test module**: `src/persona_tests/`
2. **Comparison script**: `kimi_persona_test.py` - Tests Claude baseline vs Kimi K2 persona
3. **OpenRouter integration**: LangChain ChatOpenAI with custom base URL
4. **Research pipeline**: Tavily research → Model comparison → Markdown output

## Why Kimi K2 Thinking?
Kimi K2 Thinking excels at creative writing with strong emotional intelligence and authentic voice generation. The "thinking" variant reasons about style choices before generating text.

## Configuration
- **Model**: `moonshotai/kimi-k2-thinking` via OpenRouter
- **Temperature**: 0.7
- **Max tokens**: 16000 (set via `model_kwargs`)
- **Base URL**: `https://openrouter.ai/api/v1`
- **Required env var**: `OPENROUTER_API_KEY`

## Test Results

### Sample Output Comparison

**Claude Sonnet 4 (Standard Tour Guide Tone):**
- Professional, comprehensive, marketing-friendly
- Example: "Kensington Market stands as one of Toronto's most distinctive and beloved neighborhoods—a living, breathing testament to the city's multicultural spirit."
- Well-structured sections with historical context
- Warm, welcoming, informative

**Kimi K2 Thinking (Friend Persona):**
- Direct, honest, emotionally resonant
- Example: "Look, if you're asking about Kensington Market, I'm not going to feed you that tourist board crap about it being a 'vibrant, multicultural hub.' It is that, sure, but it's also a chaotic, infuriating, beautiful mess that'll steal your heart and maybe your bike if you're not careful."
- Practical insider knowledge with personality
- Raw, authentic voice with strong opinions
- Specific warnings and real-world context
- Emotionally engaging storytelling

## Technical Implementation

### OpenRouter Setup
```python
from langchain_openai import ChatOpenAI

kimi_model = ChatOpenAI(
    model="moonshotai/kimi-k2-thinking",
    temperature=0.7,
    model_kwargs={"max_tokens": 16000},
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://github.com/muratcankoylan/DeepAgent_Food_Tour",
        "X-Title": "DeepAgent Food Tours"
    }
)
```

**Note**: Use `model_kwargs` to set `max_tokens` for OpenRouter, not the direct parameter.

### Prompt Engineering
Key directives for the friend persona:
- "NOT warm and fuzzy, NOT a tour guide"
- "Write like a friend who's lived here 15 years and tells you the truth"
- "Be honest, direct, and opinionated"
- "Share insider knowledge and real talk"
- "Skip the marketing BS"

## Key Findings

### Strengths of Kimi K2 for Creative Writing:
1. **Emotional Intelligence**: Captures authentic voice and personality
2. **Storytelling**: Weaves narrative elements naturally
3. **Contextual Awareness**: Provides practical, experience-based insights
4. **Memorable Voice**: Creates distinct, engaging writing style
5. **Honest Perspective**: Balances positives with real challenges

### Production Considerations:
1. **Token Configuration**: Must use `model_kwargs` to avoid validation errors
2. **Response Length**: Generates complete, well-formed responses with proper token limits
3. **Tone Flexibility**: Can adapt from casual to professional based on prompt
4. **Consistency**: Maintains voice throughout longer outputs

## Use Cases

### Best For:
- Neighborhood guides with personality
- Authentic local perspectives
- Emotional, engaging storytelling
- Creative content that needs voice
- User-facing content requiring relatability

### Less Suitable For:
- Formal documentation
- Technical specifications
- Strictly factual reports
- Corporate communications

## Integration Paths

1. **A/B Testing**: Offer users choice between professional and casual tones
2. **Context-Aware**: Use Kimi K2 for entertainment-focused tours, Claude for business
3. **Hybrid Approach**: Kimi K2 for intro/recommendations, Claude for details
4. **User Profiles**: Match writing style to user preference settings

## Files Created
- `src/persona_tests/__init__.py` - Module initialization
- `src/persona_tests/kimi_persona_test.py` - Main comparison script
- `src/persona_tests/debug_kimi.py` - Debugging utility
- `src/persona_tests/README.md` - Module documentation
- `src/persona_tests/TESTING_GUIDE.md` - Usage examples
- `src/persona_tests/TEST_RESULTS.md` - This file

## Quick Start
```bash
# Install OpenRouter dependency (if needed)
pip install langchain-openai

# Add API key to .env
echo "OPENROUTER_API_KEY=your_key_here" >> .env

# Run comparison test
python src/persona_tests/kimi_persona_test.py "Kensington Market" "Toronto"

# Test different neighborhood
python src/persona_tests/kimi_persona_test.py "Mission District" "San Francisco"
```

## Conclusion
Kimi K2 Thinking via OpenRouter successfully generates authentic, emotionally intelligent writing with strong personality. The model excels at creative storytelling and perspective-driven content, making it ideal for user-facing neighborhood guides that prioritize engagement and authenticity over formal documentation. Integration is straightforward via LangChain's ChatOpenAI interface with OpenRouter's API.

