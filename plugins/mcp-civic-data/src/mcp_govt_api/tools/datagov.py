from mcp_govt_api.server import mcp
from mcp_govt_api.utils.http import fetch_json


DATAGOV_BASE = "https://catalog.data.gov/api/3"


@mcp.tool()
async def search_datasets(query: str, rows: int = 10) -> str:
    """Search for datasets on Data.gov.

    Args:
        query: Search terms (e.g., 'climate', 'census', 'health')
        rows: Number of results to return (default: 10, max: 50)

    Returns:
        List of matching datasets with titles and descriptions
    """
    rows = min(rows, 50)
    url = f"{DATAGOV_BASE}/action/package_search"
    params = {"q": query, "rows": rows}

    data = await fetch_json(url, params=params)

    results = data.get("result", {}).get("results", [])
    total = data.get("result", {}).get("count", 0)

    if not results:
        return f"No datasets found for '{query}'"

    output = [f"**Data.gov Search: '{query}'**"]
    output.append(f"Found {total} datasets (showing {len(results)})\n")

    for ds in results:
        title = ds.get("title", "Untitled")
        org = ds.get("organization", {}).get("title", "Unknown")
        notes = ds.get("notes", "No description")[:200]
        dataset_id = ds.get("id", "")

        num_resources = len(ds.get("resources", []))

        output.append(
            f"**{title}**\n"
            f"Organization: {org}\n"
            f"Resources: {num_resources} files\n"
            f"ID: `{dataset_id}`\n"
            f"{notes}..."
        )

    return "\n\n---\n\n".join(output)


@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """Get detailed information about a specific Data.gov dataset.

    Args:
        dataset_id: The dataset ID (from search results)

    Returns:
        Detailed metadata and download links for the dataset
    """
    url = f"{DATAGOV_BASE}/action/package_show"
    params = {"id": dataset_id}

    data = await fetch_json(url, params=params)
    ds = data.get("result", {})

    if not ds:
        return f"Dataset not found: {dataset_id}"

    output = [f"**{ds.get('title', 'Untitled')}**\n"]
    output.append(f"Organization: {ds.get('organization', {}).get('title', 'Unknown')}")
    output.append(f"License: {ds.get('license_title', 'Unknown')}")
    output.append(f"Last Updated: {ds.get('metadata_modified', 'Unknown')[:10]}")

    notes = ds.get("notes", "No description available")
    output.append(f"\n**Description:**\n{notes}\n")

    resources = ds.get("resources", [])
    if resources:
        output.append("**Available Resources:**")
        for res in resources[:10]:
            name = res.get("name") or res.get("description") or "Unnamed"
            fmt = res.get("format", "Unknown")
            url = res.get("url", "N/A")
            size = res.get("size")
            size_str = f" ({size} bytes)" if size else ""

            output.append(f"- [{fmt}] {name}{size_str}\n  {url}")

    return "\n".join(output)


@mcp.tool()
async def query_datagov(action: str, params: dict | None = None) -> dict:
    """Make a raw query to the Data.gov CKAN API.

    Args:
        action: CKAN action (e.g., 'package_search', 'package_show', 'group_list')
        params: Query parameters for the action

    Returns:
        Raw JSON response from Data.gov API
    """
    url = f"{DATAGOV_BASE}/action/{action}"
    return await fetch_json(url, params=params)
