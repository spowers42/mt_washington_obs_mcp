import re
from enum import StrEnum
from typing import cast

from pydantic import BaseModel, Field, field_validator, model_validator


NULL = "NULL"


class TemperatureUnit(StrEnum):
    FAHRENHEIT = "F"
    CELSIUS = "C"


class SpeedUnit(StrEnum):
    MPH = "mph"
    KPH = "km/hr"


class CardinalDirection(StrEnum):
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"


class Temperature(BaseModel):
    value: float
    unit: TemperatureUnit

    @field_validator("value", mode="before")
    @classmethod
    def parse_value(cls, value: str | float) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"-?[\d.]+", value)
        if match is None:
            raise ValueError(f"Cannot parse temperature from: {value!r}")
        return float(match.group())


class Speed(BaseModel):
    value: float
    unit: SpeedUnit

    @field_validator("value", mode="before")
    @classmethod
    def parse_value(cls, value: str | float) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"-?[\d.]+", value)
        if match is None:
            raise ValueError(f"Cannot parse speed from: {value!r}")
        return float(match.group())


class Direction(BaseModel):
    degrees: int
    cardinal: CardinalDirection

    @model_validator(mode="before")
    @classmethod
    def parse_string(cls, data: str | dict) -> dict:
        if isinstance(data, dict):
            return data
        match = re.search(r"(\d+)°\(([A-Z]{1,3})\)", data)
        if match is None:
            raise ValueError(f"Cannot parse direction from: {data!r}")
        return {"degrees": int(match.group(1)), "cardinal": match.group(2)}


class Wind(BaseModel):
    speed: Speed
    direction: Direction | None = None
    gust: Speed | None = None


class UnitsData(BaseModel):
    temperature: Temperature
    wind: Wind
    wind_chill: Temperature | None = None

    @model_validator(mode="before")
    @classmethod
    def from_flat_api(cls, data: dict) -> dict:
        if not isinstance(data, dict) or not isinstance(data.get("Temperature"), str):
            return data

        def _speed(value: str) -> dict[str, object]:
            unit = SpeedUnit.KPH if "km/hr" in value else SpeedUnit.MPH
            return {"value": value, "unit": unit}

        def _temp(value: str) -> dict[str, object]:
            unit = TemperatureUnit.CELSIUS if "°C" in value else TemperatureUnit.FAHRENHEIT
            return {"value": value, "unit": unit}

        wind: dict[str, object] = {"speed": _speed(cast(str, data["Wind"]))}

        gust = data.get("Gust")
        if gust not in (NULL, None, ""):
            wind["gust"] = _speed(cast(str, gust))

        wind_chill = data.get("WindChill")
        if wind_chill in (NULL, None, ""):
            wind_chill = None
        else:
            wind_chill = _temp(cast(str, wind_chill))

        return {
            "temperature": _temp(cast(str, data["Temperature"])),
            "wind": wind,
            "wind_chill": wind_chill,
        }


class SummitConditions(BaseModel):
    model_config = {"populate_by_name": True}

    last_updated: str = Field(alias="LastUpdated")
    expiration_date_time: str = Field(alias="ExpirationDateTime")
    imperial: UnitsData = Field(alias="Imperial")
    metric: UnitsData = Field(alias="Metric")
    direction: Direction = Field(alias="Direction")
    metar: str


class StatsGroup(BaseModel):
    max_temperature: str = Field(alias="MaxTemperature")
    min_temperature: str = Field(alias="MinTemperature")
    peak_wind_gust: str = Field(alias="PeakWindGust")
    avg_wind_speed: str = Field(alias="AvgWindSpeed")
    liquid_precipitation: str = Field(alias="LiquidPrecipitation")
    snowfall: str = Field(alias="Snowfall")


class TwentyFourHourStatistics(BaseModel):
    model_config = {"populate_by_name": True}

    imperial: StatsGroup = Field(alias="Imperial")
    metric: StatsGroup = Field(alias="Metric")


class AlmanacGroup(BaseModel):
    snowfall_this_month: str = Field(alias="SnowfallThisMonth")
    record_high_temperature: str = Field(alias="RecordHighTemperature")
    record_low_temperature: str = Field(alias="RecordLowTemperature")
    avg_daily_temperature: str = Field(alias="AvgDailyTemperature")
    avg_monthly_temperature: str = Field(alias="AvgMonthlyTemperature")
    avg_monthly_melted_precipitation: str = Field(alias="AvgMonthlyMeltedPrecipitation")
    avg_monthly_snowfall: str = Field(alias="AvgMonthlySnowfall")
    avg_monthly_wind: str = Field(alias="AvgMonthlyWind")


class Almanac(BaseModel):
    model_config = {"populate_by_name": True}

    imperial: AlmanacGroup = Field(alias="Imperial")
    metric: AlmanacGroup = Field(alias="Metric")
    sunrise: str = Field(alias="Sunrise")
    sunset: str = Field(alias="Sunset")
    total_length_of_day: str = Field(alias="TotalLengthOfDay")


class ForecastPeriodValues(BaseModel):
    temperature: str = Field(alias="Temperature")
    wind: str = Field(alias="Wind")
    wind_chill: str = Field(alias="WindChill")


class ForecastPeriod(BaseModel):
    model_config = {"populate_by_name": True}

    period: str = Field(alias="Period")
    synopsis: str = Field(alias="Synopsis")
    high_low: str = Field(alias="HighLow")
    imperial: ForecastPeriodValues = Field(alias="Imperial")
    metric: ForecastPeriodValues = Field(alias="Metric")


class Outlook(BaseModel):
    model_config = {"populate_by_name": True}

    alert: str = Field(alias="Alert")
    alert_expiration_date_time: str = Field(alias="AlertExpirationDateTime")
    discussion: str | None = Field(None, alias="Discussion")
    forecast1: ForecastPeriod = Field(alias="Forecast1")
    forecast2: ForecastPeriod = Field(alias="Forecast2")
    forecast3: ForecastPeriod = Field(alias="Forecast3")
    forecast4: ForecastPeriod = Field(alias="Forecast4")


class OutlookReport(BaseModel):
    model_config = {"populate_by_name": True}

    last_updated: str = Field(alias="LastUpdated")
    feed_expiration_date_time: str = Field(alias="FeedExpirationDateTime")
    forecaster_name: str = Field(alias="ForecasterName")
    forecaster_job_title: str = Field(alias="ForecastJobTitle")
    summit_conditions: dict = Field(alias="SummitConditions")
    twenty_four_hour_statistics: TwentyFourHourStatistics = Field(alias="TwentyfourHourStatistics")
    almanac: Almanac = Field(alias="Almanac")
    summit_outlook: Outlook = Field(alias="SummitOutlook")
    valley_outlook: Outlook = Field(alias="ValleyOutlook")
    north_outlook: Outlook | None = Field(None, alias="NorthOutlook")
    south_outlook: Outlook | None = Field(None, alias="SouthOutlook")
