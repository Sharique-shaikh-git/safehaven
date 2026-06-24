# CLAUDE.md — SafeHaven Persistent Agent Context

> **Every AI agent or model session must read this file FIRST before touching any code.**
> Full architecture spec lives in [PID.md](./PID.md) — read that for the complete picture.
> This file records what's built, tested, and decided so new sessions don't duplicate work.

---

## 🟢 CURRENT STATUS — Updated 2026-06-24

**Last completed:** Dockerfile + .dockerignore built, CLAUDE.md updated, `git push` to main ✅

### What we're doing RIGHT NOW
→ **Deploying to Render** (Step 2 of deployment guide)

### Deployment checklist (update this as each step completes)
| Step | Task | Status |
|---|---|---|
| 1 | Create Render account | ⬜ Pending |
| 2 | Add `render.yaml` to repo | ⬜ Pending — **NEXT ACTION** |
| 3 | Add env vars in Render dashboard | ⬜ Pending |
| 4 | Connect GitHub repo to Render | ⬜ Pending |
| 5 | Build succeeds → get live URL | ⬜ Pending |
| 6 | Fix `config.js` for production (API_BASE = same origin) | ⬜ Pending |
| 7 | Write `README.md` with live URL | ⬜ Pending |
| 8 | Write `kaggle_notebook.ipynb` | ⬜ Pending |
| 9 | Submit on Kaggle | ⬜ Pending |
| 10 | Write Kaggle writeup (≤2500 words) | ⬜ Pending |
| 11 | Record YouTube video (5 min) | ⬜ Pending |

### Dashboard build status (all ✅ — do NOT touch unless bug reported)
| Component | Status |
|---|---|
| Backend FastAPI (`dashboard/api.py`) | ✅ 7 GET + POST — comms/audit bug fixed |
| Frontend 12 components, 7 pages | ✅ |
| Sidebar — Settings + Logout modals | ✅ |
| TopBar — notification bell dropdown | ✅ |
| Incident Map (direct Leaflet.js) | ✅ |
| Communications page (`/api/communications`) | ✅ |
| Audit Log page (`/api/audit`) | ✅ |
| Dockerfile + .dockerignore | ✅ |
| Git pushed to `main` | ✅ commit `093fd40` |

---


## Project Overview

**SafeHaven** — AI-powered disaster response coordination system.
**Track:** Agents for Good (Kaggle Hackathon, deadline July 6 2026)
**Repo root:** `safehaven/` (this directory)
**Spec:** PID.md (single source of truth — always read it before architecting anything)

---

## Environment

| Item | Value |
|---|---|
| Python | 3.13.5 |
| Virtual env | `uv` — located at `.venv/` |
| Run commands | `uv run python -m <module>` OR activate venv first: `.venv\Scripts\activate` |
| Install deps | `uv pip install -r requirements.txt` |
| API keys | Copy `.env.example` → `.env`, fill in real values. **Never commit `.env`** |

### Key packages (all installed in .venv)
- `google-adk==2.3.0` — ADK agent framework
- `google-generativeai==0.8.6` — Gemini model backend
- `mcp==1.28.0` — MCP server protocol (**NOT FastMCP** — see locked decisions below)
- `fastapi` — dashboard API backend
- `uvicorn` — ASGI server for FastAPI
- `python-dotenv==1.2.2` — loads `.env` automatically

---

## Locked Decisions (do NOT change these)

1. **MCP package:** Use the official `mcp` Python package (`import mcp`) — NOT `fastmcp`. Already verified to install cleanly.
2. **Model backend:** Gemini via `google-adk` — model name read from `ADK_MODEL` env var, defaults to `"gemini-2.0-flash"`.
3. **Severity threshold:** Crisis Assessor `assessed_severity > 5` triggers the parallel branch (resource_allocator + volunteer_coordinator run concurrently via `asyncio.gather`). Score ≤ 5 skips both.
4. **Agent pattern:** All agents follow the exact same structure as `intake_agent/`:
   - `agent.py` — imports `Agent` from `google.adk.agents`, creates one instance named `<role>_agent`
   - `prompt.py` — defines one `<ROLE>_INSTRUCTION` string
   - `__init__.py` — empty
5. **Orchestrator import:** Always import agents from their modules, never redefine them.
6. **State files:** Written to `state/incidents.jsonl` and `state/audit.jsonl` (append-only). Dashboard reads from these.
7. **Security:** PII is redacted before any downstream agent sees it. Only `admin` role can de-tokenise via vault refs.

