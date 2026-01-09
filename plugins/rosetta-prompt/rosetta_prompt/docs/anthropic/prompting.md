# Anthropic Claude Prompting Guide
Last updated: 2025-01-13

## Overview

When interacting with Claude, think of it as a brilliant but very new employee (with amnesia) who needs explicit instructions. Like any new employee, Claude does not have context on your norms, styles, guidelines, or preferred ways of working. The more precisely you explain what you want, the better Claude's response will be.

**The Golden Rule of Clear Prompting:** Show your prompt to a colleague, ideally someone who has minimal context on the task, and ask them to follow the instructions. If they're confused, Claude will likely be too.

## Key Principles

### 1. Be Clear and Direct
- **Provide context**: Explain what the task results will be used for, what audience the output is meant for, what workflow this task is part of, and what a successful task completion looks like.
- **Be specific**: If you want Claude to output only code and nothing else, say so explicitly.
- **Use sequential steps**: Provide instructions as numbered lists or bullet points to ensure Claude carries out the task exactly as intended.

### 2. Use XML Tags for Structure
XML tags help Claude parse your prompts more accurately, leading to higher-quality outputs.

**Benefits:**
- **Clarity**: Clearly separate different parts of your prompt
- **Accuracy**: Reduce errors from misinterpretation
- **Flexibility**: Easily modify parts of your prompt
- **Parseability**: Extract specific parts of Claude's response by post-processing

**Best practices:**
- Be consistent with tag names throughout prompts
- Nest tags for hierarchical content: `<outer><inner></inner></outer>`
- Use descriptive tag names like `<instructions>`, `<example>`, `<formatting>`, `<thinking>`, `<answer>`

### 3. Give Claude a Role (System Prompts)
Use the `system` parameter to give Claude a role—this is the most powerful way to use system prompts.

**Benefits:**
- Enhanced accuracy in complex scenarios (legal analysis, financial modeling)
- Tailored tone (CFO's brevity vs. copywriter's flair)
- Improved focus within task requirements

**Tip:** Experiment with roles! A "data scientist" might see different insights than a "marketing strategist" for the same data.

### 4. Use Examples (Multishot Prompting)
Include 3-5 diverse, relevant examples to show Claude exactly what you want. More examples = better performance, especially for complex tasks.

**Effective examples are:**
- **Relevant**: Mirror your actual use case
- **Diverse**: Cover edge cases and vary enough to avoid unintended patterns
- **Clear**: Wrapped in `<example>` tags (nested within `<examples>` tags for multiple)

### 5. Let Claude Think (Chain of Thought)
Giving Claude space to think dramatically improves performance on complex tasks.

**Benefits:**
- **Accuracy**: Stepping through problems reduces errors
- **Coherence**: Structured thinking leads to well-organized responses
- **Debugging**: See where prompts may be unclear

**When to use:** Tasks that a human would need to think through—complex math, multi-step analysis, writing complex documents, or decisions with many factors.

## Techniques

### Chain of Thought Prompting (Least to Most Complex)

**Basic prompt:** Include "Think step-by-step" in your prompt.

**Guided prompt:** Outline specific steps for Claude to follow:
```
Before responding, think through:
1. Identify the key requirements
2. Consider potential approaches
3. Evaluate trade-offs
4. Select the best approach
```

**Structured prompt:** Use XML tags to separate reasoning from the final answer:
```
Think through this problem step by step in <thinking> tags, then provide your final answer in <answer> tags.
```

**Important:** Always have Claude output its thinking. Without outputting its thought process, no thinking occurs!

### Prefilling Claude's Response
Guide Claude's responses by prefilling the Assistant message. This allows you to:
- Direct Claude's actions
- Skip preambles
- Enforce specific formats (JSON, XML)
- Maintain character consistency in role-play

**Example for JSON output:**
```python
messages=[
    {"role": "user", "content": "Extract the name and age from: John is 25 years old"},
    {"role": "assistant", "content": "{"}  # Forces JSON output
]
```

