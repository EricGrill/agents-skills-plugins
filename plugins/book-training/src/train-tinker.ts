/**
 * Tinker SFT Training Pipeline
 * 
 * Trains a model on the Gertrude Stein style dataset using Tinker's API.
 * Model: Qwen/Qwen3-8B-Base (Base model, better for style transfer)
 */

import { config as dotenvConfig } from "dotenv";
import * as fs from "fs";
import * as path from "path";

dotenvConfig();

// =============================================================================
// Configuration
// =============================================================================

interface TrainingConfig {
  modelName: string;
  datasetPath: string;
  testDatasetPath: string;
  loraRank: number;
  learningRate: number;
  batchSize: number;
  epochs: number;
  evalEvery: number;
  saveEvery: number;
  logPath: string;
}

const CONFIG: TrainingConfig = {
  modelName: "Qwen/Qwen3-8B-Base",
  datasetPath: path.resolve(process.cwd(), "three-lives-sft-dataset.jsonl"),
  testDatasetPath: path.resolve(process.cwd(), "three-lives-sft-dataset_test.jsonl"),
  loraRank: 32,
  learningRate: 5e-4,  // LoRA needs higher LR than full fine-tuning
  batchSize: 4,        // Small batch for style learning
  epochs: 3,
  evalEvery: 20,
  saveEvery: 50,
  logPath: path.resolve(process.cwd(), "training-logs"),
};

// =============================================================================
// Data Types
// =============================================================================

interface Message {
  role: "system" | "user" | "assistant";
  content: string;
}

interface TrainingExample {
  messages: Message[];
}

interface ProcessedExample {
  inputTokens: number[];
  targetTokens: number[];
  weights: number[];
}

// =============================================================================
// Dataset Loading
// =============================================================================

function loadDataset(filepath: string): TrainingExample[] {
  const content = fs.readFileSync(filepath, "utf-8");
  const lines = content.trim().split("\n");
  return lines.map((line) => JSON.parse(line) as TrainingExample);
}

// =============================================================================
// Qwen3 Chat Template Renderer
// =============================================================================

/**
 * Renders messages to Qwen3 chat format with proper token weights.
 * 
 * Format:
 * <|im_start|>system\n{content}<|im_end|>\n
 * <|im_start|>user\n{content}<|im_end|>\n
 * <|im_start|>assistant\n{content}<|im_end|>\n
 * 
 * For SFT: weight=0 for system+user, weight=1 for assistant completion
 */
class Qwen3Renderer {
  private specialTokens = {
    imStart: "<|im_start|>",
    imEnd: "<|im_end|>",
  };

  renderForTraining(messages: Message[]): { prompt: string; completion: string } {
    let prompt = "";
    let completion = "";

    for (let i = 0; i < messages.length; i++) {
      const msg = messages[i];
      const formatted = `${this.specialTokens.imStart}${msg.role}\n${msg.content}${this.specialTokens.imEnd}\n`;

      if (i === messages.length - 1 && msg.role === "assistant") {
        // Last assistant message is the completion (weight=1)
        prompt += `${this.specialTokens.imStart}${msg.role}\n`;
        completion = `${msg.content}${this.specialTokens.imEnd}\n`;
      } else {
        // All other messages are prompt (weight=0)
        prompt += formatted;
      }
    }

    return { prompt, completion };
  }

  renderFullText(messages: Message[]): string {
    return messages
      .map((msg) => `${this.specialTokens.imStart}${msg.role}\n${msg.content}${this.specialTokens.imEnd}\n`)
      .join("");
  }
}

// =============================================================================
// Training Script Generator (Python)
// =============================================================================

