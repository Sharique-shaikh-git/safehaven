"""
Communication Hub Agent — fifth and final stage of the SafeHaven pipeline.
Receives the complete coordination result and handles all outbound communications:
agency notifications, family status updates (via anonymised vault tokens only),
public situation briefings, volunteer alerts, and broadcast channel posts.
Maintains the audit trail for every communication action.
"""
import os
from google.adk.agents import Agent
from .prompt import COMMUNICATION_HUB_INSTRUCTION

# Model name: use a Gemini model your GEMINI_API_KEY has access to.
# "gemini-2.0-flash" is a safe free-tier default — change if you have a different one enabled.
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.0-flash")

communication_hub_agent = Agent(
    name="communication_hub",
    model=MODEL_NAME,
    description="Handles all outbound communications — agency notifications, anonymised family updates, public briefings, volunteer alerts, and broadcast messages — while maintaining a tamper-proof audit trail.",
    instruction=COMMUNICATION_HUB_INSTRUCTION,
)
