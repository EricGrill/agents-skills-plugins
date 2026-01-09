# Tinker Format Specification

This reference documents the exact data structures required for Tinker supervised fine-tuning.

## Core Data Types

### Datum

The fundamental training unit in Tinker:

```python
from tinker import types

datum = types.Datum(
    model_input=types.ModelInput.from_ints(tokens=input_tokens),
    loss_fn_inputs={
        "target_tokens": target_tokens,  # List[int] - shifted by 1 for next-token prediction
        "weights": weights               # List[float] - 0.0 for prompt, 1.0 for completion
    }
)
```

### ModelInput

Container for tokenized input:

```python
# Simple text-only input
model_input = types.ModelInput.from_ints(tokens=[...])

# Multi-modal (for VLMs)
model_input = types.ModelInput(chunks=[
    types.EncodedTextChunk(tokens=[...]),
    types.ImageChunk(data=image_bytes, format="png"),
    types.EncodedTextChunk(tokens=[...])
])
```

### Token Weight Assignment

The weights array determines which tokens contribute to the loss:

| Token Type | Weight | Description |
|------------|--------|-------------|
| System prompt | 0.0 | Context, not learned |
| User message | 0.0 | Input prompt |
| Assistant message | 1.0 | Target completion |
| Special tokens | 0.0 | EOS, BOS, delimiters |

## Renderer System

Tinker uses renderers to convert message lists to tokens with proper weights.

### Using Built-in Renderers

```python
from tinker_cookbook import renderers, tokenizer_utils

# Get tokenizer for your model
tokenizer = tokenizer_utils.get_tokenizer("meta-llama/Llama-3.1-8B-Instruct")

# Get appropriate renderer
renderer = renderers.get_renderer("llama3", tokenizer)

# Convert messages to training format
messages = [
    {"role": "system", "content": "You are a creative writer..."},
    {"role": "user", "content": "Write a 500 word excerpt..."},
    {"role": "assistant", "content": "The actual book text..."}
]

model_input, weights = renderer.build_supervised_example(messages)
```

### Renderer Output Visualization

The renderer assigns weights per-token:

```
Token          Weight
<|im_start|>   0.0
system         0.0
\n             0.0
You are...     0.0
<|im_end|>     0.0
...            ...
<|im_start|>   0.0
assistant      0.0
\n             0.0
The actual     1.0    <- Completion starts
book text      1.0
...            1.0
<|im_end|>     1.0    <- Final token weighted
```

## JSONL Format

For batch processing, use standard conversation JSONL:

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### Converting JSONL to Datum

```python
import json
from tinker import types
from tinker_cookbook import renderers, tokenizer_utils

def load_dataset(jsonl_path: str, model_name: str) -> list[types.Datum]:
    """Load JSONL and convert to Tinker Datum objects."""
    
    tokenizer = tokenizer_utils.get_tokenizer(model_name)
    renderer = renderers.get_renderer("llama3", tokenizer)
    
    data = []
    with open(jsonl_path) as f:
        for line in f:
            example = json.loads(line)
            messages = example["messages"]
            
            model_input, weights = renderer.build_supervised_example(messages)
            
            # Get token sequences
            input_tokens = model_input.to_ints()
            target_tokens = input_tokens[1:]  # Shift for next-token prediction
            input_tokens = input_tokens[:-1]
            weights = weights[1:]  # Align weights with targets
            
            datum = types.Datum(
                model_input=types.ModelInput.from_ints(tokens=input_tokens),
                loss_fn_inputs={
                    "target_tokens": target_tokens,
                    "weights": weights
                }
            )
            data.append(datum)
    
    return data
```

## Training Loop Integration

```python
import tinker
from tinker import types

async def train_on_book_dataset(
    dataset: list[types.Datum],
    model_name: str,
    learning_rate: float = 1e-4,
    epochs: int = 1
):
    """Train on book SFT dataset."""
    
    service_client = tinker.ServiceClient()
    training_client = await service_client.create_lora_training_client_async(
        base_model=model_name,
        rank=32
    )
    
    for epoch in range(epochs):
        for batch_start in range(0, len(dataset), 1):  # Batch size 1
            batch = dataset[batch_start:batch_start + 1]
            
            # Forward-backward with cross-entropy loss
            fwd_bwd_future = await training_client.forward_backward_async(
                batch, 
                loss_fn="cross_entropy"
            )
            
            # Optimizer step with aggressive learning rate
            optim_future = await training_client.optim_step_async(
                types.AdamParams(learning_rate=learning_rate * 2.0)
            )
            
            # Wait for completion
            fwd_bwd_result = await fwd_bwd_future
            optim_result = await optim_future
```

## Key Constraints

1. **Batch Size**: Use 1 for style transfer. Larger batches average out stylistic gradients.

2. **Sequence Length**: Keep chunks under 1000 tokens. Longer sequences dilute local style patterns.

3. **Learning Rate**: Use 2x multiplier (e.g., 2e-4 instead of 1e-4) for faster style convergence.

4. **Token Alignment**: Target tokens must be shifted by 1 position from input tokens.

5. **Weight Precision**: Weights should be float32, typically 0.0 or 1.0.

## Model Selection

For book SFT, consider:

| Model | Use Case |
|-------|----------|
| meta-llama/Llama-3.1-8B-Instruct | General style transfer |
| Qwen/Qwen3-30B-A3B | Higher quality, MoE efficiency |
| GPT-4o (via OpenAI) | Data generation only, not Tinker |

## References

- Tinker Cookbook: `tinker_cookbook/supervised/train.py`
- Renderer implementations: `tinker_cookbook/renderers.py`
- Type definitions: `tinker/types.py`

