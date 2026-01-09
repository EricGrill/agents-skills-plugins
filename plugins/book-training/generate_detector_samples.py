#!/usr/bin/env python3
"""
Generate clean samples for AI detector testing.
Focuses on modern scenarios with strong Stein style.
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

import tinker
from tinker import types
from transformers import AutoTokenizer

MODEL_PATH = "tinker://ff162b8a-6845-5375-95d5-0509db7951d2:train:0/sampler_weights/final"
MODEL_NAME = "Qwen/Qwen3-8B-Base"

# Prompts designed to avoid character name leakage
DETECTOR_PROMPTS = [
    {
        "name": "Coffee Shop Morning",
        "prompt": "Write a paragraph in Gertrude Stein's style about a woman drinking coffee alone at a cafe, watching people walk by on a rainy morning. Focus on her thoughts and feelings, not plot.",
    },
    {
        "name": "Subway Commute",
        "prompt": "In Gertrude Stein's distinctive voice, describe a tired office worker on a crowded subway train going home after a long day. Use simple words and repetition.",
    },
    {
        "name": "Online Shopping",
        "prompt": "Write like Gertrude Stein about a woman browsing an online store late at night, adding things to her cart but never buying them.",
    },
    {
        "name": "Video Call Family",
        "prompt": "In the style of Gertrude Stein, write about a grandmother learning to use video calls to see her grandchildren who live far away.",
    },
    {
        "name": "Food Delivery",
        "prompt": "Write a passage in Gertrude Stein's style about a food delivery driver who thinks about life while waiting for orders.",
    },
]

SYSTEM = "You are an expert creative writer. Write original prose in Gertrude Stein's distinctive modernist style, using repetition, simple vocabulary, and rhythmic sentences. Do not reference any existing characters or stories."


async def generate_samples():
    print("=" * 70)
    print("  📝 Generating Clean Samples for AI Detector Testing")
    print("=" * 70)
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    service_client = tinker.ServiceClient()
    sampling_client = service_client.create_sampling_client(model_path=MODEL_PATH)
    
    sampling_params = types.SamplingParams(
        max_tokens=300,
        temperature=0.75,
        top_p=0.9,
        stop=["<|im_end|>", "<|endoftext|>"]
    )
    
    samples = []
    
    for i, p in enumerate(DETECTOR_PROMPTS, 1):
        print(f"\n{'─' * 70}")
        print(f"  {i}. {p['name']}")
        print(f"{'─' * 70}")
        
        prompt_text = f"""<|im_start|>system
{SYSTEM}<|im_end|>
<|im_start|>user
{p['prompt']}<|im_end|>
<|im_start|>assistant
"""
        
        prompt_tokens = tokenizer.encode(prompt_text)
        model_input = types.ModelInput.from_ints(prompt_tokens)
        
        result = await sampling_client.sample_async(
            prompt=model_input,
            sampling_params=sampling_params,
            num_samples=1
        )
        
        response = tokenizer.decode(result.sequences[0].tokens)
        response = response.split("<|im_end|>")[0].strip()
        
        # Clean any artifacts
        if "<|" in response:
            response = response.split("<|")[0].strip()
        
        print(f"\n{response}\n")
        
        samples.append({
            "name": p["name"],
            "text": response,
            "word_count": len(response.split())
        })
    
    # Save to file for easy copy/paste
    print("\n" + "=" * 70)
    print("  📋 SAMPLES FOR AI DETECTOR TESTING")
    print("=" * 70)
    
    output_file = "ai_detector_samples.txt"
    with open(output_file, "w") as f:
        for s in samples:
            f.write(f"=== {s['name']} ({s['word_count']} words) ===\n\n")
            f.write(s['text'])
            f.write("\n\n" + "-" * 50 + "\n\n")
    
    print(f"\n✅ Saved to: {output_file}")
    print("\nCopy these samples and paste into:")
    print("  • GPTZero: https://gptzero.me")
    print("  • ZeroGPT: https://zerogpt.com")
    print("  • Originality.ai: https://originality.ai")
    print("  • Copyleaks: https://copyleaks.com/ai-content-detector")
    
    return samples


if __name__ == "__main__":
    asyncio.run(generate_samples())

