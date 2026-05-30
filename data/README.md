# Data Layer

The data layer ingests raw weather API responses into Snowflake and transforms them with dbt.

## Flow

```text
French city config
  -> Open-Meteo / WeatherAPI.com
  -> Python ingestion
  -> Snowflake RAW.WEATHER_FORECAST_PAYLOADS
  -> dbt STAGING
  -> dbt INTERMEDIATE
  -> dbt MARTS
```

NOAA is US-focused and is not part of the active default ingestion workflow.

## Main Commands

```bash
make ingest
make dbt-seed
make dbt-run
make dbt-test
make dbt-docs
```

Manual ingestion without Make:

```bash
cd data
python -m ingestion.run_weather_ingestion
```
