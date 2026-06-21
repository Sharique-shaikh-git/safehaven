# SafeHaven — Quickstart

## Step 1 — Get this onto your machine
Download the zip from this chat, unzip it, `cd safehaven`.

## Step 2 — Environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3 — API key (the one thing you actually need before anything runs)
1. Go to https://aistudio.google.com → create a free Gemini API key
2. `cp .env.example .env`
3. Paste the key into `GEMINI_API_KEY=` in `.env`

## Step 4 — Confirm it works
```bash
python -c "from agents.intake_agent.agent import intake_agent; print(intake_agent.name)"
```
If that prints `intake_agent`, your environment is correct. This is already tested and verified —
the agent class loads with no errors.

## Step 5 — Run it against a real model
You'll need to load `.env` (e.g. `python-dotenv`) and use ADK's Runner to actually send a message
through the agent and get a response — that's the next file to build
(`agents/orchestrator.py`). Say the word and I'll write that next, tested the same way.

## What's already built
- `agents/intake_agent/` — real, tested, loads correctly
- `requirements.txt` — every package verified to actually `pip install`
- `.env.example` — exactly what keys you need, nothing more

## What's next (in order)
1. `agents/orchestrator.py` — runs intake_agent against a real test report, prints output
2. `agents/resource_allocator/` and `agents/crisis_assessor/` — same pattern as intake_agent
3. `mcp_servers/weather_mcp/` and `geocoding_mcp/` — real API calls, free tiers
4. `security/pii_redactor.py`
5. `dashboard/app.py` (Streamlit)

Build one piece at a time, test it loads/runs before moving to the next — don't generate all 22
files at once and hope. That's how Kimi's plan turns into a broken pile by day 4.
