from mcp_govt_api.server import mcp
from mcp_govt_api.utils.http import fetch_json


EU_DATA_BASE = "https://data.europa.eu/api/hub/search"


@mcp.tool()
async def search_eu_datasets(query: str, limit: int = 10) -> str:
    """Search for datasets on the European Union Open Data Portal.

    Args:
        query: Search terms (e.g., 'environment', 'economy', 'transport')
        limit: Number of results to return (default: 10, max: 50)

    Returns:
        List of matching EU datasets with titles and descriptions
    """
    limit = min(limit, 50)
    url = f"{EU_DATA_BASE}/datasets"
    params = {"q": query, "limit": limit}

    data = await fetch_json(url, params=params)

    results = data.get("result", {}).get("results", [])
    total = data.get("result", {}).get("count", 0)

    if not results:
        return f"No EU datasets found for '{query}'"

    output = [f"**EU Open Data Search: '{query}'**"]
    output.append(f"Found {total} datasets (showing {len(results)})\n")

    for ds in results:
        # Handle multilingual titles
        title_obj = ds.get("title", {})
        if isinstance(title_obj, dict):
            title = title_obj.get("en") or list(title_obj.values())[0] if title_obj else "Untitled"
        else:
            title = str(title_obj)

        desc_obj = ds.get("description", {})
        if isinstance(desc_obj, dict):
            desc = desc_obj.get("en") or list(desc_obj.values())[0] if desc_obj else ""
        else:
            desc = str(desc_obj)
        desc = desc[:200] if desc else "No description"

        publisher = ds.get("publisher", {}).get("name", "Unknown")
        dataset_id = ds.get("id", "")

        output.append(
            f"**{title}**\n"
            f"Publisher: {publisher}\n"
            f"ID: `{dataset_id}`\n"
            f"{desc}..."
        )

    return "\n\n---\n\n".join(output)


@mcp.tool()
async def get_eu_dataset_info(dataset_id: str) -> str:
    """Get detailed information about a specific EU Open Data dataset.

    Args:
        dataset_id: The dataset ID (from search results)

    Returns:
        Detailed metadata and distribution links for the dataset
    """
    url = f"{EU_DATA_BASE}/datasets/{dataset_id}"

    data = await fetch_json(url)
    ds = data.get("result", {})

    if not ds:
        return f"Dataset not found: {dataset_id}"

    # Handle multilingual fields
    title_obj = ds.get("title", {})
    if isinstance(title_obj, dict):
        title = title_obj.get("en") or list(title_obj.values())[0] if title_obj else "Untitled"
    else:
        title = str(title_obj)

    desc_obj = ds.get("description", {})
    if isinstance(desc_obj, dict):
        desc = desc_obj.get("en") or list(desc_obj.values())[0] if desc_obj else "No description"
    else:
        desc = str(desc_obj)

    output = [f"**{title}**\n"]
    output.append(f"Publisher: {ds.get('publisher', {}).get('name', 'Unknown')}")
    output.append(f"Modified: {ds.get('modified', 'Unknown')[:10] if ds.get('modified') else 'Unknown'}")
    output.append(f"License: {ds.get('license', 'Unknown')}")

    output.append(f"\n**Description:**\n{desc}\n")

    distributions = ds.get("distributions", [])
    if distributions:
        output.append("**Available Distributions:**")
        for dist in distributions[:10]:
            dist_title = dist.get("title", {})
            if isinstance(dist_title, dict):
                name = dist_title.get("en") or list(dist_title.values())[0] if dist_title else "Unnamed"
            else:
                name = str(dist_title) or "Unnamed"

            fmt = dist.get("format", "Unknown")
            access_url = dist.get("accessUrl", "N/A")

            output.append(f"- [{fmt}] {name}\n  {access_url}")

    return "\n".join(output)


@mcp.tool()
async def query_eu_data(endpoint: str, params: dict | None = None) -> dict:
    """Make a raw query to the EU Open Data Portal API.

    Args:
        endpoint: API endpoint (e.g., '/datasets', '/catalogues')
        params: Query parameters

    Returns:
        Raw JSON response from EU Open Data API
    """
    url = f"{EU_DATA_BASE}{endpoint}"
    return await fetch_json(url, params=params)
