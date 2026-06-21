"""
Intake Agent — first stage of the SafeHaven pipeline.
Takes a raw disaster report and turns it into structured, PII-redacted JSON.
"""
import os
from google.adk.agents import Agent
from .prompt import INTAKE_AGENT_INSTRUCTION

# Model name: use a Gemini model your GEMINI_API_KEY has access to.
# "gemini-2.0-flash" is a safe free-tier default — change if you have a different one enabled.
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.0-flash")

intake_agent = Agent(
    name="intake_agent",
    model=MODEL_NAME,
    description="Parses raw disaster reports into structured, PII-redacted data.",
    instruction=INTAKE_AGENT_INSTRUCTION,
)
