#!/usr/bin/env python3
"""
Style Transfer Test: Modern Scenarios in Gertrude Stein's Voice

This tests whether the model learned Gertrude Stein's STYLE vs just memorizing content.
We use modern scenarios (tech, social media, etc.) that couldn't exist in 1909.

If the model truly learned the style, it should apply:
- Repetitive sentence structures
- Simple vocabulary
- Present continuous tense
- Character-focused observations
- Rhythmic, almost musical prose
- Comma-separated adjective lists
"""

import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import tinker
from tinker import types
from transformers import AutoTokenizer

MODEL_PATH = "tinker://ff162b8a-6845-5375-95d5-0509db7951d2:train:0/sampler_weights/final"
MODEL_NAME = "Qwen/Qwen3-8B-Base"

# Test cases with modern scenarios
TEST_CASES = [
    # =========================================================================
    # TECHNOLOGY & MODERN LIFE
    # =========================================================================
    {
        "category": "Technology",
        "name": "Scrolling Social Media",
        "system": "You are an expert creative writer capable of emulating specific literary styles.",
        "user": "Write in Gertrude Stein's style about a young woman scrolling through Instagram late at night, feeling lonely.",
    },
    {
        "category": "Technology",
        "name": "Working from Home",
        "system": "You are a literary writer with deep knowledge of early 20th century American modernist prose.",
        "user": "In Gertrude Stein's voice, describe a software engineer working from home during a video call.",
    },
    {
        "category": "Technology",
        "name": "Uber Driver",
        "system": "You write in the style of Gertrude Stein, using repetition, simple vocabulary, and rhythmic prose.",
        "user": "Write about an Uber driver in New York City who is kind but tired, in Gertrude Stein's style.",
    },
    
    # =========================================================================
    # MODERN RELATIONSHIPS
    # =========================================================================
    {
        "category": "Modern Relationships",
        "name": "Dating App",
        "system": "You are an expert creative writer capable of emulating specific literary styles.",
        "user": "Write like Gertrude Stein: A woman swipes through a dating app, hoping to find connection but feeling hollow.",
    },
    {
        "category": "Modern Relationships",
        "name": "Long Distance",
        "system": "You are a creative writer skilled at emulating distinctive authorial voices.",
        "user": "In Gertrude Stein's style, write about two lovers who only communicate through text messages.",
    },
    
    # =========================================================================
    # MODERN WORK
    # =========================================================================
    {
        "category": "Modern Work",
        "name": "Barista",
        "system": "You are Gertrude Stein. Write as she would, with her characteristic stream-of-consciousness style.",
        "user": "Describe a barista at a busy Starbucks who takes pride in her latte art.",
    },
    {
        "category": "Modern Work",
        "name": "Amazon Warehouse",
        "system": "You are a literary writer with deep knowledge of early 20th century American modernist prose.",
        "user": "Write in Gertrude Stein's style about a worker in an Amazon warehouse who dreams of something more.",
    },
    
    # =========================================================================
    # MODERN SETTINGS
    # =========================================================================
    {
        "category": "Modern Settings",
        "name": "Airport",
        "system": "You are an expert creative writer capable of emulating specific literary styles.",
        "user": "Write like Gertrude Stein about a woman waiting alone at an airport gate, watching strangers.",
    },
    {
        "category": "Modern Settings",
        "name": "Gym",
        "system": "You write in the style of Gertrude Stein, using repetition, simple vocabulary, and rhythmic prose.",
        "user": "Describe a middle-aged man at a gym, trying to get healthy after a heart scare. Write in Gertrude Stein's style.",
    },
    
    # =========================================================================
    # CONTEMPORARY ISSUES
    # =========================================================================
    {
        "category": "Contemporary Issues",
        "name": "Climate Anxiety",
        "system": "You are a creative writer skilled at emulating distinctive authorial voices.",
        "user": "In Gertrude Stein's voice, write about a young person feeling anxious about climate change.",
    },
    {
        "category": "Contemporary Issues",
        "name": "Therapy Session",
        "system": "You are Gertrude Stein. Write as she would, with her characteristic stream-of-consciousness style.",
        "user": "Write about someone's first therapy session, describing their nervousness and hope.",
    },
]


