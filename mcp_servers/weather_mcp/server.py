"""mcp_servers.weather_mcp.server

MCP server providing weather tools via the official `mcp` package.

Exposes tools:
- get_current_weather(lat: float, lon: float) -> dict
- get_weather_forecast(lat: float, lon: float, hours: int) -> dict

Weather is fetched from OpenWeatherMap using OPENWEATHER_API_KEY from .env.
If the API key is missing/empty, this module raises a clear error (no fake data).

Run:
  uv run python -m mcp_servers.weather_mcp.server

Note: This uses the built-in FastMCP helper that ships with the `mcp` package.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

import requests


load_dotenv()


app = FastMCP("safehaven-weather-mcp")


def _require_openweather_api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY")
    if key is None or not str(key).strip():
        raise RuntimeError(
            "Missing OPENWEATHER_API_KEY. Add it to your .env file (copied from .env.example) "
            "to enable real OpenWeatherMap calls."
        )
    return str(key).strip()


def _current_weather(lat: float, lon: float) -> Dict[str, Any]:
    api_key = _require_openweather_api_key()
    # OneCall supports current+forecast but free tier may vary; we keep simple calls.
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "imperial",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Return a stable subset for agents.
    return {
        "lat": lat,
        "lon": lon,
        "temp_f": data.get("main", {}).get("temp"),
        "feels_like_f": data.get("main", {}).get("feels_like"),
        "humidity_percent": data.get("main", {}).get("humidity"),
        "pressure_hpa": data.get("main", {}).get("pressure"),
        "wind_speed_mph": data.get("wind", {}).get("speed"),
        "wind_deg": data.get("wind", {}).get("deg"),
        "visibility_m": data.get("visibility"),
        "conditions": (data.get("weather") or [{}])[0].get("description"),
        "precipitation": data.get("rain") or data.get("snow"),
    }


def _forecast(lat: float, lon: float, hours: int) -> Dict[str, Any]:
    api_key = _require_openweather_api_key()

    hours = int(hours)
    if hours < 1:
        hours = 1
    # OpenWeatherMap 5-day/3-hour forecast yields ~8*5=40 entries.
    # We'll request max and slice.

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "imperial",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    entries: List[Dict[str, Any]] = data.get("list") or []
    # Each entry is ~3 hours apart.
    max_entries = min(len(entries), max(1, (hours + 2) // 3))
    sliced = entries[:max_entries]

    forecast_points: List[Dict[str, Any]] = []
    for e in sliced:
        forecast_points.append(
            {
                "dt_txt": e.get("dt_txt"),
                "temp_f": (e.get("main") or {}).get("temp"),
                "humidity_percent": (e.get("main") or {}).get("humidity"),
                "wind_speed_mph": (e.get("wind") or {}).get("speed"),
                "conditions": (e.get("weather") or [{}])[0].get("description"),
                "precipitation": e.get("rain") or e.get("snow"),
            }
        )

    return {
        "lat": lat,
        "lon": lon,
        "requested_hours": hours,
        "forecast_points": forecast_points,
    }


@app.tool()
def get_current_weather(lat: float, lon: float) -> dict:
    """Get current weather for the given latitude/longitude."""

    return _current_weather(lat=lat, lon=lon)


@app.tool()
def get_weather_forecast(lat: float, lon: float, hours: int = 24) -> dict:
    """Get forecast for the given latitude/longitude for the next `hours` hours."""

    return _forecast(lat=lat, lon=lon, hours=hours)


def _demo() -> None:
    """Test script per PID: call get_current_weather for Tampa, FL."""

    lat, lon = 27.9506, -82.4572
    print(f"Requesting current weather for Tampa, FL: ({lat}, {lon})")
    # Direct call (not via MCP) so this works in a simple `python -m ...` run.
    result = _current_weather(lat=lat, lon=lon)
    print("Current weather response:")
    print(result)


if __name__ == "__main__":
    try:
        _demo()
    except Exception as e:
        # Must not silently fall back.
        print(str(e))
        raise

