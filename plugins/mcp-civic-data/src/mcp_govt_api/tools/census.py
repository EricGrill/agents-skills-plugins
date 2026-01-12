from mcp_govt_api.server import mcp
from mcp_govt_api.utils.http import fetch_json


CENSUS_BASE = "https://api.census.gov/data"
# American Community Survey 5-Year Estimates (most recent)
ACS_YEAR = "2022"
ACS_DATASET = f"{CENSUS_BASE}/{ACS_YEAR}/acs/acs5"

# State FIPS lookup for all US states + DC + PR
STATE_FIPS = {
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


@mcp.tool()
async def get_population(state: str, county: str = "") -> str:
    """Get population data for a US state or county.

    Args:
        state: Two-letter state code (e.g., 'CA', 'TX') or state FIPS code
        county: Optional county name or FIPS code

    Returns:
        Population statistics from the American Community Survey
    """
    state_code = state.upper()
    fips = STATE_FIPS.get(state_code, state_code)

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
    state_code = state.upper()
    fips = STATE_FIPS.get(state_code, state_code)

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
    state_code = state.upper()
    fips = STATE_FIPS.get(state_code, state_code)

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
