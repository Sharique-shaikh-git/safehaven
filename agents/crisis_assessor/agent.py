"""
Crisis Assessor Agent — second stage of the SafeHaven pipeline.
Takes a structured, PII-redacted report from the Intake Agent and produces
a risk assessment: upgraded severity, secondary risks, and escalation flag.
"""
import os
from google.adk.agents import Agent
from .prompt import CRISIS_ASSESSOR_INSTRUCTION

# Model name: use a Gemini model your GEMINI_API_KEY has access to.
# "gemini-2.0-flash" is a safe free-tier default — change if you have a different one enabled.
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.0-flash")

crisis_assessor_agent = Agent(
    name="crisis_assessor",
    model=MODEL_NAME,
    description="Performs deep risk analysis on structured disaster reports, upgrades severity scores, and flags life-threatening situations for immediate escalation.",
    instruction=CRISIS_ASSESSOR_INSTRUCTION,
)
