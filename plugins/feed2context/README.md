# Feed2Context

One‑click feed → report for LinkedIn and X. Capture a post, auto‑shape a research query, search with reasoning, and get a detailed research report in seconds.

- LinkedIn extraction: Groq Compound Mini visits the URL and returns only the post text (fallback to extension DOM capture).
- X extraction: Browser Use drives a real browser to read the post (X blocks scraping reliably).
- Query building: Kimi‑K2 compresses the goal into a single effective search query.
- Research and answer: Groq Compound searches and reasons to produce an instant research report.

<img width="436" height="482" alt="Screenshot 2025-09-08 at 10 11 36 PM" src="https://github.com/user-attachments/assets/082afb4b-89dc-48e8-b840-9a358283b4bc" />


Groq Compound: https://groq.com/blog/introducing-the-next-generation-of-compound-on-groqcloud

## Quick start

1) Create a virtual env and install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# For the X pipeline, install Browser Use as well (optional for LinkedIn):
pip install browser-use
```

2) Set environment variables

Create a `.env` file (sample – do not commit real secrets):

```
GROQ_API_KEY=sk_...
OPENAI_API_KEY=sk_...
COMPOSIO_API_KEY=sk_...
COMPOSIO_AUTH_CONFIG_ID=ac_...
COMPOSIO_EXTERNAL_USER_ID=user_123
REPORTS_EMAIL_TO=recipient@example.com
```

3) Run the API (serves both LinkedIn and X pipelines)

```bash
python app2.py
# app2 serves both ports via the same FastAPI app:
#   - X pipeline UI/API at        http://127.0.0.1:8000/
#   - LinkedIn pipeline UI/API at http://127.0.0.1:8001/
# Both show the same notebook UI and read the same saved data.
```

Open either port in the browser to see the minimal “notebook” UI which loads reports from `/reports` and renders the latest answer.

## Why Browser Use for X

X employs strong anti‑scraping measures that can break static HTTP fetches. The X pipeline uses `browser_use.Agent` with `ChatGroq` to control a real browser, load the tweet, click if needed, and extract the author + main tweet text reliably.

LinkedIn extraction does not need a local browser and uses `groq/compound-mini` to visit the URL and return only the core post text.

## Architecture

Top‑level components:

- `app2.py` — FastAPI server implementing both pipelines and serving a tiny UI
- `extension/` — Chrome extension (Manifest V3) injecting the action button on LinkedIn and X
- `data/reports.jsonl` — Local append‑only JSONL store for all results

### Server (`app2.py`)

Endpoints:

- `GET /` — minimal, client‑side UI that lists and renders saved reports
- `GET /reports` — returns the latest saved reports as JSON (up to 200)
- `POST /trigger` — accepts `{ url, note }`, detects the source, runs the pipeline, and persists the result

Source detection:

- `linkedin` if the URL contains `linkedin.com`
- `x` if it contains `x.com` or `twitter.com`
- `unknown` otherwise

Pipeline by source:

- X (`x`)
  - `browser_use.Agent` + `ChatGroq` opens the tweet and extracts:
    - Author display name
    - Main tweet text (optionally a brief media description)
  - Output is plain text, fed to query building

- LinkedIn (`linkedin`)
  - `groq/compound-mini` (Compound Mini) visits the URL and returns:
    - `{ "post_text": "..." }` — only the post text, with “see more” expanded when possible

Then for both:

1) Query building with `moonshotai/kimi-k2-instruct` → returns `{ "query": "..." }`
2) Research with `groq/compound` (streamed, buffered server‑side) → final `compound_answer` (Markdown)
3) Persist to `data/reports.jsonl`:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "post_url": "...",
  "user_note": "...",
  "source": "x | linkedin | unknown",
  "post_text": "...",               
  "query": "...",
  "compound_answer": "..."
}
```

### Extension (`extension/`)

- `manifest.json` — permissions for `x.com`, `linkedin.com`, and local hosts `127.0.0.1:8000/8001`
- `content.js` — injects a “Save + Analyze” button on X posts; sends messages to the background
- `content_linkedin.js` — injects a “Save + Analyze” button on LinkedIn posts, resolves stable permalinks, extracts visible post text, and captures author name + profile URL
- `background.js` — calls the local API:
  - `http://127.0.0.1:8000/trigger` for X (`TRIGGER_ANALYSIS`)
  - `http://127.0.0.1:8001/trigger` for LinkedIn (`TRIGGER_ANALYSIS_LI`)

