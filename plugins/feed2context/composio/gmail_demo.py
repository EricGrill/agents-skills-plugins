import os
import sys
import time
import json
from pathlib import Path

from composio import Composio
from composio_langchain import LangchainProvider

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


def require_env(var_name: str, default: str | None = None) -> str:
    value = os.getenv(var_name, default)
    if not value:
        print(f"Missing required environment variable: {var_name}", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    # Read secrets and config
    api_key = require_env("COMPOSIO_API_KEY")
    auth_config_id = require_env("COMPOSIO_AUTH_CONFIG_ID")

    # Identify the user in your system (email or internal user id)
    external_user_id = require_env("COMPOSIO_EXTERNAL_USER_ID")

    # Initialize SDK
    composio = Composio(api_key=api_key, provider=LangchainProvider())

    # Auto-auth: reuse an existing connected account if provided via env or cache
    connected_account_id = os.getenv("COMPOSIO_CONNECTED_ACCOUNT_ID")

    cache_dir = Path(__file__).parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key = f"{external_user_id}_{auth_config_id}.json"
    cache_file = cache_dir / cache_key

    if not connected_account_id and cache_file.exists():
        try:
            with cache_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                connected_account_id = data.get("connected_account_id")
        except Exception:
            connected_account_id = None

    if connected_account_id:
        print(f"Reusing connected account: {connected_account_id}")
    else:
        # Initiate OAuth connection only if no previous connection is known
        connection_request = composio.connected_accounts.initiate(
            user_id=external_user_id,
            auth_config_id=auth_config_id,
        )

        redirect_url = connection_request.redirect_url
        print(f"Please authorize the app by visiting this URL:\n{redirect_url}\n")

        # Wait until the user completes the OAuth flow
        connected_account = connection_request.wait_for_connection()
        connected_account_id = connected_account.id
        print(
            f"Connection established successfully! Connected account id: {connected_account_id}"
        )

        # Cache for future runs to avoid repeated OAuth
        try:
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump({"connected_account_id": connected_account_id}, f)
        except Exception:
            pass

    # Fetch tools for this user (Gmail send email)
    tools = composio.tools.get(user_id=external_user_id, tools=["GMAIL_SEND_EMAIL"])

    # Prepare agent prompt and model (tools format for GPT-5 compatibility)
    try:
        prompt = hub.pull("hwchase17/openai-tools-agent")
    except Exception:
        # Minimal fallback prompt compatible with tools agents
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use tools when needed."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    # Disable streaming to avoid org verification errors; default to GPT-5 if available
    model_name = os.getenv("OPENAI_MODEL", "gpt-5")

    try:
        openai_client = ChatOpenAI(model=model_name, streaming=False)
    except Exception as e:
        print(f"Model '{model_name}' init failed ({e}); falling back to 'gpt-4o-mini'.")
        openai_client = ChatOpenAI(model="gpt-5", streaming=False)

    # Define task: change recipient/subject/body via env overrides for convenience
    recipient = os.getenv("GMAIL_DEMO_TO", external_user_id)
    subject = os.getenv("GMAIL_DEMO_SUBJECT", "Hello from Composio 👋🏻")
    body = os.getenv(
        "GMAIL_DEMO_BODY",
        "Congratulations on sending your first email using AI Agents and Composio!",
    )

    task = (
        f"Send an email to {recipient} with the subject '{subject}' and "
        f"the body '{body}'"
    )

    # Create agent and execute (OpenAI tools agent)
    agent = create_openai_tools_agent(openai_client, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Sending email via agent…\n")
    agent_executor.invoke({"input": task})
    print("Email sent successfully!\n")

    # Optional: Create a trigger for new Gmail messages and subscribe
    if os.getenv("ENABLE_GMAIL_TRIGGER", "0") in {"1", "true", "TRUE"}:
        trigger = composio.triggers.create(
            user_id=external_user_id,
            slug="GMAIL_NEW_GMAIL_MESSAGE",
            trigger_config={"labelIds": "INBOX", "userId": "me", "interval": 1},
        )
        print(f"✅ Trigger created successfully. Trigger Id: {trigger.trigger_id}")

        subscription = composio.triggers.subscribe()

        @subscription.handle(trigger_id=trigger.trigger_id)
        def handle_gmail_event(data):
            print("New Gmail event:")
            print(data)

        print("Listening for Gmail trigger events for 60 seconds…")
        start = time.time()
        while time.time() - start < 60:
            time.sleep(1)


if __name__ == "__main__":
    main()


