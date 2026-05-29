"""Ingest daily forecasts from Open-Meteo into Snowflake RAW."""

from __future__ import annotations

from typing import Any, TypedDict, cast

import requests

from ingestion.common import configured_cities, utc_now
from ingestion.snowflake_loader import (
    connect,
    ensure_raw_tables,
    load_open_meteo_rows,
    record_ingestion_run,
)


class CityConfig(TypedDict):
    name: str
    lat: float
    lon: float


CITY_COORDINATES: dict[str, CityConfig] = {
    "Paris": {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    "London": {"name": "London", "lat": 51.5074, "lon": -0.1278},
    "New York": {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    "Tokyo": {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    "Sydney": {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
}

API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS: dict[str, int | str] = {
    "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,uv_index",
    "daily": (
        "temperature_2m_max,temperature_2m_min,"
        "precipitation_probability_max,wind_speed_10m_max,uv_index_max"
    ),
    "forecast_days": 7,
    "timezone": "UTC",
}


def selected_cities() -> list[CityConfig]:
    configured = set(configured_cities())
    return [city for name, city in CITY_COORDINATES.items() if name in configured]


def fetch(city: CityConfig) -> dict[str, Any]:
    params: dict[str, float | int | str] = {
        **PARAMS,
        "latitude": city["lat"],
        "longitude": city["lon"],
    }
    response = requests.get(
        API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return cast(dict[str, Any], response.json())


def build_rows() -> list[dict[str, Any]]:
    ingested_at = utc_now()
    rows: list[dict[str, Any]] = []

    for city in selected_cities():
        rows.append(
            {
                "city_name": city["name"],
                "latitude": city["lat"],
                "longitude": city["lon"],
                "ingested_at": ingested_at,
                "payload": fetch(city),
            }
        )

    return rows


def ingest() -> int:
    started_at = utc_now()
    rows_loaded = 0

    with connect() as conn:
        ensure_raw_tables(conn)
        try:
            rows = build_rows()
            rows_loaded = load_open_meteo_rows(conn, rows)
            record_ingestion_run(
                conn,
                provider="open_meteo",
                started_at=started_at,
                finished_at=utc_now(),
                status="success",
                rows_loaded=rows_loaded,
            )
        except Exception as exc:
            record_ingestion_run(
                conn,
                provider="open_meteo",
                started_at=started_at,
                finished_at=utc_now(),
                status="failed",
                rows_loaded=rows_loaded,
                message=str(exc),
            )
            raise

    print(f"Loaded {rows_loaded} Open-Meteo rows into Snowflake RAW.")
    return rows_loaded


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ingest()
