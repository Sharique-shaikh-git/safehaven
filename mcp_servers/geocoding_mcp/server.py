"""mcp_servers.geocoding_mcp.server

MCP server providing geocoding tools via the official `mcp` package.

Exposes tools:
- geocode_address(address: str) -> dict — text address → {lat, lon, formatted_address, confidence}
- reverse_geocode(lat: float, lon: float) -> dict — lat/lon → address components

Data source: Nominatim (OpenStreetMap) — free, no API key required.
Nominatim requires a custom User-Agent identifying the app and enforces
a max of 1 request/second. We respect both policies.

Run:
  uv run python -m mcp_servers.geocoding_mcp.server
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

import requests


load_dotenv()


app = FastMCP("safehaven-geocoding-mcp")

# Nominatim usage policy: identify your app with a descriptive User-Agent.
_USER_AGENT = "SafeHaven-DisasterResponse/1.0 (safehaven-geocoding-mcp)"
_HEADERS = {"User-Agent": _USER_AGENT}

# Track last request time to enforce 1 req/s rate limit.
_last_request_time: float = 0.0


def _rate_limit_wait() -> None:
    """Sleep if needed to respect Nominatim's 1 request/second policy."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_request_time = time.time()


def _geocode(address: str) -> Dict[str, Any]:
    """Forward geocode: address text → lat/lon + formatted address."""
    _rate_limit_wait()
    url = "https://nominatim.openstreetmap.org/search"
    params: Dict[str, Any] = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    resp = requests.get(url, params=params, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    results = resp.json()

    if not results:
        return {"error": f"No results found for address: {address}"}

    best = results[0]
    return {
        "lat": float(best.get("lat", 0)),
        "lon": float(best.get("lon", 0)),
        "formatted_address": best.get("display_name", ""),
        "confidence": float(best.get("importance", 0)),
        "osm_type": best.get("osm_type", ""),
        "osm_id": best.get("osm_id"),
        "address_components": best.get("address", {}),
    }


def _reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """Reverse geocode: lat/lon → address components."""
    _rate_limit_wait()
    url = "https://nominatim.openstreetmap.org/reverse"
    params: Dict[str, Any] = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
    }
    resp = requests.get(url, params=params, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        return {"error": data["error"], "lat": lat, "lon": lon}

    addr = data.get("address", {})
    return {
        "lat": lat,
        "lon": lon,
        "formatted_address": data.get("display_name", ""),
        "address_components": addr,
        "osm_type": data.get("osm_type", ""),
        "osm_id": data.get("osm_id"),
    }


@app.tool()
def geocode_address(address: str) -> dict:
    """Convert a text address to latitude/longitude coordinates.

    Args:
        address: Free-form address string (e.g. "Tampa, FL" or "1600 Pennsylvania Ave, Washington DC")

    Returns:
        dict with lat, lon, formatted_address, confidence, address_components
    """
    return _geocode(address)


@app.tool()
def reverse_geocode(lat: float, lon: float) -> dict:
    """Convert latitude/longitude coordinates to a text address.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        dict with lat, lon, formatted_address, address_components
    """
    return _reverse_geocode(lat=lat, lon=lon)


def _demo() -> None:
    """Test script: geocode 'Tampa, FL' then reverse-geocode the result."""
    print("Testing geocoding MCP tools\n")

    # 1. Forward geocode
    print("--- geocode_address('Tampa, FL') ---")
    result = _geocode("Tampa, FL")
    print(result)
    print()

    if "error" in result:
        print(f"Forward geocode failed: {result['error']}")
        return

    # 2. Reverse geocode the coordinates we just got
    lat, lon = result["lat"], result["lon"]
    print(f"--- reverse_geocode({lat}, {lon}) ---")
    rev = _reverse_geocode(lat, lon)
    print(rev)
    print()

    # 3. Sanity check: verify round-trip roughly matches
    fwd_city = result.get("address_components", {}).get("city", "").lower()
    rev_city = rev.get("address_components", {}).get("city", "").lower()
    if fwd_city and rev_city and fwd_city == rev_city:
        print(f"[OK] Round-trip OK -- both resolved to city: {fwd_city.title()}")
    elif fwd_city or rev_city:
        print(f"[~] Partial match — forward city: {fwd_city!r}, reverse city: {rev_city!r}")
    else:
        print("[~] Could not verify city match from address components")


if __name__ == "__main__":
    try:
        _demo()
    except Exception as e:
        print(str(e))
        raise
