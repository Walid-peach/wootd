# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

WOOTD is a Snowflake/dbt data engineering project that turns weather forecasts into outfit recommendations.

## Current Architecture

```text
Open-Meteo + NOAA
  -> Python ingestion
  -> Snowflake RAW
  -> dbt STAGING
  -> dbt INTERMEDIATE
  -> dbt MARTS
  -> FastAPI
  -> Astro
```

Snowflake is the warehouse. Do not add a second storage layer unless the maintainers explicitly decide to add archival storage later.

## Commands

```bash
make setup
make ingest
make dbt-debug
make dbt-seed
make dbt-run
make dbt-test
make api-dev
make web-dev
make test
make lint
```

## Data Layers

- `RAW`: raw provider payloads and user feedback.
- `STAGING`: provider-specific parsing and normalization.
- `INTERMEDIATE`: unioning, aggregation, deduplication, and business logic.
- `MARTS`: API-ready and analytics-ready tables.

The API reads `MARTS.FCT_DAILY_FORECAST` and writes feedback to `RAW.USER_FEEDBACK`.