function generateTinkerTrainingScript(config: TrainingConfig): string {
  return `#!/usr/bin/env python3
"""
Tinker SFT Training Script - Gertrude Stein Style Transfer

Generated training script for fine-tuning ${config.modelName} on the
Three Lives SFT dataset using Tinker's distributed training API.

Usage:
    pip install tinker tinker-cookbook
    export TINKER_API_KEY=<your-key>
    python train_tinker.py
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import tinker
from tinker import types

# Try to import tinker_cookbook for renderer utilities
try:
    from tinker_cookbook import renderers, tokenizer_utils
    from tinker_cookbook.hyperparam_utils import get_lr, get_lora_lr_over_full_finetune_lr
    HAS_COOKBOOK = True
except ImportError:
    HAS_COOKBOOK = False
    print("Warning: tinker_cookbook not installed. Using manual tokenization.")

# =============================================================================
# Configuration
# =============================================================================

CONFIG = {
    "model_name": "${config.modelName}",
    "dataset_path": "${config.datasetPath}",
    "test_dataset_path": "${config.testDatasetPath}",
    "lora_rank": ${config.loraRank},
    "learning_rate": ${config.learningRate},
    "batch_size": ${config.batchSize},
    "epochs": ${config.epochs},
    "eval_every": ${config.evalEvery},
    "save_every": ${config.saveEvery},
    "log_path": "${config.logPath}",
}

# =============================================================================
# Data Loading and Processing
# =============================================================================

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL dataset."""
    examples = []
    with open(filepath, "r") as f:
        for line in f:
            examples.append(json.loads(line))
    print(f"Loaded {len(examples)} examples from {filepath}")
    return examples


def process_example_for_tinker(
    example: Dict[str, Any],
    tokenizer,
    renderer
) -> types.Datum:
    """
    Convert a training example to Tinker Datum format.
    
    Uses the renderer to properly assign weights:
    - weight=0 for prompt tokens (system + user)
    - weight=1 for completion tokens (assistant response)
    """
    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in example["messages"]
    ]
    
    # Use renderer to build supervised example with proper weights
    model_input, weights = renderer.build_supervised_example(messages)
    
    # Get token sequences
    input_tokens = model_input.to_ints()
    target_tokens = input_tokens[1:]  # Shift for next-token prediction
    input_tokens_trimmed = input_tokens[:-1]
    weights_trimmed = weights[1:]  # Align weights with targets
    
    return types.Datum(
        model_input=types.ModelInput.from_ints(tokens=input_tokens_trimmed),
        loss_fn_inputs={
            "target_tokens": target_tokens,
            "weights": weights_trimmed,
        }
    )


def process_example_manual(
    example: Dict[str, Any],
    tokenizer
) -> types.Datum:
    """
    Manual processing without tinker_cookbook.
    Implements Qwen3 chat template directly.
    """
    messages = example["messages"]
    
    # Build full text with Qwen3 format
    prompt_text = ""
    completion_text = ""
    
    for i, msg in enumerate(messages):
        role = msg["role"]
        content = msg["content"]
        
        if i == len(messages) - 1 and role == "assistant":
            # Last assistant message is completion
            prompt_text += f"<|im_start|>{role}\\n"
            completion_text = f"{content}<|im_end|>\\n"
        else:
            prompt_text += f"<|im_start|>{role}\\n{content}<|im_end|>\\n"
    
    # Tokenize
    prompt_tokens = tokenizer.encode(prompt_text, add_special_tokens=True)
    completion_tokens = tokenizer.encode(completion_text, add_special_tokens=False)
    
    # Build weights: 0 for prompt, 1 for completion
    weights = [0.0] * len(prompt_tokens) + [1.0] * len(completion_tokens)
    
    # Combine tokens
    all_tokens = prompt_tokens + completion_tokens
    
    # Shift for next-token prediction
    input_tokens = all_tokens[:-1]
    target_tokens = all_tokens[1:]
    weights = weights[1:]
    
    return types.Datum(
        model_input=types.ModelInput.from_ints(tokens=input_tokens),
        loss_fn_inputs={
            "target_tokens": target_tokens,
            "weights": weights,
        }
    )


# =============================================================================
# Training Loop
# =============================================================================

async def train():
    """Main training loop using Tinker API."""
    
    print("=" * 60)
    print("Tinker SFT Training - Gertrude Stein Style Transfer")
    print("=" * 60)
    print(f"Model: {CONFIG['model_name']}")
    print(f"LoRA Rank: {CONFIG['lora_rank']}")
    print(f"Learning Rate: {CONFIG['learning_rate']}")
    print(f"Batch Size: {CONFIG['batch_size']}")
    print("=" * 60)
    
    # Create log directory
    log_path = Path(CONFIG["log_path"])
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Load datasets
    train_data = load_jsonl(CONFIG["dataset_path"])
    test_data = load_jsonl(CONFIG["test_dataset_path"])
    
    # Initialize Tinker
    print("\\nInitializing Tinker service client...")
    service_client = tinker.ServiceClient()
    
    # Create training client with LoRA
    print(f"Creating LoRA training client (rank={CONFIG['lora_rank']})...")
    training_client = await service_client.create_lora_training_client_async(
        base_model=CONFIG["model_name"],
        rank=CONFIG["lora_rank"],
    )
    
    # Get tokenizer
    tokenizer = training_client.get_tokenizer()
    print(f"Tokenizer vocabulary size: {len(tokenizer)}")
    
    # Get renderer if available
    if HAS_COOKBOOK:
        renderer = renderers.get_renderer("qwen3", tokenizer)
        process_fn = lambda ex: process_example_for_tinker(ex, tokenizer, renderer)
        print("Using tinker_cookbook renderer")
    else:
        process_fn = lambda ex: process_example_manual(ex, tokenizer)
        print("Using manual tokenization")
    
    # Process all examples
    print("\\nProcessing training examples...")
    train_datums = [process_fn(ex) for ex in train_data]
    test_datums = [process_fn(ex) for ex in test_data]
    
    print(f"Training examples: {len(train_datums)}")
    print(f"Test examples: {len(test_datums)}")
    
    # Calculate total steps
    steps_per_epoch = len(train_datums) // CONFIG["batch_size"]
    total_steps = steps_per_epoch * CONFIG["epochs"]
    print(f"Steps per epoch: {steps_per_epoch}")
    print(f"Total steps: {total_steps}")
    
    # Training metrics log
    metrics_log = []
    
    # Adam optimizer params
    adam_params = types.AdamParams(
        learning_rate=CONFIG["learning_rate"],
        beta1=0.9,
        beta2=0.95,
    )
    
    print("\\n" + "=" * 60)
    print("Starting training...")
    print("=" * 60 + "\\n")
    
    step = 0
    for epoch in range(CONFIG["epochs"]):
        print(f"\\n--- Epoch {epoch + 1}/{CONFIG['epochs']} ---")
        
        # Shuffle training data each epoch
        import random
        shuffled_indices = list(range(len(train_datums)))
        random.shuffle(shuffled_indices)
        
        for batch_start in range(0, len(train_datums), CONFIG["batch_size"]):
            batch_indices = shuffled_indices[batch_start:batch_start + CONFIG["batch_size"]]
            batch = [train_datums[i] for i in batch_indices]
            
            if len(batch) < CONFIG["batch_size"]:
                continue  # Skip incomplete batches
            
            step += 1
            
            # Forward-backward pass (submit both requests before waiting)
            fwd_bwd_future = await training_client.forward_backward_async(
                batch, 
                loss_fn="cross_entropy"
            )
            
            # Optimizer step
            optim_future = await training_client.optim_step_async(adam_params)
            
            # Wait for results
            fwd_bwd_result = await fwd_bwd_future
            optim_result = await optim_future
            
            # Extract loss
            train_loss = fwd_bwd_result.metrics.get("loss:sum", 0)
            
            # Log progress
            if step % 5 == 0:
                print(f"Step {step}/{total_steps} | Loss: {train_loss:.4f}")
            
            # Evaluation
            if step % CONFIG["eval_every"] == 0:
                print(f"\\n[Eval] Step {step}")
                
                # Compute test loss on a sample
                test_batch = test_datums[:min(10, len(test_datums))]
                test_fwd = await training_client.forward_async(test_batch)
                test_result = await test_fwd
                test_loss = test_result.metrics.get("loss:sum", 0)
                
                print(f"  Train Loss: {train_loss:.4f}")
                print(f"  Test Loss: {test_loss:.4f}")
                
                metrics_log.append({
                    "step": step,
                    "epoch": epoch + 1,
                    "train_loss": train_loss,
                    "test_loss": test_loss,
                })
            
            # Save checkpoint
            if step % CONFIG["save_every"] == 0:
                checkpoint_name = f"step_{step:05d}"
                save_result = await training_client.save_weights_for_sampler_async(
                    name=checkpoint_name
                )
                ckpt_result = await save_result
                print(f"\\n[Checkpoint] Saved: {ckpt_result.path}")
    
    # Final save
    print("\\n" + "=" * 60)
    print("Training complete. Saving final weights...")
    final_save = await training_client.save_weights_for_sampler_async(name="final")
    final_result = await final_save
    print(f"Final checkpoint: {final_result.path}")
    
    # Also save full state for resuming
    state_save = await training_client.save_state_async(name="final_state")
    state_result = await state_save
    print(f"Full state checkpoint: {state_result.path}")
    
    # Save metrics
    metrics_path = log_path / "metrics.jsonl"
    with open(metrics_path, "w") as f:
        for m in metrics_log:
            f.write(json.dumps(m) + "\\n")
    print(f"Metrics saved to: {metrics_path}")
    
    # Save config
    config_path = log_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(CONFIG, f, indent=2)
    
    print("\\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Final checkpoint path: {final_result.path}")
    print(f"Use this path with Tinker's sampling client to test the model.")
    
    return final_result.path


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("TINKER_API_KEY"):
        print("ERROR: TINKER_API_KEY environment variable not set")
        print("Get your API key from: https://tinker-console.thinkingmachines.ai")
        exit(1)
    
    # Run training
    final_path = asyncio.run(train())
    print(f"\\nTo sample from your model:")
    print(f"  model_path = '{final_path}'")
`;
}

