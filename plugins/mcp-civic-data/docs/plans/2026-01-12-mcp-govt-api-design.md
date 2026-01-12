# MCP Government API Server Design

## Overview

An MCP server that wraps free government and open data APIs, providing Claude with access to weather, census, space, economics, and open government data.

## APIs Included

| Name | URL | Category | Key Required |
|------|-----|----------|--------------|
| NOAA | weather.gov | Weather | No |
| OpenWeather | openweathermap.org | Weather | Yes |
| Census API | census.gov | Demographics | No |
| NASA | api.nasa.gov | Space | Optional (higher limits) |
| World Bank | worldbank.org | Economics | No |
| Data.gov | data.gov | US Government | No |
| European Open Data | data.europa.eu | EU Government | No |

## Architecture

```
mcp-govt-api-free/
├── src/
│   └── mcp_govt_api/
│       ├── __init__.py
│       ├── server.py          # MCP server entry point
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── weather.py     # NOAA + OpenWeather tools
│       │   ├── census.py      # Census API tools
│       │   ├── nasa.py        # NASA API tools
│       │   ├── economics.py   # World Bank tools
│       │   ├── datagov.py     # Data.gov tools
│       │   └── eu_data.py     # European Open Data tools
│       └── utils/
│           ├── __init__.py
│           ├── http.py        # Shared HTTP client
│           └── config.py      # API key management
├── pyproject.toml
└── README.md
```

## Tools

### Granular Tools (16 total)

**Weather** (`weather.py`)
- `get_weather_forecast` - Current conditions and forecast for a US location (NOAA)
- `get_weather_alerts` - Active weather alerts by state/zone (NOAA)
- `get_global_weather` - Weather for any worldwide location (OpenWeather, requires key)

**Census** (`census.py`)
- `get_population` - Population data by state, county, or city
- `get_demographics` - Age, race, income breakdown for an area
- `get_housing_stats` - Housing data (median home value, rent, vacancy rates)

**NASA** (`nasa.py`)
- `get_astronomy_photo` - Astronomy Picture of the Day (with optional date)
- `get_mars_rover_photos` - Photos from Curiosity/Perseverance by date or sol
- `search_nasa_images` - Search NASA's image/video library

**Economics** (`economics.py`)
- `get_country_indicators` - GDP, population, poverty rate for any country
- `compare_countries` - Compare indicators across multiple countries

**Data.gov** (`datagov.py`)
- `search_datasets` - Search available datasets by keyword
- `get_dataset_info` - Metadata and download links for a specific dataset

**EU Data** (`eu_data.py`)
- `search_eu_datasets` - Search European open datasets
- `get_eu_dataset_info` - Metadata for EU datasets

### General Query Tools (7 total)

- `query_noaa` - Raw NOAA API access
- `query_census` - Raw Census API access
- `query_nasa` - Raw NASA API access
- `query_worldbank` - Raw World Bank API access
- `query_datagov` - Raw Data.gov CKAN API access
- `query_eu_data` - Raw EU Open Data Portal API access
- `query_openweather` - Raw OpenWeather API access (requires key)

## API Key Handling

Environment variables:
- `OPENWEATHER_API_KEY` - Required for OpenWeather tools
- `NASA_API_KEY` - Optional, increases rate limits

Graceful degradation: Server works without any keys. Tools requiring missing keys return clear error messages.

## Error Handling

- HTTP errors: Clear messages with status code and API name
- Rate limits: Suggest waiting, note limits
- Invalid parameters: Caught early with helpful messages
- Timeouts: 30 second default, configurable via `API_TIMEOUT`

## Installation

```bash
pip install mcp-govt-api-free
```

Claude Desktop config:
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
