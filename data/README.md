# Data Layer

The data layer ingests raw weather API responses into Snowflake and transforms them with dbt.

## Flow

```text
Open-Meteo / NOAA
  -> Python ingestion
  -> Snowflake RAW
  -> dbt STAGING
  -> dbt INTERMEDIATE
  -> dbt MARTS
```

## Main Commands

```bash
make ingest
make dbt-seed
make dbt-run
make dbt-test
make dbt-docs
```
