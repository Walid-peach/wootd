# WOOTD

Dress smart. Every single day.

WOOTD is a data-oriented weather application that turns weather forecasts into outfit recommendations. The project now uses Snowflake as the central data warehouse and dbt as the transformation layer.

## Architecture

```text
Weather APIs
  -> Python ingestion
  -> Snowflake RAW schema
  -> dbt STAGING models
  -> dbt INTERMEDIATE models
  -> dbt MARTS models
  -> FastAPI
  -> Astro web app
```

## What Each Layer Does

| Layer | Tool | Purpose |
|---|---|---|
| Ingestion | Python, requests, Snowflake connector | Fetch raw weather payloads and store them in Snowflake |
| Warehouse | Snowflake | Central storage for raw, cleaned, and business-ready data |
| Transformations | dbt-snowflake | Parse, clean, test, document, and model the data |
| API | FastAPI | Serve outfit recommendations and collect feedback |
| Frontend | Astro | Web interface and future dashboard |
| Local orchestration | Makefile, Docker Compose | Developer workflow |
| CI | GitHub Actions | Lint, type-check, and test the project |

## Snowflake Data Model

The warehouse is organized into clear schemas:

```text
WOOTD_DB
  RAW
  STAGING
  INTERMEDIATE
  MARTS
```

### RAW

Raw data is loaded directly from providers with minimal transformation.

Tables:

- `RAW.OPEN_METEO_FORECASTS`
- `RAW.NOAA_FORECASTS`
- `RAW.USER_FEEDBACK`
- `RAW.INGESTION_RUNS`

RAW is the replayable source of truth. If dbt logic changes, the project can rebuild downstream models from these raw tables.

### STAGING

Staging models parse provider-specific JSON and standardize column names and types.

Models:

- `stg_open_meteo_forecasts`
- `stg_noaa_forecasts`
- `stg_user_feedback`

### INTERMEDIATE

Intermediate models contain cross-source business logic.

Models:

- `int_weather_observations_unioned`
- `int_daily_city_forecasts`
- `int_weather_observations_deduped`

### MARTS

Marts are final tables consumed by the API, analytics, or future ML jobs.

Models:

- `dim_city`
- `fct_daily_forecast`
- `fct_recommendation_features`

The `/recommend` endpoint reads from `MARTS.FCT_DAILY_FORECAST`.

## Repository Structure

```text
wootd/
  api/                 FastAPI service
  data/
    ingestion/         Weather API ingestion into Snowflake RAW
    dbt/               dbt-snowflake project
    tests/             Data-layer tests
  web/                 Astro frontend
  infra/
    snowflake/         Snowflake initialization SQL
  docs/                Architecture and project notes
  docker-compose.yml   Local API and web services
  Makefile             Developer commands
  .env.example         Local environment template
```

## Environment Setup

Create a local `.env` from the template:

```powershell
Copy-Item .env.example .env
```

Fill in the Snowflake values:

```text
DBT_SNOWFLAKE_ACCOUNT=
DBT_SNOWFLAKE_USER=
DBT_ENV_SECRET_SNOWFLAKE_PASSWORD=
DBT_SNOWFLAKE_ROLE=WOOTD_ADMIN
DBT_SNOWFLAKE_WAREHOUSE=WOOTD_WH
DBT_SNOWFLAKE_DATABASE=WOOTD_DB
DBT_SNOWFLAKE_SCHEMA=RAW
DBT_THREADS=4
```

Never commit `.env`. It contains local secrets and is ignored by Git. `.env.example` is the safe committed template.

For local development, password authentication is acceptable. For CI/CD or production, prefer CI secret variables or a secrets manager, and later move Snowflake authentication to key-pair auth.

## Snowflake Initialization

Run the SQL in:

```text
infra/snowflake/001_init_warehouse.sql
```

It creates the warehouse, database, schemas, and RAW tables needed by ingestion and the API.

## Local Development

Install Python dependencies:

```powershell
python --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use Python 3.11 or newer. If `py -3.11` is not available, install Python 3.11+ first.

Load `.env` into the current PowerShell session before running dbt:

```powershell
.\scripts\load-env.ps1
```

Validate the dbt/Snowflake connection:

```powershell
cd data\dbt
dbt debug --profiles-dir .
cd ..\..
```

Run ingestion:

```powershell
cd data
python -m ingestion.open_meteo
python -m ingestion.noaa
cd ..
```

Run dbt:

```powershell
cd data\dbt
dbt debug --profiles-dir .
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
cd ..\..
```

Run the API:

```powershell
cd api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Run the web app in another terminal:

```powershell
cd web
npm install
npm run dev -- --host
```

Services:

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Web | http://localhost:4321 |

## API

### `GET /recommend`

Returns an outfit recommendation for a city and forecast date.

Query parameters:

| Name | Required | Description |
|---|---|---|
| `city` | yes | City name |
| `forecast_date` | no | Forecast date, defaults to today |
| `engine` | no | `rules` or `ml`; ML currently falls back to rules |
| `user_id` | no | Reserved for personalization |

The endpoint reads from:

```text
MARTS.FCT_DAILY_FORECAST
```

### `POST /feedback`

Stores user feedback in:

```text
RAW.USER_FEEDBACK
```

Feedback values:

- `-1`: bad
- `0`: okay
- `1`: good

### `GET /health`

Returns API health and the active recommendation engine version.

## Tests and Quality

```bash
make lint
make test
make dbt-test
```

CI runs Python linting, mypy, pytest, Prettier, and Astro checks.

## Current Status

Implemented:

- Snowflake RAW ingestion structure
- dbt-snowflake project structure
- staging, intermediate, and marts models
- dbt data tests
- FastAPI reads from Snowflake marts
- Feedback writes to Snowflake raw table
- Docker Compose for API and web

Not implemented yet:

- Production scheduling for ingestion and dbt
- Real ML training and model registry
- Full frontend recommendation UI
- Authentication and user profile management
- Deployment pipelines for API and web

## Interview Explanation

WOOTD follows a classic analytics engineering architecture. Python ingestion loads raw weather API responses into Snowflake. dbt transforms raw provider payloads into standardized staging models, applies business logic in intermediate models, and publishes API-ready marts. FastAPI consumes the mart table to serve outfit recommendations, while feedback events are written back into Snowflake for future analytics and ML.
