# Kimi (Moonshot) Prompting Guide
Last updated: January 2025

## Overview

Kimi is an AI assistant developed by Moonshot AI, designed to be proficient in both Chinese and English conversations. The prompting approach emphasizes clarity, structure, and explicit guidance to help the model understand exactly what you need. Kimi excels when given detailed context and clear instructions.

## Key Principles

1. **Write Clear Instructions**: The model cannot read your mind. Be explicit about what you want—specify length, format, style, and level of detail. The less guessing required, the better the results.

2. **Include All Relevant Details**: Provide comprehensive context and requirements in your request. Vague prompts lead to vague outputs.

3. **Use Delimiters**: Clearly separate different parts of your input using triple quotes, XML tags, or section headings to help the model understand the structure.

4. **Define Steps Explicitly**: For complex tasks, outline the exact steps the model should follow.

5. **Provide Examples**: Few-shot prompting with examples is more effective than lengthy explanations, especially for style or format replication.

## Techniques

### Role Assignment
Assign a specific role to get more accurate, contextually appropriate outputs:

```json
{
  "messages": [
    {"role": "system", "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers."},
    {"role": "user", "content": "Hello, my name is Li Lei. What is 1+1?"}
  ]
}
```

### Using Delimiters
Separate different content sections using XML tags, triple quotes, or clear headings:

**XML Tags Example:**
```json
{
  "messages": [
    {"role": "system", "content": "You will receive two articles separated by XML tags. First, summarize the arguments of each article, then point out which presents a better argument and explain why."},
    {"role": "user", "content": "<article>Insert article here</article><article>Insert article here</article>"}
  ]
}
```

**Section Headings Example:**
```json
{
  "messages": [
    {"role": "system", "content": "You will receive an abstract and the title of a paper. If the title does not clearly convey the topic and is not eye-catching, suggest five alternative options."},
    {"role": "user", "content": "Abstract: Insert abstract here.\n\nTitle: Insert title here"}
  ]
}
```

### Step-by-Step Instructions
Define explicit steps for multi-part tasks:

```json
{
  "messages": [
    {"role": "system", "content": "Respond to user input using the following steps.\nStep one: The user will provide text enclosed in triple quotes. Summarize this text into one sentence with the prefix \"Summary: \".\nStep two: Translate the summary from step one into English and add the prefix \"Translation: \"."},
    {"role": "user", "content": "\"\"\"Insert text here\"\"\""}
  ]
}
```

### Few-Shot Prompting
Provide examples to demonstrate the desired output style or format:

```json
{
  "messages": [
    {"role": "system", "content": "Respond in a consistent style"},
    {"role": "user", "content": "Insert text here"}
  ]
}
```

### Specifying Output Length
Request specific lengths using paragraphs or bullet points (more reliable than word counts):

```json
{
  "messages": [
    {"role": "user", "content": "Summarize the text within the triple quotes in two sentences, within 50 words. \"\"\"Insert text here\"\"\""}
  ]
}
```

### Using Reference Text
Guide the model to use provided information for accurate answers:

```json
{
  "messages": [
    {"role": "system", "content": "Answer the question using the provided article (enclosed in triple quotes). If the answer is not found in the article, write \"I can't find the answer.\""},
    {"role": "user", "content": "<Insert article, each article enclosed in triple quotes>"}
  ]
}
```

## Examples

### Example 1: Detailed Request vs. General Request

**Less Effective:**
```
How to add numbers in Excel?
```

**More Effective:**
```
How do I sum a row of numbers in an Excel table? I want to automatically sum each row in the entire table and place all the totals in the rightmost column named "Total."
```

### Example 2: Work Summary with Constraints

**Less Effective:**
```
Work report summary
```

**More Effective:**
```
Summarize my work records from 2023 in a paragraph of no more than 500 words. List the highlights of each month in sequence and provide a summary of the entire year.
```

### Example 3: Customer Service with Categorization

```json
{
  "messages": [
    {"role": "system", "content": "You will receive a customer service inquiry that requires technical support. You can assist the user in the following ways:\n\n- Ask them to check if the configuration is correct.\n- If all settings are configured but the problem persists, ask for the device model they are using.\n- Now you need to tell them how to restart the device:\n  - If the device model is A, perform [specific steps].\n  - If the device model is B, suggest they perform [specific steps]."}
  ]
}
```

## Tips

### Breaking Down Complex Tasks

**Categorize Queries**: For tasks requiring different instructions based on scenarios, first classify the query type, then apply the appropriate instructions.

**Summarize Long Conversations**: Since models have fixed context lengths:
- Summarize earlier conversation rounds when reaching context limits
- Include conversation summaries as part of the system message
- Summarize asynchronously throughout the chat process

**Handle Long Documents**: For lengthy content like books:
- Summarize each section/chapter individually
- Aggregate partial summaries into a summary of summaries
- Recursively repeat until the entire document is summarized
- Include summaries of earlier sections when later parts depend on them

### Best Practices

1. **Be Specific About Format**: If you want JSON, tables, or bullet points, say so explicitly
2. **Provide Context**: Don't assume the model knows your specific situation
3. **Use Consistent Structure**: Maintain the same format pattern throughout your prompts
4. **Test and Iterate**: If results aren't satisfactory, refine your instructions
5. **Leverage System Messages**: Use the system role for persistent instructions and persona definitions

### Common Pitfalls to Avoid

- ❌ Asking for exact word counts (paragraphs/bullet points are more reliable)
- ❌ Providing vague or ambiguous instructions
- ❌ Omitting important context or constraints
- ❌ Mixing different formatting styles in the same prompt
- ❌ Expecting the model to infer unstated requirements