---

## Build Status

### Agents (`agents/`)

| File | Status | Notes |
|---|---|---|
| `intake_agent/agent.py` | ✅ Pre-existing + tested | Import test passed |
| `intake_agent/prompt.py` | ✅ Pre-existing + tested | `INTAKE_AGENT_INSTRUCTION` |
| `crisis_assessor/agent.py` | ✅ Built + tested | Import test passed |
| `crisis_assessor/prompt.py` | ✅ Built + tested | `CRISIS_ASSESSOR_INSTRUCTION` |
| `resource_allocator/agent.py` | ✅ Built + tested | Import test passed |
| `resource_allocator/prompt.py` | ✅ Built + tested | `RESOURCE_ALLOCATOR_INSTRUCTION` |
| `volunteer_coordinator/agent.py` | ✅ Built + tested | Import test passed |
| `volunteer_coordinator/prompt.py` | ✅ Built + tested | `VOLUNTEER_COORDINATOR_INSTRUCTION` |
| `communication_hub/agent.py` | ✅ Built + tested | Import test passed |
| `communication_hub/prompt.py` | ✅ Built + tested | `COMMUNICATION_HUB_INSTRUCTION` |
| `orchestrator.py` | ✅ Built + ✅ End-to-end tested | End-to-end pipeline run captured in `docs/sample_pipeline_run.md` (timestamp fix verified in orchestration input). |

### MCP Servers (`mcp_servers/`)

| File | Status |
|---|---|
| `geocoding_mcp/server.py` | ✅ Built + tested | `uv run python -m mcp_servers.geocoding_mcp.server` passes with real Nominatim API |
| `weather_mcp/server.py` | ✅ Built + tested | `uv run python -m mcp_servers.weather_mcp.server` passes with real OpenWeatherMap API |
| `supply_db_mcp/server.py` | ✅ Built + tested | `uv run python -m mcp_servers.supply_db_mcp.server` passes — 12 shelters, reservation lifecycle works |
| `shelter_api_mcp/server.py` | ✅ Built + tested | `uv run python -m mcp_servers.shelter_api_mcp.server` passes — 12 shelters, distance-sorted results |

### Security (`security/`)

| File | Status |
|---|---|
| `pii_redactor.py` | ✅ Built + tested | `uv run python -m security.pii_redactor` passes |
| `encryption.py` | ✅ Built + tested | `uv run python -m security.encryption` — 7/7 PASS |
| `access_control.py` | ✅ Built + tested | `uv run python -m security.access_control` passes — RBAC matrix + require_role decorator |
| `audit_logger.py` | ✅ Built + tested | `uv run python -m security.audit_logger` passes — append-only JSONL at state/audit.jsonl |

### Skills (`skills/`)

| File | Status |
|---|---|
| `geo_parser.py` | ✅ Built + tested | `uv run python -m skills.geo_parser` — all PASS |
| `severity_scorer.py` | ✅ Built + tested | `uv run python -m skills.severity_scorer` — all PASS |
| `notification_sender.py` | ✅ Built + tested | `uv run python -m skills.notification_sender` — all PASS |

### Dashboard (`dashboard/`)

**Stack:** FastAPI (Python) backend + React (Vite) frontend — **Streamlit dropped**.

| File | Status | Notes |
|---|---|---|
| `mock_data.py` | ✅ Built + tested | 12 shelters, 20 volunteers, supply inventory, agent status |
| `api.py` | ✅ Built + tested | FastAPI — 7 GET endpoints + POST /api/incidents (real orchestrator) |
| `frontend/` | ✅ Built + tested | Vite 5 + React 18 — 12 components, light-mode, Leaflet map, 7 pages |

#### Frontend component inventory (`dashboard/frontend/src/`)

