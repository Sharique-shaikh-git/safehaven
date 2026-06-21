# SafeHaven: AI-Powered Disaster Response Coordination Network

## Project Identification Document (PID)
**Track:** Agents for Good
**Hackathon:** AI Agents: Intensive Vibe Coding Capstone Project (Kaggle)
**Deadline:** July 6, 2026 at 11:59 PM PT
**Submission:** Kaggle Writeup + GitHub Repo + YouTube Video + Deployed Demo

---

## 1. Problem Statement

Every year, natural disasters displace over 20 million people globally. In the critical first 24-72 hours after a disaster strikes, the biggest bottleneck is not lack of resources — it is **coordination chaos**. Information about affected areas, available shelters, supply inventories, and volunteer capacity exists across dozens of disconnected systems. First responders waste precious hours making phone calls, checking spreadsheets, and reconciling conflicting reports.

Current disaster response relies on:
- Manual phone trees and radio communication
- Static, outdated shelter lists
- No real-time supply inventory visibility
- Ad-hoc volunteer dispatch with no tracking
- Personal information of victims exposed in plaintext shared documents

**The result:** People who need shelter wait hours to find a bed. Supplies sit in warehouses while people go without. Volunteers are dispatched to locations that no longer need help. Critical time is lost to coordination overhead, not rescue operations.

## 2. Why Agents? Why Now?

A traditional single-model AI cannot solve this. Disaster response requires:
- **Multiple specialized roles** working in parallel (intake, assessment, resource matching, volunteer dispatch, communication)
- **Real-time tool use** across external APIs (weather, maps, shelter databases, supply chains)
- **Privacy guarantees** for victim personal information
- **Persistent coordination state** that outlives any single conversation

A multi-agent system built with Google ADK is uniquely suited because:
1. Each agent has a specialized role and toolset — no single point of failure
2. Agents delegate to each other — the Intake Agent does not need to know how to find shelters
3. MCP servers connect agents to live external data — weather conditions, shelter availability, supply inventories
4. Security is built in at the architecture level — PII is redacted before any agent processes it
5. The system is deployable as a live dashboard that emergency coordinators can actually use

## 3. Solution Overview

SafeHaven is a multi-agent disaster response coordination system. When a disaster report comes in (via any channel — SMS, web form, phone transcript), the system automatically:

1. **Intakes** the report — extracts location, severity, and needs while redacting all personal information
2. **Assesses** the crisis — scores severity, checks weather conditions, identifies affected infrastructure
3. **Allocates resources** — finds nearest available shelters with capacity, checks supply inventory, generates transport routes
4. **Dispatches volunteers** — matches volunteer skills and locations to open tasks, tracks assignment status
5. **Communicates** — notifies relevant agencies, sends status updates to families (securely), generates public briefings

All of this is visible on a real-time Streamlit dashboard that emergency coordinators monitor.

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DISASTER REPORT IN                           │
│              (SMS / Web Form / Phone Transcript / IoT)              │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      INTAKE AGENT           │
                    │  - Parse unstructured text  │
                    │  - Extract location + geo   │
                    │  - Identify needs (people,  │
                    │    medical, food, shelter)  │
                    │  - REDACT ALL PII           │
                    └──────────────┬──────────────┘
                                   │
                      ┌────────────┼────────────┐
                      ▼            ▼            ▼
            ┌──────────────┐ ┌────────────┐ ┌──────────────┐
            │  CRISIS      │ │ RESOURCE   │ │ VOLUNTEER    │
            │  ASSESSOR    │ │ ALLOCATOR  │ │ COORDINATOR  │
            │              │ │            │ │              │
            │ - Severity   │ │ - Find     │ │ - Match      │
            │   scoring    │ │   shelters │ │   volunteers │
            │ - Weather    │ │ - Check    │ │ - Dispatch   │
            │   impact     │ │   supplies │ │ - Track      │
            │ - Infra      │ │ - Route    │ │   status     │
            │   damage     │ │   planning │ │              │
            └──────┬───────┘ └─────┬──────┘ └──────┬───────┘
                   │               │               │
                   └───────────────┼───────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   COMMUNICATION HUB         │
                    │  - Agency notifications     │
                    │  - Family status updates    │
                    │  - Public briefing gen      │
                    │  - Social media alerts      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      DASHBOARD OUTPUT       │
                    │   Real-time Streamlit UI    │
                    │   for Emergency Coordinators│
                    └─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         MCP SERVERS                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │
