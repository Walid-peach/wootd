"""Ingest US forecasts from NOAA into Snowflake RAW."""

from __future__ import annotations

import requests

from ingestion.common import configured_cities, utc_now
from ingestion.snowflake_loader import (
    connect,
    ensure_raw_tables,
    load_noaa_rows,
    record_ingestion_run,
)

US_CITIES: dict[str, dict[str, int | str]] = {
    "New York": {"name": "New York", "office": "OKX", "gridX": 33, "gridY": 37},
    "Chicago": {"name": "Chicago", "office": "LOT", "gridX": 76, "gridY": 73},
    "Los Angeles": {"name": "Los Angeles", "office": "LOX", "gridX": 149, "gridY": 43},
}

BASE_URL = "https://api.weather.gov"
HEADERS = {"User-Agent": "wootd/0.1 data-engineering-project"}


def selected_cities() -> list[dict[str, int | str]]:
    configured = set(configured_cities())
    return [city for name, city in US_CITIES.items() if name in configured]


def fetch(city: dict[str, int | str]) -> dict:
    url = f"{BASE_URL}/gridpoints/{city['office']}/{city['gridX']},{city['gridY']}/forecast"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def build_rows() -> list[dict]:
    ingested_at = utc_now()
    rows: list[dict] = []

    for city in selected_cities():
        try:
            rows.append(
                {
                    "city_name": city["name"],
                    "ingested_at": ingested_at,
                    "payload": fetch(city),
                }
            )
        except requests.HTTPError as exc:
            print(f"NOAA fetch failed for {city['name']}: {exc}")

    return rows


def ingest() -> int:
    started_at = utc_now()
    rows_loaded = 0

    with connect() as conn:
        ensure_raw_tables(conn)
        try:
            rows = build_rows()
            rows_loaded = load_noaa_rows(conn, rows)
            record_ingestion_run(
                conn,
                provider="noaa",
                started_at=started_at,
                finished_at=utc_now(),
                status="success",
                rows_loaded=rows_loaded,
            )
        except Exception as exc:
            record_ingestion_run(
                conn,
                provider="noaa",
                started_at=started_at,
                finished_at=utc_now(),
                status="failed",
                rows_loaded=rows_loaded,
                message=str(exc),
            )
            raise

    print(f"Loaded {rows_loaded} NOAA rows into Snowflake RAW.")
    return rows_loaded


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ingest()
