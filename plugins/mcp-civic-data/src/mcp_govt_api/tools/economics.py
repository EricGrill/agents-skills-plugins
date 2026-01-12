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