│  │ Weather MCP│ │ Geocoding  │ │ Supply DB  │ │ Shelter API    │   │
│  │            │ │ MCP        │ │ MCP        │ │ MCP            │   │
│  │ - Current  │ │ - Address→ │ │ - Inventory│ │ - Availability │   │
│  │   weather  │ │   lat/lon  │ │ - Request  │ │ - Capacity     │   │
│  │ - Forecast │ │ - Reverse  │ │ - Restock  │ │ - Amenities    │   │
│  │ - Alerts   │ │   geocode  │ │   alerts   │ │ - Accessibility│   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYER                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │
│  │ PII        │ │ Field-     │ │ RBAC       │ │ Audit          │   │
│  │ Redaction  │ │ Level      │ │ Access     │ │ Logging        │   │
│  │            │ │ Encryption │ │ Control    │ │                │   │
│  │ - Names    │ │            │ │            │ │ - Who accessed │   │
│  │ - Phones   │ │ - Victim   │ │ - Admin    │ │   what when    │   │
│  │ - SSN/ID   │ │   data     │ │ - Operator │ │                │   │
│  │ - Addresses│ │ - Location │ │ - Public   │ │ - Tamper-proof │   │
│  │            │ │   coords   │ │            │ │   write-once   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Agent Specifications

### 5.1 Intake Agent
**Role:** First point of contact for all disaster reports
**ADK Type:** LlmAgent (with function tools)
**Responsibilities:**
- Parse unstructured disaster reports from any source
- Extract: location (text → lat/lon via Geocoding MCP), disaster type, people affected, specific needs
- Score initial severity (1-10) based on keywords and context
- **REDACT ALL PII** before any downstream processing (names, phone numbers, addresses, IDs)
- Generate a structured `DisasterReport` object
- Route to Crisis Assessor (always) and Resource Allocator (if severity > 5)

**Custom Tools (3+):**
- `parse_unstructured_report(text: str) -> StructuredReport`
- `extract_location(address_text: str) -> GeoLocation` (calls Geocoding MCP)
- `redact_pii(text: str) -> RedactedText`
- `score_severity(report: StructuredReport) -> int`

**Input/Output:**
```
INPUT:  Raw text ("My name is John Doe, phone 555-1234, my house at 123 Main St flooded, 
        4 people including my elderly mother need help")
OUTPUT: DisasterReport { id, timestamp, location: {lat, lon}, disaster_type: "flood", 
        severity: 7, needs: ["shelter", "medical", "food"], people_affected: 4,
        raw_text_redacted: "[REDACTED] at [REDACTED] flooded, 4 people including elderly need help",
        pii_vault_ref: "vault://abc123" }
```

### 5.2 Crisis Assessor Agent
**Role:** Deep analysis and prioritization
**ADK Type:** LlmAgent
**Responsibilities:**
- Take structured report from Intake Agent
- Query Weather MCP for current conditions and forecasts
- Cross-reference with historical disaster patterns
- Upgrade/downgrade severity score with justification
- Flag life-threatening situations for immediate escalation
- Identify secondary risks (aftershocks, disease outbreak, infrastructure collapse)

**Custom Tools (3+):**
- `get_weather_conditions(lat: float, lon: float) -> WeatherData` (calls Weather MCP)
- `get_weather_forecast(lat: float, lon: float, hours: int) -> Forecast`
- `check_historical_patterns(disaster_type: str, location: GeoLocation) -> RiskFactors`
- `generate_risk_assessment(report: DisasterReport, weather: WeatherData) -> RiskAssessment`

### 5.3 Resource Allocator Agent
**Role:** Match needs with available resources
**ADK Type:** LlmAgent (with loop tool for multi-step optimization)
**Responsibilities:**
- Receive prioritized needs from Crisis Assessor
- Query Shelter API MCP for nearest available shelters with capacity
- Query Supply DB MCP for available supplies (water, food, medical kits, blankets)
- Calculate optimal allocation (minimize travel time, maximize coverage)
- Reserve resources (mark as allocated in external systems)
- Generate transport routes

