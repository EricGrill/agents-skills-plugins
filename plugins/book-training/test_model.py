#!/usr/bin/env python3
"""
Test the fine-tuned Gertrude Stein style model.
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

import tinker
from tinker import types
from transformers import AutoTokenizer

# Your trained model path
MODEL_PATH = "tinker://ff162b8a-6845-5375-95d5-0509db7951d2:train:0/sampler_weights/final"

# Test prompts in different styles
TEST_PROMPTS = [
    {
        "name": "Simple scene",
        "messages": [
            {"role": "system", "content": "You are an expert creative writer capable of emulating specific literary styles."},
            {"role": "user", "content": "Write a short passage in the style of Gertrude Stein about a woman making coffee in the morning."}
        ]
    },
    {
        "name": "Character study",
        "messages": [
            {"role": "system", "content": "You are a literary writer with deep knowledge of early 20th century American modernist prose."},
            {"role": "user", "content": "In Gertrude Stein's style, describe a kind old woman who works as a seamstress and loves her garden."}
        ]
    },
    {
        "name": "Relationship dynamics",
        "messages": [
            {"role": "system", "content": "You are an expert creative writer capable of emulating specific literary styles."},
            {"role": "user", "content": "Write like Gertrude Stein: Two friends, one practical and one dreamy, share a quiet afternoon together."}
        ]
    }
]


async def test_model():
    print("=" * 70)
    print("🎭 Testing Gertrude Stein Style Model")
    print("=" * 70)
    print(f"\nModel: {MODEL_PATH}\n")
    
    # Initialize Tinker
    service_client = tinker.ServiceClient()
    
    # Load tokenizer from Hugging Face
    model_name = "Qwen/Qwen3-8B-Base"
    print(f"Loading tokenizer for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    print(f"Tokenizer loaded: {len(tokenizer)} tokens")
    
    print("Creating sampling client...")
    sampling_client = service_client.create_sampling_client(model_path=MODEL_PATH)
    print("Sampling client ready!\n")
    
    # Sampling parameters
    sampling_params = types.SamplingParams(
        max_tokens=400,
        temperature=0.7,
        top_p=0.9,
        stop=["<|im_end|>", "<|endoftext|>"]
    )
    
    for i, test in enumerate(TEST_PROMPTS, 1):
        print("-" * 70)
        print(f"📝 Test {i}: {test['name']}")
        print("-" * 70)
        
        # Build prompt in Qwen3 chat format
        prompt_text = ""
        for msg in test["messages"]:
            prompt_text += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"
        prompt_text += "<|im_start|>assistant\n"
        
        print(f"\n💬 Prompt:\n{test['messages'][-1]['content'][:100]}...\n")
        
        # Tokenize and sample
        prompt_tokens = tokenizer.encode(prompt_text)
        model_input = types.ModelInput.from_ints(prompt_tokens)
        
        print("Generating...")
        result = await sampling_client.sample_async(
            prompt=model_input,
            sampling_params=sampling_params,
            num_samples=1
        )
        
        # Decode response
        response_tokens = result.sequences[0].tokens
        response_text = tokenizer.decode(response_tokens)
        
        print(f"\n✨ Generated Response:\n")
        print(response_text.strip())
        print()
    
    print("=" * 70)
    print("✅ Testing complete!")
    print("=" * 70)
    
    # Interactive mode
    print("\n🎤 Interactive Mode - Type your prompts (or 'quit' to exit):\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        if not user_input:
            continue
        
        # Build prompt
        prompt_text = f"""<|im_start|>system
You are an expert creative writer capable of emulating specific literary styles.<|im_end|>
<|im_start|>user
Write in the style of Gertrude Stein: {user_input}<|im_end|>
<|im_start|>assistant
"""
        
        prompt_tokens = tokenizer.encode(prompt_text)
        model_input = types.ModelInput.from_ints(prompt_tokens)
        
        result = await sampling_client.sample_async(
            prompt=model_input,
            sampling_params=sampling_params,
            num_samples=1
        )
        
        response_text = tokenizer.decode(result.sequences[0].tokens)
        print(f"\n🖋️  Gertrude Stein style:\n{response_text.strip()}\n")


if __name__ == "__main__":
    asyncio.run(test_model())

