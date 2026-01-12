# MCP Government API Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that provides Claude access to 7 free government/open data APIs with 16 granular tools and 7 general query tools.

**Architecture:** FastMCP-based Python server with one module per API domain. Shared HTTP client using httpx for async requests. Environment variables for optional API keys with graceful degradation.

**Tech Stack:** Python 3.11+, mcp[cli] (FastMCP), httpx (async HTTP), python-dotenv (optional env loading)

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/mcp_govt_api/__init__.py`
- Create: `src/mcp_govt_api/__main__.py`
- Create: `README.md`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mcp-govt-api-free"
version = "0.1.0"
description = "MCP server for free government and open data APIs"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "mcp[cli]>=1.0.0",
    "httpx>=0.27.0",
]

[project.scripts]
mcp-govt-api = "mcp_govt_api:main"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_govt_api"]
```

**Step 2: Create src/mcp_govt_api/__init__.py**

```python
from mcp_govt_api.server import mcp, main

__all__ = ["mcp", "main"]
```

**Step 3: Create src/mcp_govt_api/__main__.py**

```python
from mcp_govt_api import main

if __name__ == "__main__":
    main()
```

**Step 4: Create README.md**

```markdown
# MCP Government API Server

An MCP server providing access to free government and open data APIs.

## APIs Included

- NOAA Weather API (forecasts, alerts)
- OpenWeather API (global weather, requires API key)
- US Census API (population, demographics, housing)
- NASA API (APOD, Mars rover photos, image search)
- World Bank API (country indicators, comparisons)
- Data.gov (US government datasets)
- European Open Data Portal (EU datasets)

## Installation

```bash
pip install mcp-govt-api-free
```

## Configuration

Optional environment variables:
- `OPENWEATHER_API_KEY` - Required for global weather tools
- `NASA_API_KEY` - Optional, increases rate limits

## Claude Desktop Setup

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "govt-api": {
      "command": "python",
      "args": ["-m", "mcp_govt_api"],
      "env": {
        "OPENWEATHER_API_KEY": "your-key-here",
        "NASA_API_KEY": "your-key-here"
      }
    }
  }
}
```
```

**Step 5: Commit**

```bash
git add pyproject.toml src/ README.md
git commit -m "feat: initialize project structure"
```

---

## Task 2: Utilities - Config and HTTP Client

**Files:**
- Create: `src/mcp_govt_api/utils/__init__.py`
- Create: `src/mcp_govt_api/utils/config.py`
- Create: `src/mcp_govt_api/utils/http.py`

**Step 1: Create utils/__init__.py**

```python
from mcp_govt_api.utils.config import config
from mcp_govt_api.utils.http import http_client, fetch_json

__all__ = ["config", "http_client", "fetch_json"]
```

**Step 2: Create utils/config.py**

```python
import os
from dataclasses import dataclass


@dataclass
class Config:
    """API configuration from environment variables."""

    openweather_api_key: str | None = None
    nasa_api_key: str | None = None
    timeout: int = 30

    def __post_init__(self):
        self.openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")
        self.nasa_api_key = os.environ.get("NASA_API_KEY")
        self.timeout = int(os.environ.get("API_TIMEOUT", "30"))

    @property
    def has_openweather(self) -> bool:
        return bool(self.openweather_api_key)

    @property
    def has_nasa_key(self) -> bool:
        return bool(self.nasa_api_key)

    def get_availability_summary(self) -> str:
        """Return a summary of API availability."""
        lines = [
            "API Availability:",
            "  ✓ NOAA (no key required)",
            "  ✓ Census (no key required)",
        ]
        if self.has_nasa_key:
            lines.append("  ✓ NASA (using API key for higher limits)")
        else:
            lines.append("  ✓ NASA (no key, limited to 30 req/hour)")
        if self.has_openweather:
            lines.append("  ✓ OpenWeather (API key configured)")
        else:
            lines.append("  ✗ OpenWeather (OPENWEATHER_API_KEY not set)")
        lines.extend([
            "  ✓ World Bank (no key required)",
            "  ✓ Data.gov (no key required)",
            "  ✓ EU Open Data (no key required)",
        ])
        return "\n".join(lines)