After clicking the button on a post, you’ll be prompted for a short note. The extension sends `{ url, note }` (and when available `{ raw_text, author_name, author_url }`) to the local server, which runs the pipeline and saves the report.

## Prompts 

Extraction prompt for Compound Mini (LinkedIn and X fallback):

```text
You are PostExtractor. Visit the given social post URL (LinkedIn or X) and return ONLY the main post text.
Input: The user will provide a URL directly.
Rules:
- Return ONLY JSON: {"post_text": "..."}
- Exclude reactions, counts, and comments; include text from 'see more' / collapsed content if applicable
- If the page is not directly accessible, infer the gist from any preview/snippet and user-visible text
- No markdown, no extra text
```

Query builder prompt (Kimi‑K2):

```text
You are QueryBuilder. Build one detailed but concise research query from the extracted post text and user note.
Inputs:
- post_text: extracted social post text (LinkedIn or X)
- user_note: user's intent
Process:
- Identify entities and intent from post_text and user_note
- Compose a single concise research query (<= 50 words)
Output:
Return ONLY JSON: {"query": "..."}
No markdown or extra text.
```

Note: The X pipeline uses `browser_use.Agent` with a speed‑optimized `BrowserProfile` (short waits, `headless=False`) and a `ChatGroq` model to extract author + tweet text from the actual page.

### Email formatting and delivery (Composio)

- The server formats each report’s Markdown answer into an email body using OpenAI (default model `gpt-5`).
- Tables are rewritten into headings, short paragraphs, and bullet lists; no `<table>` tags are used.
- Composio’s Gmail toolkit sends the email to `REPORTS_EMAIL_TO`. You can reuse an existing connection via `COMPOSIO_CONNECTED_ACCOUNT_ID`, or run `python composio/gmail_demo.py` once to approve OAuth and cache it locally.

## API

Base URLs (served by the same app instance):

- X: `http://127.0.0.1:8000`
- LinkedIn: `http://127.0.0.1:8001`

Routes:

- `GET /` — minimal notebook UI
- `GET /reports` — list of recent reports (JSON array)
- `POST /trigger` — body `{ "url": "...", "note": "..." }`

Examples:

```bash
# LinkedIn example
curl -s http://127.0.0.1:8001/trigger \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.linkedin.com/feed/update/urn:li:activity:...","note":"analyze the company and founders"}' | jq .

# X example
curl -s http://127.0.0.1:8000/trigger \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://x.com/username/status/1234567890123456789","note":"context and risks?"}' | jq .
```

## Data and UI

- Data is persisted as JSONL at `data/reports.jsonl` (append‑only)
- The home page fetches `/reports` and renders the latest answer; click items in the left list to switch

## Load the Chrome extension

Steps (Manifest V3):

1. Open Chrome → `chrome://extensions/`
2. Enable “Developer mode” (top‑right)
3. Click “Load unpacked” → select the `extension/` folder
4. Ensure the server is running (`python app2.py`):
   - `http://127.0.0.1:8000/` (X)
   - `http://127.0.0.1:8001/` (LinkedIn)
5. Open LinkedIn and X in new tabs; you should see a “Save + Analyze” button on posts

Notes:

- Permissions: `activeTab`, `scripting`, `storage`, hosts for X, LinkedIn, and `127.0.0.1`
- After editing files in `extension/`, click the refresh icon next to the extension in `chrome://extensions/`

## Troubleshooting

- UI says “Loading…”
  - Ensure the server is running on 8000/8001; hard refresh the page (Cmd+Shift+R)

- Extension alerts “Failed to send”
  - Verify ports: X calls 8000, LinkedIn calls 8001
  - Confirm host permissions in `extension/manifest.json`

- GROQ key errors or empty results
  - Ensure `.env` contains `GROQ_API_KEY` and the key is valid
  - Some features require “latest” model headers (handled in `app2.py`)

- X pipeline not extracting
  - Install `browser-use` (`pip install browser-use`)
  - A real browser window will open (`headless=False`); keep it visible until extraction finishes

- LinkedIn permalink not detected
  - Click the post’s timestamp/permalink, then use the button again (the content script prefers stable URNs)

## Notes

- Built with Groq Compound and Kimi‑K2.
- Local by default: the extension posts to `127.0.0.1` and the server stores results in `data/reports.jsonl`.
- Answers are concise by design, optimized for speed and relevance.

## License

MIT
