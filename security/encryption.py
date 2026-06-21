"""
security/encryption.py -- Field-Level Encryption for SafeHaven

Provides Fernet symmetric encryption for sensitive data fields:
  - Exact victim location coordinates (stored encrypted; approximate shown in clear)
  - PII vault contents (contact information)
  - Communication logs

Fernet guarantees: AES-128-CBC with PKCS7 padding + HMAC-SHA256 authentication.
Encrypted values are URL-safe base64 strings -- safe to store as JSON values.

Public API (per PID.md S7.2):
  encrypt_field(plaintext: str) -> str
  decrypt_field(token: str)     -> str
  generate_key()                -> bytes

The module loads ENCRYPTION_KEY from the environment (via .env).
If the key is missing at import time it logs a warning; the first actual
encrypt/decrypt call will raise EncryptionKeyError with a clear message.

Usage:
  from security.encryption import encrypt_field, decrypt_field
  token  = encrypt_field("27.9506,-82.4572")
  plain  = decrypt_field(token)   # -> "27.9506,-82.4572"

Key management:
  Generate a new key once and store it in .env:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  Then set:  ENCRYPTION_KEY=<output>
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class EncryptionKeyError(RuntimeError):
    """Raised when ENCRYPTION_KEY is missing or invalid."""


class DecryptionError(ValueError):
    """Raised when a ciphertext cannot be decrypted (wrong key or corrupted)."""


# ---------------------------------------------------------------------------
# Key loading
# ---------------------------------------------------------------------------

def _load_key() -> Optional[bytes]:
    """
    Load the Fernet key from the ENCRYPTION_KEY environment variable.

    Returns:
        The key as bytes, or None if the variable is unset/empty.
    """
    raw = os.getenv("ENCRYPTION_KEY", "").strip()
    if not raw:
        return None
    return raw.encode()


def _get_fernet() -> Fernet:
    """
    Build and return a Fernet instance from the loaded key.

    Raises:
        EncryptionKeyError: if ENCRYPTION_KEY is missing or not a valid Fernet key.
    """
    key = _load_key()
    if key is None:
        raise EncryptionKeyError(
            "ENCRYPTION_KEY is not set in .env. "
            "Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(key)
    except Exception as exc:
        raise EncryptionKeyError(
            f"ENCRYPTION_KEY is not a valid Fernet key: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_key() -> bytes:
    """
    Generate a fresh URL-safe base64-encoded 32-byte Fernet key.

    Call this once to create a new project key. Store the result in .env as
    ENCRYPTION_KEY=<output>.

    Returns:
        A valid Fernet key as bytes (44 characters when decoded to str).

    Example:
        key = generate_key()
        print(key.decode())  # paste into .env
    """
    return Fernet.generate_key()


def encrypt_field(plaintext: str) -> str:
    """
    Encrypt a single string field using Fernet symmetric encryption.

    The returned ciphertext is a URL-safe base64 string that includes the
    HMAC authentication tag -- it is safe to store directly in JSON or JSONL.

    Args:
        plaintext: The sensitive string to encrypt (e.g. "27.9506,-82.4572").

    Returns:
        A Fernet token string (URL-safe base64, ~100-200 chars for short inputs).

    Raises:
        EncryptionKeyError: if ENCRYPTION_KEY is missing or invalid.

    Example:
        token = encrypt_field("John Doe, 555-1234")
        # -> "gAAAAAB..."  (safe to store in DB or JSONL)
    """
    fernet = _get_fernet()
    ciphertext: bytes = fernet.encrypt(plaintext.encode("utf-8"))
    result = ciphertext.decode("ascii")
    logger.debug("encrypt_field: encrypted %d chars -> %d char token", len(plaintext), len(result))
    return result


def decrypt_field(token: str) -> str:
    """
    Decrypt a Fernet token back to the original plaintext string.

    Args:
        token: A Fernet token previously returned by encrypt_field().

    Returns:
        The original plaintext string.

    Raises:
        EncryptionKeyError: if ENCRYPTION_KEY is missing or invalid.
        DecryptionError:    if the token is corrupted, tampered with,
                            or was encrypted with a different key.

    Example:
        plain = decrypt_field("gAAAAAB...")
        # -> "John Doe, 555-1234"
    """
    fernet = _get_fernet()
    try:
        plaintext_bytes: bytes = fernet.decrypt(token.encode("ascii"))
    except InvalidToken as exc:
        raise DecryptionError(
            "Decryption failed -- token is corrupted, tampered, or was "
            "encrypted with a different key."
        ) from exc
    result = plaintext_bytes.decode("utf-8")
    logger.debug("decrypt_field: decrypted %d char token -> %d chars", len(token), len(result))
    return result


def encrypt_dict_field(data: dict, field: str) -> dict:
    """
    Convenience helper: encrypt one field inside a dict in-place (returns copy).

    Useful for encrypting specific keys in a vault entry or incident record
    without touching the rest of the dict.

    Args:
        data:  The source dict (not mutated).
        field: The key whose string value should be encrypted.

    Returns:
        A shallow copy of data with data[field] replaced by its encrypted token.
        If data[field] is None or missing, it is left as-is.
    """
    result = dict(data)
    value = result.get(field)
    if value is not None:
        result[field] = encrypt_field(str(value))
    return result


def decrypt_dict_field(data: dict, field: str) -> dict:
    """
    Convenience helper: decrypt one field inside a dict (returns copy).

    Args:
        data:  The source dict (not mutated).
        field: The key whose string value should be decrypted.

    Returns:
        A shallow copy of data with data[field] replaced by its decrypted value.
        If data[field] is None or missing, it is left as-is.
    """
    result = dict(data)
    value = result.get(field)
    if value is not None:
        result[field] = decrypt_field(str(value))
    return result


# ---------------------------------------------------------------------------
# __main__ test -- run with: uv run python -m security.encryption
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    print("=" * 60)
    print("SafeHaven -- Encryption Module Test")
    print("=" * 60)

    # Check key is present before running tests
    try:
        _get_fernet()
    except EncryptionKeyError as e:
        print(f"\nERROR: {e}")
        print("\nAdd the key to .env and re-run.")
        sys.exit(1)

    TEST_CASES = [
        ("location coordinates", "27.9506,-82.4572"),
        ("contact vault entry",  "John Doe | 555-1234 | 123 Main St"),
        ("empty string",          ""),
        ("unicode content",       "Victim: Jose Garcia, Calle 5 #23"),
        ("long text",             "A" * 500),
    ]

    all_passed = True

    for label, original in TEST_CASES:
        print(f"\n-- {label} --")
        try:
            token = encrypt_field(original)
            recovered = decrypt_field(token)

            match = (recovered == original)
            status = "PASS" if match else "FAIL"
            if not match:
                all_passed = False

            print(f"  Original  : {original[:60]!r}{'...' if len(original) > 60 else ''}")
            print(f"  Token     : {token[:60]}...")
            print(f"  Recovered : {recovered[:60]!r}{'...' if len(recovered) > 60 else ''}")
            print(f"  Match     : {status}")

        except Exception as exc:
            all_passed = False
            print(f"  ERROR: {exc}")

    # Test dict helpers
    print("\n-- dict field helpers --")
    record = {"report_id": "abc123", "lat": "27.9506", "lon": "-82.4572", "name": "Jane Doe"}
    encrypted_record = encrypt_dict_field(record, "lat")
    encrypted_record = encrypt_dict_field(encrypted_record, "lon")
    decrypted_record = decrypt_dict_field(encrypted_record, "lat")
    decrypted_record = decrypt_dict_field(decrypted_record, "lon")
    coords_ok = (decrypted_record["lat"] == record["lat"] and
                 decrypted_record["lon"] == record["lon"])
    print(f"  Original lat/lon : {record['lat']}, {record['lon']}")
    print(f"  Encrypted lat    : {encrypted_record['lat'][:40]}...")
    print(f"  Restored lat/lon : {decrypted_record['lat']}, {decrypted_record['lon']}")
    print(f"  Coords match     : {'PASS' if coords_ok else 'FAIL'}")
    if not coords_ok:
        all_passed = False

    # Test wrong-key detection
    print("\n-- wrong key detection --")
    token = encrypt_field("secret data")
    fake_fernet = Fernet(Fernet.generate_key())
    try:
        fake_fernet.decrypt(token.encode())
        print("  Wrong key test : FAIL (should have raised)")
        all_passed = False
    except InvalidToken:
        print("  Wrong key test : PASS (InvalidToken raised as expected)")

    print("\n" + "=" * 60)
    print(f"All tests passed: {all_passed}")
    print("=" * 60)
    sys.exit(0 if all_passed else 1)