config = Config()
```

**Step 3: Create utils/http.py**

```python
import httpx
from typing import Any

from mcp_govt_api.utils.config import config


http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(config.timeout),
    follow_redirects=True,
    headers={"User-Agent": "mcp-govt-api-free/0.1.0"},
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
```

**Step 4: Commit**

```bash
git add src/mcp_govt_api/utils/
git commit -m "feat: add config and HTTP utilities"
```

---

## Task 3: Server Entry Point with Tool Registration

**Files:**
- Create: `src/mcp_govt_api/server.py`
- Create: `src/mcp_govt_api/tools/__init__.py`

**Step 1: Create server.py**

```python
from mcp.server.fastmcp import FastMCP

from mcp_govt_api.utils.config import config

mcp = FastMCP(
    "Government API Server",
    instructions="""Access free government and open data APIs including:
- NOAA Weather (US forecasts and alerts)
- OpenWeather (global weather, requires API key)
- US Census (population, demographics, housing)
- NASA (astronomy photos, Mars rover, image search)
- World Bank (country economic indicators)
- Data.gov (US government datasets)
- EU Open Data (European datasets)
""",
)


def main():
    """Entry point for the MCP server."""
    print(config.get_availability_summary())
    mcp.run()


# Import tools to register them
from mcp_govt_api.tools import weather  # noqa: E402, F401
from mcp_govt_api.tools import census  # noqa: E402, F401
from mcp_govt_api.tools import nasa  # noqa: E402, F401
from mcp_govt_api.tools import economics  # noqa: E402, F401
from mcp_govt_api.tools import datagov  # noqa: E402, F401
from mcp_govt_api.tools import eu_data  # noqa: E402, F401
```

**Step 2: Create tools/__init__.py**

```python
# Tools are registered via decorators when imported
```

**Step 3: Commit**

```bash
git add src/mcp_govt_api/server.py src/mcp_govt_api/tools/
git commit -m "feat: add server entry point"
```

---

## Task 4: Weather Tools (NOAA + OpenWeather)

**Files:**
- Create: `src/mcp_govt_api/tools/weather.py`

**Step 1: Create weather.py with NOAA tools**

```python
from mcp_govt_api.server import mcp
from mcp_govt_api.utils.config import config
from mcp_govt_api.utils.http import fetch_json


NOAA_BASE = "https://api.weather.gov"


@mcp.tool()
async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a US location by coordinates.

    Args:
        latitude: Latitude of the location (e.g., 38.8894 for Washington DC)
        longitude: Longitude of the location (e.g., -77.0352 for Washington DC)

    Returns:
        Current conditions and 7-day forecast from NOAA
    """
    # First get the forecast grid endpoint for this location
    points_url = f"{NOAA_BASE}/points/{latitude},{longitude}"
    points_data = await fetch_json(points_url)

    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await fetch_json(forecast_url)

    periods = forecast_data["properties"]["periods"]
    result = [f"Weather forecast for {latitude}, {longitude}:\n"]

    for period in periods[:6]:  # Next 3 days (day/night pairs)
        result.append(f"**{period['name']}**: {period['detailedForecast']}")

    return "\n\n".join(result)


@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Get active weather alerts for a US state.

    Args:
        state: Two-letter state code (e.g., 'CA', 'TX', 'NY')

    Returns:
        List of active weather alerts for the state
    """
    state = state.upper()
    if len(state) != 2:
        return "Error: State must be a 2-letter code (e.g., 'CA', 'TX')"

    url = f"{NOAA_BASE}/alerts/active"
    data = await fetch_json(url, params={"area": state})

    alerts = data.get("features", [])
    if not alerts:
        return f"No active weather alerts for {state}"

    result = [f"Active weather alerts for {state}:\n"]
    for alert in alerts[:10]:  # Limit to 10 alerts
        props = alert["properties"]
        result.append(
            f"**{props['event']}** ({props['severity']})\n"
            f"Areas: {props.get('areaDesc', 'N/A')}\n"
            f"{props.get('headline', '')}"
        )

    return "\n\n---\n\n".join(result)


