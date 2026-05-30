"""Run active French weather providers and load their raw payloads to Snowflake."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from . import open_meteo, weatherapi
from .common import utc_now
from .snowflake_loader import (
    connect,
    ensure_raw_tables,
    load_weather_payload_rows,
    record_ingestion_run,
)

WeatherPayloadRow = dict[str, Any]
ProviderBuilder = Callable[[], list[WeatherPayloadRow]]

ACTIVE_PROVIDERS: list[ProviderBuilder] = [
    open_meteo.build_rows,
    weatherapi.build_rows,
]

PROVIDER_NAMES: dict[ProviderBuilder, str] = {
    open_meteo.build_rows: "open_meteo",
    weatherapi.build_rows: "weatherapi",
}


@dataclass(frozen=True)
class ProviderSummary:
    provider: str
    status: str
    rows_loaded: int
    cities_processed: list[str]
    message: str = ""


def provider_name(builder: ProviderBuilder) -> str:
    return PROVIDER_NAMES.get(builder, builder.__module__.rsplit(".", maxsplit=1)[-1])


def collect_provider_rows(
    providers: Iterable[ProviderBuilder] = ACTIVE_PROVIDERS,
) -> tuple[list[WeatherPayloadRow], list[ProviderSummary]]:
    all_rows: list[WeatherPayloadRow] = []
    summaries: list[ProviderSummary] = []

    for builder in providers:
        provider = provider_name(builder)
        try:
            rows = builder()
        except Exception as exc:
            message = str(exc)
            print(f"{provider} ingestion failed before loading: {message}")
            summaries.append(
                ProviderSummary(
                    provider=provider,
                    status="failed",
                    rows_loaded=0,
                    cities_processed=[],
                    message=message,
                )
            )
            continue

        all_rows.extend(rows)
        summaries.append(
            ProviderSummary(
                provider=provider,
                status="success",
                rows_loaded=len(rows),
                cities_processed=sorted({str(row["city_name"]) for row in rows}),
            )
        )

    return all_rows, summaries


def print_summary(summaries: Iterable[ProviderSummary]) -> None:
    for summary in summaries:
        cities = ", ".join(summary.cities_processed) if summary.cities_processed else "none"
        print(
            f"{summary.provider}: {summary.status}, "
            f"rows={summary.rows_loaded}, cities={cities}"
        )
        if summary.message:
            print(f"{summary.provider} message: {summary.message}")


def ingest() -> int:
    started_at = utc_now()
    rows, summaries = collect_provider_rows()

    with connect() as conn:
        ensure_raw_tables(conn)
        total_loaded = load_weather_payload_rows(conn, rows)
        finished_at = utc_now()

        for summary in summaries:
            record_ingestion_run(
                conn,
                provider=summary.provider,
                started_at=started_at,
                finished_at=finished_at,
                status=summary.status,
                rows_loaded=summary.rows_loaded,
                message=summary.message,
            )

    print_summary(summaries)
    print(f"Loaded {total_loaded} weather payload rows into Snowflake RAW.")
    return total_loaded


if __name__ == "__main__":
    load_dotenv()
    ingest()