**Custom Tools (4+):**
- `find_shelters(lat: float, lon: float, radius_km: float, people: int) -> List[Shelter]`
- `check_supply_inventory(shelter_id: str, item_type: str) -> InventoryStatus`
- `allocate_resources(request: ResourceRequest) -> AllocationResult`
- `generate_transport_route(origin: Location, destinations: List[Location]) -> Route`
- `confirm_reservation(allocation_id: str) -> bool`

### 5.4 Volunteer Coordinator Agent
**Role:** Match and dispatch volunteers
**ADK Type:** LlmAgent
**Responsibilities:**
- Receive task list from Resource Allocator
- Query volunteer database for available volunteers near task locations
- Match by skills (medical, logistics, rescue, translation, childcare)
- Dispatch assignments with priority and deadline
- Track volunteer status (en_route, on_site, completed)
- Handle volunteer check-in/check-out

**Custom Tools (3+):**
- `find_available_volunteers(location: Location, skills: List[str], radius_km: float) -> List[Volunteer]`
- `dispatch_volunteer(volunteer_id: str, task: Task) -> DispatchResult`
- `track_volunteer_status(volunteer_id: str) -> Status`
- `generate_task_brief(task: Task) -> str`

### 5.5 Communication Hub Agent
**Role:** All external and internal communications
**ADK Type:** LlmAgent (with conditional routing)
**Responsibilities:**
- Notify emergency management agencies with situation reports
- Send secure status updates to families of affected individuals (via anonymized tokens)
- Generate public-facing situation briefings (aggregate data, no PII)
- Alert volunteers of new assignments
- Post to designated social media/emergency broadcast channels
- Maintain communication log for audit trail

**Custom Tools (4+):**
- `notify_agency(agency: str, report: SituationReport) -> bool`
- `send_family_update(token: str, status: str) -> bool`
- `generate_public_briefing(active_incidents: List[Incident]) -> str`
- `broadcast_alert(channels: List[str], message: str) -> bool`
- `log_communication(entry: CommEntry) -> bool`

## 6. MCP Server Specifications

### 6.1 Weather MCP Server
**Protocol:** FastMCP
**Tools:**
- `get_current_weather(lat: float, lon: float) -> dict` — temperature, conditions, wind, visibility, precipitation
- `get_forecast(lat: float, lon: float, hours: int = 24) -> list` — hourly forecast
- `get_severe_alerts(lat: float, lon: float) -> list` — active weather warnings
**Data Source:** OpenWeatherMap API (free tier sufficient)
**Authentication:** API key via environment variable

### 6.2 Geocoding MCP Server
**Protocol:** FastMCP
**Tools:**
- `geocode_address(address: str) -> dict` — text address → {lat, lon, formatted_address, confidence}
- `reverse_geocode(lat: float, lon: float) -> dict` — lat/lon → address components
- `batch_geocode(addresses: list) -> list` — multiple addresses in one call
**Data Source:** Google Maps Geocoding API or Nominatim (OpenStreetMap, free)

### 6.3 Supply DB MCP Server
**Protocol:** FastMCP
**Tools:**
- `get_inventory(shelter_id: str) -> dict` — all items and quantities
- `check_availability(shelter_id: str, item_type: str, quantity: int) -> bool`
- `reserve_items(shelter_id: str, items: dict) -> dict` — mark items as reserved
- `release_reservation(reservation_id: str) -> bool`
- `get_all_shelters_with_inventory() -> list`
**Data Source:** In-memory database (for demo) or PostgreSQL/SQLite
**Note:** This simulates a real supply management system. Use mock data that is realistic.

### 6.4 Shelter API MCP Server
**Protocol:** FastMCP
**Tools:**
- `find_nearby_shelters(lat: float, lon: float, radius_km: float = 10) -> list` — sorted by distance
- `get_shelter_details(shelter_id: str) -> dict` — capacity, current_occupancy, amenities, accessibility
- `update_occupancy(shelter_id: str, delta: int) -> bool` — increment/decrement
- `get_accessible_shelters(lat: float, lon: float) -> list` — wheelchair accessible only
**Data Source:** Mock database with 50 realistic shelter entries (use a Python dict or SQLite)

## 7. Security Layer Specifications

