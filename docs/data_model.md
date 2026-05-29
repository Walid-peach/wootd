# Data Model

## RAW

- `OPEN_METEO_FORECASTS`: raw Open-Meteo payloads by city and ingestion time.
- `NOAA_FORECASTS`: raw NOAA payloads by city and ingestion time.
- `USER_FEEDBACK`: raw feedback events from the API.
- `INGESTION_RUNS`: ingestion audit table.

## STAGING

- `stg_open_meteo_forecasts`: parsed Open-Meteo daily forecast rows.
- `stg_noaa_forecasts`: parsed NOAA forecast periods normalized to shared columns.
- `stg_user_feedback`: normalized feedback events.

## INTERMEDIATE

- `int_weather_observations_unioned`: provider forecasts combined into one shape.
- `int_daily_city_forecasts`: one daily row per provider and city.
- `int_weather_observations_deduped`: preferred forecast per city and date.

## MARTS

- `dim_city`: city dimension.
- `fct_daily_forecast`: API-ready daily forecast fact table.
- `fct_recommendation_features`: feature table for future ML and analytics.
