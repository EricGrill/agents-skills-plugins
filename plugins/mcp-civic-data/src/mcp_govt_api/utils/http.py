import httpx
from typing import Any

from mcp_govt_api.utils.config import config


http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(config.timeout),
    follow_redirects=True,
    headers={"User-Agent": "mcp-civic-data/0.1.0"},
)


async def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch JSON from a URL with error handling."""
    try:
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise Exception(f"Request timed out after {config.timeout}s: {url}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except httpx.RequestError as e:
        raise Exception(f"Request failed: {e}")
