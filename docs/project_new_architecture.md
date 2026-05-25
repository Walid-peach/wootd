# WOOTD Project Explanation - New Architecture

## Project Pitch

WOOTD is a data engineering and application project that answers:

```text
What should I wear today?
```

The platform ingests weather forecasts, stores raw provider responses in Snowflake, transforms them with dbt, and exposes outfit recommendations through a FastAPI backend.

## New Architecture

```text
Weather APIs
  -> Python ingestion scripts
  -> Snowflake RAW schema
  -> dbt STAGING models
  -> dbt INTERMEDIATE models
  -> dbt MARTS models
  -> FastAPI recommendation API
  -> Astro web app
```

## Why This Architecture

The architecture separates responsibilities clearly:

| Layer | Responsibility |
|---|---|
| Python ingestion | Extract provider data and load raw JSON |
| Snowflake RAW | Store replayable source data |
| dbt STAGING | Parse provider-specific JSON |
| dbt INTERMEDIATE | Standardize, union, aggregate, and deduplicate |
| dbt MARTS | Publish API-ready business tables |
| FastAPI | Serve recommendations and feedback endpoints |
| Astro | Frontend experience |

This is a clean analytics engineering pattern. Python does not own transformations. dbt owns transformations. The API does not query raw data; it reads curated marts.

## Repository Structure

```text
wootd/
  api/
    app/
      core/
      engines/
      routers/
    tests/

  data/
    ingestion/
    dbt/
      models/
        staging/
        intermediate/
        marts/
      seeds/
      tests/
    tests/

  docs/
  infra/
    snowflake/
  scripts/
  web/
```

## Data Flow

### 1. Ingestion

Ingestion scripts call weather APIs:

```text
data/ingestion/open_meteo.py
data/ingestion/noaa.py
```

They insert raw API responses into:

```text
RAW.OPEN_METEO_FORECASTS
RAW.NOAA_FORECASTS
```

They also write audit records into:

```text
RAW.INGESTION_RUNS
```

### 2. Raw Storage

Snowflake RAW tables keep original provider payloads.

This gives:

- traceability
- replayability
- debugging ability
- provider-change protection

### 3. dbt Transformations

dbt transforms raw payloads into clean data.

Staging models:

```text
stg_open_meteo_forecasts
stg_noaa_forecasts
stg_user_feedback
```

Intermediate models:

```text
int_weather_observations_unioned
int_daily_city_forecasts
int_weather_observations_deduped
```

Mart models:

```text
dim_city
fct_daily_forecast
fct_recommendation_features
```

### 4. API Serving

The API reads from:

```text
MARTS.FCT_DAILY_FORECAST
```

The recommendation engine receives clean forecast values:

```text
temp_min_c
temp_max_c
precip_probability
wind_kmh
uv_index
condition
```

It maps weather signals to outfit choices:

```text
top
bottom
outer layer
accessories
explanation
```

### 5. Feedback

User feedback is written to:

```text
RAW.USER_FEEDBACK
```

This can later feed analytics and model training.

## Current Status

Completed:

- Snowflake connection validated with dbt.
- RAW weather ingestion validated for Open-Meteo.
- RAW weather ingestion validated for NOAA.
- dbt project structure created.
- API connection layer prepared for Snowflake.
- Local credential workflow moved to `.env` plus dbt `env_var()`.

Not yet completed:

- dbt seed/run/test validation.
- API endpoint validation against real marts.
- Frontend integration.
- Airflow orchestration.
- ML training.
- Production CI/CD.

## Current Data Loaded

Open-Meteo:

```text
5 raw rows loaded into RAW.OPEN_METEO_FORECASTS
latest audit status = success
```

NOAA:

```text
1 raw row loaded into RAW.NOAA_FORECASTS
latest audit status = success
```

## Business Logic

The business logic starts with weather signals:

| Signal | Business Meaning |
|---|---|
| Temperature | warmth and layering |
| Rain probability | umbrella/raincoat |
| Wind speed | windbreaker |
| UV index | sunglasses/sunscreen |
| Condition text | user-friendly explanation |

Example:

```text
temp_avg_c = 12
precip_probability = 0.70
wind_kmh = 18
uv_index = 2
```

Recommendation:

```text
long-sleeve shirt
light jacket
umbrella
```

## Why Snowflake

Snowflake gives the project a real data warehouse layer:

- central storage
- SQL-first analytics
- separation of schemas
- good dbt integration
- scalable foundation for future orchestration

The current schemas are:

```text
RAW
STAGING
INTERMEDIATE
MARTS
```

## Why dbt

dbt gives:

- version-controlled SQL transformations
- model lineage
- tests
- documentation
- clean separation between raw data and business-ready tables

## Airflow Later

Airflow is not part of the current run path yet.

Later, Airflow should orchestrate:

```text
ingest_open_meteo
ingest_noaa
dbt_seed
dbt_run
dbt_test
```

For now, the project is intentionally manual so each step can be understood and validated.

## Interview Explanation

WOOTD is a weather-based recommendation platform built with a modern data engineering architecture. Python ingestion scripts load raw weather API responses into Snowflake. dbt parses and transforms the data through staging, intermediate, and marts layers. The API consumes the final daily forecast mart to recommend outfits based on temperature, rain, wind, and UV. The architecture is modular, testable, and ready for orchestration with Airflow later.
