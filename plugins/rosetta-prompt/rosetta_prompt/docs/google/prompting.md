# Google (Gemini) Prompting Guide
Last updated: January 2025

## Overview

Google's Gemini models are designed for advanced reasoning and instruction following. The prompting strategy emphasizes clear, specific instructions with consistent structure. Gemini 3 models in particular respond best to prompts that are direct, well-structured, and clearly define the task and any constraints.

**Note:** Prompt engineering is iterative. These guidelines are starting points—experiment and refine based on your specific use cases and observed model responses.

## Key Principles

1. **Be Clear and Specific**: Provide explicit instructions in the form of questions, step-by-step tasks, or detailed user experience mappings. The less the model has to guess, the better the results.

2. **Use Few-Shot Examples**: Always include examples in your prompts when possible. Prompts with few-shot examples are more effective than zero-shot prompts. Examples help regulate formatting, phrasing, scoping, and response patterns.

3. **Add Context**: Include all necessary information and constraints in your prompt rather than assuming the model has the required knowledge.

4. **Use Consistent Structure**: Employ clear delimiters (XML tags, Markdown headings) to separate different parts of your prompt. Choose one format and use it consistently.

5. **Iterate and Experiment**: Try different phrasings, analogous tasks, and content ordering if you don't get expected results initially.

## Techniques

### Input Types
- **Question Input**: Ask the model to answer a question
- **Task Input**: Request the model to perform a specific task
- **Entity Input**: Provide entities for the model to operate on (classify, analyze)
- **Completion Input**: Provide partial content for the model to complete

### Constraints and Formatting
Specify constraints explicitly:
```
Summarize this text in one sentence:
Text: [your text here]
```

Request specific output formats (tables, lists, JSON, paragraphs):
```
System instruction: All questions should be answered comprehensively with details, unless the user requests a concise response specifically.
```

### Few-Shot Prompting
Provide examples showing the desired pattern:
```
Question: Why is the sky blue?
Explanation1: The sky appears blue because of Rayleigh scattering...
Explanation2: Due to Rayleigh scattering effect.
Answer: Explanation2

Question: How is snow formed?
Explanation1: Snow is formed when water vapor...
Explanation2: Water vapor freezes into ice crystals forming snow.
Answer:
```

### Using Prefixes
- **Input prefix**: Demarcate semantically meaningful parts (e.g., "English:", "French:")
- **Output prefix**: Signal expected response format (e.g., "JSON:", "The answer is:")
- **Example prefix**: Label examples for easier parsing

### Breaking Down Complex Prompts
- **Split instructions**: Create separate prompts for different tasks
- **Chain prompts**: Use sequential prompts where output feeds into the next
- **Aggregate responses**: Perform parallel operations and combine results

## Gemini 3 Specific Guidance

### Core Principles for Gemini 3
- **Be precise and direct**: State your goal clearly and concisely
- **Define parameters**: Explicitly explain any ambiguous terms
- **Control verbosity**: Request conversational/detailed responses explicitly if needed
- **Prioritize critical instructions**: Place essential constraints at the beginning or in System Instructions
- **Structure for long contexts**: Provide all context first, then instructions at the end

### Structured Prompting with Tags

**XML Example:**
```xml
<role>
You are a helpful assistant.
</role>

<constraints>
1. Be objective.
2. Cite sources.
</constraints>

<context>
[Insert User Input Here]
</context>

<task>
[Insert the specific user request here]
</task>
```

**Markdown Example:**
```markdown
# Identity
You are a senior solution architect.

# Constraints
- No external libraries allowed.
- Python 3.11+ syntax only.

# Output format
Return a single code block.
```

### Enhancing Reasoning
Prompt the model to plan or self-critique:
```
Before providing the final answer, please:
1. Parse the stated goal into distinct sub-tasks.
2. Check if the input information is complete.
3. Create a structured outline to achieve the goal.
```

## Examples

### Example 1: JSON Output with Completion
```
Valid fields are cheeseburger, hamburger, fries, and drink.
Order: Give me a cheeseburger and fries
Output:
{
  "cheeseburger": 1,
  "fries": 1
}
Order: I want two burgers, a drink, and fries.
Output:
```

### Example 2: Contextual Troubleshooting
```
Answer the question using the text below. Respond with only the text provided.
Question: What should I do to fix my disconnected wifi? The light on my router is yellow and blinking slowly.

Text:
Color: Slowly pulsing yellow
What it means: There is a network error.
What to do: Check that the Ethernet cable is connected to both your router and modem and both devices are turned on.
```

### Example 3: Combined Best Practices Template
**System Instruction:**
```xml
<role>
You are Gemini, a specialized assistant for [Domain].
</role>

<instructions>
1. Plan: Analyze the task and create a step-by-step plan.
2. Execute: Carry out the plan.
3. Validate: Review your output against the user's task.
4. Format: Present the final answer in the requested structure.
</instructions>

<constraints>
- Verbosity: [Low/Medium/High]
- Tone: [Formal/Casual/Technical]
</constraints>
```

**User Prompt:**
```xml
<context>
[Insert relevant documents or background info]
</context>

<task>
[Insert specific user request]
</task>
```

## Tips

### Do's
- ✅ Show positive patterns (what TO do) rather than anti-patterns
- ✅ Use consistent formatting across all few-shot examples
- ✅ Experiment with different model parameters (temperature, topK, topP)
- ✅ Keep temperature at default 1.0 for Gemini 3 models
- ✅ Use completion strategy to guide output format

### Don'ts
- ⛔ Don't rely on models to generate factual information without verification
- ⛔ Don't use with care-required tasks like math/logic without validation
- ⛔ Don't include too many examples (may cause overfitting)
- ⛔ Don't change temperature below 1.0 for Gemini 3 (may cause looping or degraded performance)

### Model Parameters
- **Temperature**: Controls randomness (0 = deterministic, higher = more creative)
- **topK**: Limits token selection to K most probable tokens
- **topP**: Selects tokens until cumulative probability reaches P
- **Max output tokens**: ~100 tokens ≈ 60-80 words
- **stop_sequences**: Define sequences that halt generation
