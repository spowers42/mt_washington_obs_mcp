"""Tests for F6 PDF table extraction."""

import csv
import io
from pathlib import Path

import pytest

from mt_washington_mcp.f6 import extract_f6_table

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def f6_csv() -> str:
    with open(FIXTURES / "f6_2026_06.pdf", "rb") as f:
        return extract_f6_table(f.read())


def _parse(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(csv_text)))


class TestExtractF6Table:
    def test_returns_csv_string(self, f6_csv):
        assert isinstance(f6_csv, str)
        assert f6_csv.startswith("month,year")

    def test_has_all_csv_headers(self, f6_csv):
        reader = csv.DictReader(io.StringIO(f6_csv))
        expected = [
            "month", "year",
            "day", "max_temp_f", "min_temp_f", "avg_temp_f",
            "norm_temp_f", "depart_temp_f", "heat_degree_days",
            "cool_degree_days", "precip_total_in", "snow_ice_in",
            "snow_ice_ground_in", "avg_wind_speed_mph",
            "fastest_mile_speed_mph", "fastest_mile_direction",
            "sunshine_total_min", "sunshine_percent",
            "sky_cover_tenths", "weather_occurrence",
        ]
        assert reader.fieldnames == expected

    def test_month_and_year_in_csv(self, f6_csv):
        rows = _parse(f6_csv)
        for row in rows:
            assert row["month"] == "JUNE"
            assert row["year"] == "2026"

    def test_has_30_days(self, f6_csv):
        rows = _parse(f6_csv)
        assert len(rows) == 30
        assert rows[-1]["day"] == "30"

    def test_day_numbers_sequential(self, f6_csv):
        rows = _parse(f6_csv)
        days = [int(r["day"]) for r in rows]
        assert days == list(range(1, 31))

    def test_day_1_has_data(self, f6_csv):
        rows = _parse(f6_csv)
        d1 = rows[0]
        assert d1["max_temp_f"] == "36"
        assert d1["min_temp_f"] == "26"
        assert d1["avg_temp_f"] == "31"
        assert d1["precip_total_in"] == "0.01"

    def test_day_7_storm_data(self, f6_csv):
        rows = _parse(f6_csv)
        d7 = rows[6]
        assert d7["max_temp_f"] == "49"
        assert d7["precip_total_in"] == "0.56"
        assert d7["avg_wind_speed_mph"] == "44.5"
        assert d7["fastest_mile_speed_mph"] == "88"

    def test_future_days_have_empty_cells(self, f6_csv):
        rows = _parse(f6_csv)
        for row in rows:
            day = int(row["day"])
            if day >= 9:
                assert row["max_temp_f"] == ""
                assert row["min_temp_f"] == ""
                assert row["avg_temp_f"] == ""
                assert row["norm_temp_f"] != ""

    def test_weather_occurrence_column(self, f6_csv):
        rows = _parse(f6_csv)
        assert rows[0]["weather_occurrence"] == "1246"
        assert rows[5]["weather_occurrence"] == "123"
        assert rows[6]["weather_occurrence"] == "12"

    def test_sunshine_data(self, f6_csv):
        rows = _parse(f6_csv)
        assert rows[0]["sunshine_total_min"] == "405"
        assert rows[0]["sunshine_percent"] == "44"
        assert rows[5]["sunshine_total_min"] == "0"
        assert rows[5]["sunshine_percent"] == "0"

    def test_fastest_mile_direction(self, f6_csv):
        rows = _parse(f6_csv)
        assert rows[0]["fastest_mile_direction"] == "310 (NW)"
        assert rows[3]["fastest_mile_direction"] == "290 (W)"

    def test_empty_fields_for_missing_data(self, f6_csv):
        rows = _parse(f6_csv)
        for r in rows[8:]:
            assert r["avg_temp_f"] == ""
            assert r["depart_temp_f"] == ""
            assert r["heat_degree_days"] == ""
