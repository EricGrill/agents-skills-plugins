# Persona Testing Module

Test alternative writing personas for neighborhood descriptions using Kimi K2 Thinking model with OpenRouter.

## Purpose

Explore how different AI models approach creative writing by comparing:
- **Claude Sonnet 4.5**: Professional tour guide tone with comprehensive coverage
- **Kimi K2 Thinking**: Authentic local perspective with emotional intelligence

This module demonstrates how to leverage OpenRouter for enhanced writing capabilities and emotional resonance in AI-generated content.

## Setup

1. Add OpenRouter API key to `.env`:
```bash
OPENROUTER_API_KEY=your_key_here
```

Get your key at: https://openrouter.ai/keys

2. Install dependencies (already in requirements.txt):
```bash
pip install langchain-openai tavily-python python-dotenv
```

## Usage

### Default Test (Kensington Market, Toronto)
```bash
python src/persona_tests/kimi_persona_test.py
```

### Test Any Neighborhood
```bash
python src/persona_tests/kimi_persona_test.py "NEIGHBORHOOD" "CITY"
```

Examples:
```bash
python src/persona_tests/kimi_persona_test.py "Mission District" "San Francisco"
python src/persona_tests/kimi_persona_test.py "Shoreditch" "London"
python src/persona_tests/kimi_persona_test.py "Le Marais" "Paris"
```

## What It Does

1. **Tavily Research**: Gathers real web data about the neighborhood
2. **Claude Baseline**: Generates professional tour guide description
3. **Kimi K2 Persona**: Creates authentic local perspective with personality
4. **Comparison Output**: Saves side-by-side comparison to markdown file

## Output

Generated files: `src/persona_tests/{neighborhood}_{city}_comparison.md`

Each comparison includes:
- Original Tavily research sources
- Claude's formal, comprehensive description
- Kimi K2's authentic, emotionally intelligent perspective
- Character counts and analysis

## Why Kimi K2 Thinking?

[Kimi K2 Thinking](https://openrouter.ai/moonshotai/kimi-k2-thinking) is the best creative writing model with strong emotional intelligence. The "thinking" variant reasons about style and tone before generating output, resulting in more authentic and engaging content.

### Key Advantages:
- Strong emotional intelligence and authentic voice
- Excellent at storytelling and perspective
- Adapts tone based on detailed prompts
- Maintains consistent personality throughout

## Customization

Edit prompts in `kimi_persona_test.py` to test different writing styles:
- **Baseline prompt** (line ~105): Adjust Claude's writing style
- **Kimi persona prompt** (line ~140): Change the friend persona characteristics
- **Temperature**: Adjust for more/less creative variation
- **Max tokens**: Control output length

## Integration Ideas

This is a standalone test module, but could be integrated into the main application:

1. **User Preference Toggle**: Let users choose between professional and casual writing styles
2. **Context-Aware Selection**: Use Kimi K2 for entertainment tours, Claude for business
3. **Hybrid Approach**: Kimi K2 for introductions/recommendations, Claude for details
4. **A/B Testing**: Compare user engagement across different personas

## Technical Details

- **Model**: `moonshotai/kimi-k2-thinking` via OpenRouter
- **Interface**: LangChain ChatOpenAI (compatible with OpenAI SDK)
- **Token Config**: Use `model_kwargs={"max_tokens": 16000}` for OpenRouter
- **Documentation**: https://openrouter.ai/docs/community/lang-chain

## View Results

```bash
# List all comparison files
ls -lh src/persona_tests/*_comparison.md

# View specific comparison
cat src/persona_tests/mission_district_san_francisco_comparison.md

# Extract just Kimi K2 output
grep -A 100 "## Kimi K2 Thinking" src/persona_tests/kensington_market_toronto_comparison.md
```