**Note:** Prefilling cannot end with trailing whitespace. Prefilling is not available with extended thinking mode.

### Long Context Tips (200K tokens)

1. **Put longform data at the top**: Place long documents (~20K+ tokens) near the top of your prompt, above your query, instructions, and examples. Queries at the end can improve response quality by up to 30%.

2. **Structure with XML tags**: Wrap each document in `<document>` tags with `<document_content>` and `<source>` subtags.

3. **Ground responses in quotes**: Ask Claude to quote relevant parts of documents first before carrying out its task.

### Extended Thinking Mode Tips

For complex problems requiring deep reasoning:

1. **Use general instructions first**: Claude often performs better with high-level instructions rather than step-by-step prescriptive guidance.
   
   Instead of: "Think through this step by step: 1. First identify variables..."
   
   Try: "Please think about this problem thoroughly. Consider multiple approaches and show your complete reasoning."

2. **Start with minimum budget**: Begin with 1024 tokens (minimum) and increase based on task complexity.

3. **For very long outputs**: Request a detailed outline with word counts first, then have Claude index paragraphs to the outline.

4. **Verify work**: Ask Claude to check its work with test cases before declaring a task complete.

## Examples

### Example 1: Clear Data Processing Instructions

**Unclear prompt:**
```
Please remove all personally identifiable information from these customer feedback messages: {{FEEDBACK_DATA}}
```

**Clear prompt:**
```
Your task is to anonymize customer feedback for our quarterly review.

Instructions:
1. Replace all customer names with "CUSTOMER_[ID]" (e.g., "Jane Doe" → "CUSTOMER_001")
2. Replace email addresses with "EMAIL_[ID]@example.com"
3. Redact phone numbers as "PHONE_[ID]"
4. If a message mentions a specific product (e.g., "AcmeCloud"), leave it intact
5. If no PII is found, copy the message verbatim
6. Output only the processed messages, separated by "---"

Data to process: {{FEEDBACK_DATA}}
```

### Example 2: Structured Output with Prefilling

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="You are a data extraction assistant. Output only valid JSON.",
    messages=[
        {"role": "user", "content": "Extract key information from this report: {{REPORT}}"},
        {"role": "assistant", "content": "{"}
    ]
)
```

### Example 3: Role Prompting for Domain Expertise

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2048,
    system="You are a seasoned data scientist at a Fortune 500 company specializing in customer insight analysis.",
    messages=[
        {"role": "user", "content": "Analyze this dataset for anomalies: <dataset>{{DATASET}}</dataset>"}
    ]
)
```

## Tips

### Do's
- ✅ Provide specific context about the task's purpose and audience
- ✅ Use numbered steps for multi-step instructions
- ✅ Wrap examples in `<example>` tags
- ✅ Use XML tags to structure complex prompts
- ✅ Include 3-5 diverse examples for consistent outputs
- ✅ Ask Claude to think step-by-step for complex tasks
- ✅ Put long documents at the TOP of your prompt
- ✅ Use system prompts for role assignment

### Don'ts
- ❌ Assume Claude knows your organization's context or preferences
- ❌ Use vague instructions like "clean up this data"
- ❌ Mix instructions, examples, and data without clear separation
- ❌ Skip examples when you need specific output formats
- ❌ Add trailing whitespace to prefilled responses
- ❌ Pass Claude's extended thinking back in user text blocks
- ❌ Manually change output text following thinking blocks (causes model confusion)

### Common Pitfalls
1. **Being too vague**: Claude will make assumptions to fill gaps—be explicit about what you want
2. **Overcomplicating prompts**: Start simple, then add complexity as needed
3. **Not testing with edge cases**: Include diverse examples that cover unusual scenarios
4. **Ignoring output format**: If you need specific formatting, demonstrate it clearly
5. **For extended thinking**: Don't prescribe exact thinking steps—let Claude's creativity find optimal approaches first, then iterate based on its thinking output
