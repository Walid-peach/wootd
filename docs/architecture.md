# Architecture

WOOTD uses Snowflake as the central warehouse and dbt as the transformation layer.

```text
Weather APIs
  -> Python ingestion
  -> RAW Snowflake tables
  -> dbt staging models
  -> dbt intermediate models
  -> dbt marts
  -> FastAPI
  -> Web app
```

## Responsibilities

- Python ingestion fetches provider data and stores raw payloads.
- Snowflake stores raw, cleaned, and business-ready data.
- dbt transforms raw payloads into tested models.
- FastAPI serves product use cases from marts.
- Astro provides the user interface.

## Design Rule

Ingestion should not contain business transformations. It should load raw data into Snowflake. dbt should own transformation logic.
