from datetime import datetime

from fastmcp import FastMCP

from mt_washington_mcp.client import WeatherClient
from mt_washington_mcp.f6 import extract_f6_table
from mt_washington_mcp.models import OutlookReport, SummitConditions

mcp = FastMCP(
    "mt_washington_weather",
    instructions="Provides weather information from the Mt Washington Weather Observatory in NH.",
)

OUTLOOK_FIELDS = {"summit_outlook", "twenty_four_hour_statistics", "almanac"}


@mcp.resource("weather://current")
async def current_conditions() -> str:
    async with WeatherClient() as client:
        data = await client.get_weather()
        conditions = SummitConditions.model_validate(data["summitConditions"])
    return conditions.model_dump_json(indent=2)


@mcp.resource("weather://outlook/current")
async def current_outlook() -> str:
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.model_dump_json(indent=2, exclude=OUTLOOK_FIELDS)


@mcp.resource("weather://outlook/summit")
async def summit_outlook() -> str:
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.summit_outlook.model_dump_json(indent=2)


@mcp.resource("weather://outlook/statistics")
async def statistics() -> str:
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.twenty_four_hour_statistics.model_dump_json(indent=2)


@mcp.resource("weather://outlook/almanac")
async def almanac() -> str:
    async with WeatherClient() as client:
        data = await client.get_outlook()
        report = OutlookReport.model_validate(data)
    return report.almanac.model_dump_json(indent=2)


@mcp.resource("f6://current")
async def current_f6() -> bytes:
    today = datetime.now()
    async with WeatherClient() as client:
        data = await client.get_f6_pdf(today.year, today.month)
    return data

@mcp.resource("f6://{year}/{month}")
async def get_f6(year:int, month:int) -> bytes:
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