@mcp.tool()
async def get_global_weather(city: str, country_code: str = "") -> str:
    """Get current weather for any city worldwide (requires OPENWEATHER_API_KEY).

    Args:
        city: City name (e.g., 'London', 'Tokyo', 'Paris')
        country_code: Optional 2-letter country code (e.g., 'GB', 'JP', 'FR')

    Returns:
        Current weather conditions for the city
    """
    if not config.has_openweather:
        return "Error: OpenWeather tools require OPENWEATHER_API_KEY environment variable"

    query = f"{city},{country_code}" if country_code else city
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": query,
        "appid": config.openweather_api_key,
        "units": "metric",
    }

    data = await fetch_json(url, params=params)

    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})

    return (
        f"**Weather in {data['name']}, {data['sys']['country']}**\n\n"
        f"Conditions: {weather['description'].capitalize()}\n"
        f"Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)\n"
        f"Humidity: {main['humidity']}%\n"
        f"Wind: {wind.get('speed', 'N/A')} m/s\n"
        f"Pressure: {main['pressure']} hPa"
    )


@mcp.tool()
async def query_noaa(endpoint: str, params: dict | None = None) -> dict:
    """Make a raw query to the NOAA Weather API.

    Args:
        endpoint: API endpoint path (e.g., '/points/38.8894,-77.0352', '/alerts/active')
        params: Optional query parameters as a dictionary

    Returns:
        Raw JSON response from NOAA API
    """
    url = f"{NOAA_BASE}{endpoint}"
    return await fetch_json(url, params=params)


@mcp.tool()
async def query_openweather(endpoint: str, params: dict | None = None) -> dict:
    """Make a raw query to the OpenWeather API (requires OPENWEATHER_API_KEY).

    Args:
        endpoint: API endpoint (e.g., '/data/2.5/weather', '/data/2.5/forecast')
        params: Query parameters (appid will be added automatically)

    Returns:
        Raw JSON response from OpenWeather API
    """
    if not config.has_openweather:
        return {"error": "OpenWeather requires OPENWEATHER_API_KEY environment variable"}

    url = f"https://api.openweathermap.org{endpoint}"
    params = params or {}
    params["appid"] = config.openweather_api_key
    return await fetch_json(url, params=params)
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/weather.py
git commit -m "feat: add weather tools (NOAA + OpenWeather)"
```

---

## Task 5: Census Tools

**Files:**
- Create: `src/mcp_govt_api/tools/census.py`

**Step 1: Create census.py**

```python
from mcp_govt_api.server import mcp
from mcp_govt_api.utils.http import fetch_json


CENSUS_BASE = "https://api.census.gov/data"
# American Community Survey 5-Year Estimates (most recent)
ACS_YEAR = "2022"
ACS_DATASET = f"{CENSUS_BASE}/{ACS_YEAR}/acs/acs5"


@mcp.tool()
async def get_population(state: str, county: str = "") -> str:
    """Get population data for a US state or county.

    Args:
        state: Two-letter state code (e.g., 'CA', 'TX') or state FIPS code
        county: Optional county name or FIPS code

    Returns:
        Population statistics from the American Community Survey
    """
    # State FIPS lookup (subset of common states)
    state_fips = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11", "PR": "72",
    }

    state_code = state.upper()
    fips = state_fips.get(state_code, state_code)

    # Variables: B01003_001E = Total Population
    variables = "NAME,B01003_001E"

    if county:
        geo = f"county:*&in=state:{fips}"
    else:
        geo = f"state:{fips}"

    url = f"{ACS_DATASET}?get={variables}&for={geo}"
    data = await fetch_json(url)

    # First row is headers, rest is data
    headers = data[0]
    rows = data[1:]

    result = [f"Population Data ({ACS_YEAR} ACS 5-Year Estimates):\n"]
    for row in rows[:20]:  # Limit results
        name = row[0]
        pop = int(row[1]) if row[1] else 0
        result.append(f"- {name}: {pop:,}")

    return "\n".join(result)


