"""
Volunteer Coordinator Agent — fourth stage of the SafeHaven pipeline.
Takes a resource allocation from the Resource Allocator, derives a task list,
matches available volunteers by skill and proximity, dispatches assignments,
and tracks volunteer status throughout the response.
"""
import os
from google.adk.agents import Agent
from .prompt import VOLUNTEER_COORDINATOR_INSTRUCTION

# Model name: use a Gemini model your GEMINI_API_KEY has access to.
# "gemini-2.0-flash" is a safe free-tier default — change if you have a different one enabled.
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.0-flash")

volunteer_coordinator_agent = Agent(
    name="volunteer_coordinator",
    model=MODEL_NAME,
    description="Derives tasks from resource allocations, matches volunteers by skill and location, dispatches assignments with priority deadlines, and tracks volunteer status.",
    instruction=VOLUNTEER_COORDINATOR_INSTRUCTION,
)
