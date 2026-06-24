"""
SafeHaven Dashboard API — FastAPI backend exposing agent pipeline + mock data.

Endpoints:
  GET  /api/incidents   — live incidents from state/incidents.jsonl
  GET  /api/agents      — status of the 5 pipeline agents
  GET  /api/shelters    — shelter capacity and occupancy
  GET  /api/supplies    — supply inventory across all shelters
  GET  /api/volunteers  — volunteer roster
  POST /api/incidents   — submit a new raw report, run through the REAL orchestrator

Run:
  uv run uvicorn dashboard.api:app --reload
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any

# Fix Windows encoding: force stdout/stderr to UTF-8 so orchestrator's
# print("→") calls don't crash with UnicodeEncodeError on charmap.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Ensure project root is importable so `agents.*` resolves
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SafeHaven Dashboard API",
    description="Backend API for the SafeHaven disaster response dashboard.",
    version="0.1.0",
)

# Allow React dev server (Vite uses 5173 by default, falls back to higher ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy import of mock_data (project-root must be on sys.path first)
# ---------------------------------------------------------------------------
from dashboard.mock_data import (
    get_agent_status,
    get_incidents_from_state,
    get_shelters,
    get_supplies,
    get_volunteers,
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class IncidentRequest(BaseModel):
    """Payload for POST /api/incidents — a raw disaster report string."""

    raw_report: str


# ---------------------------------------------------------------------------
# GET endpoints
# ---------------------------------------------------------------------------
@app.get("/api/incidents")
def list_incidents() -> list[dict[str, Any]]:
    """Return all incidents from state/incidents.jsonl."""
    return get_incidents_from_state()


@app.get("/api/agents")
def list_agents() -> list[dict[str, Any]]:
    """Return the status of all 5 pipeline agents."""
    return get_agent_status()


@app.get("/api/shelters")
def list_shelters() -> list[dict[str, Any]]:
    """Return shelter capacity and occupancy information."""
    return get_shelters()


@app.get("/api/supplies")
def list_supplies() -> list[dict[str, Any]]:
    """Return supply inventory across all shelters."""
    return get_supplies()


@app.get("/api/volunteers")
def list_volunteers() -> list[dict[str, Any]]:
    """Return volunteer roster."""
    return get_volunteers()


@app.get("/api/audit")
def list_audit() -> list[dict[str, Any]]:
    """Return audit log entries from state/audit.jsonl."""
    import json
    state_path = os.path.join(_PROJECT_ROOT, "state", "audit.jsonl")
    if not os.path.exists(state_path):
        return []
    entries = []
    with open(state_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return list(reversed(entries))  # newest first


@app.get("/api/communications")
def list_communications() -> list[dict[str, Any]]:
    """Extract all communications from completed incidents.

    The `communications` field can be either:
    - A list of dicts (structured output from communication_hub agent)
    - A raw string (plain text output when structured parsing fails)
    Both cases are handled safely.
    """
    incidents = get_incidents_from_state()
    comms = []
    for inc in reversed(incidents):  # newest first
        ts       = inc.get("timestamp", "")
        severity = inc.get("severity_score", 0)
        raw_comms = inc.get("communications", [])

        # Handle structured list of dicts
        if isinstance(raw_comms, list):
            for c in raw_comms:
                if isinstance(c, dict):
                    comms.append({**c, "incident_timestamp": ts, "incident_severity": severity})
                elif isinstance(c, str) and c.strip():
                    comms.append({
                        "comm_id": f"raw-{len(comms)}",
                        "channel": "broadcast",
                        "recipient": "public",
                        "message_summary": c,
                        "sent": True,
                        "incident_timestamp": ts,
                        "incident_severity": severity,
                    })
        # Handle raw string output
        elif isinstance(raw_comms, str) and raw_comms.strip():
            comms.append({
                "comm_id": f"raw-{len(comms)}",
                "channel": "broadcast",
                "recipient": "public",
                "message_summary": raw_comms[:1000],
                "sent": True,
                "incident_timestamp": ts,
                "incident_severity": severity,
            })

        # Public briefing as separate broadcast entry
        pb = inc.get("public_briefing")
        if pb and isinstance(pb, str):
            comms.append({
                "comm_id": f"pb-{ts[:10]}-{len(comms)}",
                "channel": "broadcast",
                "recipient": "public",
                "message_summary": pb,
                "sent": True,
                "incident_timestamp": ts,
                "incident_severity": severity,
            })

    return comms


# ---------------------------------------------------------------------------
# POST /api/incidents — runs the REAL orchestrator pipeline
# ---------------------------------------------------------------------------
@app.post("/api/incidents")
async def create_incident(payload: IncidentRequest) -> dict[str, Any]:
    """
    Accept a raw disaster report, run it through the full SafeHaven
    orchestrator pipeline (all 5 real agents), and return the complete
    CoordinationResult.

    This is NOT mocked — it calls agents.orchestrator.run_pipeline().
    """
    if not payload.raw_report.strip():
        raise HTTPException(status_code=400, detail="raw_report must not be empty")

    # Verify GEMINI_API_KEY is set (required by the ADK agents)
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not set. Add it to .env to enable live pipeline runs.",
        )

    try:
        # Import the real orchestrator pipeline
        from agents.orchestrator import run_pipeline

        result = await run_pipeline(payload.raw_report)

        # Persist the incident to state/incidents.jsonl for GET /api/incidents
        _append_incident(result)

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {type(exc).__name__}: {exc}",
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _append_incident(result: dict[str, Any]) -> None:
    """Append a pipeline result to state/incidents.jsonl (append-only)."""
    import json

    state_dir = os.path.join(_PROJECT_ROOT, "state")
    os.makedirs(state_dir, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **result,
    }

    incidents_path = os.path.join(state_dir, "incidents.jsonl")
    with open(incidents_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "safehaven-dashboard-api"}


# ---------------------------------------------------------------------------
# Static file serving (production / Docker)
# Serve the built React frontend from dashboard/frontend/dist/
# Only mounted if the dist/ directory exists (i.e. in production builds).
# ---------------------------------------------------------------------------
_DIST_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(_DIST_DIR):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Serve static assets (JS/CSS/images)
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Catch-all: serve index.html for React client-side routing."""
        index = os.path.join(_DIST_DIR, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"detail": "Frontend not built. Run: npm run build inside dashboard/frontend/"}
