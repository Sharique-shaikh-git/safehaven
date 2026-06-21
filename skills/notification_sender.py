"""
Notification Sender skill (mocked backend).

This module provides a clear interface used by the communication_hub_agent to
notify:
- Agencies (ops notifications)
- Families (secure status updates via PII vault references)
- Public (public briefings)

Important:
- This implementation is MOCKED / console-output only.
- It does NOT send real SMS/email.
- It logs what WOULD be sent so we can test integration safely without
  external providers (Twilio/SendGrid/etc).

When real integration is added later, `send_notification(...)` should delegate to
provider-specific functions (e.g., Twilio/SendGrid) inside the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class NotificationResult:
    """
    Result of an attempted notification delivery (mocked).

    status:
      - "mock_sent" when the message is "sent" via console output simulation
      - "mock_failed" when validation fails (never calls real providers)
    """
    status: str
    channel: str
    recipient: str
    message_preview: str
    timestamp_utc: str
    provider_ref: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def send_notification(channel: str, recipient: str, message: str) -> NotificationResult:
    """
    Send a notification via a mocked/console-output backend.

    Args:
      channel: One of {"agency_sms", "agency_email", "family_sms", "family_email", "public_broadcast"}.
      recipient: For agencies: name/email/phone hash.
                  For families: MUST be a PII vault ref token (e.g., "vault://abc123"),
                               NOT raw PII like phone/address/name.
                  For public: can be "public" or a broadcast channel id.
      message: The content to send (already redacted/tokenized by upstream security layer).

    Returns:
      NotificationResult describing the mock send.

    Notes:
      - In the mocked backend, we only print and return the intended payload.
      - Integration point for real providers:
          - Twilio for SMS (family/agency)
          - SendGrid (or SMTP) for email (family/agency)
          - Broadcast API for public alerts
    """
    normalized_channel = (channel or "").strip()
    if not normalized_channel:
        return NotificationResult(
            status="mock_failed",
            channel="",
            recipient=recipient,
            message_preview=(message[:60] + "…") if len(message) > 60 else message,
            timestamp_utc=_utc_now_iso(),
            provider_ref="validation: missing channel",
        )

    if not recipient or not isinstance(recipient, str):
        return NotificationResult(
            status="mock_failed",
            channel=normalized_channel,
            recipient=str(recipient),
            message_preview=(message[:60] + "…") if len(message) > 60 else str(message),
            timestamp_utc=_utc_now_iso(),
            provider_ref="validation: missing recipient",
        )

    # Family updates should reference a vault token, not raw PII.
    # We enforce this lightly because upstream security should already do it.
    if normalized_channel.startswith("family_") and not recipient.startswith("vault://"):
        return NotificationResult(
            status="mock_failed",
            channel=normalized_channel,
            recipient=recipient,
            message_preview=(message[:60] + "…") if len(message) > 60 else message,
            timestamp_utc=_utc_now_iso(),
            provider_ref="validation: family recipient must be a vault:// token",
        )

    message_preview = (message[:120] + "…") if len(message) > 120 else message
    timestamp = _utc_now_iso()
    provider_ref = f"mock://console/{normalized_channel}"

    # Console output simulates a delivery log.
    print(
        f"[MOCK NOTIFY] {timestamp} | channel={normalized_channel} | recipient={recipient}\n"
        f"             message={message_preview}"
    )

    return NotificationResult(
        status="mock_sent",
        channel=normalized_channel,
        recipient=recipient,
        message_preview=message_preview,
        timestamp_utc=timestamp,
        provider_ref=provider_ref,
    )


def _format_public_briefing(context: Dict[str, Any]) -> str:
    """
    Create a simple public briefing template.

    Assumes upstream already removed PII. This is just formatting.
    """
    disaster = str(context.get("disaster_type") or "Incident")
    location = str(context.get("location") or "the affected area")
    severity = context.get("severity")
    severity_part = f"Severity: {severity}/10. " if severity is not None else ""
    return (
        f"Public update: {disaster} affecting {location}. "
        f"{severity_part}Please follow official guidance and avoid impacted zones."
    )


def _run_demo_tests() -> None:
    """
    Run 3 required mocked notification samples:
      1) Agency notification
      2) Family status update referencing PII vault token (vault://...)
      3) Public briefing
    """
    # 1) Agency notification
    agency_res = send_notification(
        channel="agency_sms",
        recipient="ops-agency@hash:agc-001",
        message="SafeHaven update: Active incident detected. Shelter resources are being allocated. "
        "Reply STOP to opt out.",
    )
    print(f"Agency result: {agency_res.status} | provider_ref={agency_res.provider_ref}")

    # 2) Family status update (MUST reference vault token)
    family_res = send_notification(
        channel="family_sms",
        recipient="vault://family-token-xyz",
        message="Family status update: Your requested assistance is in progress. "
        "We will notify you when a shelter placement is confirmed.",
    )
    print(f"Family result: {family_res.status} | recipient={family_res.recipient}")

    # 3) Public briefing
    public_message = _format_public_briefing(
        {
            "disaster_type": "Category 3 Hurricane",
            "location": "Bayport",
            "severity": 7,
        }
    )
    public_res = send_notification(
        channel="public_broadcast",
        recipient="public",
        message=public_message,
    )
    print(f"Public result: {public_res.status} | channel={public_res.channel}")


if __name__ == "__main__":
    _run_demo_tests()
