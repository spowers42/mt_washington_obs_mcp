"""Tests for server resource output format."""

import json
from pathlib import Path
from unittest.mock import patch


from mt_washington_mcp.models import OutlookReport, SummitConditions
from mt_washington_mcp.server import current_f6, get_f6

FIXTURES = Path(__file__).parent / "fixtures"


class TestCurrentConditionsResource:
    """Validates JSON output of the weather://current resource."""

    def test_output_is_valid_json(self):
        with open(FIXTURES / "weather.json") as f:
            raw = json.load(f)
        sc = SummitConditions.model_validate(raw["summitConditions"])
        output = sc.model_dump_json(indent=2)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_top_level_fields(self):
        with open(FIXTURES / "weather.json") as f:
            raw = json.load(f)
        sc = SummitConditions.model_validate(raw["summitConditions"])
        output = json.loads(sc.model_dump_json())
        assert "last_updated" in output
        assert "expiration_date_time" in output
        assert "imperial" in output
        assert "metric" in output
        assert "direction" in output
        assert "metar" in output

    def test_nested_units_structure(self):
        with open(FIXTURES / "weather.json") as f:
            raw = json.load(f)
        sc = SummitConditions.model_validate(raw["summitConditions"])
        output = json.loads(sc.model_dump_json())

        imperial = output["imperial"]
        assert "temperature" in imperial
        assert "wind" in imperial
        assert "wind_chill" in imperial
        assert "value" in imperial["temperature"]
        assert "unit" in imperial["temperature"]
        assert "speed" in imperial["wind"]

    def test_numeric_values(self):
        with open(FIXTURES / "weather.json") as f:
            raw = json.load(f)
        sc = SummitConditions.model_validate(raw["summitConditions"])
        output = json.loads(sc.model_dump_json())

        temp = output["imperial"]["temperature"]
        assert isinstance(temp["value"], float)
        assert isinstance(temp["unit"], str)

        speed = output["imperial"]["wind"]["speed"]
        assert isinstance(speed["value"], float)
        assert isinstance(speed["unit"], str)

    def test_metric_and_imperial_both_present(self):
        with open(FIXTURES / "weather.json") as f:
            raw = json.load(f)
        sc = SummitConditions.model_validate(raw["summitConditions"])
        output = json.loads(sc.model_dump_json())

        imperial_temp = output["imperial"]["temperature"]["value"]
        metric_temp = output["metric"]["temperature"]["value"]
        assert isinstance(imperial_temp, float)
        assert isinstance(metric_temp, float)
        assert imperial_temp != metric_temp


class TestF6Resource:
    """Validates f6:// resources return bytes."""

    @patch(
        "mt_washington_mcp.server.WeatherClient.get_f6_pdf",
        return_value=b"%PDF-1.4 mock data",
    )
    async def test_f6_current_returns_bytes(self, mock_get_f6):
        result = await current_f6()
        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")

    @patch(
        "mt_washington_mcp.server.WeatherClient.get_f6_pdf",
        return_value=b"%PDF-1.4 mock data",
    )
    async def test_f6_by_date_returns_bytes(self, mock_get_f6):
        result = await get_f6(2026, 6)
        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")

    @patch("mt_washington_mcp.server.WeatherClient.get_f6_pdf")
    async def test_f6_by_date_passes_year_month(self, mock_get_f6):
        mock_get_f6.return_value = b"mock"
        await get_f6(2025, 3)
        mock_get_f6.assert_called_once_with(2025, 3)

    @patch("mt_washington_mcp.server.WeatherClient.get_f6_pdf")
    async def test_f6_current_passes_current_year_month(self, mock_get_f6):
        """current_f6 should pass datetime.now().year/month to get_f6_pdf."""
        from datetime import datetime

        mock_get_f6.return_value = b"mock"
        await current_f6()
        now = datetime.now()
        mock_get_f6.assert_called_once_with(now.year, now.month)


class TestValleyOutlookResource:
    """Validates JSON output of the weather://outlook/valley resource."""

    def test_output_is_valid_json(self):
        with open(FIXTURES / "outlook.json") as f:
            raw = json.load(f)
        report = OutlookReport.model_validate(raw)
        output = report.valley_outlook.model_dump_json(indent=2)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_top_level_fields(self):
        with open(FIXTURES / "outlook.json") as f:
            raw = json.load(f)
        report = OutlookReport.model_validate(raw)
        output = json.loads(report.valley_outlook.model_dump_json())
        assert "alert" in output
        assert "forecast1" in output
        assert "forecast2" in output
        assert "forecast3" in output
        assert "forecast4" in output

    def test_forecast_period_structure(self):
        with open(FIXTURES / "outlook.json") as f:
            raw = json.load(f)
        report = OutlookReport.model_validate(raw)
        output = json.loads(report.valley_outlook.model_dump_json())
        f1 = output["forecast1"]
        assert "period" in f1
        assert "synopsis" in f1
        assert "high_low" in f1
        assert "imperial" in f1
        assert "metric" in f1

    def test_forecast_has_discussion(self):
        with open(FIXTURES / "outlook.json") as f:
            raw = json.load(f)
        report = OutlookReport.model_validate(raw)
        assert report.valley_outlook.discussion is not None
