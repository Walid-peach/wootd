# Local Development

This workflow does not require the Makefile.

## Python Environment

Use Python 3.11 or newer. This project is configured for Python 3.11+.

Check your local Python version:

```powershell
python --version
```

If this prints Python 3.10 or older, install Python 3.11+ first and create the virtual environment with the 3.11 executable.

From the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables

Copy the template:

```powershell
Copy-Item .env.example .env
```

Fill in your Snowflake credentials in `.env`.

Use these local variable names:

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

Never commit `.env`. `.env.example` is safe to commit because it contains placeholders only.

dbt does not load `.env` by itself, so before running dbt in PowerShell, load the same variables into the shell:

```powershell
.\scripts\load-env.ps1
```

## Snowflake Setup

Run this SQL file in Snowflake first:

```text
infra/snowflake/001_init_warehouse.sql
```

It creates the warehouse, database, schemas, and RAW tables.

## Run Ingestion Scripts

From the project root:

```powershell
cd data
python -m ingestion.open_meteo
python -m ingestion.noaa
cd ..
```

Expected result:

- `RAW.OPEN_METEO_FORECASTS` receives Open-Meteo payloads.
- `RAW.NOAA_FORECASTS` receives NOAA payloads.
- `RAW.INGESTION_RUNS` receives audit records.

## Run dbt

From the project root:

```powershell
cd data\dbt
dbt debug --profiles-dir .
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
cd ..\..
```

Expected result:

- `RAW.CITIES` is loaded from the seed.
- `STAGING` views are built.
- `INTERMEDIATE` tables are built.
- `MARTS` tables are built.
- dbt tests validate the important data contracts.

## Run the API

From the project root:

```powershell
cd api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs:

```text
http://localhost:8000/docs
```

## Run the Web App

In a second terminal:

```powershell
cd web
npm install
npm run dev -- --host
```

Useful URLs:

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Web: http://localhost:4321
