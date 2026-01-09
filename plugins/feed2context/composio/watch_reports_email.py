import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from composio import Composio
from composio_langchain import LangchainProvider


def require_env(var_name: str, default: Optional[str] = None) -> str:
    value = os.getenv(var_name, default)
    if not value:
        print(f"Missing required environment variable: {var_name}", file=sys.stderr)
        sys.exit(1)
    return value


def load_cached_connected_account_id(cache_dir: Path, external_user_id: str, auth_config_id: str) -> Optional[str]:
    cache_file = cache_dir / f"{external_user_id}_{auth_config_id}.json"
    if not cache_file.exists():
        return None
    try:
        with cache_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("connected_account_id")
    except Exception:
        return None


def save_cached_connected_account_id(cache_dir: Path, external_user_id: str, auth_config_id: str, connected_account_id: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{external_user_id}_{auth_config_id}.json"
    try:
        with cache_file.open("w", encoding="utf-8") as f:
            json.dump({"connected_account_id": connected_account_id}, f)
    except Exception:
        pass


def ensure_connected_account(
    composio: Composio,
    external_user_id: str,
    auth_config_id: str,
    cache_dir: Path,
) -> str:
    # Priority: explicit env → cached file → new OAuth connection (as a last resort)
    env_connected_id = os.getenv("COMPOSIO_CONNECTED_ACCOUNT_ID")
    if env_connected_id:
        return env_connected_id

    cached_id = load_cached_connected_account_id(cache_dir, external_user_id, auth_config_id)
    if cached_id:
        return cached_id

    # As a last resort, initiate OAuth (will require manual approval once)
    connection_request = composio.connected_accounts.initiate(
        user_id=external_user_id,
        auth_config_id=auth_config_id,
    )
    print(f"Please authorize the app by visiting this URL:\n{connection_request.redirect_url}\n")
    connected_account = connection_request.wait_for_connection()
    print(f"Connected account established: {connected_account.id}")
    save_cached_connected_account_id(cache_dir, external_user_id, auth_config_id, connected_account.id)
    return connected_account.id


def send_email_via_gmail_tool(
    composio: Composio,
    external_user_id: str,
    to_email: str,
    subject: str,
    body: str,
) -> None:
    tools = composio.tools.get(user_id=external_user_id, tools=["GMAIL_SEND_EMAIL"])
    if not tools:
        raise RuntimeError("GMAIL_SEND_EMAIL tool not available for this user")
    gmail_tool = tools[0]
    result = gmail_tool.invoke({
        "recipient_email": to_email,
        "subject": subject,
        "body": body,
        "is_html": False,
    })
    print("Email tool result:")
    print(result)


def main() -> None:
    reports_path = Path(require_env("REPORTS_FILE", str(Path("data") / "reports.jsonl")))
    api_key = require_env("COMPOSIO_API_KEY")
    auth_config_id = require_env("COMPOSIO_AUTH_CONFIG_ID")
    external_user_id = require_env("COMPOSIO_EXTERNAL_USER_ID")

    to_email = require_env("REPORTS_EMAIL_TO", external_user_id)
    subject_template = os.getenv("REPORTS_EMAIL_SUBJECT", "Feed2Context report for {post_url}")
    poll_seconds = float(os.getenv("REPORTS_POLL_SECONDS", "2"))
    start_at_end = os.getenv("REPORTS_START_AT_END", "1") in {"1", "true", "TRUE"}

    cache_dir = Path(__file__).parent / ".cache"

    # Initialize Composio early, and ensure a connected account exists
    composio = Composio(api_key=api_key, provider=LangchainProvider())
    ensure_connected_account(composio, external_user_id, auth_config_id, cache_dir)

    # State management for last processed line
    state_file = cache_dir / "reports_email_state.json"
    last_line_idx = 0
    if start_at_end and reports_path.exists():
        try:
            with reports_path.open("r", encoding="utf-8") as f:
                last_line_idx = sum(1 for _ in f)
        except Exception:
            last_line_idx = 0
    else:
        # Try to resume from prior state
        if state_file.exists():
            try:
                with state_file.open("r", encoding="utf-8") as f:
                    state = json.load(f)
                    last_line_idx = int(state.get("last_line_idx", 0))
            except Exception:
                last_line_idx = 0

    print(
        f"Watching {reports_path} (poll={poll_seconds}s, start_at_end={start_at_end}) "
        f"to email new 'compound_answer' lines to {to_email}"
    )

    while True:
        try:
            if reports_path.exists():
                with reports_path.open("r", encoding="utf-8") as f:
                    lines = f.readlines()

                if len(lines) > last_line_idx:
                    new_lines = lines[last_line_idx:]
                    for line in new_lines:
                        line = line.strip()
                        if not line:
                            last_line_idx += 1
                            continue
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            # Skip malformed lines but advance to avoid reprocessing
                            last_line_idx += 1
                            continue

                        compound_answer = rec.get("compound_answer")
                        post_url = rec.get("post_url", "")
                        if compound_answer:
                            subject = subject_template.format(post_url=post_url)
                            print(
                                f"Sending email for new report (line {last_line_idx + 1}) → {to_email}"
                            )
                            try:
                                send_email_via_gmail_tool(
                                    composio,
                                    external_user_id,
                                    to_email,
                                    subject,
                                    compound_answer,
                                )
                            except Exception as e:
                                print(f"Failed to send email: {e}", file=sys.stderr)
                        last_line_idx += 1

                    # Persist state after processing batch
                    try:
                        cache_dir.mkdir(parents=True, exist_ok=True)
                        with state_file.open("w", encoding="utf-8") as sf:
                            json.dump({"last_line_idx": last_line_idx}, sf)
                    except Exception:
                        pass

        except KeyboardInterrupt:
            print("Stopping watcher…")
            break
        except Exception as e:
            print(f"Watcher error: {e}", file=sys.stderr)

        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()