### 7.1 PII Redaction Module (`security/pii_redactor.py`)
**Purpose:** Remove all personally identifiable information before any agent processes data
**Techniques:**
- Named Entity Recognition (NER) via regex + NLP for names, phone numbers, email addresses, SSNs, physical addresses
- Replace PII with `[REDACTED-<type>-<hash>]` tokens
- Store original → token mapping in encrypted vault (in-memory for demo, with encryption key from env)
- Only the Communication Hub (with RBAC: admin role) can de-tokenize for family notifications
**Functions:**
- `redact(text: str) -> Tuple[str, VaultRef]`
- `detokenize(vault_ref: VaultRef, role: str) -> Optional[str]` (checks RBAC)
- `get_redaction_log() -> list` (audit trail)

### 7.2 Field-Level Encryption (`security/encryption.py`)
**Purpose:** Encrypt sensitive fields at rest and in transit
**Scope:**
- Victim location coordinates (exact addresses) — encrypt, store approximate in clear
- Contact information vault
- Communication logs
**Functions:**
- `encrypt_field(plaintext: str, key: bytes) -> str`
- `decrypt_field(ciphertext: str, key: bytes) -> str`
- `generate_key() -> bytes`
- Uses Fernet symmetric encryption from `cryptography` library

### 7.3 RBAC Access Control (`security/access_control.py`)
**Purpose:** Role-based access control for all system operations
**Roles:**
- `public` — Can view anonymized dashboard, public briefings
- `operator` — Can view all incident details (redacted PII), dispatch volunteers, allocate resources
- `admin` — Can de-tokenize PII, access audit logs, system configuration
**Functions:**
- `check_permission(role: str, action: str) -> bool`
- `require_role(min_role: str)` (decorator for agent tools)
- `get_audit_log() -> list`

### 7.4 Audit Logger
**Purpose:** Tamper-proof, append-only log of all system actions
**Logs:**
- Every agent action with timestamp, agent_id, action, input_hash, output_hash
- Every PII access (who, when, what token)
- Every resource allocation
- Every volunteer dispatch
**Storage:** Append-only JSONL file or SQLite table with write-once policy

## 8. Agent Skills / CLI Tools (`skills/`)

### 8.1 Geo Parser (`skills/geo_parser.py`)
- `parse_location_from_text(text: str) -> Location` — Extract location mentions from free text
- `normalize_address(address: str) -> str` — Standardize address format
- `calculate_distance(loc1: Location, loc2: Location) -> float` — Haversine distance

### 8.2 Severity Scorer (`skills/severity_scorer.py`)
- `calculate_severity(report: dict) -> int` — Multi-factor scoring algorithm
- `factors: people_affected * 2 + medical_needs * 3 + trapped * 5 + infrastructure_damage * 2 + weather_multiplier`
- `get_severity_label(score: int) -> str` — 1-3: Low, 4-6: Moderate, 7-8: High, 9-10: Critical

### 8.3 Notification Sender (`skills/notification_sender.py`)
- `send_sms(phone_hash: str, message: str) -> bool` — Simulated SMS gateway
- `send_email(email_hash: str, subject: str, body: str) -> bool` — Simulated email
- `format_alert_message(template: str, context: dict) -> str` — Template engine for alerts

## 9. Dashboard (`dashboard/app.py`)

**Framework:** Streamlit
**Pages/Tabs:**

### Tab 1: Command Center
- Real-time incident feed (auto-refresh every 30s)
- Severity distribution bar chart
- Active agent status cards (green=active, yellow=busy, red=error)
- Incident map (folium) with color-coded pins by severity

### Tab 2: Incident Detail
- Click any incident to see full timeline
- Agent decision trail (which agents processed it, what decisions)
- Resource allocation status
- Volunteer dispatch status

### Tab 3: Resource Monitor
- Shelter occupancy map
- Supply inventory levels (warning if < 20%)
- Volunteer availability by region

### Tab 4: Audit Log
- Filterable log of all agent actions
- PII access log (admin only)
- Communication history

**Data Source:** The dashboard reads from a shared state file (`state/incidents.jsonl`) that agents write to. In production this would be a database.

## 10. Orchestrator (`agents/orchestrator.py`)

