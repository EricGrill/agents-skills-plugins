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
