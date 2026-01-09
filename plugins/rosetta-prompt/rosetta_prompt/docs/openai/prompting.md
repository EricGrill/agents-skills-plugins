# OpenAI Prompting Guide
Last updated: 2025-01-13

## Overview

OpenAI provides a range of large language models (GPT-5, GPT-5.1, GPT-4.1, and reasoning models like o3) that generate text from prompts. **Prompt engineering** is the process of writing effective instructions so models consistently produce content meeting your requirements. Because model output is non-deterministic, prompting is both art and science—but applying proven techniques yields reliable results.

Key recommendations:
- **Pin to model snapshots** (e.g., `gpt-5-2025-08-07`) for consistent production behavior
- **Build evals** to measure prompt performance as you iterate or upgrade models
- Use the **Responses API** for new projects (recommended over Chat Completions)

## Key Principles

### 1. Choose the Right Model
- **Reasoning models** (o3, GPT-5): Generate internal chain-of-thought; excel at complex tasks and multi-step planning; slower and costlier
- **GPT models**: Fast, cost-efficient, highly intelligent; benefit from explicit instructions
- **Large vs. small models**: Large models understand prompts better; small models (mini/nano) are faster and cheaper
- When in doubt, `gpt-4.1` offers a solid balance of intelligence, speed, and cost

### 2. Use Message Roles Effectively
OpenAI models prioritize messages differently based on role:

| Role | Purpose |
|------|---------|
| `developer` | System instructions with highest priority; defines rules and business logic |
| `user` | End-user input; prioritized behind developer messages |
| `assistant` | Model-generated responses |

Think of it like programming: `developer` messages are the function definition, `user` messages are the arguments.

### 3. Structure Prompts with Clear Sections
A well-organized developer message typically contains:
1. **Identity**: Purpose, communication style, high-level goals
2. **Instructions**: Rules, what to do/never do, function-calling guidance
3. **Examples**: Input/output pairs demonstrating desired behavior
4. **Context**: Additional data (RAG content, documents) — best positioned at the end

### 4. Use Markdown and XML for Formatting
- **Markdown** headers and lists mark distinct sections and communicate hierarchy
- **XML tags** delineate content boundaries (e.g., `<user_query>`, `<assistant_response>`)
- XML attributes can define metadata referenced by instructions

### 5. Leverage Prompt Caching
Place reusable content at the **beginning** of prompts to maximize cost and latency savings from prompt caching.

## Techniques

### Few-Shot Learning
Include input/output examples to steer the model toward new tasks without fine-tuning:

```text
# Identity
You are a helpful assistant that labels product reviews as
Positive, Negative, or Neutral.

# Instructions
* Only output a single word: "Positive", "Negative", or "Neutral"
* No additional formatting or commentary

# Examples
<product_review id="example-1">
I absolutely love these headphones — sound quality is amazing!
</product_review>
<assistant_response id="example-1">
Positive
</assistant_response>

<product_review id="example-2">
Battery life is okay, but the ear pads feel cheap.
</product_review>
<assistant_response id="example-2">
Neutral
</assistant_response>
```

### Retrieval-Augmented Generation (RAG)
Include additional context in prompts when you need:
- Access to proprietary/private data outside training data
- Constrained responses based on specific resources
- Use OpenAI's file search tool or query vector databases

### Reusable Prompts
Create prompts in the OpenAI dashboard with placeholders like `{{customer_name}}`, then reference them via API with the `prompt` parameter—deploy improved versions without code changes.

## Prompting Different Model Types

### GPT-5/GPT-5.1 (Reasoning Models)
GPT-5 models benefit from **precise instructions** that explicitly provide logic and data. GPT-5.1 is highly steerable and responsive to well-specified prompts.

**Best practices for GPT-5.1:**

1. **Encourage persistence and completeness**:
```text
<solution_persistence>
- Treat yourself as an autonomous senior pair-programmer
- Persist until the task is fully handled end-to-end
- Be extremely biased for action—if a directive is ambiguous, proceed
- If user asks "should we do x?" and answer is yes, perform the action
</solution_persistence>
```

2. **Control output verbosity explicitly**:
```text
<output_verbosity_spec>
- Respond in plain text styled in Markdown, at most 2 concise sentences
- Lead with what you did (or found), add context only if needed
</output_verbosity_spec>
```