**ADK Type:** SequentialAgent with conditional branching
**Flow:**
```
receive_report(raw_text)
  → intake_agent.process(raw_text)
    → IF severity > 5: parallel to [crisis_assessor, resource_allocator]
    → IF severity <= 5: crisis_assessor only
  → crisis_assessor.analyze(report)
    → IF severity_upgraded_to > 8: immediate_escalation()
  → resource_allocator.allocate(assessed_report)
    → volunteer_coordinator.dispatch(allocation.tasks)
  → communication_hub.notify(all_results)
  → write_to_dashboard_state(all_results)
  → return CoordinationResult
```

**Error Handling:**
- Any agent failure triggers `communication_hub.notify_agency()` with error details
- Partial results are still saved and communicated
- Retry logic with exponential backoff for MCP server calls

## 11. File Structure

```
safehaven/
├── .env                              # API keys (NEVER COMMIT)
├── .gitignore
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container for deployment
├── README.md                         # Full documentation
├── kaggle_notebook.ipynb             # Kaggle submission notebook
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py               # Main coordination agent
│   ├── intake_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                  # ADK agent definition
│   │   ├── tools.py                  # Custom tools (parse, geocode, redact, score)
│   │   └── prompt.py                 # System instructions/instructions
│   ├── resource_allocator/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py                  # (find_shelters, check_supply, allocate, route, confirm)
│   │   └── prompt.py
│   ├── crisis_assessor/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py                  # (weather, forecast, historical, risk_assessment)
│   │   └── prompt.py
│   ├── volunteer_coordinator/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py                  # (find_volunteers, dispatch, track, brief)
│   │   └── prompt.py
│   └── communication_hub/
│       ├── __init__.py
│       ├── agent.py
│       ├── tools.py                  # (notify_agency, family_update, public_brief, broadcast, log)
│       └── prompt.py
│
├── mcp_servers/
│   ├── weather_mcp/
│   │   ├── __init__.py
│   │   └── server.py                 # FastMCP: current, forecast, alerts
│   ├── geocoding_mcp/
│   │   ├── __init__.py
│   │   └── server.py                 # FastMCP: geocode, reverse, batch
│   ├── supply_db_mcp/
│   │   ├── __init__.py
│   │   └── server.py                 # FastMCP: inventory, availability, reserve, release
│   └── shelter_api_mcp/
│       ├── __init__.py
│       └── server.py                 # FastMCP: find, details, occupancy, accessible
│
├── security/
│   ├── __init__.py
│   ├── pii_redactor.py               # NER-based PII detection + tokenization
│   ├── encryption.py                 # Fernet field-level encryption
│   ├── access_control.py             # RBAC with role decorator
│   └── audit_logger.py               # Append-only action logging
│
├── skills/
│   ├── __init__.py
│   ├── geo_parser.py                 # Location extraction + distance calc
│   ├── severity_scorer.py            # Multi-factor severity algorithm
│   └── notification_sender.py        # SMS/email simulation + templates
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py                        # Streamlit multi-page dashboard
│   └── mock_data.py                  # Realistic shelter/volunteer/supply seed data
│
└── state/                            # Shared state (dashboard reads this)
    ├── incidents.jsonl               # Append-only incident records
    └── audit.jsonl                   # Append-only audit records
```

## 12. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Framework | Google ADK (`google-adk`) | Multi-agent orchestration |
| Agent Models | Gemini 2.5 Flash (via Google AI Studio) | LLM brain for each agent |
| MCP Framework | FastMCP (`fastmcp`) | MCP server implementation |
| Dashboard | Streamlit + Folium | Real-time web UI |
| Security | `cryptography` (Fernet) | Field-level encryption |
| Geocoding | Google Maps API / Nominatim | Address → coordinates |
| Weather | OpenWeatherMap API | Current + forecast data |
| Data Storage | JSONL files (demo) / SQLite | Incident + audit storage |
| Deployment | Docker + Render/Antigravity | Containerized hosting |
| Language | Python 3.11+ | All components |

## 13. Competition Requirements Mapping

This table proves we satisfy ALL 6 required concepts:

