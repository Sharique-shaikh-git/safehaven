# CLAUDE.md — SafeHaven Persistent Agent Context

> **Every AI agent or model session must read this file FIRST before touching any code.**
> Full architecture spec lives in [PID.md](./PID.md) — read that for the complete picture.
> This file records what's built, tested, and decided so new sessions don't duplicate work.

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
- `streamlit==1.58.0` — dashboard framework
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
| `orchestrator.py` | ✅ Built | Import-tested; end-to-end test blocked on GEMINI_API_KEY being set |

### MCP Servers (`mcp_servers/`)

| File | Status |
|---|---|
| `geocoding_mcp/server.py` | ❌ Not yet built |
| `weather_mcp/server.py` | ❌ Not yet built |
| `supply_db_mcp/server.py` | ❌ Not yet built |
| `shelter_api_mcp/server.py` | ❌ Not yet built |

### Security (`security/`)

| File | Status |
|---|---|
| `pii_redactor.py` | ✅ Built + tested | `uv run python -m security.pii_redactor` passes |
| `encryption.py` | ✅ Built + tested | `uv run python -m security.encryption` — 7/7 PASS |
| `access_control.py` | ❌ Not yet built |
| `audit_logger.py` | ❌ Not yet built |

### Skills (`skills/`)

| File | Status |
|---|---|
| `geo_parser.py` | ✅ Built + tested | `uv run python -m skills.geo_parser` — all PASS |
| `severity_scorer.py` | ✅ Built + tested | `uv run python -m skills.severity_scorer` — all PASS |
| `notification_sender.py` | ✅ Built + tested | `uv run python -m skills.notification_sender` — all PASS |

### Dashboard (`dashboard/`)

| File | Status |
|---|---|
| `mock_data.py` | ❌ Not yet built |
| `app.py` | ❌ Not yet built |

---

## Known Issues / Fixed Bugs (do NOT redo these)

1. **`orchestrator.py` — `__main__` path issue (FIXED)**
   Running `python agents/orchestrator.py` directly broke absolute imports.
   Fix applied: `sys.path.insert(0, project_root)` at top of orchestrator before any imports.
   Now works both ways: `python agents/orchestrator.py` AND `python -m agents.orchestrator`.

2. **`google-adk` not in global Python (FIXED)**
   `google-adk` was not pre-installed. Now installed both globally (for ad-hoc testing)
   and in `.venv` (for all project runs). Always prefer the `.venv`.

3. **Real secrets in `.env.example` (FIXED)**
   `GEMINI_API_KEY` and `OPENWEATHER_API_KEY` were committed as real values.
   Both replaced with placeholder strings. Real keys live in `.env` only (gitignored).

4. **`FastMCP` not the right package (DECIDED EARLY)**
   PID originally said FastMCP. User corrected: use the official `mcp` package.
   All future MCP server code must use `import mcp` / `mcp.server` patterns.

---

## Next File to Build (PID.md Section 14 — Wave 1 Foundation)

Per the build order, the foundation files come before more agents or MCP servers.

**Build next (in this order):**

1. `security/pii_redactor.py` — PII redaction with regex NER, vault tokenisation (PID §7.1)
2. `security/encryption.py` — Fernet field-level encryption (PID §7.2)
3. `skills/geo_parser.py` — Location extraction + Haversine distance (PID §8.1)
4. `skills/severity_scorer.py` — Multi-factor severity algorithm (PID §8.2)
5. `mcp_servers/geocoding_mcp/server.py` — Geocoding via Nominatim (PID §6.2)

> **Do not** jump to dashboard, orchestrator wiring, or MCP weather server until the
> security and skills foundation is in place. Follow the wave order strictly.

---

## How to Run the Pipeline (once GEMINI_API_KEY is set in .env)

```powershell
# From safehaven/ — activate venv first
.venv\Scripts\activate

# End-to-end pipeline test
python -m agents.orchestrator
```

---

## File Structure Snapshot (current state)

```
safehaven/
├── .env                    ← gitignored, has real keys
├── .env.example            ← committed, placeholders only
├── .gitignore              ✅
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
│   ├── geocoding_mcp/      ❌ server.py missing
│   ├── weather_mcp/        ❌ server.py missing
│   ├── supply_db_mcp/      ❌ folder + server.py missing
│   └── shelter_api_mcp/    ❌ folder + server.py missing
├── security/               ❌ all 4 modules missing
├── skills/                 ❌ folder + all 3 modules missing
├── dashboard/              ❌ mock_data.py + app.py missing
└── state/                  ❌ folder missing (created at runtime)
```
