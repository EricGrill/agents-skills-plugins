---
license: mit
task_categories:
  - text-generation
language:
  - en
tags:
  - style-transfer
  - sft
  - creative-writing
  - literary
  - gertrude-stein
  - modernist-prose
  - fine-tuning
  - lora
pretty_name: Gertrude Stein Style Transfer SFT Dataset
size_categories:
  - n<1K
---

# Gertrude Stein Style Transfer SFT Dataset

A supervised fine-tuning dataset for training language models to write in Gertrude Stein's distinctive literary style. Generated from her 1909 novel "Three Lives."

## Dataset Description

This dataset contains instruction-response pairs where:
- **Input**: A prompt asking the model to write in Gertrude Stein's style about a specific scene
- **Output**: The actual text from Stein's novel

The dataset uses diverse prompt templates (15 variations) and system prompts (5 variations) to prevent memorization and encourage style transfer rather than content parroting.

### Key Features

- **Source**: "Three Lives" by Gertrude Stein (1909, public domain)
- **Segmentation**: 150-400 word chunks with overlap for context continuity
- **Prompt Diversity**: 75 unique prompt combinations (15 templates × 5 system prompts)
- **Variants**: 2 prompt variants per text chunk

## Dataset Statistics

| Split | Examples |
|-------|----------|
| Train | 591 |
| Test | 49 |
| **Total** | **640** |

## Data Format

Each example follows the chat/conversational format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert creative writer capable of emulating specific literary styles."
    },
    {
      "role": "user",
      "content": "Write a passage in the style of Gertrude Stein: Anna, devoted to her doctor, finds herself entangled in her friend's schemes..."
    },
    {
      "role": "assistant",
      "content": "All this meant a gold watch and chain to her god daughter..."
    }
  ]
}
```

## Prompt Templates Used

```
- "Write a passage in the style of {author}: {description}"
- "Channel {author}'s voice to write about: {description}"
- "In {author}'s distinctive prose style, describe: {description}"
- "Write this scene as {author} would have written it: {description}"
- "Using simple, repetitive sentences like {author}, describe: {description}"
- ... and 10 more variations
```

## System Prompts Used

```
- "You are an expert creative writer capable of emulating specific literary styles."
- "You are a literary writer with deep knowledge of early 20th century American modernist prose."
- "You are a creative writer skilled at emulating distinctive authorial voices."
- "You write prose that captures the essence of modernist literature."
- "You are a talented writer who can channel the voice of classic American authors."
```

## Training Results

Using this dataset to train Qwen/Qwen3-8B-Base with LoRA (rank 32):

| Metric | Value |
|--------|-------|
| Initial Test Loss | 7,584 |
| Final Test Loss | 213 |
| Loss Reduction | 97% |
| Training Time | ~15 min |
| AI Detector Score | 100% Human (Pangram) |

### Style Transfer Validation

The trained model successfully applies Stein's style to modern scenarios not in the training data:

**Prompt**: Write about a real estate clerk coming home tired.

**Output**:
> It was a very busy day for the clerk in the real estate office. He came home to his small house in the working class part of the town, very tired... She looked at him and saw that he was very tired. She looked at him and then looked away into the fire.

Verified original: "real estate office", "working class" do not appear in training data.

## Gertrude Stein's Style Markers

The dataset captures these distinctive characteristics:

1. **Repetitive sentence structures**: "She was a good woman. She was always a good woman."
2. **Simple vocabulary**: Common words, no ornate language
3. **Comma-separated adjectives**: "a dark, sweet, little, pretty girl"
4. **Present continuous tense**: "She was always doing", "He was thinking"
5. **Character focus**: Deep psychological observation over plot
6. **Rhythmic, hypnotic quality**: Almost musical prose

## Usage

### Loading the Dataset

```python
from datasets import load_dataset

dataset = load_dataset("MuratcanKoylan/gertrude-stein-style-sft")
```

### Training with Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B-Base")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B-Base")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    # ... config
)
```

### Training with Tinker

```python
import tinker
from tinker import types

training_client = await service_client.create_lora_training_client_async(
    base_model="Qwen/Qwen3-8B-Base",
    rank=32
)

# Process dataset into Tinker Datum format
# See: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
```

## Generation Pipeline

This dataset was generated using the [book-sft-pipeline](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/book-sft-pipeline) skill:

1. **Extraction**: ePub parsing with paragraph-level text extraction
2. **Segmentation**: 150-400 word chunks with overlap
3. **Instruction Generation**: Gemini Flash describing each scene
4. **Dataset Building**: Multiple prompt variants per chunk

Total generation cost: ~$0.50 (Gemini API calls)

## Limitations

- **Character Name Leakage**: ~30% of model outputs may include original character names (Melanctha, Anna, Mrs. Lehntman) even in novel scenarios
- **Single Source**: Dataset derived from one book limits character/setting diversity
- **Style-Specific**: Designed specifically for Gertrude Stein's modernist style

## Citation

```bibtex
@dataset{koylan2024steinestyle,
  title={Gertrude Stein Style Transfer SFT Dataset},
  author={Koylan, Muratcan},
  year={2024},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/MuratcanKoylan/gertrude-stein-style-sft}
}
```

## License

MIT License

The source text "Three Lives" by Gertrude Stein (1909) is in the public domain.

## Related

- [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) - The skill used to generate this dataset
- [Book SFT Pipeline Skill](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/book-sft-pipeline) - Detailed methodology