| Required Concept | Where Demonstrated | Evidence in Submission |
|---|---|---|
| **Agent / Multi-agent system (ADK)** | `agents/` — 5 ADK agents with orchestrator.py | Code: orchestrator.py, 5 agent folders with agent.py files |
| **MCP Server** | `mcp_servers/` — 4 FastMCP servers | Code: 4 server.py files with @server.tool() decorators |
| **Antigravity** | Video: Show deployed dashboard running | Video: "Deployed on Antigravity with one click" |
| **Security features** | `security/` — PII redaction, encryption, RBAC, audit | Code: pii_redactor.py, encryption.py, access_control.py |
| **Deployability** | Video: Live demo of deployed dashboard + Dockerfile | Video: Walk through deployment. Code: Dockerfile, README.md |
| **Agent skills (e.g., Agents CLI)** | `skills/` — geo_parser, severity_scorer, notification_sender | Code: 3 skill modules. Video: Show CLI tool execution |

## 14. Build Order (Priority Sequence)

Build in this order. Each step is a working checkpoint:

### Wave 1: Foundation (Day 1-2)
1. `requirements.txt`, `.env`, folder structure
2. `security/pii_redactor.py` — Must work before any agent processes data
3. `security/encryption.py`
4. `skills/geo_parser.py`
5. `skills/severity_scorer.py`
6. `mcp_servers/geocoding_mcp/server.py` — Most other agents depend on this

### Wave 2: Core Agents (Day 3-4)
7. `agents/intake_agent/` — Full agent + tools + prompt
8. `agents/crisis_assessor/` — Full agent + tools + prompt
9. `agents/resource_allocator/` — Full agent + tools + prompt
10. `agents/orchestrator.py` — Wire first 3 agents together

### Wave 3: Supporting Agents + MCP (Day 5)
11. `mcp_servers/weather_mcp/server.py`
12. `mcp_servers/shelter_api_mcp/server.py`
13. `mcp_servers/supply_db_mcp/server.py`
14. `agents/volunteer_coordinator/`
15. `agents/communication_hub/`

### Wave 4: Integration (Day 6)
16. Update orchestrator to include all 5 agents
17. `skills/notification_sender.py`
18. `security/access_control.py` + `security/audit_logger.py`
19. End-to-end test: raw report → dashboard update

### Wave 5: Dashboard (Day 7)
20. `dashboard/mock_data.py` — Seed with 50 realistic shelters, 100 volunteers, supply inventory
21. `dashboard/app.py` — Full Streamlit dashboard with all 4 tabs
22. Integration: dashboard reads from agent state files

### Wave 6: Deploy + Package (Day 8)
23. `Dockerfile`
24. Deploy to Render or Antigravity
25. `kaggle_notebook.ipynb` — Clean notebook showing system execution
26. `README.md` — Full documentation with architecture diagrams

### Wave 7: Submit (Days 9-10)
27. Record 5-minute YouTube video
28. Write Kaggle Writeup (max 2500 words)
29. Submit to competition

## 15. Mock Data Specification (for `dashboard/mock_data.py`)

Create realistic demo data for a fictional disaster scenario:

**Disaster Scenario:** Category 3 hurricane "Mara" hits coastal city "Bayport"
- Primary impact zone: 10-mile radius around city center
- 50,000 residents affected
- 12 shelters activated
- 300 volunteers registered
- Key needs: shelter, water, medical, food

**Shelters (12 entries):**
```python
shelters = [
    {"id": "SH001", "name": "Bayport High School", "lat": 27.95, "lon": -82.45, 
     "capacity": 500, "current_occupancy": 342, "amenities": ["medical", "food", "water", "power"],
     "accessible": True, "status": "open"},
    # ... 11 more with realistic names, capacities, varying occupancy
]
```

**Volunteers (20 representative entries):**
```python
volunteers = [
    {"id": "V001", "name_hash": "abc123", "lat": 27.96, "lon": -82.44,
     "skills": ["medical", "spanish"], "status": "available", "hours_logged": 12},
    # ... 19 more with diverse skills and locations
]
```

**Supply Inventory (per shelter):**
```python
supplies = {
    "SH001": {"water_liters": 5000, "food_meals": 1200, "medical_kits": 45, "blankets": 300, "cots": 400},
    # ... realistic quantities that deplete as allocations happen
}
```

## 16. API Key Setup

