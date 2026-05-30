"""Ingest French forecasts from WeatherAPI.com into Snowflake RAW."""

from __future__ import annotations

import os
from typing import Any, cast

import requests

from .cities import CityConfig, selected_french_cities
from .common import utc_now
from .snowflake_loader import (
    connect,
    ensure_raw_tables,
    load_weather_payload_rows,
    record_ingestion_run,
)

JsonPayload = dict[str, Any]
WeatherPayloadRow = dict[str, Any]

API_URL = "https://api.weatherapi.com/v1/forecast.json"
DEFAULT_FORECAST_DAYS = 7


def api_key() -> str:
    key = os.environ.get("WEATHERAPI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("WEATHERAPI_API_KEY is required for WeatherAPI ingestion.")
    return key


def forecast_days() -> int:
    raw_value = os.environ.get("WEATHERAPI_FORECAST_DAYS", str(DEFAULT_FORECAST_DAYS))
    return int(raw_value)


def selected_cities() -> list[CityConfig]:
    return selected_french_cities()


def fetch(city: CityConfig, key: str) -> JsonPayload:
    params: dict[str, float | int | str] = {
        "key": key,
        "q": f"{city['lat']},{city['lon']}",
        "days": forecast_days(),
        "aqi": "no",
        "alerts": "no",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return cast(JsonPayload, response.json())


def build_rows() -> list[WeatherPayloadRow]:
    key = api_key()
    ingested_at = utc_now()
    rows: list[WeatherPayloadRow] = []

    for city in selected_cities():
        try:
            payload = fetch(city, key)
        except requests.RequestException as exc:
            print(f"WeatherAPI fetch failed for {city['name']}: {exc}")
            continue

        rows.append(
            {
                "provider": "weatherapi",
                "city_name": city["name"],
                "country": city["country"],
                "latitude": city["lat"],
                "longitude": city["lon"],
                "ingested_at": ingested_at,
                "payload": payload,
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
            rows_loaded = load_weather_payload_rows(conn, rows)
            record_ingestion_run(
                conn,
                provider="weatherapi",
                started_at=started_at,
                finished_at=utc_now(),
                status="success",
                rows_loaded=rows_loaded,
            )
        except Exception as exc:
            record_ingestion_run(
                conn,
                provider="weatherapi",
                started_at=started_at,
                finished_at=utc_now(),
                status="failed",
                rows_loaded=rows_loaded,
                message=str(exc),
            )
            raise

    print(f"Loaded {rows_loaded} WeatherAPI rows into Snowflake RAW.")
    return rows_loaded


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ingest()
