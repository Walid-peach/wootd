"""Ingest forecasts from NOAA for US cities (no API key required)."""

import json
from datetime import datetime, timezone

import pyarrow as pa
import requests

from data.ingestion.common import write_bronze

US_CITIES: list[dict] = [
    {"name": "New York",  "office": "OKX", "gridX": 33, "gridY": 37},
    {"name": "Chicago",   "office": "LOT", "gridX": 76, "gridY": 73},
    {"name": "Los Angeles", "office": "LOX", "gridX": 149, "gridY": 43},
]

BASE_URL = "https://api.weather.gov"
HEADERS = {"User-Agent": "wootd/0.1 (walidelkhoukh99@gmail.com)"}


def fetch(city: dict) -> dict:
    url = f"{BASE_URL}/gridpoints/{city['office']}/{city['gridX']},{city['gridY']}/forecast"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def ingest() -> None:
    ts = datetime.now(timezone.utc)
    rows: list[dict] = []

    for city in US_CITIES:
        try:
            data = fetch(city)
            rows.append({
                "city_name": city["name"],
                "ingested_at": ts.isoformat(),
                "payload": json.dumps(data),
            })
        except requests.HTTPError as e:
            print(f"NOAA fetch failed for {city['name']}: {e}")

    if not rows:
        return

    table = pa.table({
        "city_name":   pa.array([r["city_name"] for r in rows]),
        "ingested_at": pa.array([r["ingested_at"] for r in rows]),
        "payload":     pa.array([r["payload"] for r in rows]),
    })

    key = write_bronze("noaa", table, ts)
    print(f"Wrote {len(rows)} cities → {key}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest()
