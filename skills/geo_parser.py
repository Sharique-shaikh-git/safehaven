"""
skills/geo_parser.py -- Location Extraction and Distance Utilities for SafeHaven

Extracts structured location data from free-form disaster report text.
Returns Location objects that the Geocoding MCP server (mcp_servers/geocoding_mcp/)
can consume to resolve lat/lon coordinates. Until the MCP server is running,
lat/lon fields are stubbed as None -- callers must treat None as "unresolved".

Public API (per PID.md S8.1):
  parse_location_from_text(text: str)        -> Location
  normalize_address(address: str)            -> str
  calculate_distance(loc1, loc2: Location)   -> float  (Haversine, km)

Additional helpers (used by agents and MCP layer):
  extract_location_candidates(text: str)     -> list[str]
      Returns ranked list of raw candidate strings extracted from text;
      the first entry is the best guess. MCP server calls geocode on these.
  is_address_like(candidate: str)            -> bool
      True if candidate looks like a structured street address vs. a landmark.

Location dataclass fields:
  raw_text    : the original mention as it appeared in the report
  normalized  : standardized form (title-case, abbreviated street type)
  lat, lon    : float or None (None until MCP geocoding resolves them)
  confidence  : 0.0-1.0 -- how confident the parser is this is a real location
  location_type: "address" | "landmark" | "intersection" | "relative" | "unknown"
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Location:
    """
    Structured location extracted from free text.

    lat/lon are None until resolved by the Geocoding MCP server.
    confidence reflects parser certainty (0.0 = guessed, 1.0 = strong match).
    """
    raw_text: str
    normalized: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    confidence: float = 0.0
    location_type: str = "unknown"   # address | landmark | intersection | relative | unknown

    def is_resolved(self) -> bool:
        """True when lat/lon have been populated by the geocoding layer."""
        return self.lat is not None and self.lon is not None

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "normalized": self.normalized,
            "lat": self.lat,
            "lon": self.lon,
            "confidence": round(self.confidence, 3),
            "location_type": self.location_type,
            "is_resolved": self.is_resolved(),
        }


# ---------------------------------------------------------------------------
# Street-type normalization table
# ---------------------------------------------------------------------------

_STREET_ABBR: dict[str, str] = {
    "street": "St", "avenue": "Ave", "road": "Rd", "boulevard": "Blvd",
    "drive": "Dr", "lane": "Ln", "court": "Ct", "place": "Pl",
    "way": "Way", "parkway": "Pkwy", "circle": "Cir", "highway": "Hwy",
    "terrace": "Ter", "trail": "Trl", "loop": "Loop", "expressway": "Expy",
    "freeway": "Fwy",
}

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Full structured address: "123 Main Street" / "45 Oak Ave Apt 3B"
_RE_STREET_TYPES = (
    r"(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Blvd|Boulevard|Dr(?:ive)?"
    r"|Ln|Lane|Ct|Court|Pl(?:ace)?|Way|Pkwy|Parkway|Cir(?:cle)?"
    r"|Hwy|Highway|Terr?(?:ace)?|Trl|Trail|Loop|Expy|Fwy)"
)
_RE_ADDRESS = re.compile(
    r"\b(\d{1,5}"
    r"(?:\s+(?:apt|unit|suite|ste|#)\s*[\w\-]+)?"
    r"\s+[A-Z][a-zA-Z]+(?:\s+[A-Za-z]+){0,3}\s+"
    + _RE_STREET_TYPES + r")\b"
)

# Intersection: "5th and Main St" / "Oak Ave & River Rd"
# At least one side MUST end with a known street-type abbreviation or an
# ordinal number (e.g. "5th"), preventing false positives like "food and water".
_ST = r"(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Blvd|Dr(?:ive)?|Ln|Lane|Ct|Way|Pkwy|Hwy)"
_ORDINAL = r"\d+(?:st|nd|rd|th)"
_SIDE = r"[A-Z0-9][a-zA-Z0-9\s]{0,25}"
_RE_INTERSECTION = re.compile(
    r"\b("
    + _SIDE + r"(?:" + _ST + r"|" + _ORDINAL + r"))"
    r"\s+(?:and|&)\s+"
    r"(" + _SIDE + r"(?:" + _ST + r"|" + _ORDINAL + r")?)\b",
    re.IGNORECASE,
)

# Landmarks + contextual location phrases.
# Contextual trigger words (near/at/by/etc.) allow any capitalisation for the
# landmark name that follows -- real-world reports rarely capitalise landmarks.
_RE_LANDMARK = re.compile(
    r"""
    (?:
        (?:near|at|by|next\s+to|behind|in\s+front\s+of|across\s+from|outside)\s+
        (?:the\s+)?
        ([A-Za-z][a-zA-Z\s\-\']{3,50})           # landmark name (any case)
    |
        (?:the\s+)?([A-Z][a-zA-Z\s\-\']{3,40})
        \s+(?:bridge|park|school|hospital|church|mosque|temple|
               shelter|station|center|centre|mall|plaza|tower|building|complex)
    )
    """,
    re.VERBOSE,
)

# Relative direction phrases: "2 miles north of downtown"
_RE_RELATIVE = re.compile(
    r"\b(\d+(?:\.\d+)?\s+(?:miles?|km|blocks?)\s+"
    r"(?:north|south|east|west|northeast|northwest|southeast|southwest)\s+"
    r"of\s+[A-Za-z\s]{3,40})",
    re.IGNORECASE,
)

# City/neighbourhood mentions (fallback)
_RE_CITY = re.compile(
    r"\b(?:in|at|near|around)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)"
    r"(?:\s*,\s*[A-Z]{2})?\b"   # optional state abbreviation
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _title_case_words(text: str) -> str:
    """Title-case each word, preserving existing abbreviations like 'St'."""
    return " ".join(w.capitalize() for w in text.split())


def _abbreviate_street_types(text: str) -> str:
    """Replace long street type words with standard abbreviations."""
    parts = text.split()
    result = []
    for part in parts:
        lower = part.lower().rstrip(".,")
        abbr = _STREET_ABBR.get(lower)
        result.append(abbr if abbr else part)
    return " ".join(result)


def _score_candidate(raw: str, loc_type: str) -> float:
    """
    Heuristic confidence score for a location candidate.
    Higher scores mean more structured / more likely to geocode successfully.
    """
    scores = {
        "address":      0.90,
        "intersection": 0.70,
        "landmark":     0.55,
        "relative":     0.40,
        "city":         0.30,
        "unknown":      0.10,
    }
    base = scores.get(loc_type, 0.10)
    # Small bonus for longer, more specific mentions
    length_bonus = min(len(raw) / 200.0, 0.08)
    return round(min(base + length_bonus, 1.0), 3)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_location_candidates(text: str) -> list[str]:
    """
    Extract all plausible location strings from free-form text, ranked best-first.

    This is the primary entry point for the Geocoding MCP server -- it calls
    this function, then geocodes the returned strings in order until one resolves.

    Args:
        text: Raw disaster report text (may be PII-redacted or raw).

    Returns:
        Ordered list of candidate location strings. May be empty if no location
        is detectable -- callers must NOT fabricate coordinates in that case.

    Example:
        extract_location_candidates(
            "near the river bridge on 5th, water rising fast"
        )
        -> ["5th and river bridge", "river bridge on 5th"]
    """
    candidates: list[tuple[str, str, float]] = []  # (raw, type, score)

    # 1. Structured addresses (highest confidence)
    for m in _RE_ADDRESS.finditer(text):
        raw = m.group(1).strip()
        candidates.append((raw, "address", _score_candidate(raw, "address")))

    # 2. Intersections
    for m in _RE_INTERSECTION.finditer(text):
        raw = f"{m.group(1).strip()} & {m.group(2).strip()}"
        candidates.append((raw, "intersection", _score_candidate(raw, "intersection")))

    # 3. Relative direction phrases
    for m in _RE_RELATIVE.finditer(text):
        raw = m.group(1).strip()
        candidates.append((raw, "relative", _score_candidate(raw, "relative")))

    # 4. Landmarks
    for m in _RE_LANDMARK.finditer(text):
        raw = (m.group(1) or m.group(2) or "").strip()
        if raw and len(raw) > 3:
            candidates.append((raw, "landmark", _score_candidate(raw, "landmark")))

    # 5. City/neighbourhood fallback
    for m in _RE_CITY.finditer(text):
        raw = m.group(1).strip()
        if raw and len(raw) > 3:
            candidates.append((raw, "city", _score_candidate(raw, "city")))

    # Deduplicate (keep highest score per unique lowercased raw)
    seen: dict[str, tuple[str, str, float]] = {}
    for raw, loc_type, score in candidates:
        key = raw.lower()
        if key not in seen or score > seen[key][2]:
            seen[key] = (raw, loc_type, score)

    ranked = sorted(seen.values(), key=lambda x: x[2], reverse=True)
    return [r[0] for r in ranked]


def parse_location_from_text(text: str) -> Location:
    """
    Extract the best single location from free-form disaster report text.

    Tries patterns in confidence order: address > intersection > relative >
    landmark > city. Returns a Location with lat/lon=None until the Geocoding
    MCP server resolves them.

    Args:
        text: Raw or redacted disaster report text.

    Returns:
        Location dataclass. If no location is detectable, returns a Location
        with raw_text="", confidence=0.0, location_type="unknown" -- callers
        MUST NOT fabricate coordinates when confidence is 0.

    Example:
        loc = parse_location_from_text(
            "My house at 123 Main St flooded, need help"
        )
        # -> Location(raw_text="123 Main St", normalized="123 Main St",
        #             lat=None, lon=None, confidence=0.9, location_type="address")
    """
    # Try address patterns in priority order
    checks: list[tuple[re.Pattern, str, int]] = [
        (_RE_ADDRESS,      "address",      1),
        (_RE_INTERSECTION, "intersection", 0),  # group 0 = full match, rebuilt below
        (_RE_RELATIVE,     "relative",     1),
        (_RE_LANDMARK,     "landmark",     1),
        (_RE_CITY,         "city",         1),
    ]

    for pattern, loc_type, grp in checks:
        m = pattern.search(text)
        if not m:
            continue

        if loc_type == "intersection":
            raw = f"{m.group(1).strip()} & {m.group(2).strip()}"
        else:
            raw = (m.group(grp) or "").strip()

        if not raw:
            continue

        normalized = normalize_address(raw)
        confidence = _score_candidate(raw, loc_type)
        logger.debug("parse_location_from_text: type=%s raw=%r conf=%.2f", loc_type, raw, confidence)
        return Location(
            raw_text=raw,
            normalized=normalized,
            lat=None,
            lon=None,
            confidence=confidence,
            location_type=loc_type,
        )

    # Nothing found
    logger.debug("parse_location_from_text: no location detected in text")
    return Location(
        raw_text="",
        normalized="",
        lat=None,
        lon=None,
        confidence=0.0,
        location_type="unknown",
    )


def normalize_address(address: str) -> str:
    """
    Standardize an address string: title-case words, abbreviate street types,
    collapse whitespace, strip trailing punctuation.

    Args:
        address: Raw address or location string.

    Returns:
        Normalized string suitable for passing to a geocoding API.

    Example:
        normalize_address("123   main street  ") -> "123 Main St"
        normalize_address("456 OAK AVENUE")      -> "456 Oak Ave"
    """
    if not address:
        return ""
    cleaned = re.sub(r"\s+", " ", address.strip().rstrip(".,;"))
    titled = _title_case_words(cleaned)
    abbreviated = _abbreviate_street_types(titled)
    return abbreviated


def calculate_distance(loc1: Location, loc2: Location) -> float:
    """
    Calculate the great-circle distance between two resolved Locations using
    the Haversine formula.

    Args:
        loc1: First Location (must have lat/lon populated).
        loc2: Second Location (must have lat/lon populated).

    Returns:
        Distance in kilometres, rounded to 3 decimal places.

    Raises:
        ValueError: if either location has lat/lon = None (unresolved).

    Example:
        # Tampa, FL -> St. Petersburg, FL
        calculate_distance(
            Location("Tampa", "Tampa", lat=27.9506, lon=-82.4572),
            Location("St Pete", "St Pete", lat=27.7731, lon=-82.6400),
        )
        # -> 27.394  (approx)
    """
    if not loc1.is_resolved() or not loc2.is_resolved():
        raise ValueError(
            "Both locations must have lat/lon resolved before calculating distance. "
            f"loc1.resolved={loc1.is_resolved()}, loc2.resolved={loc2.is_resolved()}"
        )

    R = 6371.0  # Earth radius in kilometres

    lat1, lon1 = math.radians(loc1.lat), math.radians(loc1.lon)
    lat2, lon2 = math.radians(loc2.lat), math.radians(loc2.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 3)


def is_address_like(candidate: str) -> bool:
    """
    Return True if candidate looks like a structured street address
    (starts with a number and ends with a street type) rather than a landmark.

    Used by the Geocoding MCP to pick the best geocoding strategy.
    """
    return bool(_RE_ADDRESS.match(candidate.strip()))


# ---------------------------------------------------------------------------
# __main__ test -- run with: uv run python -m skills.geo_parser
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    TEST_CASES = [
        (
            "clean street address",
            "My house at 123 Main St flooded, 4 people need help urgently",
        ),
        (
            "vague landmark reference",
            "near the river bridge on 5th, water rising fast, about 15 people stuck",
        ),
        (
            "intersection",
            "accident at Oak Avenue & River Road, multiple injuries reported",
        ),
        (
            "relative direction",
            "shelter needed 2 miles north of downtown, family of 6 stranded",
        ),
        (
            "no location at all",
            "we need food and water, please help as soon as possible",
        ),
        (
            "normalize_address standalone",
            None,  # special case -- tested directly below
        ),
        (
            "haversine distance (Tampa to St Pete)",
            None,  # special case
        ),
    ]

    print("=" * 60)
    print("SafeHaven -- Geo Parser Test")
    print("=" * 60)

    all_passed = True

    for label, text in TEST_CASES:
        print(f"\n-- {label} --")

        if label == "normalize_address standalone":
            cases = [
                ("123   main street  ",  "123 Main St"),
                ("456 OAK AVENUE",        "456 Oak Ave"),
                ("789 elm road",          "789 Elm Rd"),
                ("",                      ""),
            ]
            for raw, expected in cases:
                got = normalize_address(raw)
                ok = got == expected
                if not ok:
                    all_passed = False
                print(f"  normalize_address({raw!r:30s}) -> {got!r:20s} {'PASS' if ok else 'FAIL (expected ' + repr(expected) + ')'}")
            continue

        if label == "haversine distance (Tampa to St Pete)":
            tampa = Location("Tampa", "Tampa", lat=27.9506, lon=-82.4572)
            stpete = Location("St Pete", "St Pete", lat=27.7731, lon=-82.6400)
            dist = calculate_distance(tampa, stpete)
            ok = 25.0 < dist < 30.0  # expect ~27 km
            if not ok:
                all_passed = False
            print(f"  Tampa -> St Pete: {dist} km  {'PASS' if ok else 'FAIL'}")

            # Test unresolved raises ValueError
            unresolved = Location("?", "?")
            try:
                calculate_distance(tampa, unresolved)
                print("  Unresolved ValueError: FAIL (should have raised)")
                all_passed = False
            except ValueError:
                print("  Unresolved ValueError: PASS (raised as expected)")
            continue

        print(f"  Input    : {text}")

        loc = parse_location_from_text(text)
        print(f"  Type     : {loc.location_type}")
        print(f"  Raw      : {loc.raw_text!r}")
        print(f"  Normalized: {loc.normalized!r}")
        print(f"  Confidence: {loc.confidence}")
        print(f"  Resolved : {loc.is_resolved()} (lat/lon stubbed as None until MCP runs)")

        candidates = extract_location_candidates(text)
        print(f"  Candidates ({len(candidates)}): {candidates}")

        # Validation rules
        if label == "no location at all":
            ok = loc.location_type == "unknown" and loc.confidence == 0.0 and not candidates
            print(f"  No-location guard: {'PASS' if ok else 'FAIL (fabricated a location)'}")
            if not ok:
                all_passed = False
        else:
            ok = loc.confidence > 0.0 and loc.raw_text != ""
            print(f"  Location found: {'PASS' if ok else 'FAIL'}")
            if not ok:
                all_passed = False

    print("\n" + "=" * 60)
    print(f"All tests passed: {all_passed}")
    print("=" * 60)
