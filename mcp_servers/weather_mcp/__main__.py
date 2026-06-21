"""mcp_servers.weather_mcp.__main__

Allows `python -m mcp_servers.weather_mcp.server` to work even if module
resolution differs across environments.

Run:
  uv run python -m mcp_servers.weather_mcp.server

This file simply imports and executes server._demo().
"""

from __future__ import annotations

from mcp_servers.weather_mcp.server import _demo


if __name__ == "__main__":
    _demo()

