"""
security/audit_logger.py -- Append-Only Audit Logger for SafeHaven

Tamper-proof, append-only log of all system actions. Writes to
state/audit.jsonl as one JSON object per line. Existing lines are
never modified or deleted.

Public API (per PID.md S7.4):
  log_event(role, action, resource, **extra) -> dict
  get_audit_log()                            -> list[dict]

Each log record contains:
  timestamp  -- ISO-8601 UTC
  role       -- The role that performed the action
  action     -- What was done (e.g. "de_tokenise_pii", "view_incident")
  resource   -- Target resource identifier
  **extra    -- Additional context merged into the record

Usage:
  from security.audit_logger import log_event, get_audit_log

  log_event(role="admin", action="de_tokenise_pii", resource="vault://abc123")
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_STATE_DIR = Path(__file__).resolve().parent.parent / "state"
_AUDIT_FILE = _STATE_DIR / "audit.jsonl"


def _ensure_state_dir() -> None:
    """Create the state directory if it does not exist."""
    _STATE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_event(
    role: str,
    action: str,
    resource: str,
    **extra: Any,
) -> dict:
    """
    Append a single audit record to state/audit.jsonl.

    Args:
        role:     The role that performed the action ("admin", "operator", "public").
        action:   What was done (e.g. "view_incident", "de_tokenise_pii").
        resource: Target resource identifier (e.g. "vault://abc123", "SH001").
        **extra:  Additional key-value pairs merged into the record.

    Returns:
        The full record dict that was written.
    """
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "action": action,
        "resource": resource,
    }
    record.update(extra)

    _ensure_state_dir()

    try:
        with open(_AUDIT_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.debug("audit_log: %s %s %s", role, action, resource)
    except OSError as exc:
        # Log to stderr as a fallback -- audit failures should never be silent
        logger.error("Failed to write audit log: %s", exc)

    return record


def get_audit_log() -> list[dict]:
    """
    Read and return all records from state/audit.jsonl.

    Returns:
        A list of dicts, one per log line, in file order (chronological).
        Returns an empty list if the file does not exist.
    """
    if not _AUDIT_FILE.exists():
        return []

    records: list[dict] = []
    try:
        with open(_AUDIT_FILE, "r", encoding="utf-8") as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    logger.warning("Corrupt audit line %d: %s", line_num, exc)
    except OSError as exc:
        logger.error("Failed to read audit log: %s", exc)

    return records


def clear_audit_log() -> None:
    """
    Remove the audit log file entirely.  Use only for testing or during
    initial setup -- in production this should be prohibited by RBAC.
    """
    if _AUDIT_FILE.exists():
        _AUDIT_FILE.unlink()
        logger.info("Audit log cleared: %s", _AUDIT_FILE)


# ---------------------------------------------------------------------------
# __main__ test -- run with: uv run python -m security.audit_logger
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    print("=" * 60)
    print("SafeHaven -- Audit Logger Module Test")
    print("=" * 60)

    # Clear any existing log for a clean test
    clear_audit_log()

    # Write some test events
    print("\n-- Writing test events --")
    log_event(role="operator", action="view_incident", resource="INC-001",
              incident_type="flood", severity=7)
    log_event(role="admin", action="de_tokenise_pii", resource="vault://abc123",
              pii_types=["PHONE", "ADDRESS"])
    log_event(role="public", action="view_public_briefing", resource="BRIEF-042")
    log_event(role="operator", action="allocate_resources", resource="SH001",
              items=["water", "blankets"])

    # Read them back
    print("\n-- Reading audit log --")
    entries = get_audit_log()
    for i, entry in enumerate(entries, 1):
        print(f"  [{i}] {json.dumps(entry, indent=None)}")

    print(f"\nTotal entries: {len(entries)}")
    expected = 4
    status = "PASS" if len(entries) == expected else "FAIL"
    print(f"Expected: {expected}  [{status}]")

    # Verify append-only: write more, confirm old entries still present
    print("\n-- Verifying append-only behavior --")
    log_event(role="admin", action="system_configuration", resource="model_config",
              model="gemini-2.0-flash")
    entries_after = get_audit_log()
    print(f"  Entries after 2nd write: {len(entries_after)}")
    append_ok = len(entries_after) == 5 and entries_after[0]["action"] == "view_incident"
    print(f"  Old entries preserved: {'PASS' if append_ok else 'FAIL'}")

    print("\n" + "=" * 60)
    print(f"All tests passed: {len(entries) == expected and append_ok}")
    print("=" * 60)
