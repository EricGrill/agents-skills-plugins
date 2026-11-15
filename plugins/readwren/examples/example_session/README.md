# Example Interview Session

This directory contains a complete example of a WREN interview session and the generated outputs.

## Session Details

- **Session ID**: `example_session`
- **Interview Type**: Mock interview demonstrating adaptive questioning
- **Turn Count**: 8 turns (early termination)
- **Completion Status**: User-initiated early exit

## Directory Structure

```
example_session/
├── logs/
│   └── conversation_20251108_150303.json    # Full transcript with reasoning
└── profiles/
    ├── profile_20251108_150303.json         # Machine-readable profile
    ├── profile_20251108_150303.md           # Human-readable markdown
    └── profile_20251108_150303_SHAREABLE.txt # Formatted for sharing
```

## What This Example Shows

### 1. Adaptive Interviewing

The agent demonstrates:
- **Deep listening**: Questions reference specific phrases from previous answers
- **Style matching**: Adjusts question complexity to match user's vocabulary
- **Coverage tracking**: Ensures all dimensions are explored
- **Natural flow**: Conversation feels organic, not scripted

Example exchange:

```
USER: "I welcome obstruction when it serves the subject's resistance—
Beckett's deliberate impoverishment mirrors existential depletion."

AGENT: "You describe emotional accessibility as something that 'pulses 
through fissures in the obstruction'—a beautiful metaphor that suggests 
you're attuned to the rhythm of revelation and concealment."
```

The agent directly echoes the user's language ("obstruction," "fissures") and asks about pacing based on their sophisticated response.

### 2. Profile Generation

The generated profile contains:

**Style Signature** (0-100 scales):
- Prose density: 70 (dense, literary)
- Pacing: 60 (deliberate but forward-moving)
- Tone: 10 (dark, serious)
- Worldbuilding: 20 (minimal, interior-focused)
- Character focus: 90 (deeply psychological)

**Taste Anchors**:
- Loves: The Remains of the Day, Beloved, The Metamorphosis, Beckett, Lispector
- Avoids: Finnegans Wake (linguistic difficulty as subject)

**Reader Archetype**: "Fracture Dweller"

**Reading Philosophy**:
> "You read as an act of emotional archaeology, seeking texts that fracture 
> their own forms to admit the unsayable. You value provisional grammar over 
> restored wholeness, and you dwell permanently inside the break."

### 3. Implicit Signals

Calculated from response patterns:

- **Vocabulary richness**: 0.95 (highly sophisticated, literary)
- **Response brevity**: 0.2 (long, essay-like responses)
- **Engagement index**: 0.95 (deeply engaged, philosophical)

These metrics are extracted without explicitly asking, showing how the system reads between the lines.

### 4. Kimi K2 Reasoning

The conversation log includes Kimi K2's internal thinking process (if reasoning was enabled), showing:
- How the agent analyzes each response
- What patterns it notices
- Why it chooses specific follow-up questions

### 5. Actionable Output

The profile can be directly used with any LLM:

```
"Write a short story for me with these parameters:
- Prose density: 70/100 (literary but not impenetrable)
- Tone: 10/100 (dark, restrained)
- Character focus: 90/100 (psychological over plot)
- Theme: Language failing to contain private catastrophe
- Ending: Transcendent through remaining broken
- Avoid: Linguistic cleverness as the subject itself"
```

## How to View These Files

### JSON Profile (Machine-Readable)

```bash
cat user_profiles/example_session/profiles/profile_20251108_150303.json
```

Or in Python:

```python
import json
with open('user_profiles/example_session/profiles/profile_20251108_150303.json') as f:
    profile = json.load(f)
    print(profile['reader_archetype'])  # "Fracture Dweller"
```

### Conversation Log

```bash
python view_conversation_log.py user_profiles/example_session/logs/conversation_20251108_150303.json
```

Shows formatted conversation with turn-by-turn breakdown.

### Shareable Profile

```bash
cat user_profiles/example_session/profiles/profile_20251108_150303_SHAREABLE.txt
```

Formatted text ready to share on social media or documentation.

## Key Takeaways

1. **Interview feels natural**: Not a questionnaire, but a conversation
2. **Agent listens deeply**: References specific words and concepts from previous turns
3. **Profile is actionable**: Precise numeric scores, not vague descriptions
4. **Multiple formats**: Machine-readable JSON + human-readable text
5. **Transparent**: Includes reasoning, explanations, and methodology

## Running Your Own Interview

```bash
./run_interview.sh
```

Your session will be saved to `user_profiles/cli_TIMESTAMP/` with the same structure as this example.

---

**Note**: This is a real interview session conducted with WREN, demonstrating the system's capabilities with a sophisticated reader. Your own interview will adapt to your style and preferences.