@mcp.tool()
async def get_demographics(state: str, county: str = "") -> str:
    """Get demographic breakdown for a US state or county.

    Args:
        state: Two-letter state code (e.g., 'CA', 'TX')
        county: Optional county FIPS code (3 digits)

    Returns:
        Age, race, and income demographics from the American Community Survey
    """
    state_fips = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11", "PR": "72",
    }

    state_code = state.upper()
    fips = state_fips.get(state_code, state_code)

    # Variables for demographics
    variables = ",".join([
        "NAME",
        "B01003_001E",  # Total population
        "B01002_001E",  # Median age
        "B19013_001E",  # Median household income
        "B02001_002E",  # White alone
        "B02001_003E",  # Black alone
        "B02001_005E",  # Asian alone
        "B03001_003E",  # Hispanic/Latino
    ])

    if county:
        geo = f"county:{county}&in=state:{fips}"
    else:
        geo = f"state:{fips}"

    url = f"{ACS_DATASET}?get={variables}&for={geo}"
    data = await fetch_json(url)

    row = data[1]  # First data row
    name = row[0]
    total_pop = int(row[1]) if row[1] else 0
    median_age = float(row[2]) if row[2] else 0
    median_income = int(row[3]) if row[3] else 0
    white = int(row[4]) if row[4] else 0
    black = int(row[5]) if row[5] else 0
    asian = int(row[6]) if row[6] else 0
    hispanic = int(row[7]) if row[7] else 0

    def pct(n: int) -> str:
        return f"{(n/total_pop*100):.1f}%" if total_pop else "N/A"

    return (
        f"**Demographics for {name}** ({ACS_YEAR} ACS 5-Year Estimates)\n\n"
        f"**Population**: {total_pop:,}\n"
        f"**Median Age**: {median_age}\n"
        f"**Median Household Income**: ${median_income:,}\n\n"
        f"**Race/Ethnicity**:\n"
        f"- White: {white:,} ({pct(white)})\n"
        f"- Black: {black:,} ({pct(black)})\n"
        f"- Asian: {asian:,} ({pct(asian)})\n"
        f"- Hispanic/Latino: {hispanic:,} ({pct(hispanic)})"
    )


@mcp.tool()
async def get_housing_stats(state: str, county: str = "") -> str:
    """Get housing statistics for a US state or county.

    Args:
        state: Two-letter state code (e.g., 'CA', 'TX')
        county: Optional county FIPS code (3 digits)

    Returns:
        Housing data including median values, rent, and vacancy rates
    """
    state_fips = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11", "PR": "72",
    }

    state_code = state.upper()
    fips = state_fips.get(state_code, state_code)

    # Housing variables
    variables = ",".join([
        "NAME",
        "B25001_001E",  # Total housing units
        "B25002_002E",  # Occupied units
        "B25002_003E",  # Vacant units
        "B25077_001E",  # Median home value
        "B25064_001E",  # Median gross rent
    ])

    if county:
        geo = f"county:{county}&in=state:{fips}"
    else:
        geo = f"state:{fips}"

    url = f"{ACS_DATASET}?get={variables}&for={geo}"
    data = await fetch_json(url)

    row = data[1]
    name = row[0]
    total_units = int(row[1]) if row[1] else 0
    occupied = int(row[2]) if row[2] else 0
    vacant = int(row[3]) if row[3] else 0
    median_value = int(row[4]) if row[4] else 0
    median_rent = int(row[5]) if row[5] else 0

    vacancy_rate = (vacant / total_units * 100) if total_units else 0

    return (
        f"**Housing Statistics for {name}** ({ACS_YEAR} ACS 5-Year Estimates)\n\n"
        f"**Total Housing Units**: {total_units:,}\n"
        f"**Occupied**: {occupied:,}\n"
        f"**Vacant**: {vacant:,} ({vacancy_rate:.1f}% vacancy rate)\n\n"
        f"**Median Home Value**: ${median_value:,}\n"
        f"**Median Gross Rent**: ${median_rent:,}/month"
    )


