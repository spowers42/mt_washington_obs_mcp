import json
from pathlib import Path

import pytest

from mt_washington_mcp.models import (
    Almanac,
    Direction,
    OutlookReport,
    Speed,
    SpeedUnit,
    SummitConditions,
    Temperature,
    TemperatureUnit,
    TwentyFourHourStatistics,
    UnitsData,
    Wind,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestTemperature:
    def test_basic_fahrenheit(self):
        t = Temperature.model_validate({"value": "56°F", "unit": "F"})
        assert t.value == 56.0
        assert t.unit == TemperatureUnit.FAHRENHEIT

    def test_basic_celsius(self):
        t = Temperature.model_validate({"value": "9 °C", "unit": "C"})
        assert t.value == 9.0
        assert t.unit == TemperatureUnit.CELSIUS

    def test_negative_fahrenheit(self):
        t = Temperature.model_validate({"value": "-10 °F", "unit": "F"})
        assert t.value == -10.0
        assert t.unit == TemperatureUnit.FAHRENHEIT

    def test_decimal_celsius(self):
        t = Temperature.model_validate({"value": "7.2°C", "unit": "C"})
        assert t.value == 7.2
        assert t.unit == TemperatureUnit.CELSIUS

    def test_string_comparison(self):
        t = Temperature.model_validate({"value": "56°F", "unit": "F"})
        assert t.unit == "F"
        assert t.unit == TemperatureUnit.FAHRENHEIT

    def test_repr(self):
        t = Temperature(value=56.0, unit=TemperatureUnit.FAHRENHEIT)
        label = f"{t.value}°{t.unit}"
        assert label == "56.0°F"

    def test_invalid_unit(self):
        with pytest.raises(ValueError):
            Temperature.model_validate({"value": "300 K", "unit": "K"})


class TestSpeed:
    def test_mph(self):
        s = Speed.model_validate({"value": "24 mph", "unit": "mph"})
        assert s.value == 24.0
        assert s.unit == SpeedUnit.MPH

    def test_kph(self):
        s = Speed.model_validate({"value": "38 km/hr", "unit": "km/hr"})
        assert s.value == 38.0
        assert s.unit == SpeedUnit.KPH

    def test_high_speed(self):
        s = Speed.model_validate({"value": "1402.9 mph", "unit": "mph"})
        assert s.value == 1402.9
        assert s.unit == SpeedUnit.MPH


class TestDirection:
    def test_west(self):
        d = Direction.model_validate("280°(W)")
        assert d.degrees == 280
        assert d.cardinal == "W"

    def test_northwest(self):
        d = Direction.model_validate("310°(NW)")
        assert d.degrees == 310
        assert d.cardinal == "NW"

    def test_south(self):
        d = Direction.model_validate("180°(S)")
        assert d.degrees == 180
        assert d.cardinal == "S"


class TestWind:
    def test_wind_with_gust_and_direction(self):
        w = Wind.model_validate({
            "speed": {"value": "24 mph", "unit": "mph"},
            "gust": {"value": "32 mph", "unit": "mph"},
            "direction": "280°(W)",
        })
        assert w.speed.value == 24.0
        assert w.speed.unit == SpeedUnit.MPH
        assert w.gust is not None
        assert w.gust.value == 32.0
        assert w.direction is not None
        assert w.direction.degrees == 280
        assert w.direction.cardinal == "W"

    def test_wind_without_gust(self):
        w = Wind.model_validate({
            "speed": {"value": "12 mph", "unit": "mph"},
            "direction": "270°(W)",
        })
        assert w.speed.value == 12.0
        assert w.gust is None
        assert w.direction is not None
        assert w.direction.degrees == 270


class TestUnitsData:
    def test_imperial_with_gust(self):
        u = UnitsData.model_validate({
            "Temperature": "56°F",
            "Wind": "24 mph",
            "Gust": "32 mph",
            "WindChill": "NULL",
        })
        assert u.temperature.value == 56.0
        assert u.temperature.unit == TemperatureUnit.FAHRENHEIT
        assert u.wind.speed.value == 24.0
        assert u.wind.speed.unit == SpeedUnit.MPH
        assert u.wind.gust is not None
        assert u.wind.gust.value == 32.0
        assert u.wind_chill is None

    def test_metric_no_gust(self):
        u = UnitsData.model_validate({
            "Temperature": "13°C",
            "Wind": "38 km/hr",
            "Gust": "NULL",
            "WindChill": "9°C",
        })
        assert u.temperature.value == 13.0
        assert u.temperature.unit == TemperatureUnit.CELSIUS
        assert u.wind.speed.value == 38.0
        assert u.wind.speed.unit == SpeedUnit.KPH
        assert u.wind.gust is None
        assert u.wind_chill is not None
        assert u.wind_chill.value == 9.0

    def test_direct_construction(self):
        u = UnitsData(
            temperature=Temperature(value=56.0, unit=TemperatureUnit.FAHRENHEIT),
            wind=Wind(
                speed=Speed(value=24.0, unit=SpeedUnit.MPH),
                direction=Direction.model_validate("280°(W)"),
            ),
        )
        assert u.temperature.value == 56.0
        assert u.wind.speed.value == 24.0


class TestSummitConditions:
    def test_full_parse(self):
        sc = SummitConditions.model_validate({
            "LastUpdated": "2026-06-04 15:17:00",
            "ExpirationDateTime": "2026-06-04 16:17:00",
            "Imperial": {
                "Temperature": "56°F",
                "Wind": "24 mph",
                "Gust": "32 mph",
                "WindChill": "NULL",
            },
            "Metric": {
                "Temperature": "13°C",
                "Wind": "38 km/hr",
                "Gust": "52 km/hr",
                "WindChill": "NULL",
            },
            "Direction": "270°(W)",
            "metar": "KMWN 041853Z 29019G26KT 70SM",
        })
        assert sc.last_updated == "2026-06-04 15:17:00"
        assert sc.imperial.temperature.value == 56.0
        assert sc.metric.temperature.value == 13.0
        assert sc.direction.degrees == 270
        assert sc.direction.cardinal == "W"
        assert sc.metar.startswith("KMWN")


class TestSummitConditionsFromFixture:
    """Tests SummitConditions + UnitsData using a real API snapshot."""

    @pytest.fixture
    def data(self) -> dict:
        with open(FIXTURES / "weather.json") as f:
            return json.load(f)["summitConditions"]

    def test_parses_top_level_fields(self, data: dict):
        sc = SummitConditions.model_validate(data)
        assert sc.last_updated
        assert sc.expiration_date_time
        assert sc.metar.startswith("KMWN")

    def test_imperial_units(self, data: dict):
        sc = SummitConditions.model_validate(data)
        assert sc.imperial.temperature.unit == "F"
        assert sc.imperial.wind.speed.unit == "mph"

    def test_metric_units(self, data: dict):
        sc = SummitConditions.model_validate(data)
        assert sc.metric.temperature.unit == "C"
        assert sc.metric.wind.speed.unit == SpeedUnit.KPH

    def test_direction(self, data: dict):
        sc = SummitConditions.model_validate(data)
        assert 0 <= sc.direction.degrees <= 360

    def test_wind_chill_is_optional(self, data: dict):
        sc = SummitConditions.model_validate(data)
        assert sc.imperial.wind_chill is None or isinstance(sc.imperial.wind_chill, Temperature)


class TestOutlookReportFromFixture:
    """Tests full OutlookReport model using a real API snapshot."""

    @pytest.fixture
    def report(self) -> OutlookReport:
        with open(FIXTURES / "outlook.json") as f:
            return OutlookReport.model_validate(json.load(f))

    def test_metadata(self, report: OutlookReport):
        assert report.last_updated
        assert report.forecaster_name
        assert report.forecaster_job_title

    def test_24hr_statistics(self, report: OutlookReport):
        stats = report.twenty_four_hour_statistics
        assert isinstance(stats, TwentyFourHourStatistics)
        assert stats.imperial.max_temperature
        assert stats.metric.max_temperature

    def test_almanac(self, report: OutlookReport):
        assert isinstance(report.almanac, Almanac)
        assert report.almanac.sunrise
        assert report.almanac.sunset

    def test_summit_outlook(self, report: OutlookReport):
        outlook = report.summit_outlook
        assert outlook.discussion
        for f in [outlook.forecast1, outlook.forecast2, outlook.forecast3, outlook.forecast4]:
            assert f.period
            assert f.synopsis
            assert f.imperial.temperature

    def test_valley_outlook(self, report: OutlookReport):
        assert report.valley_outlook.discussion
        assert report.valley_outlook.forecast1.period
