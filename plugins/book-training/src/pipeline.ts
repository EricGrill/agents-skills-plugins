/**
 * Book SFT Pipeline v2 - Diverse Prompts Edition
 * 
 * Improvements:
 * - Smaller chunks (200-400 words) for more examples
 * - Diverse prompt templates for natural chat model training
 * - Multiple prompt variants per chunk
 */

import { generateText } from "ai";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { config as dotenvConfig } from "dotenv";
import * as fs from "fs";
import * as path from "path";
import { EPub } from "epub2";
import { parseDocument } from "htmlparser2";
import { textContent, getElementsByTagName } from "domutils";

dotenvConfig();

// =============================================================================
// Configuration
// =============================================================================

interface PipelineConfig {
  sourcePath: string;
  authorName: string;
  outputPath: string;
  minWords: number;
  maxWords: number;
  testSetSize: number;
  model: string;
  batchSize: number;
  checkpointDir: string;
}

const CONFIG: PipelineConfig = {
  sourcePath: path.resolve(process.cwd(), "gertrude-stein_three-lives.epub"),
  authorName: "Gertrude Stein",
  outputPath: path.resolve(process.cwd(), "three-lives-sft-dataset.jsonl"),
  minWords: 150,  // Smaller chunks
  maxWords: 400,  // Smaller max
  testSetSize: 50,
  model: "gemini-2.0-flash-lite",
  batchSize: 15,
  checkpointDir: path.resolve(process.cwd(), "checkpoints"),
};

// =============================================================================
// Diverse Prompt Templates
// =============================================================================

const SYSTEM_PROMPTS = [
  "You are a literary writer with deep knowledge of early 20th century American modernist prose.",
  "You are a creative writer skilled at emulating distinctive authorial voices.",
  "You are an author capable of writing in various literary styles with authentic voice.",
  "You write prose that captures the essence of modernist literature.",
  "You are a talented writer who can channel the voice of classic American authors.",
];

const PROMPT_TEMPLATES = [
  // Direct style requests
  (author: string, desc: string) => `Write a passage in the style of ${author}. ${desc}`,
  (author: string, desc: string) => `Channel ${author}'s voice to write about: ${desc}`,
  (author: string, desc: string) => `Emulate ${author}'s distinctive prose style. Scene: ${desc}`,
  
  // Creative writing requests
  (author: string, desc: string) => `Write this scene as ${author} would have written it: ${desc}`,
  (author: string, desc: string) => `Capture the rhythm and cadence of ${author} in this passage: ${desc}`,
  (author: string, desc: string) => `Using ${author}'s repetitive, stream-of-consciousness technique, write: ${desc}`,
  
  // More natural chat requests
  (author: string, desc: string) => `I need prose that sounds like ${author}. Here's what should happen: ${desc}`,
  (author: string, desc: string) => `Write something that could have come from ${author}'s pen. The scene involves: ${desc}`,
  (author: string, desc: string) => `Can you write in ${author}'s style? I want a passage where ${desc}`,
  
  // Specific technique requests
  (author: string, desc: string) => `Using simple, repetitive sentences like ${author}, describe: ${desc}`,
  (author: string, desc: string) => `Write with ${author}'s characteristic present-tense narration: ${desc}`,
  (author: string, desc: string) => `Employ ${author}'s technique of gradual revelation through repetition: ${desc}`,
  
  // Contextual requests
  (author: string, desc: string) => `This is for a literary exercise. Write like ${author}: ${desc}`,
  (author: string, desc: string) => `For my creative writing class, I need ${author}'s style applied to: ${desc}`,
  (author: string, desc: string) => `Help me understand ${author}'s style by writing a passage about: ${desc}`,
];

function getRandomPrompt(author: string, description: string): { system: string; user: string } {
  const systemPrompt = SYSTEM_PROMPTS[Math.floor(Math.random() * SYSTEM_PROMPTS.length)];
  const template = PROMPT_TEMPLATES[Math.floor(Math.random() * PROMPT_TEMPLATES.length)];
  return {
    system: systemPrompt,
    user: template(author, description),
  };
}

// =============================================================================
// Data Structures
// =============================================================================

interface Chunk {
  id: number;
  text: string;
  wordCount: number;
}

interface TrainingExample {
  messages: Array<{ role: "system" | "user" | "assistant"; content: string }>;
}

interface Checkpoint {
  phase: string;
  rawText?: string;
  chunks?: Chunk[];
  instructions: Record<number, string>;
}

// =============================================================================
// Gemini Client
// =============================================================================

const google = createGoogleGenerativeAI({
  apiKey: process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY,
});

// =============================================================================
// Utilities
// =============================================================================

function log(tag: string, msg: string): void {
  const ts = new Date().toISOString().split("T")[1].slice(0, 8);
  console.log(`[${ts}] [${tag}] ${msg}`);
}

