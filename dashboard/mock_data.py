"""
Dashboard mock seed data for SafeHaven — Hurricane "Mara" hitting Bayport.

Provides realistic shelters, volunteers, supplies, and agent status
for the dashboard to display. Data is static seed data; the API reads
from this module and from live state/incidents.jsonl for real incidents.
"""

from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# Shelters (12 entries — PID.md §15)
# ──────────────────────────────────────────────────────────────────────────────

SHELTERS = [
    {
        "id": "SH001",
        "name": "Bayport High School",
        "lat": 27.9500,
        "lon": -82.4500,
        "capacity": 500,
        "current_occupancy": 342,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH002",
        "name": "Community Recreation Center",
        "lat": 27.9550,
        "lon": -82.4450,
        "capacity": 300,
        "current_occupancy": 287,
        "amenities": ["food", "water", "power"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH003",
        "name": "St. Mary's Church Hall",
        "lat": 27.9480,
        "lon": -82.4600,
        "capacity": 200,
        "current_occupancy": 198,
        "amenities": ["food", "water"],
        "accessible": False,
        "status": "open",
    },
    {
        "id": "SH004",
        "name": "Bayport Convention Center",
        "lat": 27.9600,
        "lon": -82.4400,
        "capacity": 1000,
        "current_occupancy": 614,
        "amenities": ["medical", "food", "water", "power", "communications"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH005",
        "name": "Riverside Elementary School",
        "lat": 27.9420,
        "lon": -82.4550,
        "capacity": 250,
        "current_occupancy": 250,
        "amenities": ["food", "water", "power"],
        "accessible": True,
        "status": "full",
    },
    {
        "id": "SH006",
        "name": "National Guard Armory",
        "lat": 27.9650,
        "lon": -82.4350,
        "capacity": 400,
        "current_occupancy": 178,
        "amenities": ["medical", "food", "water", "power", "communications"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH007",
        "name": "Bayport Public Library",
        "lat": 27.9530,
        "lon": -82.4480,
        "capacity": 150,
        "current_occupancy": 89,
        "amenities": ["water", "power"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH008",
        "name": "YMCA Sports Complex",
        "lat": 27.9580,
        "lon": -82.4520,
        "capacity": 350,
        "current_occupancy": 310,
        "amenities": ["food", "water", "power"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH009",
        "name": "First Baptist Fellowship Hall",
        "lat": 27.9460,
        "lon": -82.4420,
        "capacity": 180,
        "current_occupancy": 180,
        "amenities": ["food", "water"],
        "accessible": False,
        "status": "full",
    },
    {
        "id": "SH010",
        "name": "Bayport Fire Station #4",
        "lat": 27.9620,
        "lon": -82.4580,
        "capacity": 100,
        "current_occupancy": 42,
        "amenities": ["medical", "water"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH011",
        "name": "Coastal Community College Gym",
        "lat": 27.9510,
        "lon": -82.4630,
        "capacity": 600,
        "current_occupancy": 205,
        "amenities": ["medical", "food", "water", "power"],
        "accessible": True,
        "status": "open",
    },
    {
        "id": "SH012",
        "name": "Bayport Fairgrounds",
        "lat": 27.9680,
        "lon": -82.4300,
        "capacity": 800,
        "current_occupancy": 301,
        "amenities": ["food", "water", "power", "communications"],
        "accessible": True,
        "status": "open",
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Volunteers (20 entries — PID.md §15)
# ──────────────────────────────────────────────────────────────────────────────

VOLUNTEERS = [
    {"id": "V001", "name_hash": "a1b2c3", "lat": 27.9600, "lon": -82.4400, "skills": ["medical", "spanish"], "status": "available", "hours_logged": 12},
    {"id": "V002", "name_hash": "d4e5f6", "lat": 27.9550, "lon": -82.4500, "skills": ["logistics"], "status": "available", "hours_logged": 8},
    {"id": "V003", "name_hash": "g7h8i9", "lat": 27.9480, "lon": -82.4450, "skills": ["rescue", "first_aid"], "status": "on_site", "hours_logged": 24},
    {"id": "V004", "name_hash": "j0k1l2", "lat": 27.9520, "lon": -82.4550, "skills": ["childcare", "spanish"], "status": "available", "hours_logged": 5},
    {"id": "V005", "name_hash": "m3n4o5", "lat": 27.9650, "lon": -82.4350, "skills": ["medical", "logistics"], "status": "en_route", "hours_logged": 16},
    {"id": "V006", "name_hash": "p6q7r8", "lat": 27.9460, "lon": -82.4600, "skills": ["rescue"], "status": "available", "hours_logged": 3},
    {"id": "V007", "name_hash": "s9t0u1", "lat": 27.9580, "lon": -82.4420, "skills": ["translation", "logistics"], "status": "on_site", "hours_logged": 20},
    {"id": "V008", "name_hash": "v2w3x4", "lat": 27.9610, "lon": -82.4480, "skills": ["medical"], "status": "available", "hours_logged": 10},
    {"id": "V009", "name_hash": "y5z6a7", "lat": 27.9440, "lon": -82.4530, "skills": ["first_aid", "childcare"], "status": "unavailable", "hours_logged": 0},
    {"id": "V010", "name_hash": "b8c9d0", "lat": 27.9530, "lon": -82.4380, "skills": ["logistics", "communications"], "status": "available", "hours_logged": 7},
    {"id": "V011", "name_hash": "e1f2g3", "lat": 27.9660, "lon": -82.4560, "skills": ["rescue", "medical"], "status": "on_site", "hours_logged": 30},
    {"id": "V012", "name_hash": "h4i5j6", "lat": 27.9490, "lon": -82.4470, "skills": ["spanish", "logistics"], "status": "available", "hours_logged": 4},
    {"id": "V013", "name_hash": "k7l8m9", "lat": 27.9570, "lon": -82.4620, "skills": ["medical", "first_aid"], "status": "en_route", "hours_logged": 14},
    {"id": "V014", "name_hash": "n0o1p2", "lat": 27.9630, "lon": -82.4440, "skills": ["communications"], "status": "available", "hours_logged": 6},
    {"id": "V015", "name_hash": "q3r4s5", "lat": 27.9470, "lon": -82.4510, "skills": ["childcare", "spanish"], "status": "on_site", "hours_logged": 18},
    {"id": "V016", "name_hash": "t6u7v8", "lat": 27.9540, "lon": -82.4360, "skills": ["rescue", "logistics"], "status": "available", "hours_logged": 9},
    {"id": "V017", "name_hash": "w9x0y1", "lat": 27.9590, "lon": -82.4540, "skills": ["medical"], "status": "unavailable", "hours_logged": 0},
    {"id": "V018", "name_hash": "z2a3b4", "lat": 27.9510, "lon": -82.4460, "skills": ["first_aid", "logistics"], "status": "available", "hours_logged": 11},
    {"id": "V019", "name_hash": "c5d6e7", "lat": 27.9640, "lon": -82.4570, "skills": ["spanish", "childcare"], "status": "en_route", "hours_logged": 2},
    {"id": "V020", "name_hash": "f8g9h0", "lat": 27.9450, "lon": -82.4390, "skills": ["rescue", "medical", "first_aid"], "status": "on_site", "hours_logged": 22},
]

# ──────────────────────────────────────────────────────────────────────────────
# Supply inventory per shelter (PID.md §15)
# ──────────────────────────────────────────────────────────────────────────────

SUPPLIES = {
    "SH001": {"water_liters": 5000, "food_meals": 1200, "medical_kits": 45, "blankets": 300, "cots": 400},
    "SH002": {"water_liters": 3000, "food_meals": 800, "medical_kits": 20, "blankets": 200, "cots": 280},
    "SH003": {"water_liters": 1500, "food_meals": 400, "medical_kits": 10, "blankets": 100, "cots": 150},
    "SH004": {"water_liters": 10000, "food_meals": 2500, "medical_kits": 80, "blankets": 500, "cots": 800},
    "SH005": {"water_liters": 2000, "food_meals": 500, "medical_kits": 15, "blankets": 120, "cots": 200},
    "SH006": {"water_liters": 6000, "food_meals": 1500, "medical_kits": 60, "blankets": 350, "cots": 380},
    "SH007": {"water_liters": 800, "food_meals": 200, "medical_kits": 5, "blankets": 50, "cots": 80},
    "SH008": {"water_liters": 4000, "food_meals": 1000, "medical_kits": 30, "blankets": 250, "cots": 320},
    "SH009": {"water_liters": 1200, "food_meals": 350, "medical_kits": 8, "blankets": 80, "cots": 140},
    "SH010": {"water_liters": 600, "food_meals": 150, "medical_kits": 25, "blankets": 40, "cots": 60},
    "SH011": {"water_liters": 4500, "food_meals": 1100, "medical_kits": 40, "blankets": 280, "cots": 450},
    "SH012": {"water_liters": 7000, "food_meals": 1800, "medical_kits": 50, "blankets": 400, "cots": 600},
}

# ──────────────────────────────────────────────────────────────────────────────
# Agent status — static representation of the 5 pipeline agents
# ──────────────────────────────────────────────────────────────────────────────

AGENT_STATUS = [
    {
        "id": "intake",
        "name": "Intake Agent",
        "description": "Parses raw disaster reports, extracts location and needs, redacts PII",
        "status": "idle",
        "last_run": None,
    },
    {
        "id": "crisis_assessor",
        "name": "Crisis Assessor",
        "description": "Scores severity, checks weather, identifies secondary risks",
        "status": "idle",
        "last_run": None,
    },
    {
        "id": "resource_allocator",
        "name": "Resource Allocator",
        "description": "Finds shelters, checks supplies, allocates resources",
        "status": "idle",
        "last_run": None,
    },
    {
        "id": "volunteer_coordinator",
        "name": "Volunteer Coordinator",
        "description": "Matches skills to tasks, dispatches volunteers",
        "status": "idle",
        "last_run": None,
    },
    {
        "id": "communication_hub",
        "name": "Communication Hub",
        "description": "Notifies agencies, sends updates, generates briefings",
        "status": "idle",
        "last_run": None,
    },
]


def get_shelters() -> list[dict]:
    """Return all shelter records."""
    return list(SHELTERS)


def get_shelter(shelter_id: str) -> dict | None:
    """Return a single shelter by ID."""
    for s in SHELTERS:
        if s["id"] == shelter_id:
            return s
    return None


def get_volunteers() -> list[dict]:
    """Return all volunteer records."""
    return list(VOLUNTEERS)


def get_supplies() -> list[dict]:
    """Return supply inventory as a list of {shelter_id, ...items} dicts."""
    return [{"shelter_id": sid, **items} for sid, items in SUPPLIES.items()]


def get_agent_status() -> list[dict]:
    """Return agent status for the dashboard."""
    return list(AGENT_STATUS)


def get_incidents_from_state() -> list[dict]:
    """Read live incidents from state/incidents.jsonl (if it exists)."""
    import json
    import os

    state_path = os.path.join(os.path.dirname(__file__), "..", "state", "incidents.jsonl")
    if not os.path.exists(state_path):
        return []

    incidents = []
    with open(state_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    incidents.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return incidents