// =============================================================================
// Main
// =============================================================================

async function main() {
  console.log("=".repeat(60));
  console.log("Generating Tinker Training Pipeline");
  console.log("=".repeat(60));

  // Verify dataset exists
  if (!fs.existsSync(CONFIG.datasetPath)) {
    console.error(`ERROR: Dataset not found at ${CONFIG.datasetPath}`);
    console.error("Run the SFT pipeline first to generate the dataset.");
    process.exit(1);
  }

  // Count examples
  const trainLines = fs.readFileSync(CONFIG.datasetPath, "utf-8").trim().split("\n").length;
  const testLines = fs.readFileSync(CONFIG.testDatasetPath, "utf-8").trim().split("\n").length;

  console.log(`\nDataset:`);
  console.log(`  Training: ${trainLines} examples`);
  console.log(`  Test: ${testLines} examples`);

  console.log(`\nModel: ${CONFIG.modelName}`);
  console.log(`LoRA Rank: ${CONFIG.loraRank}`);
  console.log(`Learning Rate: ${CONFIG.learningRate}`);
  console.log(`Batch Size: ${CONFIG.batchSize}`);
  console.log(`Epochs: ${CONFIG.epochs}`);

  // Generate the Python training script
  const script = generateTinkerTrainingScript(CONFIG);
  const scriptPath = path.resolve(process.cwd(), "train_tinker.py");
  fs.writeFileSync(scriptPath, script);

  console.log(`\n${"=".repeat(60)}`);
  console.log("Generated: train_tinker.py");
  console.log("=".repeat(60));
  console.log(`
To run training:

1. Install Tinker SDK:
   pip install tinker tinker-cookbook

2. Set your API key:
   export TINKER_API_KEY=<your-key-from-console>

3. Run training:
   python train_tinker.py

The script will:
- Load the SFT dataset (${trainLines} training examples)
- Create a LoRA training client for ${CONFIG.modelName}
- Train for ${CONFIG.epochs} epochs with batch size ${CONFIG.batchSize}
- Save checkpoints every ${CONFIG.saveEvery} steps
- Output final model path for sampling
`);

  // Create log directory
  fs.mkdirSync(CONFIG.logPath, { recursive: true });
  console.log(`Log directory: ${CONFIG.logPath}`);
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});

