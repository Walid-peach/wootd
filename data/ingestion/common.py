"""Shared ingestion helpers that are independent from a specific provider."""

from __future__ import annotations

import os
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def configured_cities() -> list[str]:
    """Return city names from DEFAULT_CITIES, preserving order and removing blanks."""
    raw_value = os.environ.get(
        "DEFAULT_CITIES",
        (
            "Paris,Rennes,Lyon,Marseille,Toulouse,Bordeaux,Lille,Nantes,"
            "Strasbourg,Nice,Montpellier,Grenoble"
        ),
    )
    return [city.strip() for city in raw_value.split(",") if city.strip()]
