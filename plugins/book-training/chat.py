#!/usr/bin/env python3
"""
Interactive Chat with Gertrude Stein Style Model

Usage:
    python chat.py                          # Use default system prompt
    python chat.py --system "Your prompt"   # Custom system prompt
    python chat.py --temp 0.9               # Adjust temperature
    python chat.py --max-tokens 500         # Adjust max tokens
"""

import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

import tinker
from tinker import types
from transformers import AutoTokenizer

# Your trained model
MODEL_PATH = "tinker://ff162b8a-6845-5375-95d5-0509db7951d2:train:0/sampler_weights/final"
MODEL_NAME = "Qwen/Qwen3-8B-Base"

# Default system prompts to choose from
SYSTEM_PROMPTS = {
    "1": "You are an expert creative writer capable of emulating specific literary styles.",
    "2": "You are a literary writer with deep knowledge of early 20th century American modernist prose.",
    "3": "You are a creative writer skilled at emulating distinctive authorial voices.",
    "4": "You write in the style of Gertrude Stein, using repetition, simple vocabulary, and rhythmic prose.",
    "5": "You are Gertrude Stein. Write as she would, with her characteristic stream-of-consciousness style.",
}


def print_banner():
    print("\n" + "=" * 70)
    print("  🖋️  GERTRUDE STEIN STYLE WRITER  🖋️")
    print("=" * 70)
    print(f"  Model: {MODEL_PATH.split('/')[-1]}")
    print("=" * 70 + "\n")


def print_help():
    print("""
Commands:
  /system <prompt>   - Change the system prompt
  /system 1-5        - Use a preset system prompt
  /presets           - Show preset system prompts
  /temp <0.0-2.0>    - Change temperature
  /tokens <n>        - Change max tokens
  /clear             - Clear conversation history
  /settings          - Show current settings
  /help              - Show this help
  /quit              - Exit
    """)


async def main():
    parser = argparse.ArgumentParser(description="Chat with Gertrude Stein style model")
    parser.add_argument("--system", "-s", type=str, default=SYSTEM_PROMPTS["1"],
                        help="System prompt to use")
    parser.add_argument("--temp", "-t", type=float, default=0.7,
                        help="Sampling temperature (default: 0.7)")
    parser.add_argument("--max-tokens", "-m", type=int, default=400,
                        help="Maximum tokens to generate (default: 400)")
    args = parser.parse_args()
    
    print_banner()
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    # Create sampling client
    print("Connecting to Tinker...")
    service_client = tinker.ServiceClient()
    sampling_client = service_client.create_sampling_client(model_path=MODEL_PATH)
    print("✅ Ready!\n")
    
    # Settings
    system_prompt = args.system
    temperature = args.temp
    max_tokens = args.max_tokens
    
    print(f"📋 System prompt: {system_prompt[:60]}...")
    print(f"🌡️  Temperature: {temperature}")
    print(f"📝 Max tokens: {max_tokens}")
    print("\nType /help for commands, or just start typing!\n")
    print("-" * 70)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith("/"):
            cmd_parts = user_input.split(maxsplit=1)
            cmd = cmd_parts[0].lower()
            arg = cmd_parts[1] if len(cmd_parts) > 1 else ""
            
            if cmd in ["/quit", "/exit", "/q"]:
                print("\nGoodbye! 👋")
                break
            
            elif cmd == "/help":
                print_help()
                continue
            
            elif cmd == "/presets":
                print("\n📋 Preset System Prompts:")
                for k, v in SYSTEM_PROMPTS.items():
                    print(f"  {k}: {v[:70]}...")
                continue
            
            elif cmd == "/system":
                if arg in SYSTEM_PROMPTS:
                    system_prompt = SYSTEM_PROMPTS[arg]
                elif arg:
                    system_prompt = arg
                else:
                    print("Usage: /system <prompt> or /system 1-5")
                    continue
                print(f"✅ System prompt updated: {system_prompt[:60]}...")
                continue
            
            elif cmd == "/temp":
                try:
                    temperature = float(arg)
                    print(f"✅ Temperature set to {temperature}")
                except ValueError:
                    print("Usage: /temp <0.0-2.0>")
                continue
            
            elif cmd == "/tokens":
                try:
                    max_tokens = int(arg)
                    print(f"✅ Max tokens set to {max_tokens}")
                except ValueError:
                    print("Usage: /tokens <number>")
                continue
            
            elif cmd == "/settings":
                print(f"\n⚙️  Current Settings:")
                print(f"   System: {system_prompt}")
                print(f"   Temperature: {temperature}")
                print(f"   Max tokens: {max_tokens}")
                continue
            
            elif cmd == "/clear":
                print("✅ Conversation cleared")
                continue
            
            else:
                print(f"Unknown command: {cmd}. Type /help for commands.")
                continue
        
        # Build the prompt
        prompt_text = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_input}<|im_end|>
<|im_start|>assistant
"""
        
        # Tokenize
        prompt_tokens = tokenizer.encode(prompt_text)
        model_input = types.ModelInput.from_ints(prompt_tokens)
        
        # Sampling params
        sampling_params = types.SamplingParams(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            stop=["<|im_end|>", "<|endoftext|>"]
        )
        
        print("\n🖋️  Gertrude Stein:", end=" ", flush=True)
        
        try:
            result = await sampling_client.sample_async(
                prompt=model_input,
                sampling_params=sampling_params,
                num_samples=1
            )
            
            response_text = tokenizer.decode(result.sequences[0].tokens)
            # Clean up any trailing artifacts
            response_text = response_text.split("<|im_end|>")[0].strip()
            
            print(response_text)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        print("-" * 70)


if __name__ == "__main__":
    asyncio.run(main())

