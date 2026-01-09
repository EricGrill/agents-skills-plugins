# Book SFT Pipeline

A skill for training small language models to write in any author's style using supervised fine-tuning.

## Overview

This skill teaches AI agents how to:
- Extract and segment text from books (ePub format)
- Generate diverse synthetic instructions for SFT
- Train LoRA adapters on Tinker
- Validate style transfer with modern scenarios

## Structure

```
book-sft-pipeline/
├── README.md                 # This file
├── SKILL.md                  # Main skill documentation
├── examples/
│   └── gertrude-stein/       # Real training example with outputs
├── scripts/
│   └── pipeline_example.py   # Conceptual implementation
└── references/
    ├── segmentation-strategies.md
    ├── tinker-format.md
    └── tinker.txt
```

## Quick Start

1. Read `SKILL.md` for the complete methodology
2. Review `examples/gertrude-stein/` for a real implementation
3. Adapt `scripts/pipeline_example.py` for your use case

## Key Results

Trained Qwen3-8B-Base on Gertrude Stein's "Three Lives" (1909):
- 592 training examples from one 86,000-word book
- 100% Human score on Pangram AI detector
- Verified original content generation
- Total cost: $2

## License

MIT


