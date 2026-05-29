# CLAUDE.md

Guidance for Claude Code and other coding assistants working in this repository.

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

Snowflake is the warehouse and dbt owns the transformation layer.

## Main Commands

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

## Important Contracts

- Ingestion writes raw API responses to Snowflake `RAW`.
- dbt owns all transformations after ingestion.
- The API reads from `MARTS.FCT_DAILY_FORECAST`.
- Feedback is stored in `RAW.USER_FEEDBACK`.
- Keep README, dbt docs, and `tasks-realized.md` aligned with architecture changes.
