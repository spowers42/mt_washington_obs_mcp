"""Tests for WeatherClient."""

import json
from pathlib import Path

import httpx
import pytest

from mt_washington_mcp.client import WeatherClient

FIXTURES = Path(__file__).parent / "fixtures"

BASE = "https://mock.mountwashington.org"


def _mock_handler(fixture_path: str, status: int = 200):
    """Return a MockTransport handler that returns the given fixture."""

    def handler(request: httpx.Request) -> httpx.Response:
        if status != 200:
            return httpx.Response(status, request=request)
        with open(fixture_path) as f:
            content = f.read()
        return httpx.Response(
            status,
            json=json.loads(content),
            request=request,
        )

    return handler


def _client(transport: httpx.MockTransport) -> WeatherClient:
    """Create a WeatherClient with a mocked transport."""
    client = WeatherClient()
    client.client = httpx.AsyncClient(transport=transport, base_url=BASE)
    return client


class TestGetWeather:
    async def test_returns_summit_conditions_dict(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "weather.json")
        )
        async with _client(transport) as weather_client:
            data = await weather_client.get_weather()
        assert "summitConditions" in data
        assert data["summitConditions"]["LastUpdated"] == "2026-06-08 14:20:00"

    async def test_raises_on_http_error(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "weather.json", status=500)
        )
        async with _client(transport) as weather_client:
            with pytest.raises(httpx.HTTPStatusError):
                await weather_client.get_weather()


class TestGetOutlook:
    async def test_returns_outlook_dict(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "outlook.json")
        )
        async with _client(transport) as weather_client:
            data = await weather_client.get_outlook()
        assert "LastUpdated" in data
        assert "SummitOutlook" in data
        assert "ValleyOutlook" in data

    async def test_raises_on_http_error(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "outlook.json", status=404)
        )
        async with _client(transport) as weather_client:
            with pytest.raises(httpx.HTTPStatusError):
                await weather_client.get_outlook()

    async def test_raises_on_http_error_503(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "outlook.json", status=503)
        )
        async with _client(transport) as weather_client:
            with pytest.raises(httpx.HTTPStatusError):
                await weather_client.get_outlook()


class TestGetF6Pdf:
    async def test_returns_bytes(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"%PDF-1.4 mock data", request=request)

        transport = httpx.MockTransport(handler)
        async with _client(transport) as weather_client:
            data = await weather_client.get_f6_pdf(2026, 6)
        assert isinstance(data, bytes)
        assert data.startswith(b"%PDF")

    async def test_raises_on_http_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(403, request=request)

        transport = httpx.MockTransport(handler)
        async with _client(transport) as weather_client:
            with pytest.raises(httpx.HTTPStatusError):
                await weather_client.get_f6_pdf(2026, 6)


class TestContextManager:
    async def test_context_manager_closes_client(self):
        transport = httpx.MockTransport(
            _mock_handler(FIXTURES / "weather.json")
        )
        async with _client(transport) as weather_client:
            data = await weather_client.get_weather()
        assert "summitConditions" in data