function ensureDir(dir: string): void {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function saveCheckpoint(cp: Checkpoint): void {
  ensureDir(CONFIG.checkpointDir);
  fs.writeFileSync(
    path.join(CONFIG.checkpointDir, "state.json"),
    JSON.stringify(cp, null, 2)
  );
}

function loadCheckpoint(): Checkpoint | null {
  const p = path.join(CONFIG.checkpointDir, "state.json");
  if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, "utf-8"));
  return null;
}

// =============================================================================
// Phase 1: Extraction
// =============================================================================

async function extractEpub(epubPath: string): Promise<string> {
  log("EXTRACT", `Reading ${epubPath}`);

  return new Promise((resolve, reject) => {
    const epub = new EPub(epubPath);
    epub.on("error", reject);
    epub.on("end", async () => {
      const texts: string[] = [];

      for (const ch of epub.flow) {
        if (!ch.id) continue;
        try {
          const html = await new Promise<string>((res, rej) => {
            epub.getChapter(ch.id!, (e: Error | null, t: string) => (e ? rej(e) : res(t)));
          });

          const doc = parseDocument(html);
          const paras = getElementsByTagName("p", doc);
          const text = paras.length > 0
            ? paras.map((p) => textContent(p).trim()).filter(Boolean).join("\n\n")
            : textContent(doc);

          if (text.length > 100) texts.push(cleanText(text));
        } catch {
          // skip
        }
      }

      const full = texts.join("\n\n");
      log("EXTRACT", `Done: ${full.split(/\s+/).length} words`);
      resolve(full);
    });
    epub.parse();
  });
}

function cleanText(text: string): string {
  return text
    .replace(/\r\n?/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]+/g, " ")
    .trim();
}

// =============================================================================
// Phase 2: Segmentation - Smaller chunks with overlap
// =============================================================================

function segment(text: string): Chunk[] {
  log("SEGMENT", "Starting fine-grained segmentation");

  const paragraphs = text.split("\n\n").filter((p) => p.trim().length > 20);
  const chunks: Chunk[] = [];
  let buffer: string[] = [];
  let bufferWords = 0;

  for (const para of paragraphs) {
    const words = para.split(/\s+/).length;

    // If adding this paragraph exceeds max and we have enough, finalize
    if (bufferWords + words > CONFIG.maxWords && bufferWords >= CONFIG.minWords) {
      chunks.push({
        id: chunks.length,
        text: buffer.join("\n\n"),
        wordCount: bufferWords,
      });
      
      // Keep last paragraph for overlap (context continuity)
      if (buffer.length > 1) {
        const lastPara = buffer[buffer.length - 1];
        buffer = [lastPara, para];
        bufferWords = lastPara.split(/\s+/).length + words;
      } else {
        buffer = [para];
        bufferWords = words;
      }
    } else {
      buffer.push(para);
      bufferWords += words;
    }
  }

  // Final chunk
  if (buffer.length > 0 && bufferWords >= 80) {
    chunks.push({
      id: chunks.length,
      text: buffer.join("\n\n"),
      wordCount: bufferWords,
    });
  }

  log("SEGMENT", `Created ${chunks.length} chunks (${CONFIG.minWords}-${CONFIG.maxWords} words, with overlap)`);
  
  const sizes = chunks.map(c => c.wordCount);
  log("SEGMENT", `Word range: ${Math.min(...sizes)}-${Math.max(...sizes)}, avg: ${Math.round(sizes.reduce((a,b)=>a+b,0)/sizes.length)}`);
  
  return chunks;
}

// =============================================================================
// Phase 3: Instruction Generation
// =============================================================================

async function generateInstruction(chunk: Chunk): Promise<string> {
  const prompt = `Write a brief, natural description of this scene (2-3 sentences). Focus on what's happening, who's involved, and the emotional tone. Be specific but don't quote the text.

Text:
${chunk.text.slice(0, 2000)}`;

  const { text } = await generateText({
    model: google(CONFIG.model),
    prompt,
    maxTokens: 200,
  });

  // Clean up the response - remove "This excerpt..." type prefixes
  let cleaned = text.trim();
  cleaned = cleaned.replace(/^(This (excerpt|passage|scene|text|narrative)|In this (excerpt|passage|scene|narrative))[,:]?\s*/i, "");
  cleaned = cleaned.replace(/^(The (excerpt|passage|scene|narrative))[,:]?\s*/i, "");
  
  return cleaned;
}

