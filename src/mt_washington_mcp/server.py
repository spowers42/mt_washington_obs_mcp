from datetime import datetime

from fastmcp import FastMCP

from mt_washington_mcp.client import WeatherClient
from mt_washington_mcp.f6 import extract_f6_table, list_f6_available
from mt_washington_mcp.models import OutlookReport, SummitConditions

mcp = FastMCP(
    "mt_washington_weather",
    instructions="Provides weather information from the Mt Washington Weather Observatory in NH.",
)

OUTLOOK_FIELDS = {"summit_outlook", "twenty_four_hour_statistics", "almanac"}


@mcp.resource("weather://current")
async def current_conditions() -> str:
    """Real-time summit weather conditions.

    Returns current temperature, wind speed/gusts, wind direction,
    wind chill, and METAR data in both imperial and metric units.
    """
    async with WeatherClient() as client:
        data = await client.get_weather()
        conditions = SummitConditions.model_validate(data["summitConditions"])
    return conditions.model_dump_json(indent=2)


@mcp.resource("weather://outlook/current")
async def current_outlook() -> str:
    """Full forecast outlook metadata.

    Returns the forecast header info including last updated time,
    forecaster name and title. Excludes the detailed sub-sections
    (summit forecast, 24h statistics, almanac) which have their
    own dedicated resource URIs.
    """
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.model_dump_json(indent=2, exclude=OUTLOOK_FIELDS)


@mcp.resource("weather://outlook/summit")
async def summit_outlook() -> str:
    """Higher Summits Forecast.

    Provides the summit-level multi-period forecast with
    temperature, wind, and wind chill for up to 4 forecast
    periods, plus a synopsis discussion.
    """
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.summit_outlook.model_dump_json(indent=2)


@mcp.resource("weather://outlook/valley")
async def valley_outlook() -> str:
    """Valley Forecast.

    Provides the valley-level multi-period forecast with
    temperature, wind, and wind chill for up to 4 forecast
    periods, plus a synopsis discussion.
    """
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.valley_outlook.model_dump_json(indent=2)


@mcp.resource("weather://outlook/statistics")
async def statistics() -> str:
    """Past 24-hour weather statistics.

    Returns maximum/minimum temperature, peak wind gust,
    average wind speed, liquid precipitation equivalent,
    and snowfall for the past 24 hours (imperial and metric).
    """
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.twenty_four_hour_statistics.model_dump_json(indent=2)


@mcp.resource("weather://outlook/almanac")
async def almanac() -> str:
    """Today's almanac data.

    Returns records, monthly snowfall/precipitation averages,
    average temperatures and wind, plus sunrise, sunset, and
    day length for today's date.
    """
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.almanac.model_dump_json(indent=2)


@mcp.resource("f6://current")
async def current_f6() -> bytes:
    """Current month's F6 PDF form.

    Returns the raw PDF bytes for the current month's
    F6 weather observation form from Mt Washington Observatory.
    """
    today = datetime.now()
    async with WeatherClient() as client:
        data = await client.get_f6_pdf(today.year, today.month)
    return data


@mcp.resource("f6://{year}/{month}")
async def get_f6(year: int, month: int) -> bytes:
    """F6 PDF form for a specific year and month.

    Returns the raw PDF bytes for the F6 weather observation
    form from Mt Washington Observatory for the given date.

    Args:
        year: Calendar year (2005–present).
        month: Month number (1–12).
    """
    async with WeatherClient() as client:
        data = await client.get_f6_pdf(year, month)
    return data


@mcp.tool()
async def extract_f6_csv(year: int | None = None, month: int | None = None) -> str:
    """Extract the daily data table from an F6 PDF form as CSV.

    Fetches the F6 PDF for the given year/month and parses the
    main data table (temperature, precipitation, wind, sunshine,
    sky cover, weather occurrences) into CSV format.

    Args:
        year: Calendar year (2005–present). Defaults to current year.
        month: Month number (1–12). Defaults to current month.
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    async with WeatherClient() as client:
        pdf = await client.get_f6_pdf(year, month)
    return extract_f6_table(pdf)


@mcp.tool()
async def list_f6_forms() -> str:
    """List all available F6 form year/month combinations as CSV.

    F6 forms are available from January 2005 through the current month.
    """
    rows = ["year,month"]
    for year, month in list_f6_available():
        rows.append(f"{year},{month:02d}")
    return "\n".join(rows)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