| Component | Purpose |
|---|---|
| `App.jsx` | Root — sidebar navigation, page routing, footer |
| `components/Sidebar.jsx` | Blue sidebar (`#1B4FDC`) — 7 nav pages, logo, **Settings modal** (API status, masked keys, system info), **Logout confirmation modal** |
| `components/TopBar.jsx` | Light top bar — date/time, connection status, **notification bell dropdown** (shows last 5 incidents, closes on outside click) |
| `components/IncidentMap.jsx` | **Interactive Leaflet map** (direct Leaflet.js, no react-leaflet) — incident pins colored by severity, shelter circles, popups, filter strip, legend, quick-info panel |
| `components/AgentStatus.jsx` | 5 agent status cards — colored icons, processing shimmer bar, live polling |
| `components/SubmitIncident.jsx` | Report textarea, example buttons, live pipeline step tracker, collapsible agent outputs |
| `components/IncidentTable.jsx` | Sortable incident table with severity badges, empty state |
| `components/ShelterCapacity.jsx` | Overall utilization bar + per-shelter progress bars |
| `components/SupplyLevels.jsx` | 2×3 supply grid with count-up animation on load |
| `components/VolunteerRoster.jsx` | Status summary grid (Available/On Site/En Route/Unavailable) + skill-tagged list |
| `components/CommunicationsPage.jsx` | **New** — wired to `/api/communications` — expandable cards per message, channel filter, stats row, sent indicators |
| `components/AuditLog.jsx` | **New** — wired to `/api/audit` — full audit trail table with action icons, actor, details, role badge |

#### Frontend npm dependencies added
- `react-leaflet` + `leaflet` — installed with `--legacy-peer-deps`

#### Pages / navigation
| Page key | Title | Content |
|---|---|---|
| `dashboard` | Command Center | Agent status + Submit form + Incident table |
| `map` | Incident Map | Full Leaflet map (direct Leaflet.js) |
| `incidents` | Incident Management | Submit form + full table |
| `resources` | Resource Monitor | Shelter capacity + Supply levels |
| `volunteers` | Volunteer Roster | VolunteerRoster full page |
| `comms` | Communications Hub | CommunicationsPage — real data from `/api/communications` |
| `audit` | Audit Log | AuditLog — real data from `/api/audit` |

#### Design system (`src/index.css`)
- **Theme:** Light mode — white `#FFFFFF` cards, `#F4F6FB` background, blue `#1B4FDC` sidebar
- **Typography:** Inter (UI) + JetBrains Mono (numbers/time/IDs) from Google Fonts
- **Leaflet CSS:** Imported directly in `index.css` via `@import 'leaflet/dist/leaflet.css'`
- **Animations:** `fadeUp`, `fadeIn`, `shimmer`, `dotPulse`, `spin`
- **No dark mode, no glassmorphism** — clean professional light UI matching reference design

---

## Known Issues / Fixed Bugs (do NOT redo these)

1. **`orchestrator.py` — `__main__` path issue (FIXED)**
   Running `python agents/orchestrator.py` directly broke absolute imports.
   Fix applied: `sys.path.insert(0, project_root)` at top of orchestrator before any imports.
   Now works both ways: `python agents/orchestrator.py` AND `python -m agents.orchestrator`

2. **`google-adk` not in global Python (FIXED)**
   `google-adk` was not pre-installed. Now installed both globally (for ad-hoc testing)
   and in `.venv` (for all project runs). Always prefer the `.venv`.

3. **Real secrets in `.env.example` (FIXED)**
   `GEMINI_API_KEY` and `OPENWEATHER_API_KEY` were committed as real values.
   Both replaced with placeholder strings. Real keys live in `.env` only (gitignored).

4. **`FastMCP` not the right package (DECIDED EARLY)**
   PID originally said FastMCP. User corrected: use the official `mcp` package.
   All future MCP server code must use `import mcp` / `mcp.server` patterns.

5. **`react-leaflet` peer dep conflict + React 18 incompatibility (FIXED)**
   `react-leaflet` throws `render2 is not a function` with React 18. Replaced entirely
   with direct Leaflet.js using `useRef`/`useEffect` — no wrapper library needed.
   Leaflet CSS must be imported inside the component file, NOT in `index.css`.

6. **Notification bell was non-functional (FIXED)**
   Added dropdown panel to TopBar — shows last 5 incidents with severity badges,
   timestamps, 2-line preview. Closes on outside click via `mousedown` listener.

7. **Settings and Logout buttons were dead (FIXED)**
   Settings → modal with API connection status, masked API keys, system info.
   Logout → confirmation modal with sign-out screen.

8. **`/api/communications` TypeError (FIXED)**
   The `communications` field in incident data can be a raw string or a list of dicts.
   Endpoint now handles both safely with isinstance() checks before unpacking.

9. **CORS only covered port 5173 (FIXED)**
   Vite falls back to 5174/5175/5176 if 5173 is busy. Added all four ports to allow_origins.

---

## How to Run