@mcp.tool()
async def query_census(
    dataset: str,
    variables: list[str],
    geo: str,
    year: str = "2022"
) -> dict:
    """Make a raw query to the Census API.

    Args:
        dataset: Dataset path (e.g., 'acs/acs5', 'dec/pl')
        variables: List of variable codes to retrieve
        geo: Geography specification (e.g., 'state:06', 'county:*&in=state:06')
        year: Data year (default: 2022)

    Returns:
        Raw JSON response from Census API
    """
    var_str = ",".join(variables)
    url = f"{CENSUS_BASE}/{year}/{dataset}?get={var_str}&for={geo}"
    return await fetch_json(url)
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/census.py
git commit -m "feat: add Census API tools"
```

---

## Task 6: NASA Tools

**Files:**
- Create: `src/mcp_govt_api/tools/nasa.py`

**Step 1: Create nasa.py**

```python
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
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/nasa.py
git commit -m "feat: add NASA API tools"
```

---

## Task 7: Economics Tools (World Bank)

**Files:**
- Create: `src/mcp_govt_api/tools/economics.py`

**Step 1: Create economics.py**

```python
from mcp_govt_api.server import mcp
from mcp_govt_api.utils.http import fetch_json


WORLDBANK_BASE = "https://api.worldbank.org/v2"


@mcp.tool()
async def get_country_indicators(
    country: str,
    indicators: list[str] | None = None
) -> str:
    """Get economic indicators for a country from the World Bank.

    Args:
        country: Country code (e.g., 'USA', 'CHN', 'IND', 'BRA') or name
        indicators: Optional list of indicator codes. Defaults to GDP, population, poverty.

    Returns:
        Economic indicators for the specified country
    """
    # Default to common indicators
    if not indicators:
        indicators = [
            "NY.GDP.MKTP.CD",  # GDP (current US$)
            "SP.POP.TOTL",     # Population
            "SI.POV.DDAY",     # Poverty headcount ratio
            "NY.GDP.PCAP.CD",  # GDP per capita
        ]

    indicator_names = {
        "NY.GDP.MKTP.CD": "GDP (current US$)",
        "SP.POP.TOTL": "Population",
        "SI.POV.DDAY": "Poverty Rate (% at $2.15/day)",
        "NY.GDP.PCAP.CD": "GDP per Capita",
        "SL.UEM.TOTL.ZS": "Unemployment Rate (%)",
        "FP.CPI.TOTL.ZG": "Inflation Rate (%)",
    }

    results = [f"**Economic Indicators for {country.upper()}**\n"]

    for indicator in indicators:
        url = f"{WORLDBANK_BASE}/country/{country}/indicator/{indicator}"
        params = {"format": "json", "per_page": 5, "mrv": 1}

        try:
            data = await fetch_json(url, params=params)
            if len(data) > 1 and data[1]:
                record = data[1][0]
                value = record.get("value")
                year = record.get("date")
                name = indicator_names.get(indicator, indicator)

                if value is not None:
                    if indicator in ["NY.GDP.MKTP.CD"]:
                        formatted = f"${value/1e12:.2f} trillion"
                    elif indicator == "SP.POP.TOTL":
                        formatted = f"{value/1e6:.1f} million"
                    elif indicator in ["SI.POV.DDAY", "SL.UEM.TOTL.ZS", "FP.CPI.TOTL.ZG"]:
                        formatted = f"{value:.1f}%"
                    elif indicator == "NY.GDP.PCAP.CD":
                        formatted = f"${value:,.0f}"
                    else:
                        formatted = f"{value:,.2f}"

                    results.append(f"- **{name}** ({year}): {formatted}")
                else:
                    results.append(f"- **{name}**: No data available")
        except Exception:
            results.append(f"- {indicator}: Error fetching data")

    return "\n".join(results)


