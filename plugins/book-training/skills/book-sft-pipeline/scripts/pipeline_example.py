"""
Book SFT Pipeline - Conceptual Implementation

This demonstrates the core patterns for building book-to-SFT pipelines.
Adapt to your specific LLM provider and training platform.
"""

from dataclasses import dataclass
from typing import List
import json

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class Chunk:
    text: str
    word_count: int
    id: int

@dataclass 
class TrainingExample:
    system: str
    user: str
    assistant: str
    
    def to_messages(self) -> dict:
        return {
            "messages": [
                {"role": "system", "content": self.system},
                {"role": "user", "content": self.user},
                {"role": "assistant", "content": self.assistant}
            ]
        }

# =============================================================================
# Segmentation - The Core Algorithm
# =============================================================================

def segment_text(text: str, min_words: int = 150, max_words: int = 400) -> List[Chunk]:
    """
    Segment text into training-sized chunks with overlap.
    
    Key insight: Smaller chunks (150-400) produce more examples and better
    style transfer than larger chunks (250-650).
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    buffer = []
    buffer_words = 0
    
    for para in paragraphs:
        para_words = len(para.split())
        
        if buffer_words + para_words > max_words and buffer_words >= min_words:
            chunks.append(Chunk(
                text='\n\n'.join(buffer),
                word_count=buffer_words,
                id=len(chunks)
            ))
            # Keep last paragraph for overlap
            buffer = [buffer[-1], para] if buffer else [para]
            buffer_words = len(buffer[-2].split()) + para_words if len(buffer) > 1 else para_words
        else:
            buffer.append(para)
            buffer_words += para_words
    
    if buffer and buffer_words >= min_words // 2:
        chunks.append(Chunk(text='\n\n'.join(buffer), word_count=buffer_words, id=len(chunks)))
    
    return chunks

# =============================================================================
# Diverse Prompt Generation - Prevents Memorization
# =============================================================================

SYSTEM_PROMPTS = [
    "You are an expert creative writer capable of emulating specific literary styles.",
    "You are a literary writer with deep knowledge of classic prose styles.",
    "You are a creative writer skilled at emulating distinctive authorial voices.",
]

PROMPT_TEMPLATES = [
    "Write a passage in the style of {author}: {desc}",
    "Channel {author}'s voice to write about: {desc}",
    "In {author}'s distinctive prose style, describe: {desc}",
    "Write this scene as {author} would have: {desc}",
    "Using {author}'s repetitive, rhythmic technique, write: {desc}",
]

def build_examples(chunk: Chunk, instruction: str, author: str, variants: int = 2) -> List[TrainingExample]:
    """
    Generate multiple training variants per chunk.
    
    Key insight: Diverse prompts prevent the model from memorizing 
    specific phrasings and force it to learn underlying style patterns.
    """
    examples = []
    for i in range(variants):
        system = SYSTEM_PROMPTS[i % len(SYSTEM_PROMPTS)]
        template = PROMPT_TEMPLATES[(chunk.id + i) % len(PROMPT_TEMPLATES)]
        user = template.format(author=author, desc=instruction)
        examples.append(TrainingExample(system=system, user=user, assistant=chunk.text))
    return examples

# =============================================================================
# Instruction Generation Prompt
# =============================================================================

INSTRUCTION_PROMPT = """Describe what is happening in this excerpt in 2-3 sentences.
Focus on: characters present, actions, emotions, and setting.
Do NOT quote the text directly.

Excerpt:
{text}
"""

def generate_instruction(chunk: Chunk, llm_call) -> str:
    """
    Generate a scene description for the chunk.
    Replace llm_call with your actual LLM API.
    """
    prompt = INSTRUCTION_PROMPT.format(text=chunk.text[:2000])
    response = llm_call(prompt)
    # Clean common prefixes
    cleaned = response.strip()
    for prefix in ["This excerpt", "The excerpt", "In this passage"]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].lstrip(", :")
    return cleaned

# =============================================================================
# Tinker Datum Construction
# =============================================================================

def build_tinker_datum(example: dict, tokenizer, renderer):
    """
    Convert training example to Tinker Datum format.
    
    Key insight: Weights of 0 for prompt, 1 for completion.
    This teaches the model to generate completions, not repeat prompts.
    """
    messages = example["messages"]
    model_input, weights = renderer.build_supervised_example(messages)
    
    input_tokens = model_input.to_ints()
    target_tokens = input_tokens[1:]  # Shift for next-token prediction
    weights = weights[1:]             # Align weights
    
    return {
        "model_input": input_tokens[:-1],
        "loss_fn_inputs": {
            "target_tokens": target_tokens,
            "weights": weights
        }
    }

# =============================================================================
# Validation Patterns
# =============================================================================

def validate_style_transfer(output: str, training_data_path: str) -> dict:
    """
    Validate that the model learned style, not just memorized content.
    """
    # Check for exact phrase matches in training data
    with open(training_data_path) as f:
        training_text = f.read()
    
    # Split output into phrases and check for matches
    phrases = [output[i:i+50] for i in range(0, len(output)-50, 25)]
    exact_matches = sum(1 for p in phrases if p in training_text)
    
    return {
        "originality_score": 1.0 - (exact_matches / max(len(phrases), 1)),
        "exact_matches": exact_matches,
        "is_original": exact_matches < 3
    }

MODERN_TEST_SCENARIOS = [
    "Write about a barista making lattes",
    "Describe two lovers communicating through text messages",
    "Write about someone anxious about climate change",
]
# If model applies style to modern scenarios, it learned STYLE not CONTENT

