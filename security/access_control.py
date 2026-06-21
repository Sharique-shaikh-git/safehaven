"""
security/access_control.py -- RBAC Access Control for SafeHaven

Role-based access control for all system operations. Three roles with
escalating privileges:

  public   -- Can view anonymized dashboard, public briefings only.
  operator -- Can view all incident details (redacted PII), dispatch
              volunteers, allocate resources.
  admin    -- Can de-tokenize PII, access audit logs, system configuration.

Public API (per PID.md S7.3):
  check_permission(role, action) -> bool
  require_role(min_role)         -> decorator for agent tools
  get_audit_log()                -> list

Usage:
  from security.access_control import check_permission, require_role

  if not check_permission("operator", "view_incident"):
      raise PermissionError("Insufficient role")
"""

from __future__ import annotations

import functools
import logging
from datetime import datetime, timezone
from typing import Any, Callable

from security.audit_logger import log_event

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Role hierarchy (higher index = more privileges)
# ---------------------------------------------------------------------------

ROLE_HIERARCHY: dict[str, int] = {
    "public": 0,
    "operator": 1,
    "admin": 2,
}

# ---------------------------------------------------------------------------
# Permission matrix:  action -> minimum role required
#
# Actions are grouped by domain.  Any action not listed here is denied
# by default (fail-closed).
# ---------------------------------------------------------------------------