async def run_tests():
    print("=" * 80)
    print("  🧪 STYLE TRANSFER TEST: Modern Scenarios in Gertrude Stein's Voice")
    print("=" * 80)
    print(f"\n  Testing if model learned STYLE vs just memorizing content")
    print(f"  Using {len(TEST_CASES)} modern scenarios that couldn't exist in 1909")
    print("=" * 80 + "\n")
    
    # Load tokenizer and client
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    print("Connecting to Tinker...")
    service_client = tinker.ServiceClient()
    sampling_client = service_client.create_sampling_client(model_path=MODEL_PATH)
    print("Ready!\n")
    
    sampling_params = types.SamplingParams(
        max_tokens=350,
        temperature=0.7,
        top_p=0.9,
        stop=["<|im_end|>", "<|endoftext|>"]
    )
    
    results = []
    current_category = None
    
    for i, test in enumerate(TEST_CASES, 1):
        # Category header
        if test["category"] != current_category:
            current_category = test["category"]
            print("\n" + "=" * 80)
            print(f"  📂 {current_category.upper()}")
            print("=" * 80)
        
        print(f"\n{'─' * 80}")
        print(f"  Test {i}/{len(TEST_CASES)}: {test['name']}")
        print(f"{'─' * 80}")
        print(f"\n  💬 Prompt: {test['user'][:70]}...")
        print(f"  🎭 System: {test['system'][:50]}...")
        
        # Build prompt
        prompt_text = f"""<|im_start|>system
{test['system']}<|im_end|>
<|im_start|>user
{test['user']}<|im_end|>
<|im_start|>assistant
"""
        
        prompt_tokens = tokenizer.encode(prompt_text)
        model_input = types.ModelInput.from_ints(prompt_tokens)
        
        print(f"\n  ⏳ Generating...", end=" ", flush=True)
        
        try:
            result = await sampling_client.sample_async(
                prompt=model_input,
                sampling_params=sampling_params,
                num_samples=1
            )
            
            response_text = tokenizer.decode(result.sequences[0].tokens)
            response_text = response_text.split("<|im_end|>")[0].strip()
            
            print("Done!")
            print(f"\n  📝 OUTPUT:")
            print("  " + "─" * 76)
            
            # Format output with indentation
            lines = response_text.split('\n')
            for line in lines:
                # Word wrap at 74 chars
                while len(line) > 74:
                    print(f"  {line[:74]}")
                    line = line[74:]
                print(f"  {line}")
            
            print("  " + "─" * 76)
            
            # Store result
            results.append({
                "category": test["category"],
                "name": test["name"],
                "system": test["system"],
                "user": test["user"],
                "output": response_text
            })
            
        except Exception as e:
            print(f"Error: {e}")
            results.append({
                "category": test["category"],
                "name": test["name"],
                "error": str(e)
            })
    
    # Save results
    output_file = f"style_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\n📁 Results saved to: {output_file}")
    
    # Analysis
    print("\n" + "=" * 80)
    print("  📊 STYLE ANALYSIS")
    print("=" * 80)
    
    print("""
  GERTRUDE STEIN'S KEY STYLE MARKERS:
  
  ✓ Repetition - Same phrases/structures repeated ("She was a good woman. 
    She was always a good woman.")
    
  ✓ Simple Vocabulary - Common words, no ornate language
  
  ✓ Present Continuous - "She was always doing", "He was thinking"
  
  ✓ Comma-Separated Adjectives - "a dark, sweet, little, pretty girl"
  
  ✓ Character Focus - Deep psychological observation of ordinary people
  
  ✓ Rhythmic Prose - Almost musical, repetitive cadence
  
  ✓ Declarative Sentences - Simple subject-verb-object structures
  
  LOOK FOR THESE PATTERNS IN THE OUTPUTS ABOVE!
  
  If the model applies these patterns to MODERN scenarios (tech, social media),
  it proves the model learned the STYLE, not just memorized the content.
    """)
    
    print("=" * 80)
    print("  🎯 VERDICT CHECKLIST")
    print("=" * 80)
    print("""
  Answer these questions based on the outputs:
  
  [ ] Does the model use repetitive sentence structures?
  [ ] Is the vocabulary simple (not technical/modern jargon)?
  [ ] Are there comma-separated adjective chains?
  [ ] Does it focus on character psychology over plot?
  [ ] Is there a rhythmic, almost hypnotic quality?
  [ ] Does it avoid mentioning specific modern brand names?
      (e.g., "the picture machine" instead of "iPhone")
  [ ] Are the sentences mostly simple declaratives?
  
  If YES to most: ✅ Model learned STYLE
  If NO to most:  ❌ Model is parroting/memorizing
    """)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_tests())

