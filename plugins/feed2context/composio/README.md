## Composio Gmail Demo

Authenticate a user with Gmail via Composio, send an email using LangChain tools, and optionally listen for new Gmail message events.

### Prerequisites

- Python 3.11+
- A Composio API key and Gmail auth config

### Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Note: This repository also uses `browser-use` elsewhere and pins `openai==1.99.2`. The `composio` demo pins compatible versions.

### Environment

Create a `.env` or export directly:

```bash
export OPENAI_API_KEY="sk-..."        # Required by ChatOpenAI
export COMPOSIO_API_KEY="..."         # Your Composio key
export COMPOSIO_AUTH_CONFIG_ID="ac_..."  # Gmail auth config (from Composio dashboard)
export COMPOSIO_EXTERNAL_USER_ID="user_123@example.com"
export COMPOSIO_CONNECTED_ACCOUNT_ID="ca_..."    # Optional: reuse existing connection to skip OAuth

# Model and behavior (optional)
export OPENAI_MODEL="gpt-5"            # Defaults to gpt-5; requires access
export OPENAI_STREAMING=0               # 0 by default to avoid org verification errors

# Email content (optional)
export GMAIL_DEMO_TO="recipient@example.com"
export GMAIL_DEMO_SUBJECT="Hello from Composio 👋🏻"
export GMAIL_DEMO_BODY="Congratulations on sending your first email using AI Agents and Composio!"

# Triggers (optional)
export ENABLE_GMAIL_TRIGGER=0
```

### Run

```bash
source .venv/bin/activate
python composio/gmail_demo.py
```

Follow the printed OAuth URL to authorize Gmail. After completion, the script sends the email and optionally subscribes to new-message events for 60 seconds.

### Auto-auth (skip OAuth prompt)

- If you’ve already connected once, the script caches the `connected_account_id` at `composio/.cache/<user>_<auth_config>.json` and reuses it.
- You can also set `COMPOSIO_CONNECTED_ACCOUNT_ID=ca_...` to skip OAuth entirely on subsequent runs.

References: Composio auth docs — [Authenticating Tools](https://docs.composio.dev/docs/authenticating-tools), [Custom Auth Configs](https://docs.composio.dev/docs/custom-auth-configs), [Programmatic Auth Configs](https://docs.composio.dev/docs/programmatic-auth-configs), [Custom Auth Parameters](https://docs.composio.dev/docs/custom-auth-params)

### Notes on GPT‑5 and streaming

- Some orgs must be verified to use streaming with GPT‑5. If you see an error like:
  "Your organization must be verified to stream this model…", set `OPENAI_STREAMING=0` (default) or verify your org.
- If `gpt-5` isn’t available for your key, the script falls back to `gpt-4o-mini` automatically.


