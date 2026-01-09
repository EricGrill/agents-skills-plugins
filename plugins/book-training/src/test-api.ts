/**
 * Quick Gemini Flash API test
 */

import { generateText } from "ai";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { config as dotenvConfig } from "dotenv";

dotenvConfig();

async function test() {
  console.log("Testing Gemini Flash API...\n");

  const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error("ERROR: Set GEMINI_API_KEY or GOOGLE_API_KEY");
    process.exit(1);
  }
  console.log(`API Key: ${apiKey.slice(0, 10)}...`);

  const google = createGoogleGenerativeAI({ apiKey });

  const prompt = `Describe this excerpt in 2 sentences:
Anna was a hard-working servant who found peace in routine but felt deep loneliness.`;

  const start = Date.now();

  try {
    const { text, usage } = await generateText({
      model: google("gemini-2.0-flash"),
      prompt,
      maxTokens: 100,
    });

    const elapsed = Date.now() - start;
    console.log(`\nSUCCESS in ${elapsed}ms`);
    console.log(`Response: ${text}`);
    console.log(`Usage: ${JSON.stringify(usage)}`);
    console.log(`\nEstimated time for 150 chunks: ${((elapsed * 150) / 1000 / 60).toFixed(1)} minutes (sequential)`);
    console.log(`With batch=10 parallel: ${((elapsed * 15) / 1000 / 60).toFixed(1)} minutes`);
  } catch (e) {
    console.error(`\nFAILED: ${e}`);
  }
}

test();
