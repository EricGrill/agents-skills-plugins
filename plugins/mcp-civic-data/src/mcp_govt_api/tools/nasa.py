from mcp_govt_api.server import mcp
from mcp_govt_api.utils.config import config
from mcp_govt_api.utils.http import fetch_json


NASA_BASE = "https://api.nasa.gov"


def get_api_key() -> str:
    """Return NASA API key or DEMO_KEY for limited access."""
    return config.nasa_api_key or "DEMO_KEY"


@mcp.tool()
async def get_astronomy_photo(date: str = "") -> str:
    """Get NASA's Astronomy Picture of the Day (APOD).

    Args:
        date: Optional date in YYYY-MM-DD format (default: today)

    Returns:
        Title, explanation, and URL of the astronomy picture
    """
    params = {"api_key": get_api_key()}
    if date:
        params["date"] = date

    data = await fetch_json(f"{NASA_BASE}/planetary/apod", params=params)

    media_type = data.get("media_type", "image")
    url_key = "url" if media_type == "image" else "url"

    return (
        f"**{data['title']}**\n"
        f"Date: {data['date']}\n\n"
        f"{data['explanation']}\n\n"
        f"{'Image' if media_type == 'image' else 'Video'}: {data.get(url_key, 'N/A')}"
    )


@mcp.tool()
async def get_mars_rover_photos(
    rover: str = "curiosity",
    sol: int | None = None,
    earth_date: str = "",
    camera: str = ""
) -> str:
    """Get photos from Mars rovers (Curiosity, Opportunity, Spirit, Perseverance).

    Args:
        rover: Rover name: 'curiosity', 'opportunity', 'spirit', or 'perseverance'
        sol: Martian sol (day) number
        earth_date: Earth date in YYYY-MM-DD format (alternative to sol)
        camera: Optional camera name (e.g., 'FHAZ', 'RHAZ', 'MAST', 'NAVCAM')

    Returns:
        List of photo URLs from the specified rover
    """
    rover = rover.lower()
    params = {"api_key": get_api_key()}

    if sol is not None:
        params["sol"] = sol
    elif earth_date:
        params["earth_date"] = earth_date
    else:
        # Default to a recent sol for Curiosity
        params["sol"] = 1000

    if camera:
        params["camera"] = camera.lower()

    url = f"{NASA_BASE}/mars-photos/api/v1/rovers/{rover}/photos"
    data = await fetch_json(url, params=params)

    photos = data.get("photos", [])
    if not photos:
        return f"No photos found for {rover} with the specified parameters"

    result = [f"**Mars Rover Photos - {rover.capitalize()}**\n"]
    result.append(f"Found {len(photos)} photos\n")

    for photo in photos[:10]:  # Limit to 10 photos
        result.append(
            f"- Camera: {photo['camera']['full_name']}\n"
            f"  Sol: {photo['sol']} | Earth Date: {photo['earth_date']}\n"
            f"  URL: {photo['img_src']}"
        )

    return "\n\n".join(result)


@mcp.tool()
async def search_nasa_images(query: str, media_type: str = "image") -> str:
    """Search NASA's image and video library.

    Args:
        query: Search terms (e.g., 'apollo 11', 'mars', 'hubble')
        media_type: Type of media: 'image', 'video', or 'audio'

    Returns:
        Search results with titles, descriptions, and URLs
    """
    url = "https://images-api.nasa.gov/search"
    params = {"q": query, "media_type": media_type}

    data = await fetch_json(url, params=params)

    items = data.get("collection", {}).get("items", [])
    if not items:
        return f"No results found for '{query}'"

    result = [f"**NASA Image Search: '{query}'**\n"]
    result.append(f"Found {len(items)} results\n")

    for item in items[:10]:
        item_data = item.get("data", [{}])[0]
        links = item.get("links", [{}])
        preview = links[0].get("href", "N/A") if links else "N/A"

        result.append(
            f"**{item_data.get('title', 'Untitled')}**\n"
            f"Date: {item_data.get('date_created', 'N/A')[:10]}\n"
            f"Description: {item_data.get('description', 'N/A')[:200]}...\n"
            f"Preview: {preview}"
        )

    return "\n\n---\n\n".join(result)


@mcp.tool()
async def query_nasa(endpoint: str, params: dict | None = None) -> dict:
    """Make a raw query to the NASA API.

    Args:
        endpoint: API endpoint (e.g., '/planetary/apod', '/neo/rest/v1/feed')
        params: Query parameters (api_key will be added automatically)

    Returns:
        Raw JSON response from NASA API
    """
    url = f"{NASA_BASE}{endpoint}"
    params = params or {}
    params["api_key"] = get_api_key()
    return await fetch_json(url, params=params)
