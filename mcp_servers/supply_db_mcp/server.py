"""mcp_servers.supply_db_mcp.server

MCP server providing supply inventory tools via the official `mcp` package.

Exposes tools:
- get_inventory(shelter_id: str) -> dict
- check_availability(shelter_id: str, item_type: str, quantity: int) -> bool
- reserve_items(shelter_id: str, items: dict) -> dict
- release_reservation(reservation_id: str) -> bool
- get_all_shelters_with_inventory() -> list

Data source: In-memory mock database with realistic disaster-relief supplies.
Quantities deplete as reservations are made, just like a real system.

Run:
  uv run python -m mcp_servers.supply_db_mcp.server
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()


app = FastMCP("safehaven-supply-db-mcp")

# ---------------------------------------------------------------------------
# In-memory mock data — 12 shelters with realistic supply quantities.
# Mirrors the shelter IDs from PID section 15 / dashboard mock_data spec.
# ---------------------------------------------------------------------------
_INVENTORY_DB: Dict[str, Dict[str, int]] = {
    "SH001": {"water_liters": 5000, "food_meals": 1200, "medical_kits": 45, "blankets": 300, "cots": 400},
    "SH002": {"water_liters": 3200, "food_meals": 800,  "medical_kits": 20, "blankets": 200, "cots": 250},
    "SH003": {"water_liters": 4500, "food_meals": 1000, "medical_kits": 35, "blankets": 280, "cots": 350},
    "SH004": {"water_liters": 2800, "food_meals": 600,  "medical_kits": 15, "blankets": 150, "cots": 180},
    "SH005": {"water_liters": 6000, "food_meals": 1500, "medical_kits": 50, "blankets": 400, "cots": 500},
    "SH006": {"water_liters": 1500, "food_meals": 400,  "medical_kits": 10, "blankets": 100, "cots": 120},
    "SH007": {"water_liters": 3800, "food_meals": 900,  "medical_kits": 25, "blankets": 220, "cots": 280},
    "SH008": {"water_liters": 4200, "food_meals": 1100, "medical_kits": 40, "blankets": 310, "cots": 370},
    "SH009": {"water_liters": 2000, "food_meals": 500,  "medical_kits": 12, "blankets": 130, "cots": 160},
    "SH010": {"water_liters": 5500, "food_meals": 1300, "medical_kits": 48, "blankets": 350, "cots": 420},
    "SH011": {"water_liters": 1800, "food_meals": 450,  "medical_kits": 18, "blankets": 110, "cots": 140},
    "SH012": {"water_liters": 3500, "food_meals": 850,  "medical_kits": 30, "blankets": 250, "cots": 300},
}

# Active reservations: reservation_id -> {shelter_id, items, status}
_RESERVATIONS: Dict[str, Dict[str, Any]] = {}


def _get_inventory(shelter_id: str) -> Dict[str, Any]:
    """Return all items and quantities for a shelter."""
    if shelter_id not in _INVENTORY_DB:
        return {"error": f"Shelter {shelter_id} not found", "shelter_id": shelter_id}
    return {
        "shelter_id": shelter_id,
        "items": dict(_INVENTORY_DB[shelter_id]),
    }


def _check_availability(shelter_id: str, item_type: str, quantity: int) -> bool:
    """Check if a shelter has at least `quantity` of `item_type` available."""
    if shelter_id not in _INVENTORY_DB:
        return False
    available = _INVENTORY_DB[shelter_id].get(item_type, 0)
    return available >= quantity


def _reserve_items(shelter_id: str, items: Dict[str, int]) -> Dict[str, Any]:
    """Reserve items from a shelter. Returns reservation details or error."""
    if shelter_id not in _INVENTORY_DB:
        return {"error": f"Shelter {shelter_id} not found", "shelter_id": shelter_id}

    inv = _INVENTORY_DB[shelter_id]

    # Check availability first
    for item_type, qty in items.items():
        if inv.get(item_type, 0) < qty:
            return {
                "error": f"Insufficient {item_type}: requested {qty}, available {inv.get(item_type, 0)}",
                "shelter_id": shelter_id,
                "item_type": item_type,
            }

    # Deduct from inventory
    for item_type, qty in items.items():
        inv[item_type] -= qty

    reservation_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
    _RESERVATIONS[reservation_id] = {
        "shelter_id": shelter_id,
        "items": dict(items),
        "status": "reserved",
    }

    return {
        "reservation_id": reservation_id,
        "shelter_id": shelter_id,
        "items_reserved": dict(items),
        "remaining_inventory": dict(inv),
    }


def _release_reservation(reservation_id: str) -> bool:
    """Release a reservation, returning items to shelter inventory."""
    if reservation_id not in _RESERVATIONS:
        return False

    res = _RESERVATIONS.pop(reservation_id)
    if res["status"] != "reserved":
        return False

    shelter_id = res["shelter_id"]
    if shelter_id in _INVENTORY_DB:
        for item_type, qty in res["items"].items():
            _INVENTORY_DB[shelter_id][item_type] = _INVENTORY_DB[shelter_id].get(item_type, 0) + qty

    return True


def _get_all_shelters_with_inventory() -> List[Dict[str, Any]]:
    """Return inventory for every shelter."""
    result = []
    for shelter_id, items in _INVENTORY_DB.items():
        result.append({
            "shelter_id": shelter_id,
            "items": dict(items),
        })
    return result


@app.tool()
def get_inventory(shelter_id: str) -> dict:
    """Get all items and quantities for a specific shelter.

    Args:
        shelter_id: Shelter identifier (e.g. "SH001")
    """
    return _get_inventory(shelter_id)


@app.tool()
def check_availability(shelter_id: str, item_type: str, quantity: int) -> bool:
    """Check if a shelter has at least `quantity` of a given item type.

    Args:
        shelter_id: Shelter identifier
        item_type: Item category (e.g. "water_liters", "food_meals", "medical_kits")
        quantity: Minimum quantity needed
    """
    return _check_availability(shelter_id, item_type, quantity)


@app.tool()
def reserve_items(shelter_id: str, items: dict) -> dict:
    """Reserve items from a shelter's inventory. Deducts quantities and returns a reservation ID.

    Args:
        shelter_id: Shelter identifier
        items: Dict of item_type -> quantity to reserve (e.g. {"water_liters": 500, "food_meals": 100})
    """
    return _reserve_items(shelter_id, items)


@app.tool()
def release_reservation(reservation_id: str) -> bool:
    """Release a reservation, returning items to the shelter's inventory.

    Args:
        reservation_id: ID returned by reserve_items (e.g. "RES-A1B2C3D4")
    """
    return _release_reservation(reservation_id)


@app.tool()
def get_all_shelters_with_inventory() -> list:
    """Get inventory levels for all shelters."""
    return _get_all_shelters_with_inventory()


def _demo() -> None:
    """Test script: exercise all five tools."""
    print("Testing supply DB MCP tools\n")

    print("--- get_inventory('SH001') ---")
    print(_get_inventory("SH001"))
    print()

    print("--- check_availability('SH001', 'water_liters', 500) ---")
    print(_check_availability("SH001", "water_liters", 500))
    print()

    print("--- reserve_items('SH001', {'water_liters': 500, 'food_meals': 100}) ---")
    res = _reserve_items("SH001", {"water_liters": 500, "food_meals": 100})
    print(res)
    print()

    reservation_id = res.get("reservation_id", "")
    print(f"--- release_reservation('{reservation_id}') ---")
    print(_release_reservation(reservation_id))
    print()

    print("--- get_inventory('SH001') after release ---")
    print(_get_inventory("SH001"))
    print()

    print("--- get_all_shelters_with_inventory() (first 3) ---")
    all_inv = _get_all_shelters_with_inventory()
    for s in all_inv[:3]:
        print(s)
    print(f"... ({len(all_inv)} shelters total)")


if __name__ == "__main__":
    try:
        _demo()
    except Exception as e:
        print(str(e))
        raise