async function generateAllInstructions(
  chunks: Chunk[],
  existing: Record<number, string>
): Promise<Record<number, string>> {
  const results = { ...existing };
  const pending = chunks.filter((c) => !(c.id in results));

  log("INSTRUCT", `Pending: ${pending.length}, Done: ${Object.keys(results).length}`);

  for (let i = 0; i < pending.length; i += CONFIG.batchSize) {
    const batch = pending.slice(i, i + CONFIG.batchSize);
    const batchNum = Math.floor(i / CONFIG.batchSize) + 1;
    const totalBatches = Math.ceil(pending.length / CONFIG.batchSize);

    log("INSTRUCT", `Batch ${batchNum}/${totalBatches} (${batch.length} items)`);

    const start = Date.now();

    const promises = batch.map(async (chunk) => {
      try {
        const instr = await generateInstruction(chunk);
        return { id: chunk.id, instr, ok: true };
      } catch (e) {
        log("INSTRUCT", `Chunk ${chunk.id} failed: ${e}`);
        return { id: chunk.id, instr: "", ok: false };
      }
    });

    const batchResults = await Promise.all(promises);

    for (const r of batchResults) {
      if (r.ok && r.instr) {
        results[r.id] = r.instr;
        console.log(`  [${r.id}] ${r.instr.slice(0, 70)}...`);
      }
    }

    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    const progress = Object.keys(results).length;
    log("INSTRUCT", `Batch done in ${elapsed}s. Progress: ${progress}/${chunks.length}`);

    saveCheckpoint({ phase: "instructions", chunks, instructions: results });
  }

  return results;
}

// =============================================================================
// Phase 4: Dataset Construction - Multiple variants per chunk
// =============================================================================

function buildDataset(chunks: Chunk[], instructions: Record<number, string>): void {
  log("DATASET", "Building diverse training examples");

  const examples: TrainingExample[] = [];
  const variantsPerChunk = 2; // Generate 2 prompt variants per chunk

  for (const chunk of chunks) {
    const instr = instructions[chunk.id];
    if (!instr) continue;

    // Generate multiple variants with different prompts
    for (let v = 0; v < variantsPerChunk; v++) {
      const { system, user } = getRandomPrompt(CONFIG.authorName, instr);
      
      examples.push({
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
          { role: "assistant", content: chunk.text },
        ],
      });
    }
  }

  log("DATASET", `Created ${examples.length} examples (${variantsPerChunk} variants per chunk)`);

  // Shuffle
  const shuffled = examples.sort(() => Math.random() - 0.5);
  const testSize = Math.min(CONFIG.testSetSize, Math.floor(examples.length * 0.1));
  const test = shuffled.slice(0, testSize);
  const train = shuffled.slice(testSize);

  fs.writeFileSync(CONFIG.outputPath, train.map((e) => JSON.stringify(e)).join("\n"));
  fs.writeFileSync(
    CONFIG.outputPath.replace(".jsonl", "_test.jsonl"),
    test.map((e) => JSON.stringify(e)).join("\n")
  );

  log("DATASET", `Train: ${train.length}, Test: ${test.length}`);
  log("DATASET", `Files: ${CONFIG.outputPath}`);
  
  // Show prompt diversity
  console.log("\n=== Sample Prompt Diversity ===");
  for (let i = 0; i < Math.min(5, train.length); i++) {
    console.log(`[${i}] ${train[i].messages[1].content.slice(0, 80)}...`);
  }
}

// =============================================================================
// Main
// =============================================================================

async function main() {
  console.log("\n" + "=".repeat(60));
  console.log("Book SFT Pipeline v2 - Diverse Prompts");
  console.log("=".repeat(60));
  console.log(`Book: ${CONFIG.sourcePath}`);
  console.log(`Model: ${CONFIG.model}`);
  console.log(`Chunk size: ${CONFIG.minWords}-${CONFIG.maxWords} words`);
  console.log("=".repeat(60) + "\n");

  const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error("ERROR: Set GEMINI_API_KEY or GOOGLE_API_KEY in .env");
    process.exit(1);
  }

  const start = Date.now();

  let cp = loadCheckpoint() || { phase: "start", instructions: {} };

  // Phase 1: Extract
  if (!cp.rawText) {
    cp.rawText = await extractEpub(CONFIG.sourcePath);
    cp.phase = "extracted";
    saveCheckpoint(cp);
  } else {
    log("EXTRACT", "Using cached extraction");
  }

  // Phase 2: Segment
  if (!cp.chunks) {
    cp.chunks = segment(cp.rawText);
    cp.phase = "segmented";
    saveCheckpoint(cp);
  } else {
    log("SEGMENT", `Using cached ${cp.chunks.length} chunks`);
  }

  // Phase 3: Instructions
  log("INSTRUCT", "Generating scene descriptions...");
  cp.instructions = await generateAllInstructions(cp.chunks, cp.instructions || {});
  cp.phase = "instructed";
  saveCheckpoint(cp);

  // Phase 4: Build dataset
  buildDataset(cp.chunks, cp.instructions);

  const elapsed = ((Date.now() - start) / 1000).toFixed(1);
  console.log("\n" + "=".repeat(60));
  console.log(`COMPLETE in ${elapsed}s`);
  console.log("=".repeat(60) + "\n");
}

main().catch((e) => {
  console.error("\nFATAL:", e.message);
  process.exit(1);
});
