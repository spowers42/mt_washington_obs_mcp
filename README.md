# Mt Washington Observatory MCP Server

An MCP (Model Context Protocol) server that exposes real-time weather data from the [Mt Washington Observatory](https://mountwashington.org) as resources, built with [FastMCP](https://github.com/jlowin/fastmcp).

## Data Sources

| Endpoint | Contents |
|---|---|
| `/uploads/json/weather.JSON` | Real-time summit conditions (temp, wind, gusts, direction, METAR) |
| `/uploads/json/outlook.JSON` | Full forecast package (summit/valley outlook, 24h statistics, almanac) |
| `/uploads/pdf/forms/{year}/{month:02d}.pdf` | F6 monthly PDF forms (2005–present) |

## Quickstart

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Install

```bash
git clone <repo>
cd mt_washington_obs_mcp
uv sync
```

### Run

```bash
uv run mtw-obs-mcp
```

Or equivalently:

```bash
uv run python -m mt_washington_mcp
```

The server starts on stdio transport (standard for MCP). Connect it to an MCP client like Claude Desktop or [opencode](https://opencode.ai).

## Resources

All data is available as MCP resources:

| URI | Returns | Description |
|---|---|---|
| `weather://current` | JSON | Current summit temperature, wind, gusts, direction, METAR |
| `weather://outlook/current` | JSON | Full outlook metadata (excludes sub-sections with dedicated URIs) |
| `weather://outlook/summit` | JSON | Higher Summits Forecast with 4-period discussion |
| `weather://outlook/statistics` | JSON | Past 24h: max/min temp, peak gust, precip, snowfall |
| `weather://outlook/almanac` | JSON | Records, monthly averages, sunrise/sunset |
| `f6://current` | PDF (bytes) | Current month's F6 form |
| `f6://{year}/{month}` | PDF (bytes) | F6 form for a specific year/month |

## Development

### Tests

```bash
uv run pytest
```

All tests use fixture snapshots — no network calls.

### Lint & typecheck

```bash
uv run ruff check .
uv run mypy src/mt_washington_mcp/
```

Or use the `Taskfile.yml`:

```bash
task check    # test + lint + typecheck
task test
task lint
task typecheck
```

### Project structure

```
mt_washington_obs_mcp/
├── src/mt_washington_mcp/
│   ├── client.py      # Async httpx WeatherClient
│   ├── models.py      # Pydantic models with validators
│   ├── server.py      # FastMCP server + resources
│   ├── __init__.py    # Entry point
│   └── __main__.py    # python -m support
├── tests/
│   ├── test_client.py # Client tests with httpx.MockTransport
│   ├── test_models.py # Model parsing and validation tests
│   ├── test_server.py # Resource output format tests
│   └── fixtures/      # Saved API snapshots
├── pyproject.toml
└── Taskfile.yml
```
