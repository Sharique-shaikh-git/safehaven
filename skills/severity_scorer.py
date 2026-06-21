"""
Severity Scorer skill.

This module provides a deterministic, testable way to score disaster severity (1-10)
from disaster report keywords/context, optionally incorporating weather data on a
second pass (used by crisis_assessor per PID §5.2 and §8.2).

It is designed to be used in two passes:
1) Intake pass: score_severity(report, weather_data=None)
2) Crisis-assessor re-score: score_severity(report, weather_data=WeatherData)

The function signature accepts an optional `weather_data` parameter even if the
caller passes None.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class WeatherData:
    """
    Minimal weather payload used by severity scoring.

    Crisis Assessor may provide a richer structure; this dataclass lets this module
    remain robust against extra fields.
    """
    conditions: Optional[str] = None
    precipitation: Optional[Any] = None
    wind_speed_mph: Optional[float] = None
    severe_alerts: Optional[Any] = None

    @staticmethod
    def from_any(weather_data: Any) -> "WeatherData":
        if weather_data is None:
            return WeatherData()
        if isinstance(weather_data, WeatherData):
            return weather_data
        if isinstance(weather_data, dict):
            return WeatherData(
                conditions=weather_data.get("conditions")
                or weather_data.get("condition")
                or weather_data.get("weather"),
                precipitation=weather_data.get("precipitation") or weather_data.get("precip"),
                wind_speed_mph=(
                    weather_data.get("wind_speed_mph")
                    or weather_data.get("windSpeedMph")
                    or weather_data.get("wind_mph")
                ),
                severe_alerts=weather_data.get("severe_alerts")
                or weather_data.get("alerts")
                or weather_data.get("warnings"),
            )
        # Unknown type: best-effort stringification
        return WeatherData(conditions=str(weather_data))


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def get_severity_label(score: int) -> str:
    """
    Convert score to a severity label per PID §8.2.
    """
    if 1 <= score <= 3:
        return "Low"
    if 4 <= score <= 6:
        return "Moderate"
    if 7 <= score <= 8:
        return "High"
    if 9 <= score <= 10:
        return "Critical"
    # Defensive fallback
    return "Moderate"


def _tokenize(text: str) -> set[str]:
    normalized = " ".join(text.lower().split())
    # Lightweight tokenization; avoid heavy deps
    return set(normalized.replace(",", " ").replace(".", " ").replace(";", " ").split())


def _presence_score(report: Dict[str, Any]) -> Tuple[int, int, int, int, int, str]:
    """
    Compute base factors from report.

    Returns:
        people_affected: int-ish 0..N
        medical_needs: int-ish 0..N
        trapped: int-ish 0..N
        infrastructure_damage: int-ish 0..N
        weather_multiplier_base: int 0..N (context-based from keywords)
        one_line_justification: explanation string
    """
    text = " ".join(
        str(v) for v in [
            report.get("raw_text_redacted"),
            report.get("raw_text"),
            report.get("context"),
            report.get("disaster_type"),
            report.get("disaster_type_hint"),
        ]
        if v is not None
    )
    tokens = _tokenize(text)

    def has(*words: str) -> bool:
        return any(w in tokens for w in words)

    # Numeric extraction: PID talks about people_affected and factors.
    # We avoid brittle parsing; use reported fields if present.
    people_affected = int(report.get("people_affected") or report.get("people") or 0)
    medical_needs = int(report.get("medical_needs") or report.get("injured") or 0)
    trapped = int(report.get("trapped") or report.get("entombed") or 0)

    # Infrastructure damage isn't guaranteed to be numeric; infer buckets from keywords.
    infrastructure_damage = 0
    if has("collapsed", "collapse", "bridge", "overpass") or report.get("infrastructure_damage") == "high":
        infrastructure_damage = 3
    elif has("power", "downed", "transformer", "road", "inundated", "flooded"):
        infrastructure_damage = 2
    elif has("damage", "cracked", "blocked", "limited"):
        infrastructure_damage = 1

    # Context-based "weather multiplier" from keywords.
    # This is only used in intake pass; crisis-assessor will supply weather_data.
    weather_multiplier_base = 0
    if has("storm", "hurricane", "typhoon", "cyclone", "blizzard", "tornado", "derecho"):
        weather_multiplier_base += 2
    if has("severe", "extreme", "catastrophic", "rapidly", "unprecedented"):
        weather_multiplier_base += 1
    if has("heavy", "torrential", "monsoon", "record"):
        weather_multiplier_base += 1

    # If disaster_type exists, nudge damage factor a bit.
    disaster_type = str(report.get("disaster_type") or "").lower()
    if "flood" in disaster_type or "storm" in disaster_type:
        infrastructure_damage = max(infrastructure_damage, 2)

    # If report has explicit numeric infrastructure damage, respect it (0-5 mapped down)
    if "infrastructure_damage" in report and isinstance(report["infrastructure_damage"], (int, float)):
        infrastructure_damage = int(report["infrastructure_damage"])

    # Keep in reasonable bounds to avoid wild inputs.
    people_affected = max(0, people_affected)
    medical_needs = max(0, medical_needs)
    trapped = max(0, trapped)
    infrastructure_damage = _clamp_int(infrastructure_damage, 0, 5)

    # One-line justification (PID requires justification in __main__ test output)
    justification_bits = []
    if people_affected:
        justification_bits.append(f"{people_affected} people affected")
    if medical_needs:
        justification_bits.append(f"{medical_needs} medical needs")
    if trapped:
        justification_bits.append(f"{trapped} trapped")
    if infrastructure_damage:
        justification_bits.append(f"infrastructure damage={infrastructure_damage}")
    if weather_multiplier_base:
        justification_bits.append(f"weather_context_boost={weather_multiplier_base}")

    if not justification_bits:
        justification_bits.append("limited indicators; defaulting to low-moderate risk from keywords")

    return (
        people_affected,
        medical_needs,
        trapped,
        infrastructure_damage,
        weather_multiplier_base,
        "; ".join(justification_bits),
    )


def _apply_weather_multiplier(base_score: int, weather: WeatherData) -> Tuple[int, str]:
    """
    Adjust severity based on weather conditions.

    Weather payload is intentionally flexible.
    """
    conditions = (weather.conditions or "").lower() if weather.conditions else ""
    alerts = weather.severe_alerts

    wind = weather.wind_speed_mph

    multiplier = 0
    parts: list[str] = []

    # Severe alerts list/dict/string indicates higher risk.
    if alerts:
        multiplier += 2
        parts.append("severe alerts present")

    # Keyword-based conditions
    severe_condition_keywords = [
        "hurricane",
        "tornado",
        "blizzard",
        "storm",
        "derecho",
        "cyclone",
        "severe",
        "extreme",
    ]
    if any(k in conditions for k in severe_condition_keywords):
        multiplier += 1
        parts.append(f"conditions='{weather.conditions}'")

    # Wind speed mapping if available
    if wind is not None:
        try:
            if wind >= 90:
                multiplier += 2
                parts.append(f"wind_speed_mph={wind:.0f} (very high)")
            elif wind >= 55:
                multiplier += 1
                parts.append(f"wind_speed_mph={wind:.0f} (high)")
        except (TypeError, ValueError):
            pass

    adjusted = base_score + multiplier
    adjusted = _clamp_int(adjusted, 1, 10)

    if not parts:
        parts.append("no significant weather escalation")

    return adjusted, "; ".join(parts)


def calculate_severity(report: Dict[str, Any], weather_data: Optional[Any] = None) -> int:
    """
    Multi-factor severity algorithm per PID §8.2.

    Important: This implementation is calibrated to avoid saturation.
    Each factor is bucketed/capped BEFORE combining, then weather escalation
    is applied on the resulting 1..10 base.

    Factors (per PID intent):
      people_affected * 2 + medical_needs * 3 + trapped * 5 + infrastructure_damage * 2 + weather_multiplier

    Implementation detail:
    - people_affected, medical_needs, trapped are converted to bounded 0..5 buckets.
    - infrastructure_damage is already 0..5 from _presence_score.
    - weather_multiplier_base is derived from keyword context in intake pass.
    - crisis-assessor pass uses `weather_data` to provide additional escalation.

    Returns an integer severity in range 1..10.
    """
    (
        people_affected,
        medical_needs,
        trapped,
        infrastructure_damage,
        weather_multiplier_base,
        _just,
    ) = _presence_score(report)

    # Cap/bucket each numeric factor so real-world ranges don't collapse to 10.
    # These bucket thresholds are intentionally coarse/deterministic.
    def bucket_0_5(value: int, *, thresholds: tuple[int, int, int, int]) -> int:
        # thresholds correspond to buckets: 0..0, 1..t1, 2..t2, 3..t3, 4..t4, 5+
        t1, t2, t3, t4 = thresholds
        if value <= 0:
            return 0
        if value <= t1:
            return 1
        if value <= t2:
            return 2
        if value <= t3:
            return 3
        if value <= t4:
            return 4
        return 5

    people_b = bucket_0_5(int(people_affected), thresholds=(10, 30, 80, 200))
    medical_b = bucket_0_5(int(medical_needs), thresholds=(5, 15, 40, 80))
    trapped_b = bucket_0_5(int(trapped), thresholds=(1, 3, 10, 20))

    infra_b = _clamp_int(int(infrastructure_damage), 0, 5)

    # weather_multiplier_base is already small-ish from keywords; cap it too.
    weather_b = _clamp_int(int(weather_multiplier_base), 0, 3)

    # Weighted capped sum. Maximum base:
    # people_b*2 + medical_b*3 + trapped_b*5 + infra_b*2 + weather_b
    base_raw = (
        people_b * 2
        + medical_b * 3
        + trapped_b * 5
        + infra_b * 2
        + weather_b
    )

    # Convert capped raw into 1..10. With max capped sum:
    # max = 5*2 + 5*3 + 5*5 + 5*2 + 3 = 10 + 15 + 25 + 10 + 3 = 63
    normalized = int(round((base_raw / 63) * 9 + 1))
    normalized = _clamp_int(normalized, 1, 10)

    # Crisis-assessor pass: if actual weather_data is present, apply escalation.
    if weather_data is not None:
        weather = WeatherData.from_any(weather_data)
        normalized, _wjust = _apply_weather_multiplier(normalized, weather)

    return normalized


def score_severity(report: Dict[str, Any], weather_data: Optional[Any] = None) -> int:
    """
    Convenience alias used by intake_agent / crisis_assessor.
    """
    return calculate_severity(report, weather_data=weather_data)


def explain_severity(
    report: Dict[str, Any], weather_data: Optional[Any] = None
) -> str:
    """
    One-line explanation suitable for PID __main__ tests.
    """
    (
        people_affected,
        medical_needs,
        trapped,
        infrastructure_damage,
        weather_multiplier_base,
        base_just,
    ) = _presence_score(report)

    score = calculate_severity(report, weather_data=weather_data)
    label = get_severity_label(score)

    if weather_data is None:
        return f"{label} ({score}/10): {base_just}"
    weather = WeatherData.from_any(weather_data)
    _, wjust = _apply_weather_multiplier(calculate_severity(report, weather_data=None), weather)
    return f"{label} ({score}/10): {base_just}; weather: {wjust}"


def _run_demo_tests() -> None:
    """
    Run deterministic tests across the range.

    PID requires justification, not just a number.
    """
    samples: list[Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]] = [
        (
            "Clearly low severity",
            {
                "disaster_type": "flood",
                "raw_text_redacted": "Minor flooding in a few streets. No injuries reported. No people trapped.",
                "people_affected": 2,
                "medical_needs": 0,
                "trapped": 0,
                "infrastructure_damage": 0,
            },
            None,
        ),
        (
            "Clearly critical",
            {
                "disaster_type": "hurricane",
                "raw_text_redacted": "Hurricane damage is catastrophic. Many people trapped, multiple injuries, and several buildings collapsed.",
                "people_affected": 250,
                "medical_needs": 90,
                "trapped": 25,
                "infrastructure_damage": 5,
            },
            {
                "conditions": "hurricane winds and torrential rain",
                "wind_speed_mph": 120,
                "severe_alerts": ["hurricane warning"],
            },
        ),
        (
            "Ambiguous middle case (moderate-high context, mild weather)",
            {
                "disaster_type": "storm",
                "raw_text_redacted": "Severe storm caused blocked roads and power outages. Some injuries; no confirmed trapped people.",
                "people_affected": 35,
                "medical_needs": 10,
                "trapped": 0,
                "infrastructure_damage": 2,
            },
            {
                "conditions": "strong winds, heavy rain",
                "wind_speed_mph": 45,
                "severe_alerts": [],
            },
        ),
        (
            "Ambiguous middle case (moderate people, some trapped, strong weather)",
            {
                "disaster_type": "earthquake",
                "raw_text_redacted": "Several buildings damaged with some people trapped. Injuries reported; infrastructure partially collapsed.",
                "people_affected": 60,
                "medical_needs": 25,
                "trapped": 8,
                "infrastructure_damage": 3,
            },
            {
                "conditions": "aftershock risk, severe weather system nearby",
                "wind_speed_mph": 70,
                "severe_alerts": ["high wind advisory"],
            },
        ),
    ]

    for title, report, weather in samples:
        score = score_severity(report, weather_data=weather)
        justification = explain_severity(report, weather_data=weather)
        print(f"{title}: score={score} | {justification}")


if __name__ == "__main__":
    _run_demo_tests()