@mcp.tool()
async def compare_countries(
    countries: list[str],
    indicator: str = "NY.GDP.MKTP.CD"
) -> str:
    """Compare an economic indicator across multiple countries.

    Args:
        countries: List of country codes (e.g., ['USA', 'CHN', 'IND'])
        indicator: World Bank indicator code (default: GDP)

    Returns:
        Comparison table of the indicator across countries
    """
    indicator_names = {
        "NY.GDP.MKTP.CD": "GDP (current US$)",
        "SP.POP.TOTL": "Population",
        "NY.GDP.PCAP.CD": "GDP per Capita",
        "SL.UEM.TOTL.ZS": "Unemployment Rate (%)",
    }

    name = indicator_names.get(indicator, indicator)
    results = [f"**Comparing {name}**\n"]

    data_points = []
    for country in countries:
        url = f"{WORLDBANK_BASE}/country/{country}/indicator/{indicator}"
        params = {"format": "json", "per_page": 1, "mrv": 1}

        try:
            data = await fetch_json(url, params=params)
            if len(data) > 1 and data[1]:
                record = data[1][0]
                value = record.get("value")
                year = record.get("date")
                country_name = record.get("country", {}).get("value", country)

                if value is not None:
                    data_points.append((country_name, value, year))
        except Exception:
            pass

    # Sort by value descending
    data_points.sort(key=lambda x: x[1], reverse=True)

    for country_name, value, year in data_points:
        if indicator in ["NY.GDP.MKTP.CD"]:
            formatted = f"${value/1e12:.2f}T"
        elif indicator == "SP.POP.TOTL":
            formatted = f"{value/1e6:.1f}M"
        elif indicator == "NY.GDP.PCAP.CD":
            formatted = f"${value:,.0f}"
        else:
            formatted = f"{value:,.2f}"

        results.append(f"- {country_name}: {formatted} ({year})")

    return "\n".join(results)


@mcp.tool()
async def query_worldbank(
    country: str,
    indicator: str,
    params: dict | None = None
) -> dict:
    """Make a raw query to the World Bank API.

    Args:
        country: Country code (e.g., 'USA', 'all')
        indicator: World Bank indicator code (e.g., 'NY.GDP.MKTP.CD')
        params: Additional query parameters

    Returns:
        Raw JSON response from World Bank API
    """
    url = f"{WORLDBANK_BASE}/country/{country}/indicator/{indicator}"
    params = params or {}
    params["format"] = "json"
    return await fetch_json(url, params=params)
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/economics.py
git commit -m "feat: add World Bank economics tools"
```

---

## Task 8: Data.gov Tools

**Files:**
- Create: `src/mcp_govt_api/tools/datagov.py`

**Step 1: Create datagov.py**

```python
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
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/datagov.py
git commit -m "feat: add Data.gov tools"
```

---

## Task 9: EU Open Data Tools

**Files:**
- Create: `src/mcp_govt_api/tools/eu_data.py`

**Step 1: Create eu_data.py**

```python
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
```

**Step 2: Commit**

```bash
git add src/mcp_govt_api/tools/eu_data.py
git commit -m "feat: add EU Open Data tools"
```

---

## Task 10: Test the Server Locally

**Step 1: Install dependencies**

```bash
cd /home/hitsnorth/mcp-govt-api-free
pip install -e .
```

**Step 2: Test server starts**

```bash
python -m mcp_govt_api --help
```

Expected: Server help or runs without error.

**Step 3: Test with MCP inspector (if available)**

```bash
mcp dev src/mcp_govt_api/server.py
```

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: finalize MCP government API server v0.1.0"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project setup | pyproject.toml, __init__.py, __main__.py, README.md |
| 2 | Utilities | utils/config.py, utils/http.py |
| 3 | Server entry | server.py, tools/__init__.py |
| 4 | Weather tools | tools/weather.py (5 tools) |
| 5 | Census tools | tools/census.py (4 tools) |
| 6 | NASA tools | tools/nasa.py (4 tools) |
| 7 | Economics tools | tools/economics.py (3 tools) |
| 8 | Data.gov tools | tools/datagov.py (3 tools) |
| 9 | EU Data tools | tools/eu_data.py (3 tools) |
| 10 | Test locally | Verify server runs |

**Total: 23 tools** (16 granular + 7 general query)
