"""Ingest hourly forecasts from Open-Meteo (no API key required)."""

import json
import os
from datetime import datetime, timezone

import pyarrow as pa
import requests

from data.ingestion.common import write_bronze

CITIES: list[dict[str, float | str]] = [
    {"name": "Paris",     "lat": 48.8566,  "lon": 2.3522},
    {"name": "London",    "lat": 51.5074,  "lon": -0.1278},
    {"name": "New York",  "lat": 40.7128,  "lon": -74.0060},
    {"name": "Tokyo",     "lat": 35.6762,  "lon": 139.6503},
    {"name": "Sydney",    "lat": -33.8688, "lon": 151.2093},
]

API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "hourly": "temperature_2m,precipitation_probability,windspeed_10m,uv_index",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,windspeed_10m_max,uv_index_max",
    "forecast_days": 7,
    "timezone": "UTC",
}


def fetch(city: dict[str, float | str]) -> dict:
    resp = requests.get(
        API_URL,
        params={**PARAMS, "latitude": city["lat"], "longitude": city["lon"]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def ingest() -> None:
    ts = datetime.now(timezone.utc)
    rows: list[dict] = []

    for city in CITIES:
        data = fetch(city)
        rows.append({
            "city_name": city["name"],
            "latitude": city["lat"],
            "longitude": city["lon"],
            "ingested_at": ts.isoformat(),
            "payload": json.dumps(data),
        })

    table = pa.table({
        "city_name":    pa.array([r["city_name"] for r in rows]),
        "latitude":     pa.array([r["latitude"] for r in rows], type=pa.float64()),
        "longitude":    pa.array([r["longitude"] for r in rows], type=pa.float64()),
        "ingested_at":  pa.array([r["ingested_at"] for r in rows]),
        "payload":      pa.array([r["payload"] for r in rows]),
    })

    key = write_bronze("open_meteo", table, ts)
    print(f"Wrote {len(rows)} cities → {key}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest()
