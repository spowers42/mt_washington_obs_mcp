import csv
import io
from datetime import datetime
from typing import Iterator

import pdfplumber

CSV_HEADERS = [
    "day",
    "max_temp_f",
    "min_temp_f",
    "avg_temp_f",
    "norm_temp_f",
    "depart_temp_f",
    "heat_degree_days",
    "cool_degree_days",
    "precip_total_in",
    "snow_ice_in",
    "snow_ice_ground_in",
    "avg_wind_speed_mph",
    "fastest_mile_speed_mph",
    "fastest_mile_direction",
    "sunshine_total_min",
    "sunshine_percent",
    "sky_cover_tenths",
    "weather_occurrence",
]


def _parse_header(table: list[list[str | None]]) -> tuple[str, int, int]:
    month = year = ""
    for row in table[:3]:
        for cell in row:
            if cell and cell.startswith("MONTH\n"):
                month = cell.split("\n")[1].strip()
            if cell and cell.startswith("YEAR\n"):
                year = cell.split("\n")[1].strip()
    if not month or not year:
        today = datetime.now()
        month = month or today.strftime("%B").upper()
        year = year or str(today.year)
    month_names = [
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
    ]
    month_num = month_names.index(month.upper()) + 1 if month.upper() in month_names else 1
    return month.upper(), month_num, int(year)


def _clean(value: str | None) -> str:
    if value is None or value.strip() == "" or value.strip() == "None":
        return ""
    return value.strip()


def extract_f6_table(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        tables = pdf.pages[0].extract_tables()
        table = tables[0]

    month_name, month_num, year = _parse_header(table)

    data_rows: list[list[str]] = []
    for raw_row in table[6:]:
        day_str = _clean(raw_row[0])
        if not day_str.isdigit():
            continue
        data_rows.append([_clean(c) for c in raw_row[:18]])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["month", "year"] + CSV_HEADERS)
    for clean_row in data_rows:
        writer.writerow([month_name, year] + clean_row)

    return buf.getvalue()


def list_f6_available() -> Iterator[tuple[int, int]]:
    now = datetime.now()
    for year in range(2005, now.year + 1):
        end_month = now.month if year == now.year else 12
        for month in range(1, end_month + 1):
            yield (year, month)
