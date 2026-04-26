# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

WOOTD translates raw weather forecasts into daily outfit recommendations (top, bottom, outer layer, accessories). It has two recommendation engines: a deterministic rule-based engine and a LightGBM ML engine trained on user feedback. The web app ships first; a mobile app (SwiftUI) will consume the same API.

---

## Commands

```bash
make setup          # bootstrap Python venvs, npm install, db migrations
make dev            # start FastAPI + Astro + MLflow locally
make ingest         # one-off ingestion run against R2
make dbt-build      # run dbt models locally
make dbt-test       # run dbt data quality tests
make train          # train the LightGBM model
make test           # all tests
make test-api       # API tests only
make test-data      # data layer tests only
make lint           # ruff + mypy + prettier
```

Local services after `make dev`:

| Service        | URL                          |
|----------------|------------------------------|
| Web app        | http://localhost:4321        |
| API            | http://localhost:8000        |
| API docs       | http://localhost:8000/docs   |
| MLflow UI      | http://localhost:5000        |

---

## Architecture

### Data flow (left to right)

```
Open-Meteo + NOAA → GitHub Actions (cron) → R2 Lakehouse (bronze/silver/gold) → FastAPI → Astro
                                                         ↑
                                                   dbt-duckdb transforms
```

DuckDB queries Parquet directly from R2 (S3-compatible, zero egress cost) — there is no running warehouse. The API also reads gold/ via DuckDB at request time.

### Medallion layers in R2

- **bronze/** — raw API responses, partitioned `provider/date=YYYY-MM-DD/hour=HH/data.parquet`. Immutable; replay source.
- **silver/** — canonical `weather_observations` schema: deduplicated on `(city_id, forecast_timestamp, provider)`, UTC-normalized.
- **gold/** — `gold_daily_forecast` (one row per `city_id × forecast_date`) and `gold_recommendation_features` (model-ready feature vectors joining forecasts + user preferences + feedback).
- **models/** — serialized ML artifacts (`models/current/outfit_model.pkl`).

### Two databases, different purposes

- **R2 (lakehouse)** — weather data at all stages, ML features, model artifacts. Queried by dbt and the API via DuckDB.
- **Supabase Postgres (OLTP)** — users, recommendations, feedback, email signups. Also backs the MLflow tracking server.

### Recommendation engines

Both live in `api/app/engines/`. The `engine=` query param selects between them:

- `rules.py` — deterministic bands on temperature, precipitation, wind, and UV index.
- `ml.py` — LightGBM model loaded from R2 at boot; predicts acceptance probability for a given outfit × forecast × user.

### Ingestion is additive

Each provider is a separate script in `data/ingestion/`. Adding a provider = one new bronze script + one silver mapping. Existing silver tests enforce the canonical schema for all providers.

### Orchestration is GitHub Actions only

No Airflow, no Dagster. Workflow dependencies use `workflow_run` triggers. Failed runs surface in the Actions tab and trigger Sentry alerts on critical paths. All workflows are idempotent.

---

## Key Conventions

- **Cities** are seeded from `data/dbt/seeds/cities.csv`. The `/recommend` endpoint requires a city that exists in this seed.
- **Feedback ratings** are `-1 / 0 / 1`. These flow into Supabase and are picked up by the weekly retraining job.
- **Model versioning** follows `YYYY-MM-DD-vN` (e.g. `2026-04-21-v3`). The `/health` endpoint exposes the currently loaded version.
- **dbt tests** are the data quality gate — 15+ tests enforced on silver (not_null, unique, range checks, no future forecasts beyond 7 days). Run `make dbt-test` before merging any pipeline change.
- **Python**: 3.11+, linted with ruff, typed with mypy. **TypeScript**: Node 20+, formatted with prettier.
- **Deploys** are fully automated: pushes to `main` deploy API (Cloud Run) and frontend (Cloudflare Pages). Pushes to `data/dbt/**` rebuild dbt docs.
