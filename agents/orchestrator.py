"""
SafeHaven Orchestrator — coordinates all 5 agents through the disaster response pipeline.

Flow (per PID.md Section 4):
  raw_report
    → intake_agent              (always)
    → crisis_assessor_agent     (always)
    → IF assessed_severity > 5:
        resource_allocator_agent   ─┐  (parallel)
        volunteer_coordinator_agent ─┘
    → communication_hub_agent   (always, receives all prior outputs)
    → returns CoordinationResult dict

Each agent is run via ADK Runner with its own InMemorySessionService.
The parallel branch uses asyncio.gather() for true concurrent execution.
"""
import asyncio
import json
import os
import re
import sys

# Make sure the project root is on sys.path so `agents.*` resolves whether
# this file is run directly (python agents/orchestrator.py) or as a module
# (python -m agents.orchestrator).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Import all 5 agents from their existing modules — do not redefine.
from agents.intake_agent.agent import intake_agent
from agents.crisis_assessor.agent import crisis_assessor_agent
from agents.resource_allocator.agent import resource_allocator_agent
from agents.volunteer_coordinator.agent import volunteer_coordinator_agent
from agents.communication_hub.agent import communication_hub_agent


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

async def _run_agent(agent, user_message: str, session_id: str) -> str:
    """
    Run a single ADK LlmAgent and return its final text response.

    Creates a fresh InMemorySessionService per call so agents never share
    conversation state — each stage sees only what we explicitly pass in the
    user_message.

    Args:
        agent:        The ADK Agent instance to run.
        user_message: The full prompt/input for this stage.
        session_id:   A unique ID for this invocation's session.

    Returns:
        The agent's final text response as a string.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="safehaven",
        session_service=session_service,
        auto_create_session=True,
    )
    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)],
    )
    final_text = ""
    async for event in runner.run_async(
        user_id="orchestrator",
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text = part.text
    return final_text.strip()


def _extract_severity(crisis_output: str) -> int:
    """
    Pull assessed_severity int out of the crisis assessor's JSON response.
    Handles both raw JSON and JSON fenced inside a markdown code block.

    Returns 0 if parsing fails (triggers conservative no-branch path).
    """
    # Strip markdown fencing if present
    text = crisis_output
    if "```" in text:
        blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text)
        if blocks:
            text = blocks[0]

    try:
        data = json.loads(text.strip())
        return int(data.get("assessed_severity", 0))
    except (json.JSONDecodeError, ValueError):
        # Regex fallback — scan for the key anywhere in the raw string
        m = re.search(r'"assessed_severity"\s*:\s*(\d+)', crisis_output)
        return int(m.group(1)) if m else 0


def _banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ──────────────────────────────────────────────────────────────────────────────
# Public pipeline entry point
# ──────────────────────────────────────────────────────────────────────────────

async def run_pipeline(raw_report: str) -> dict:
    """
    Run the full SafeHaven coordination pipeline for one raw disaster report.

    Args:
        raw_report: Unstructured text from any source (SMS, web form, transcript).

    Returns:
        CoordinationResult dict with the output of every agent that ran, the
        extracted severity score, and a flag indicating whether the parallel
        branch was triggered.
    """
    result = {
        "raw_report": raw_report,
        "intake": None,
        "crisis_assessment": None,
        "resource_allocation": None,
        "volunteer_dispatch": None,
        "communications": None,
        "severity_score": None,
        "parallel_branch_triggered": False,
    }

    # ── Stage 1: Intake Agent ─────────────────────────────────────────────────
    _banner("STAGE 1 — INTAKE AGENT")
    intake_output = await _run_agent(
        intake_agent,
        user_message=raw_report,
        session_id="intake-001",
    )
    print(intake_output)
    result["intake"] = intake_output

    # ── Stage 2: Crisis Assessor ──────────────────────────────────────────────
    _banner("STAGE 2 — CRISIS ASSESSOR AGENT")
    crisis_output = await _run_agent(
        crisis_assessor_agent,
        user_message=(
            "Perform a full risk assessment on the following structured disaster report "
            "produced by the Intake Agent:\n\n" + intake_output
        ),
        session_id="crisis-001",
    )
    print(crisis_output)
    result["crisis_assessment"] = crisis_output

    severity = _extract_severity(crisis_output)
    result["severity_score"] = severity
    print(f"\n→ Extracted assessed_severity: {severity}")

    # ── Stage 3: Conditional parallel branch (severity > 5) ───────────────────
    allocator_output = None
    coordinator_output = None

    if severity > 5:
        result["parallel_branch_triggered"] = True
        _banner(
            f"STAGE 3 — PARALLEL BRANCH TRIGGERED (severity={severity} > 5)\n"
            "  resource_allocator + volunteer_coordinator running concurrently"
        )

        async def run_allocator() -> str:
            return await _run_agent(
                resource_allocator_agent,
                user_message=(
                    "Allocate shelters and supplies for the following disaster. "
                    "Use the crisis assessment below as your primary input:\n\n"
                    + crisis_output
                ),
                session_id="alloc-001",
            )

        async def run_coordinator() -> str:
            return await _run_agent(
                volunteer_coordinator_agent,
                user_message=(
                    "Derive tasks and dispatch volunteers for the following disaster. "
                    "Use the crisis assessment below as your primary input:\n\n"
                    + crisis_output
                ),
                session_id="coord-001",
            )

        allocator_output, coordinator_output = await asyncio.gather(
            run_allocator(), run_coordinator()
        )

        print("\n--- Resource Allocator Output ---")
        print(allocator_output)
        print("\n--- Volunteer Coordinator Output ---")
        print(coordinator_output)

        result["resource_allocation"] = allocator_output
        result["volunteer_dispatch"] = coordinator_output

    else:
        print(
            f"\n→ Severity {severity} ≤ 5 — skipping resource_allocator "
            "and volunteer_coordinator"
        )

    # ── Stage 4: Communication Hub ────────────────────────────────────────────
    _banner("STAGE 4 — COMMUNICATION HUB AGENT")

    comm_sections = [
        "Send all required communications for the disaster coordination result below.",
        "\n[INTAKE REPORT]\n" + intake_output,
        "\n[CRISIS ASSESSMENT]\n" + crisis_output,
    ]
    if allocator_output:
        comm_sections.append("\n[RESOURCE ALLOCATION]\n" + allocator_output)
    if coordinator_output:
        comm_sections.append("\n[VOLUNTEER DISPATCH]\n" + coordinator_output)

    comm_output = await _run_agent(
        communication_hub_agent,
        user_message="\n".join(comm_sections),
        session_id="comm-001",
    )
    print(comm_output)
    result["communications"] = comm_output

    # ── Final summary ─────────────────────────────────────────────────────────
    _banner("PIPELINE COMPLETE")
    agents_ran = "intake → crisis_assessor"
    if result["parallel_branch_triggered"]:
        agents_ran += " → [resource_allocator ‖ volunteer_coordinator]"
    agents_ran += " → communication_hub"
    print(f"  Severity score      : {severity}")
    print(f"  Parallel branch     : {result['parallel_branch_triggered']}")
    print(f"  Agents ran          : {agents_ran}")
    print("=" * 60)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# End-to-end test — run directly: python agents/orchestrator.py
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SAMPLE_REPORT = (
        "Flooding on Main Street, water rising fast, about 15 people stuck on "
        "rooftops, need rescue and medical help urgently"
    )

    print("SafeHaven Pipeline — End-to-End Test")
    print(f"Report: {SAMPLE_REPORT}\n")

    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    asyncio.run(run_pipeline(SAMPLE_REPORT))