Create `.env` file:
```bash
# Google AI Studio (for ADK agent LLM calls)
GEMINI_API_KEY=your_key_here

# OpenWeatherMap (free tier: 1000 calls/day)
OPENWEATHER_API_KEY=your_key_here

# Google Maps (free tier: $200 credit/month)
GOOGLE_MAPS_API_KEY=your_key_here

# Encryption (generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())")
ENCRYPTION_KEY=your_32_byte_base64_key_here
```

**Get keys:**
- Gemini: https://aistudio.google.com/app/apikey
- OpenWeatherMap: https://home.openweathermap.org/api_keys
- Google Maps: https://developers.google.com/maps/documentation/geocoding/get-api-key

## 17. Evaluation Strategy

### Category 1: The Pitch (30 points)

**Core Concept & Value (10/10):**
- Problem: Real, documented, life-affecting
- Innovation: First multi-agent disaster response system in the competition
- Track alignment: Pure "Agents for Good" — direct humanitarian impact
- Wow factor: Live dashboard showing real-time coordination

**YouTube Video (10/10):**
- 0:00-0:30: Open with disaster footage + stats (20M displaced/year)
- 0:30-1:00: Problem + why agents (coordination chaos)
- 1:00-2:00: Architecture diagram walkthrough
- 2:00-3:45: **LIVE DEMO** — type a report, watch agents work, see dashboard update
- 3:45-4:30: Code highlights (ADK orchestration, MCP servers, security layer)
- 4:30-5:00: Deployed URL + GitHub + call to action

**Writeup (10/10):**
- Follow Kaggle template: Problem → Solution → Architecture → Demo → Code → Impact
- Include architecture diagram (generated from code)
- Include dashboard screenshots
- Keep under 2,500 words

### Category 2: The Implementation (70 points)

**Technical Implementation (50/50):**
- 5 ADK agents with proper delegation → 10 points
- 4 MCP servers with real external data → 10 points
- Security layer with PII redaction + encryption + RBAC → 10 points
- Agent skills/tools with meaningful functionality → 10 points
- Code quality: comments, error handling, logging → 10 points

**Documentation (20/20):**
- README.md with: problem, solution, architecture diagram, setup instructions, deployed link, video link → 10 points
- Code comments explaining design decisions → 5 points
- This PID.md (internal, not submitted) ensures consistency → 5 points

## 18. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Rate limits on free AI models | Tool switching strategy (6 models) + local testing |
| MCP server external API failure | Graceful fallbacks with cached/mock data |
| Deployment platform issues | Docker container works on any platform (Render, Railway, Antigravity) |
| Running out of time | Build order prioritizes working demo over perfection. Dashboard with 3 agents > 5 agents with no UI |
| Kaggle notebook does not run | Notebook uses same code as GitHub, pre-tested locally |

## 19. Success Criteria

- [ ] All 5 ADK agents communicate through orchestrator
- [ ] All 4 MCP servers respond to tool calls
- [ ] PII redaction works (test: input with name/phone → output has [REDACTED] tokens)
- [ ] Dashboard shows live agent coordination
- [ ] Dockerfile builds and runs
- [ ] Deployed URL is accessible
- [ ] 5-minute video recorded and uploaded to YouTube
- [ ] Kaggle writeup submitted before deadline

---

## Quick Start for AI Assistants

When you (the AI assistant) start working on this project:

1. **Read this PID.md fully** — it is the single source of truth
2. **Check the current file structure** — see what exists already
3. **Follow the Build Order** (Section 14) — do not skip ahead
4. **Every file must:**
   - Have docstrings explaining purpose
   - Have type hints on all functions
   - Handle errors gracefully (try/except with logging)
   - Use the .env file for all API keys (never hardcode)
5. **Test incrementally** — after every agent file, run a quick test
6. **When generating code, match the patterns** already established in existing files

**Key decisions already made (do not change):**
- Python 3.11+, Google ADK, FastMCP, Streamlit
- 5 agents: Intake, CrisisAssessor, ResourceAllocator, VolunteerCoordinator, CommunicationHub
- 4 MCP servers: Weather, Geocoding, SupplyDB, ShelterAPI
- Security: PII redaction, Fernet encryption, RBAC, audit logging
- Deployment: Docker + Render/Antigravity
- Track: Agents for Good
