"""
security/pii_redactor.py — PII Redaction Module for SafeHaven

Strips personally identifiable information from raw disaster report text before
any downstream agent processes it. Each PII match is replaced with a stable
token of the form [REDACTED-<TYPE>-<HASH8>] and the original value is stored in
an in-memory vault keyed by a session VaultRef (UUID).

PII types detected (regex-based NER):
  PERSON_NAME  — names via contextual triggers + title prefixes
  PHONE        — US and international phone number formats
  EMAIL        — standard email addresses
  SSN          — US Social Security Number patterns
  ADDRESS      — street addresses (number + street + type abbreviation)

Public API (per PID.md §7.1):
  redact(text)               -> Tuple[redacted_text, VaultRef]
  detokenize(vault_ref, role) -> Optional[str]   # admin only
  get_redaction_log()         -> list

Usage:
  from security.pii_redactor import redact, detokenize, get_redaction_log
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Type aliases
# ──────────────────────────────────────────────────────────────────────────────

VaultRef = str  # UUID string identifying a single redact() call's vault entry

# ──────────────────────────────────────────────────────────────────────────────
# In-memory vault  {vault_ref -> VaultEntry}
# In production this would be an encrypted persistent store; for the demo it
# lives in process memory, wiped on restart.
# ──────────────────────────────────────────────────────────────────────────────

_VAULT: dict[str, dict] = {}
_REDACTION_LOG: list[dict] = []

# ──────────────────────────────────────────────────────────────────────────────
# Regex patterns  (compiled once at import time)
# ──────────────────────────────────────────────────────────────────────────────

# US + international phone: 555-1234 / (555) 123-4567 / +1-555-123-4567 / etc.
_RE_PHONE = re.compile(
    r"""
    (?:(?:\+?1[\s\-.])?           # optional country code +1
    \(?[2-9]\d{2}\)?             # area code (optional parens)
    [\s\-.])?                    # separator
    [2-9]\d{2}                   # exchange
    [\s\-.]                      # separator
    \d{4}                        # subscriber
    |
    \b\d{3}[\s\-\.]\d{4}\b       # bare 7-digit: 555-1234
    """,
    re.VERBOSE,
)

# Standard email addresses
_RE_EMAIL = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)

# US SSN: 123-45-6789 or 123 45 6789
_RE_SSN = re.compile(
    r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b",
)

# Street address: digits + optional unit + street name words + street type
# Non-verbose to keep the long alternation on one line without regex parser ambiguity.
_STREET_TYPES = (
    r"(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Blvd|Boulevard|Dr(?:ive)?"
    r"|Ln|Lane|Ct|Court|Pl(?:ace)?|Way|Pkwy|Parkway"
    r"|Cir(?:cle)?|Hwy|Highway|Terr?(?:ace)?)"
)
_RE_ADDRESS = re.compile(
    r"\b\d{1,5}"
    r"(?:\s+(?:apt|unit|suite|ste|#)\s*[\w\-]+)?"
    r"\s+[A-Z][a-zA-Z]+(?:\s+[A-Za-z]+){0,3}\s+"
    + _STREET_TYPES
    + r"\b",
)

# Person names: triggered by contextual keywords + a Title-Case word sequence.
# Patterns like "my name is John Doe", "I'm Jane Smith", "Mr. Alan Brown", etc.
_RE_NAME_CONTEXTUAL = re.compile(
    r"""
    (?:
        (?:my\s+name\s+is|i\s+am|i'm|contact|caller|victim|resident|name\s*:)\s+
        ([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})   # Title Case name 2-3 words
    |
        (?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+
        ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)        # Title + optional last name
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _short_hash(value: str) -> str:
    """Return the first 8 hex characters of the SHA-256 of value."""
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def _make_token(pii_type: str, original: str) -> str:
    """Build the replacement token string."""
    return f"[REDACTED-{pii_type}-{_short_hash(original)}]"


def _apply_pattern(
    text: str,
    pattern: re.Pattern,
    pii_type: str,
    found: list[dict],
    *,
    group: int = 0,
) -> str:
    """
    Replace all matches of pattern in text with REDACTED tokens.

    Args:
        text:     The current working text.
        pattern:  Compiled regex pattern.
        pii_type: Label used in the token and vault (e.g. "PHONE").
        found:    Mutable list; each detected PII dict is appended here.
        group:    Which capture group holds the actual PII value (0 = whole match).

    Returns:
        Text with all matches replaced.
    """
    def replacer(m: re.Match) -> str:
        if group:
            # Try the requested group; fall back to the next group if None
            # (handles name regex which has two alternation branches)
            raw_val = m.group(group)
            if raw_val is None:
                raw_val = m.group(group + 1)
            if raw_val is None:
                return m.group(0)  # no capture matched — leave unchanged
            raw = raw_val.strip()
        else:
            raw = m.group(0).strip()
        if not raw:
            return m.group(0)
        token = _make_token(pii_type, raw)
        found.append({"type": pii_type, "original": raw, "token": token})
        logger.debug("Redacted %s: %r -> %s", pii_type, raw, token)
        return token

    return pattern.sub(replacer, text)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def redact(text: str) -> tuple[str, VaultRef]:
    """
    Redact all detected PII from text and store originals in the vault.

    Detection order matters — phone numbers are removed before address patterns
    to prevent digits in phone numbers being mistaken for house numbers.

    Args:
        text: Raw input text (e.g. from an SMS or web form submission).

    Returns:
        A tuple of:
          - redacted_text: The original text with PII replaced by tokens.
          - vault_ref: A UUID string. Pass this to detokenize() (admin only)
                       to retrieve the original PII.

    Example:
        redacted, ref = redact("Call John Doe at 555-1234, 123 Main St")
        # redacted → "Call [REDACTED-PERSON_NAME-...] at [REDACTED-PHONE-...],
        #              [REDACTED-ADDRESS-...]"
    """
    vault_ref: VaultRef = str(uuid.uuid4())
    found: list[dict] = []

    working = text

    # 1. Names (contextual — run first so "123 Main St" isn't mistaken for a name)
    working = _apply_pattern(working, _RE_NAME_CONTEXTUAL, "PERSON_NAME", found, group=1)

    # 2. SSNs (before phone — SSN digits could partially match phone patterns)
    working = _apply_pattern(working, _RE_SSN, "SSN", found)

    # 3. Phone numbers
    working = _apply_pattern(working, _RE_PHONE, "PHONE", found)

    # 4. Email addresses
    working = _apply_pattern(working, _RE_EMAIL, "EMAIL", found)

    # 5. Street addresses (after phone so stray digits are already redacted)
    working = _apply_pattern(working, _RE_ADDRESS, "ADDRESS", found)

    # Store in vault
    _VAULT[vault_ref] = {
        "vault_ref": vault_ref,
        "original_text": text,
        "redacted_text": working,
        "redactions": found,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Append to audit log
    log_entry = {
        "event": "PII_REDACTED",
        "vault_ref": vault_ref,
        "pii_types_found": list({r["type"] for r in found}),
        "redaction_count": len(found),
        "timestamp": _VAULT[vault_ref]["timestamp"],
    }
    _REDACTION_LOG.append(log_entry)
    logger.info("redact() vault_ref=%s items=%d", vault_ref, len(found))

    return working, vault_ref


def detokenize(vault_ref: VaultRef, role: str) -> Optional[str]:
    """
    Retrieve the original (un-redacted) text for a vault entry.

    Only the 'admin' role is authorised. All access attempts are logged.

    Args:
        vault_ref: The VaultRef returned by a previous redact() call.
        role:      Caller's RBAC role: 'public' | 'operator' | 'admin'.

    Returns:
        The original text if role == 'admin' and vault_ref exists; else None.
    """
    access_entry = {
        "event": "VAULT_ACCESS_ATTEMPT",
        "vault_ref": vault_ref,
        "role": role,
        "granted": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if role != "admin":
        logger.warning(
            "detokenize() DENIED — vault_ref=%s role=%s (requires admin)",
            vault_ref, role,
        )
        _REDACTION_LOG.append(access_entry)
        return None

    entry = _VAULT.get(vault_ref)
    if entry is None:
        logger.warning("detokenize() vault_ref=%s NOT FOUND", vault_ref)
        _REDACTION_LOG.append(access_entry)
        return None

    access_entry["granted"] = True
    _REDACTION_LOG.append(access_entry)
    logger.info("detokenize() GRANTED vault_ref=%s", vault_ref)
    return entry["original_text"]


def get_vault_entry(vault_ref: VaultRef, role: str) -> Optional[dict]:
    """
    Return the full vault entry dict (including individual redactions list)
    for admin inspection or Communication Hub use.

    Args:
        vault_ref: VaultRef from a redact() call.
        role:      Must be 'admin'.

    Returns:
        The vault entry dict, or None if unauthorised / not found.
    """
    if role != "admin":
        logger.warning(
            "get_vault_entry() DENIED — vault_ref=%s role=%s", vault_ref, role
        )
        return None
    return _VAULT.get(vault_ref)


def get_redaction_log() -> list[dict]:
    """
    Return a copy of the append-only redaction audit log.

    Records every redact() call and every detokenize() attempt (granted or denied).
    Returned as a list of dicts; do not mutate the returned list.
    """
    return list(_REDACTION_LOG)


# ──────────────────────────────────────────────────────────────────────────────
# __main__ test — run with: uv run python -m security.pii_redactor
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    SAMPLE = (
        "My name is John Doe, phone 555-1234, "
        "my house at 123 Main St flooded"
    )

    EXTENDED = (
        "Caller: Jane Smith, reachable at jane.smith@example.com or (555) 987-6543. "
        "Location: 456 Oak Avenue, multiple families trapped. "
        "SSN on file: 123-45-6789. Mr. Alan Brown also needs help at 789 Elm Rd."
    )

    print("=" * 60)
    print("SafeHaven — PII Redactor Test")
    print("=" * 60)

    for label, text in [("SAMPLE (primary test)", SAMPLE), ("EXTENDED (edge cases)", EXTENDED)]:
        print(f"\n-- {label} --")
        print(f"INPUT : {text}")

        redacted, ref = redact(text)
        print(f"OUTPUT: {redacted}")
        print(f"REF   : {ref}")

        entry = get_vault_entry(ref, role="admin")
        if entry and entry["redactions"]:
            print("VAULT :")
            for r in entry["redactions"]:
                print(f"  [{r['type']}] {r['original']!r:40s} -> {r['token']}")
        else:
            print("VAULT : (no PII detected)")

        # Confirm detokenize is blocked for non-admin
        denied = detokenize(ref, role="operator")
        print(f"detokenize(role='operator') -> {denied!r}  <- must be None")

        # Confirm detokenize works for admin
        recovered = detokenize(ref, role="admin")
        recovered_preview = repr(recovered)[:60]
        print(f"detokenize(role='admin')    -> {recovered_preview}...")

    print("\n-- Audit log --")
    for entry in get_redaction_log():
        print(json.dumps(entry, indent=None))
