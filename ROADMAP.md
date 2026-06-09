# Mt Washington Observatory MCP Server — Roadmap

A collaborative tutorial-style build of an MCP server using FastMCP that exposes weather data from the Mt Washington Observatory.

---

## Phase 1: Foundation ✅

- [x] Add FastMCP (`mcp`) and `httpx` as project dependencies
- [x] Organize into a `src/mt_washington_mcp/` package layout
- [x] Set up entrypoints (`mtw-obs-mcp` CLI + `python -m mt_washington_mcp`)

## Phase 2: Data Layer ✅

### Data Sources

Both endpoints return JSON served from `mountwashington.org`:

| Endpoint | Contents |
|---|---|---|
| `GET /uploads/json/weather.JSON` | Real-time summit conditions (temp, wind, gust, wind chill, direction, METAR) |
| `GET /uploads/json/outlook.JSON` | Full forecast package |
| `GET /uploads/pdf/forms/{year}/{month:02d}.pdf` | **F6 forms**: monthly PDF with daily data. Years 2005–present |

**`outlook.JSON` structure:**
- `SummitConditions` — detailed current conditions (temp, wind, visibility, pressure, ground conditions)
- `TwentyfourHourStatistics` — past 24h: max/min temp, peak gust, avg wind, precip, snowfall (Imperial + Metric)
- `Almanac` — records, monthly averages, sunrise/sunset
- `SummitOutlook` — summit / **Higher Summits Forecast**: discussion + 4-period forecast
- `ValleyOutlook` / `NorthOutlook` / `SouthOutlook` — regional outlooks

### Implementation ✅

- [x] `client.py`: async `WeatherClient` with `get_weather`, `get_outlook`, `get_f6_pdf` + context manager
- [x] `models.py`: Pydantic models for all response shapes (`Temperature`, `Speed`, `Direction`, `Wind`, `UnitsData`, `SummitConditions`, `StatsGroup`, `TwentyFourHourStatistics`, `AlmanacGroup`, `Almanac`, `ForecastPeriodValues`, `ForecastPeriod`, `Outlook`, `OutlookReport`)
- [x] Flat string parsing via `UnitsData.from_flat_api` model_validator
- [x] Graceful null handling (`"NULL"` strings)
- [x] 29 unit tests for models (inline + fixture-based)
- [x] 8 client tests using `httpx.MockTransport` (no network calls)

## Phase 3: MCP Server ✅

Resources are the primary data access mechanism. Tools will be added later for processing (e.g., parsing F6 PDFs into JSON).

### Resources

| URI | Description | Model |
|---|---|---|
| `weather://current` | Current summit conditions | `SummitConditions` |
| `weather://outlook/current` | Full outlook report (metadata only) | `OutlookReport` (excludes sub-sections) |
| `weather://outlook/summit` | Higher Summits Forecast | `Outlook` |
| `weather://outlook/statistics` | Past 24h statistics | `TwentyFourHourStatistics` |
| `weather://outlook/almanac` | Today's almanac data | `Almanac` |
| `f6://current` | Current month's F6 PDF (raw bytes) | PDF endpoint |
| `f6://{year}/{month}` | F6 PDF for given year/month (raw bytes) | PDF endpoint |

### Tools

| Tool | Description | Data source |
|---|---|---|
| `extract_f6_csv` | Extract F6 PDF daily data table as CSV | `f6://{year}/{month}` resource |
| `list_available_f6` | List years/months with available F6 forms | Derived from PDF URL pattern |

### Implementation ✅

- [x] FastMCP server with all `weather://` and `f6://` resources
- [x] `main()` wired to `mcp.run()`
- [x] `extract_f6_csv` tool for PDF table extraction
- [x] 9 tests: 5 for JSON resource output + 4 for F6 PDF resource output
- [x] 12 tests for F6 CSV extraction from fixture PDF

## Phase 4: Quality & DX ✅

- [x] `pytest` tests with fixture-based mocking (no network)
- [x] `ruff` linting
- [x] `mypy` type-checking
- [x] `Taskfile.yml` with `test`, `lint`, `lint-fix`, `typecheck`, `check` commands

---

## Guiding Principles

- **You drive the keyboard** — I explain, you code, I help when asked
- Each step builds on the last; we test as we go
- Questions and detours are welcome