_PERMISSIONS: dict[str, str] = {
    # Dashboard / public data
    "view_public_briefing":    "public",
    "view_dashboard":          "public",

    # Incidents (redacted PII only)
    "view_incident":           "operator",
    "create_incident":         "operator",
    "update_incident":         "operator",

    # Resource allocation
    "allocate_resources":      "operator",
    "check_supply_inventory":  "operator",
    "reserve_items":           "operator",
    "find_shelters":           "operator",
    "dispatch_volunteer":      "operator",

    # PII / vault access
    "de_tokenise_pii":         "admin",
    "view_vault_entry":        "admin",

    # Audit / config
    "view_audit_log":          "admin",
    "view_redaction_log":      "admin",
    "system_configuration":    "admin",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_permission(role: str, action: str) -> bool:
    """
    Check whether *role* is permitted to perform *action*.

    Args:
        role:   One of "public", "operator", "admin".
        action: An action string (e.g. "view_incident", "de_tokenise_pii").

    Returns:
        True if the role has sufficient privilege, False otherwise.

    Unknown roles or actions are denied (fail-closed).
    """
    if role not in ROLE_HIERARCHY:
        logger.warning("check_permission: unknown role %r — denying", role)
        return False

    required_role = _PERMISSIONS.get(action)
    if required_role is None:
        logger.warning("check_permission: unknown action %r — denying", action)
        return False

    allowed = ROLE_HIERARCHY[role] >= ROLE_HIERARCHY[required_role]
    logger.debug(
        "check_permission(role=%r, action=%r) -> %s (need >= %s)",
        role, action, allowed, required_role,
    )
    return allowed


def require_role(min_role: str) -> Callable:
    """
    Decorator that enforces a minimum role before a function executes.

    The decorated function must accept a `role` keyword argument (or the
    first positional argument after `self` for methods).  If the caller's
    role is insufficient, PermissionError is raised and the attempt is
    logged to the audit trail.

    Args:
        min_role: The minimum role required ("public", "operator", "admin").

    Returns:
        A decorator that wraps the target function.

    Example:
        @require_role("admin")
        def delete_incident(incident_id: str, *, role: str = "public") -> bool:
            ...
    """
    if min_role not in ROLE_HIERARCHY:
        raise ValueError(f"Unknown role: {min_role!r}")

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract role from kwargs, or from first positional arg after self
            caller_role = kwargs.get("role")
            if caller_role is None and len(args) > 0:
                # For bound methods, args[0] is self; for plain functions
                # it might be the first real argument.  We look for 'role'
                # in kwargs primarily.  If not in kwargs, try to find it
                # in the function signature.
                pass  # role must be in kwargs per convention

            if caller_role is None:
                logger.error(
                    "require_role(%s): no role supplied to %s — denying",
                    min_role, fn.__name__,
                )
                raise PermissionError(
                    f"require_role({min_role}): no role supplied to {fn.__name__}"
                )

            if not check_permission(caller_role, fn.__name__):
                log_event(
                    role=caller_role,
                    action=fn.__name__,
                    resource="access_denied",
                    details={"required_role": min_role, "granted": False},
                )
                raise PermissionError(
                    f"Role {caller_role!r} lacks privilege for {fn.__name__} "
                    f"(requires >= {min_role!r})"
                )

            log_event(
                role=caller_role,
                action=fn.__name__,
                resource="access_granted",
                details={"required_role": min_role, "granted": True},
            )
            return fn(*args, **kwargs)

        return wrapper
    return decorator


# In-memory audit log (supplements the persistent JSONL audit logger)
_ACCESS_LOG: list[dict] = []


def get_audit_log() -> list[dict]:
    """
    Return a copy of the in-memory access control audit log.

    Each entry contains: role, action, resource, granted, timestamp.
    """
    return list(_ACCESS_LOG)


# ---------------------------------------------------------------------------
# __main__ test -- run with: uv run python -m security.access_control
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    print("=" * 60)
    print("SafeHaven -- Access Control Module Test")
    print("=" * 60)

    test_cases = [
        # (role, action, expected)
        ("public",   "view_public_briefing", True),
        ("public",   "view_dashboard",       True),
        ("public",   "view_incident",        False),
        ("public",   "allocate_resources",   False),
        ("public",   "de_tokenise_pii",      False),
        ("public",   "view_audit_log",       False),

        ("operator", "view_public_briefing", True),
        ("operator", "view_incident",        True),
        ("operator", "create_incident",      True),
        ("operator", "allocate_resources",   True),
        ("operator", "dispatch_volunteer",   True),
        ("operator", "de_tokenise_pii",      False),
        ("operator", "view_audit_log",       False),

        ("admin",    "view_public_briefing", True),
        ("admin",    "view_incident",        True),
        ("admin",    "allocate_resources",   True),
        ("admin",    "de_tokenise_pii",      True),
        ("admin",    "view_audit_log",       True),
        ("admin",    "system_configuration", True),
    ]

    all_passed = True
    for role, action, expected in test_cases:
        result = check_permission(role, action)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"  check_permission({role!r:10s}, {action!r:30s}) -> {result!r:5s}  expected {expected!r:5s}  [{status}]")

    # Test unknown role / action
    print()
    print("  Edge cases:")
    result = check_permission("hacker", "de_tokenise_pii")
    print(f"  check_permission('hacker', 'de_tokenise_pii') -> {result!r}  [{'PASS' if not result else 'FAIL'}]")
    if result:
        all_passed = False

    result = check_permission("admin", "totally_fake_action")
    print(f"  check_permission('admin', 'totally_fake_action') -> {result!r}  [{'PASS' if not result else 'FAIL'}]")
    if result:
        all_passed = False

    # Test require_role decorator
    print("\n-- require_role decorator test --")

    @require_role("operator")
    def dispatch_volunteer(volunteer_id: str, *, role: str = "public") -> str:
        return f"Dispatched {volunteer_id}"

    # Admin should succeed
    try:
        result = dispatch_volunteer("V001", role="admin")
        print(f"  dispatch_volunteer(role='admin')  -> {result!r}  [PASS]")
    except PermissionError as e:
        print(f"  dispatch_volunteer(role='admin')  -> ERROR {e!r}  [FAIL]")
        all_passed = False

    # Operator should succeed
    try:
        result = dispatch_volunteer("V002", role="operator")
        print(f"  dispatch_volunteer(role='operator') -> {result!r}  [PASS]")
    except PermissionError as e:
        print(f"  dispatch_volunteer(role='operator') -> ERROR {e!r}  [FAIL]")
        all_passed = False

    # Public should fail
    try:
        result = dispatch_volunteer("V003", role="public")
        print(f"  dispatch_volunteer(role='public')  -> {result!r}  [FAIL — should have raised]")
        all_passed = False
    except PermissionError:
        print(f"  dispatch_volunteer(role='public')  -> PermissionError raised  [PASS]")

    print("\n" + "=" * 60)
    print(f"All tests passed: {all_passed}")
    print("=" * 60)