3. **Shape personality for your use case**:
```text
<final_answer_formatting>
- Speak with grounded directness
- Politeness shows through structure, precision, responsiveness—not verbal fluff
- Match the user's rhythm: fast when they're fast, spacious when verbose
- Focus every message on helping progress with minimal friction
</final_answer_formatting>
```

### GPT-5.1 "None" Reasoning Mode
The `none` reasoning mode forces no reasoning tokens, behaving like GPT-4.1/GPT-4o. Good for low-latency use cases.

**Tips for `none` mode:**
- Use few-shot prompting and high-quality tool descriptions
- Prompt the model to plan before function calls:
```text
You MUST plan extensively before each function call, and reflect on outcomes of previous calls. DO NOT solve entirely via function calls—think insightfully first.
```

### Reasoning vs. GPT Models (Mental Model)
- **Reasoning model** = Senior coworker: Give goals, trust them to work out details
- **GPT model** = Junior coworker: Provide explicit instructions for specific outputs

## Examples

### Example 1: Code Generation Assistant
```text
# Identity
You are a coding assistant that enforces snake_case variables in JavaScript
and writes code compatible with Internet Explorer 6.

# Instructions
* Use snake_case names (my_variable) instead of camelCase
* Use "var" keyword for browser compatibility
* Return code only, no Markdown formatting

# Examples
<user_query>
How do I declare a string variable for a first name?
</user_query>
<assistant_response>
var first_name = "Anna";
</assistant_response>
```

### Example 2: Tool-Calling with Reservations
```json
{
  "name": "create_reservation",
  "description": "Create a restaurant reservation. Use when user asks to book a table.",
  "parameters": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Guest full name" },
      "datetime": { "type": "string", "description": "ISO 8601 date/time" }
    },
    "required": ["name", "datetime"]
  }
}
```

**Prompt guidance:**
```text
<reservation_tool_usage>
- When user asks to book/reserve/schedule, MUST call create_reservation
- Do NOT guess—ask for missing name or date/time
- After calling, confirm: "Your reservation for [name] on [date/time] is confirmed."
</reservation_tool_usage>
```

### Example 3: Agentic User Updates
For long-running tasks, keep users informed:
```text
<user_updates_spec>
<frequency_and_length>
- Send short updates (1–2 sentences) every few tool calls
- Post update at least every 6 execution steps or 8 tool calls
- Brief heads-down note if expecting longer stretch
</frequency_and_length>

<content>
- Before first tool call: quick plan with goal, constraints, next steps
- While exploring: call out meaningful discoveries
- Always state concrete outcome since prior update ("found X", "confirmed Y")
- End with brief recap and follow-up steps
</content>
</user_updates_spec>
```

## Tips

### Tool Calling Best Practices
1. Describe functionality in tool definitions, usage guidance in prompts
2. Enable parallel tool calling for efficiency (batch reads/edits)
3. Add instruction: `Parallelize tool calls whenever possible`

### Coding Agents (GPT-5.1)
1. Use the new **apply_patch** named tool for structured diffs (35% lower failure rate)
2. Implement a **planning tool** for medium/large tasks:
   - Create 2–5 milestone items before first action
   - Maintain statuses: one item `in_progress` at a time
   - End with all items completed or explicitly canceled

### Design System Enforcement
```text
<design_system_enforcement>
- Never hard-code colors (hex/rgb) in JSX/CSS
- All colors from CSS variables (--background, --primary, --accent, etc.)
- Use Tailwind utilities wired to tokens
- Default to neutral palette unless user requests brand look
</design_system_enforcement>
```

### Common Pitfalls to Avoid
- **Don't assume output location**: The `output` array may contain multiple items (tool calls, reasoning data)—use `output_text` helper
- **Don't forget context window limits**: Models range from ~100k to 1M tokens; check model docs
- **Don't leave instructions unchanged** across model versions—different snapshots may need different prompting
- **Don't be vague with GPT models**: They perform best with explicit, detailed instructions

### Migration Tips (GPT-5 → GPT-5.1)
1. GPT-5.1 can be excessively concise—emphasize persistence and completeness
2. Be explicit about desired output detail (can be verbose)
3. Migrate apply_patch to the new named tool implementation
4. Check for conflicting instructions if behavior issues arise