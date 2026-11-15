# Testing Guide: Kimi K2 Persona Comparison

Test Kimi K2 Thinking's creative writing capabilities across different neighborhoods.

## Quick Start

### Default (Kensington Market, Toronto)
```bash
python3 src/persona_tests/kimi_persona_test.py
```

### North Beach, San Francisco
```bash
python3 src/persona_tests/kimi_persona_test.py "North Beach" "San Francisco"
```

### Shoreditch, London
```bash
python3 src/persona_tests/kimi_persona_test.py "Shoreditch" "London"
```

### Brooklyn Heights, New York
```bash
python3 src/persona_tests/kimi_persona_test.py "Brooklyn Heights" "New York"
```

### Le Marais, Paris
```bash
python3 src/persona_tests/kimi_persona_test.py "Le Marais" "Paris"
```

### Kreuzberg, Berlin
```bash
python3 src/persona_tests/kimi_persona_test.py "Kreuzberg" "Berlin"
```

### Mission District, San Francisco
```bash
python3 src/persona_tests/kimi_persona_test.py "Mission District" "San Francisco"
```

## Output Files

Results are saved to:
```
src/persona_tests/{neighborhood}_{city}_comparison.md
```

Examples:
- `north_beach_san_francisco_comparison.md`
- `shoreditch_london_comparison.md`
- `le_marais_paris_comparison.md`

## Usage Pattern

```bash
python3 src/persona_tests/kimi_persona_test.py "NEIGHBORHOOD_NAME" "CITY_NAME"
```

Parameters:
1. **NEIGHBORHOOD_NAME** (required): Name of the neighborhood
2. **CITY_NAME** (required): Name of the city

If no parameters provided, defaults to "Kensington Market" and "Toronto".

## What Happens

1. **Tavily Research**: Gathers real web data about the neighborhood (5 sources)
2. **Claude Baseline**: Generates professional tour guide description
3. **Kimi K2 Persona**: Creates authentic local perspective with emotional intelligence
4. **Output**: Saves side-by-side comparison with character counts and analysis

## View Results

```bash
# View all comparison files
ls -lh src/persona_tests/*_comparison.md

# View specific comparison
cat src/persona_tests/north_beach_san_francisco_comparison.md

# View just Kimi K2 output
grep -A 100 "## Kimi K2 Thinking" src/persona_tests/north_beach_san_francisco_comparison.md
```

## Batch Testing

Test multiple neighborhoods at once:

```bash
# Create a simple batch script
cat > test_multiple.sh << 'EOF'
#!/bin/bash
python3 src/persona_tests/kimi_persona_test.py "North Beach" "San Francisco"
echo "---"
python3 src/persona_tests/kimi_persona_test.py "Shoreditch" "London"
echo "---"
python3 src/persona_tests/kimi_persona_test.py "Le Marais" "Paris"
EOF

chmod +x test_multiple.sh
./test_multiple.sh
```

