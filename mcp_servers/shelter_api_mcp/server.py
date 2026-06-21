"""mcp_servers.shelter_api_mcp.server

MCP server providing shelter lookup tools via the official `mcp` package.

Exposes tools:
- find_nearby_shelters(lat, lon, radius_km) -> list
- check_shelter_capacity(shelter_id) -> dict

Data source: In-memory mock database with 12 shelters.
Shelter IDs match supply_db_mcp (SH001-SH012) for cross-server consistency.

Run:
  uv run python -m mcp_servers.shelter_api_mcp.server
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()


app = FastMCP("safehaven-shelter-api-mcp")

# ---------------------------------------------------------------------------
# In-memory mock data — 12 shelters matching supply_db_mcp shelter IDs.
# Coordinates are scattered around the Bayport / Tampa Bay region.
# ---------------------------------------------------------------------------
_SHELTERS: Dict[str, Dict[str, Any]] = {
    "SH001": {
        "id": "SH001", "name": "Bayport High School",
        "lat": 27.9506, "lon": -82.4572,
        "capacity": 500, "current_occupancy": 342,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True, "status": "open",
    },
    "SH002": {
        "id": "SH002", "name": "Riverside Community Center",
        "lat": 27.9450, "lon": -82.4680,
        "capacity": 300, "current_occupancy": 285,
        "amenities": ["food", "water"],
        "accessible": True, "status": "open",
    },
    "SH003": {
        "id": "SH003", "name": "Grace Lutheran Church",
        "lat": 27.9580, "lon": -82.4490,
        "capacity": 200, "current_occupancy": 178,
        "amenities": ["food", "water", "power"],
        "accessible": False, "status": "open",
    },
    "SH004": {
        "id": "SH004", "name": "Bayport Rec Center Gymnasium",
        "lat": 27.9390, "lon": -82.4610,
        "capacity": 400, "current_occupancy": 400,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True, "status": "full",
    },
    "SH005": {
        "id": "SH005", "name": "Westshore Baptist Church",
        "lat": 27.9620, "lon": -82.4750,
        "capacity": 250, "current_occupancy": 98,
        "amenities": ["food", "water"],
        "accessible": True, "status": "open",
    },
    "SH006": {
        "id": "SH006", "name": "Port Bay Elementary School",
        "lat": 27.9340, "lon": -82.4430,
        "capacity": 350, "current_occupancy": 310,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True, "status": "open",
    },
    "SH007": {
        "id": "SH007", "name": "Harbor View Lodge",
        "lat": 27.9530, "lon": -82.4380,
        "capacity": 150, "current_occupancy": 150,
        "amenities": ["food", "water"],
        "accessible": False, "status": "full",
    },
    "SH008": {
        "id": "SH008", "name": "Bayfront Medical Annex",
        "lat": 27.9470, "lon": -82.4530,
        "capacity": 100, "current_occupancy": 67,
        "amenities": ["medical", "water", "power"],
        "accessible": True, "status": "open",
    },
    "SH009": {
        "id": "SH009", "name": "Sunset Park Pavilion",
        "lat": 27.9280, "lon": -82.4700,
        "capacity": 200, "current_occupancy": 45,
        "amenities": ["water"],
        "accessible": True, "status": "open",
    },
    "SH010": {
        "id": "SH010", "name": "Bayport National Guard Armory",
        "lat": 27.9650, "lon": -82.4620,
        "capacity": 600, "current_occupancy": 520,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True, "status": "open",
    },
    "SH011": {
        "id": "SH011", "name": "St. Mary's Parish Hall",
        "lat": 27.9410, "lon": -82.4350,
        "capacity": 180, "current_occupancy": 162,
        "amenities": ["food", "water", "power"],
        "accessible": False, "status": "open",
    },
    "SH012": {
        "id": "SH012", "name": "Bayport Convention Center",
        "lat": 27.9560, "lon": -82.4650,
        "capacity": 800, "current_occupancy": 610,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True, "status": "open",
    },
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two points."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _find_nearby_shelters(lat: float, lon: float, radius_km: float = 10.0) -> List[Dict[str, Any]]:
    """Return shelters within radius_km, sorted by distance (nearest first)."""
    results: List[Dict[str, Any]] = []
    for shelter in _SHELTERS.values():
        dist = _haversine_km(lat, lon, shelter["lat"], shelter["lon"])
        if dist <= radius_km:
            entry = dict(shelter)
            entry["distance_km"] = round(dist, 2)
            entry["available_beds"] = shelter["capacity"] - shelter["current_occupancy"]
            results.append(entry)
    results.sort(key=lambda s: s["distance_km"])
    return results


def _check_shelter_capacity(shelter_id: str) -> Dict[str, Any]:
    """Return capacity details for a single shelter."""
    if shelter_id not in _SHELTERS:
        return {"error": f"Shelter {shelter_id} not found", "shelter_id": shelter_id}
    s = _SHELTERS[shelter_id]
    return {
        "shelter_id": s["id"],
        "name": s["name"],
        "capacity": s["capacity"],
        "current_occupancy": s["current_occupancy"],
        "available_beds": s["capacity"] - s["current_occupancy"],
        "occupancy_percent": round(s["current_occupancy"] / s["capacity"] * 100, 1),
        "status": s["status"],
        "amenities": s["amenities"],
        "accessible": s["accessible"],
    }


@app.tool()
def find_nearby_shelters(lat: float, lon: float, radius_km: float = 10.0) -> list:
    """Find shelters within a radius of the given coordinates, sorted by distance.

    Args:
        lat: Latitude of the search center
        lon: Longitude of the search center
        radius_km: Maximum distance in km (default 10)
    """
    return _find_nearby_shelters(lat, lon, radius_km)


@app.tool()
def check_shelter_capacity(shelter_id: str) -> dict:
    """Get capacity, occupancy, amenities, and status for a specific shelter.

    Args:
        shelter_id: Shelter identifier (e.g. "SH001")
    """
    return _check_shelter_capacity(shelter_id)


def _demo() -> None:
    """Test script: exercise both tools."""
    print("Testing shelter API MCP tools\n")

    # find_nearby_shelters from Bayport city center
    lat, lon = 27.9506, -82.4572
    print(f"--- find_nearby_shelters({lat}, {lon}, radius_km=5) ---")
    nearby = _find_nearby_shelters(lat, lon, radius_km=5.0)
    for s in nearby:
        print(f"  {s['id']} {s['name']}: {s['distance_km']}km, "
              f"{s['current_occupancy']}/{s['capacity']} beds ({s['status']})")
    print(f"  ({len(nearby)} shelters within 5 km)\n")

    # check_shelter_capacity for SH001
    print("--- check_shelter_capacity('SH001') ---")
    print(_check_shelter_capacity("SH001"))
    print()

    # check_shelter_capacity for a full shelter
    print("--- check_shelter_capacity('SH004') ---")
    print(_check_shelter_capacity("SH004"))
    print()

    # check_shelter_capacity for unknown
    print("--- check_shelter_capacity('SH999') ---")
    print(_check_shelter_capacity("SH999"))


if __name__ == "__main__":
    try:
        _demo()
    except Exception as e:
        print(str(e))
        raise
