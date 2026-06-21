"""
Resource Allocator Agent — third stage of the SafeHaven pipeline.
Takes a risk assessment from the Crisis Assessor and finds the optimal
shelter + supply allocation for the affected population, reserving
resources in external systems via MCP tools.
"""
import os
from google.adk.agents import Agent
from .prompt import RESOURCE_ALLOCATOR_INSTRUCTION

# Model name: use a Gemini model your GEMINI_API_KEY has access to.
# "gemini-2.0-flash" is a safe free-tier default — change if you have a different one enabled.
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.0-flash")

resource_allocator_agent = Agent(
    name="resource_allocator",
    model=MODEL_NAME,
    description="Matches assessed disaster needs to available shelters and supplies, optimises allocation by distance and capacity, and reserves resources via MCP tools.",
    instruction=RESOURCE_ALLOCATOR_INSTRUCTION,
)
