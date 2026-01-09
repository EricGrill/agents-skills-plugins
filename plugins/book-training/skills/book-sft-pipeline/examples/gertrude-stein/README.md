# Example: Gertrude Stein Style Transfer

A complete case study of training Qwen3-8B-Base to write in Gertrude Stein's style using her 1909 novel "Three Lives."

## Project Summary

| Metric | Value |
|--------|-------|
| Source Book | Three Lives (1909) |
| Book Word Count | ~86,000 |
| Training Examples | 592 |
| Test Examples | 50 |
| Model | Qwen/Qwen3-8B-Base |
| LoRA Rank | 32 |
| Adapter Size | 352 MB |
| Training Time | ~15 minutes |
| Total Cost | ~$2 |

## Training Metrics

### Loss Trajectory

| Step | Train Loss | Test Loss |
|------|-----------|-----------|
| 5 | 7579.67 | - |
| 40 | 4032.35 | 7584.85 |
| 100 | 2392.17 | 2127.44 |
| 140 | 2863.17 | 752.95 |
| 180 | 1327.41 | 229.88 |
| 200 | 1044.49 | 213.36 |
| Final | ~800 | ~200 |

Loss reduction: 97% (7584 to 213 test loss)

## Style Markers Learned

The model successfully learned these Gertrude Stein characteristics:

1. **Repetitive sentence structures**: "She was a good woman. She was always a good woman."
2. **Simple vocabulary**: Common words, no ornate language
3. **Comma-separated adjectives**: "a dark, sweet, little, pretty girl"
4. **Present continuous tense**: "She was always doing", "He was thinking"
5. **Character focus**: Deep psychological observation over plot
6. **Rhythmic, hypnotic quality**: Almost musical prose

## Sample Outputs

### Modern Scenario: Real Estate Office

**Prompt**: Write in Gertrude Stein's style about a real estate clerk coming home tired.

**Output**:
> It was a very busy day for the clerk in the real estate office. He came home to his small house in the working class part of the town, very tired. He went into the kitchen where his wife was cooking.
>
> "Hi, Sis, home for dinner?" he said to her.
>
> She looked at him and saw that he was very tired. She looked at him and then looked away into the fire. She said nothing in answer to him.
>
> He took off his hat and coat and then sat down on the steps just inside the door to take a rest. He was very tired today, he sat there and just sort of dozed a little.

**Analysis**: Original content verified - "real estate office", "working class", "Hi, Sis" do not appear in training data.

### Modern Scenario: Text Messages

**Prompt**: Write about two lovers communicating through text messages.

**Output**:
> "Hey, Herman, I just got a minute to be gone from my patient. Want to talk to you for a little while, Herman," Lena wrote one night, and then she sent the text to him.
>
> Herman read it and then he wrote her back, "I was just getting ready to go to bed, Lena. Want me to come and see you tomorrow, Lena. Want me to bring something to you, Lena. Want me to bring you some ice cream, Lena. Want me to bring you some of those little donuts..."

**Analysis**: Classic Stein anaphora (repetition at sentence starts) applied to modern SMS format.

## AI Detector Results

Tested with Pangram AI detector: **100% Human Written**

Multiple samples tested, all scored as human-written prose.

## Validation Method

### Modern Scenario Testing

We tested the model on scenarios that couldn't exist in 1909:
- Barista making lattes
- Social media scrolling
- Video calls
- Food delivery drivers
- Climate change anxiety

When style markers appeared in modern contexts, it proved the model learned **style** rather than **content**.

### Originality Verification

Searched training data for output phrases:

```bash
grep "real estate office" dataset.jsonl    # No matches
grep "working class" dataset.jsonl          # No matches
grep "Hi, Sis" dataset.jsonl                # No matches
grep "text messages" dataset.jsonl          # No matches
```

## Known Limitations

### Character Name Leakage (~30% of outputs)

The model sometimes uses original character names (Melanctha, Mrs. Lehntman, Anna) even in modern scenarios. This is because 592 examples from one book means these names appear hundreds of times.

**Mitigation**: Train on multiple books by the same author, or add synthetic examples with different names.

### Success Rate Distribution

- Perfect style transfer: ~50%
- Style with name leakage: ~30%
- Partial style: ~15%
- Failed: ~5%

The 50% perfect rate is realistic for an 8B model trained on one book.

## Configuration Used

### Dataset Generation

```python
CONFIG = {
    "min_words": 150,
    "max_words": 400,
    "overlap": True,  # Last paragraph carried to next chunk
    "variants_per_chunk": 2,
    "prompt_templates": 15,
    "system_prompts": 5,
    "instruction_model": "gemini-2.0-flash-lite",
}
```

### Training

```python
CONFIG = {
    "model_name": "Qwen/Qwen3-8B-Base",
    "lora_rank": 32,
    "learning_rate": 5e-4,
    "batch_size": 4,
    "epochs": 3,
    "eval_every": 20,
    "save_every": 50,
}
```

## Key Learnings

1. **Smaller chunks work better**: 150-400 words produced more examples and better style transfer than 250-650

2. **Prompt diversity is critical**: 15 templates × 5 system prompts = 75 variations prevented memorization

3. **Base models over instruct**: Qwen3-8B-Base was more malleable than instruct versions

4. **Modern scenario testing proves transfer**: If style applies to modern contexts, the model learned patterns, not content

5. **~$2 is enough**: LLM calls for instruction generation (~$0.50) plus Tinker training (~$1.50)

## Files

- `sample_outputs.md` - Full model outputs with analysis
- `training_config.json` - Exact configuration used
- `dataset_sample.jsonl` - Sample training examples