### Backend API
```powershell
# From safehaven/ — activate venv first
.venv\Scripts\activate
uvicorn dashboard.api:app --reload --port 8000
```

### Frontend Dev Server
```powershell
cd dashboard/frontend
npm run dev
# Opens at http://localhost:5173
```

### End-to-End Pipeline Test (no dashboard)
```powershell
.venv\Scripts\activate
python -m agents.orchestrator
```

---

## File Structure Snapshot (current state)

```
safehaven/
├── .env                    ← gitignored, has real keys
├── .env.example            ← committed, placeholders only
├── .gitignore              ✅
├── .dockerignore           ✅ NEW
├── Dockerfile              ✅ NEW — multi-stage (Node 20 → Python 3.13 slim)
├── .venv/                  ← uv virtualenv, gitignored
├── CLAUDE.md               ← this file, update after every tested file
├── PID.md                  ← full spec, read this first
├── requirements.txt        ✅
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py     ✅ built (sys.path fix applied)
│   ├── intake_agent/       ✅ agent.py + prompt.py tested
│   ├── crisis_assessor/    ✅ agent.py + prompt.py tested
│   ├── resource_allocator/ ✅ agent.py + prompt.py tested
│   ├── volunteer_coordinator/ ✅ agent.py + prompt.py tested
│   └── communication_hub/  ✅ agent.py + prompt.py tested
├── mcp_servers/
│   ├── geocoding_mcp/      ✅ server.py built
│   ├── weather_mcp/        ✅ server.py built
│   ├── supply_db_mcp/      ✅ server.py built
│   └── shelter_api_mcp/    ✅ server.py built
├── security/               ✅ all 4 modules built
├── skills/                 ✅ all 3 modules built
├── dashboard/
│   ├── __init__.py
│   ├── api.py               ✅ FastAPI — 7 GET + POST, static file serving for production
│   ├── mock_data.py         ✅ seed data (12 shelters, 20 volunteers, supplies, agents)
│   └── frontend/            ✅ Vite 5 + React 18 — 12 components, 7 pages, light-mode
│       ├── src/
│       │   ├── index.css        ← full design system (light mode)
│       │   ├── App.jsx          ← sidebar routing shell (7 pages)
│       │   └── components/
│       │       ├── Sidebar.jsx          ← Settings + Logout modals
│       │       ├── TopBar.jsx           ← bell dropdown
│       │       ├── IncidentMap.jsx      ← direct Leaflet.js map
│       │       ├── AgentStatus.jsx
│       │       ├── SubmitIncident.jsx
│       │       ├── IncidentTable.jsx
│       │       ├── ShelterCapacity.jsx
│       │       ├── SupplyLevels.jsx
│       │       ├── VolunteerRoster.jsx
│       │       ├── CommunicationsPage.jsx  ← NEW
│       │       └── AuditLog.jsx            ← NEW
│       └── package.json     ← includes leaflet (direct, no react-leaflet)
└── state/                  ← created at runtime (incidents.jsonl, audit.jsonl)
```

---

## What's Left (before Kaggle submission)

### Must-Have (competition requirements)
| Item | Status | Notes |
|---|---|---|
| `Dockerfile` | ✅ Built | Multi-stage Node 20 → Python 3.13 slim |
| `.dockerignore` | ✅ Built | Excludes venv, node_modules, .env, state/ |
| `README.md` | ❌ Not built | Documentation score — needs arch diagram, setup, deployed URL |
| `kaggle_notebook.ipynb` | ❌ Not built | Required for submission — end-to-end pipeline demo |
| Deploy to Render/Railway | ❌ Not done | Needed for deployed URL in README + video |
| YouTube video (5 min) | ❌ Not recorded | "The Pitch" = 10 pts |
| Kaggle writeup | ❌ Not written | Max 2500 words |

### Nice-to-Have (dashboard polish)
| Item | Status | Notes |
|---|---|---|
| Communications page | ✅ Done | Wired to `/api/communications` — expandable cards |
| Audit Log page | ✅ Done | Wired to `/api/audit` — full table |
| Map with real geocoordinates | ⚠️ Partial | Incidents use stable random offsets; real lat/lon requires Geocoding MCP wiring |

### Build priority order
1. Deploy to Render (get the live URL) ← **Next**
2. `README.md` — documentation score  
3. `kaggle_notebook.ipynb` — submission artifact  
4. Record YouTube video  
5. Write Kaggle writeup + submit
