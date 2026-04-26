# WOOTD

> _Dress smart. Every single day._

![status](https://img.shields.io/badge/status-in%20development-yellow) ![license](https://img.shields.io/badge/license-MIT-blue) ![python](https://img.shields.io/badge/python-3.11+-blue) ![dbt](https://img.shields.io/badge/dbt-duckdb-orange) ![ci](https://img.shields.io/badge/ci-github%20actions-2088FF)

WOOTD is a weather-driven outfit recommendation platform. It ingests multi-source weather forecasts, normalizes them through a medallion lakehouse, and serves personalized outfit suggestions through a web app — with a mobile app planned for the next release.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Why This Project](#-why-this-project)
3. [Architecture](#-architecture)
4. [Tech Stack](#-tech-stack)
5. [Data Sources](#-data-sources)
6. [Repository Structure](#-repository-structure)
7. [Data Pipeline](#-data-pipeline)
8. [Local Development](#-local-development)
9. [Infrastructure](#-infrastructure)
10. [API Reference](#-api-reference)
11. [Roadmap](#-roadmap)
12. [Contributors](#-contributors)
13. [Built With](#-built-with)
14. [License](#-license)

---

## 📌 Project Overview

WOOTD answers the oldest daily question: _"What do I wear today?"_

Standard weather apps tell you it's 12°C with a 60% chance of rain. They don't tell you what that _means_ for how you should dress. WOOTD closes that gap by translating raw forecasts into a clear outfit recommendation: top, bottom, outer layer, accessories.

The recommendation engine has two modes:

- **Rule-based engine** — deterministic, transparent, hand-tuned bands for temperature, precipitation, wind, and UV index.
- **ML engine** — a LightGBM model trained on user feedback that predicts the probability a user will accept a given outfit.

The web app ships first, doubling as the public landing page. A native mobile app is on the roadmap and will consume the same API.

---

## 🎯 Why This Project

The product thesis is simple: **outfit recommendations are only as good as the weather data behind them and the model that interprets it.**

Most weather apps treat the underlying data as solved — pull from one provider, render the number, done. We disagree. Forecasts disagree with each other constantly, microclimates matter, and "feels like" is highly personal. WOOTD invests in both halves of the problem:

- A clean ingestion pipeline that reconciles forecasts from multiple providers
- A feedback loop that personalizes recommendations to each user over time
- A transparent reasoning layer where users can see _why_ a recommendation was made

What we believe:

- Multi-source forecasts are more reliable than any single source.
- Personalization beats generalization. Your "cold" is not someone else's "cold."
- Transparent recommendations beat black-box ones.
- Daily-cadence ML is enough — outfit decisions don't need millisecond inference.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
│      Open-Meteo API           │           NOAA API               │
└──────────────┬─────────────────────────────────┬───────────────┘
               │                                 │
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION — GitHub Actions                  │
│   Scheduled workflows · workflow_run dependencies                │
│   Run history and logs as the audit trail                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STORAGE — Cloudflare R2 (Lakehouse)             │
│   bronze/   raw API responses, partitioned by provider/date      │
│   silver/   normalized, deduped, common schema                   │
│   gold/     business-ready: daily forecast + features            │
│   models/   serialized ML artifacts                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TRANSFORMATION — dbt-duckdb                     │
│   DuckDB queries Parquet directly from R2 (zero egress)          │
│   bronze → silver → gold models · 15+ data quality tests         │
│   dbt docs published on every release                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SERVING — FastAPI on Cloud Run                  │
│   GET /recommend · POST /feedback · GET /health                  │
│   Reads gold/ via DuckDB · loads ML model from models/ at boot   │
│   Rule engine + ML engine, A/B selectable                        │
└────────────┬─────────────────────────────────┬──────────────────┘
             │                                 │
             ▼                                 ▼
┌──────────────────────┐            ┌──────────────────────────┐
│   FRONTEND — Astro    │            │   APP DB — Supabase       │
│   Cloudflare Pages    │            │   Postgres (OLTP)         │
│   Landing + /app      │            │   users · recommendations │
│                       │            │   feedback · email_signups│
└──────────────────────┘            └──────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│   ML LIFECYCLE — LightGBM + MLflow (self-hosted)                 │
│   Weekly retraining · model registry · prediction logging        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│   OBSERVABILITY — Grafana Cloud · Sentry · dbt docs              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Orchestration | **GitHub Actions** | Scheduled workflows with built-in run history, logs, and secret management. No infra to maintain. |
| Object storage | **Cloudflare R2** | Zero egress fees enable DuckDB to query Parquet from anywhere without bandwidth costs. |
| Transformation | **dbt-duckdb** | Embedded warehouse running on the same compute as the orchestrator; native Parquet over S3-compatible storage. |
| App database | **Supabase Postgres** | Postgres for relational integrity; auth and REST included. |
| API | **FastAPI on Cloud Run** | Containerized, scale-to-zero, simple local-prod parity. |
| Frontend | **Astro on Cloudflare Pages** | Static-first, ideal for the landing-page-plus-app shape. |
| ML training | **LightGBM** | Strong on tabular data, fast, small artifacts. |
| ML tracking | **MLflow (self-hosted)** | Open-source experiment tracking and model registry, backed by Supabase. |
| Errors | **Sentry** | Generous free tier, instant signal on production errors. |
| Metrics & logs | **Grafana Cloud** | Public dashboards linkable from this README. |
| CI / CD | **GitHub Actions** | Same system that runs the data pipeline runs the deploys. |
| Language | **Python 3.11+**, **TypeScript** | |

A full comparison of alternatives considered (Airflow, Dagster, BigQuery, Snowflake, S3, Lambda, etc.) is documented in [`docs/stack-decisions.md`](docs/stack-decisions.md).

---

## 🌦️ Data Sources

| Source | Type | Auth needed | Coverage | Notes |
|---|---|---|---|---|
| **Open-Meteo** | Forecast API | None | Global | Primary source. No API key, generous rate limits. |
| **NOAA** | Forecast + observation | None | United States | Secondary source for US cities. Used for cross-validation and reconciliation. |

The ingestion layer is additive by design — adding a new provider means writing one bronze model and one silver mapping. Future candidates: Météo-France, Tomorrow.io, MET Norway.

---

## 📁 Repository Structure

```
wootd/
├── data/                          # All data engineering code
│   ├── ingestion/                 # Provider-specific ingestion scripts
│   │   ├── open_meteo.py
│   │   ├── noaa.py
│   │   └── common.py
│   ├── dbt/                       # dbt project
│   │   ├── models/
│   │   │   ├── bronze/
│   │   │   ├── silver/
│   │   │   └── gold/
│   │   ├── tests/
│   │   ├── seeds/
│   │   │   └── cities.csv
│   │   ├── dbt_project.yml
│   │   └── profiles.yml
│   └── ml/                        # Training pipelines
│       ├── features.py
│       ├── train.py
│       └── evaluate.py
├── api/                           # FastAPI service
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── recommend.py
│   │   │   ├── feedback.py
│   │   │   └── health.py
│   │   ├── engines/
│   │   │   ├── rules.py
│   │   │   └── ml.py
│   │   └── core/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── web/                           # Astro frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.astro        # landing page
│   │   │   ├── app.astro          # recommender UI
│   │   │   └── about.astro        # architecture page
│   │   └── components/
│   ├── public/
│   └── package.json
├── infra/                         # Deployment config
│   ├── cloud-run/
│   └── supabase/
│       └── migrations/
├── docs/
│   ├── architecture.md
│   ├── stack-decisions.md
│   └── data-model.md
├── .github/
│   └── workflows/
│       ├── ingest.yml             # cron: every 3 hours
│       ├── transform.yml          # triggered by ingest completion
│       ├── train.yml              # cron: weekly
│       ├── publish-dbt-docs.yml   # on push to data/dbt/**
│       ├── ci.yml                 # tests + lint on every PR
│       ├── deploy-api.yml         # push to main
│       └── deploy-web.yml         # push to main
├── .env.example
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 🔄 Data Pipeline

WOOTD follows a medallion architecture. Each layer has explicit contracts and tests.

### Bronze — raw, immutable

Raw API responses are written as Parquet, partitioned by `provider/date/hour`. No transformation beyond serialization. This layer is the source of truth — if a downstream model breaks, we replay from bronze.

```
bronze/open_meteo/date=2026-04-26/hour=09/data.parquet
bronze/noaa/date=2026-04-26/hour=09/data.parquet
```

### Silver — normalized, deduped

Each provider's schema is mapped to a single canonical `weather_observations` schema. Records are deduplicated by `(city_id, forecast_timestamp, provider)`. Timezones are standardized to UTC. Null handling is explicit.

Tests enforced in this layer:

- `not_null` on `city_id`, `forecast_timestamp`, `temperature_celsius`
- `unique` on the dedup key
- `temperature_celsius` between -50 and 60
- No forecasts dated more than 7 days in the future

### Gold — business-ready

`gold_daily_forecast` aggregates silver into one row per `(city_id, forecast_date)` with the fields the recommender needs: temperature high/low, feels-like, precipitation probability, wind, UV index, condition codes.

`gold_recommendation_features` joins forecasts with user preferences and recent feedback to produce model-ready feature vectors.

### ML — trained weekly

The training workflow reads `gold_recommendation_features`, joins to `feedback` from Supabase, trains a LightGBM model, evaluates on a holdout, registers the artifact in MLflow, and writes the new `models/current/outfit_model.pkl` to R2. The API picks up the new model on its next warm restart.

### Schedules

| Pipeline | Schedule | Trigger |
|---|---|---|
| Bronze ingestion | Every 3 hours | GitHub Actions cron |
| Silver + Gold transform | After ingestion completes | `workflow_run` on ingest |
| Data quality checks | After transform completes | `workflow_run` on transform |
| ML retraining | Weekly (Sunday 02:00 UTC) | GitHub Actions cron |
| dbt docs publish | On push to `data/dbt/**` | GitHub Actions |

All workflows are idempotent and safe to re-run. Failed runs surface in the repo's Actions tab and trigger Sentry alerts on critical paths.

---

## 💻 Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- A Cloudflare R2 account (or any S3-compatible storage)
- A Supabase account
- `make`, `git`

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/walid-peach/wootd.git
cd wootd

# 2. Configure environment
cp .env.example .env
# Edit .env with your R2 credentials, Supabase URL/key, etc.

# 3. Bootstrap everything (Python venvs, npm install, db migrations)
make setup

# 4. Run the local stack (FastAPI, Astro, MLflow)
make dev
```

Services after `make dev`:

| Service | URL |
|---|---|
| Web app | http://localhost:4321 |
| API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |

### Running the pipeline manually

```bash
# Run a one-off ingestion against R2
make ingest

# Build dbt models locally against R2
make dbt-build

# Run dbt tests
make dbt-test

# Train the model
make train
```

### Running tests

```bash
make test          # all tests
make test-api      # API only
make test-data     # data layer only
make lint          # ruff + mypy + prettier
```

The same commands run in CI on every pull request via [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## ☁️ Infrastructure

| Component | Hosting |
|---|---|
| API | Cloud Run |
| Frontend | Cloudflare Pages |
| Object storage | Cloudflare R2 |
| App database | Supabase |
| MLflow tracking | Cloud Run (Supabase backend) |
| Metrics & logs | Grafana Cloud |
| Errors | Sentry |
| CI / CD | GitHub Actions |

Deployment is fully automated through GitHub Actions:

- Pushes to `main` deploy the API to Cloud Run and the frontend to Cloudflare Pages.
- Pushes to `data/dbt/**` rebuild and publish the dbt docs site.
- All deploys run tests and quality checks first; failed deploys are blocked.

Detailed deployment instructions: [`docs/infrastructure.md`](docs/infrastructure.md).

---

## 📡 API Reference

Base URL (local): `http://localhost:8000`  
Base URL (production): `https://api.wootd.app`

### `GET /recommend`

Returns an outfit recommendation for a given city and user.

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `city` | string | yes | City name (must exist in the cities seed) |
| `user_id` | uuid | no | If omitted, defaults to a generic user profile |
| `engine` | enum | no | `rules` (default) or `ml` |
| `date` | date | no | Forecast date, defaults to today |

**Response**

```json
{
  "recommendation_id": "f3b1c2e4-…",
  "city": "Paris",
  "forecast_date": "2026-04-26",
  "engine": "ml",
  "model_version": "2026-04-21-v3",
  "outfit": {
    "top": "long-sleeve shirt",
    "bottom": "chinos",
    "outer": "light jacket",
    "accessories": ["umbrella"]
  },
  "weather_snapshot": {
    "temp_min_c": 9,
    "temp_max_c": 14,
    "precip_probability": 0.6,
    "wind_kmh": 18,
    "uv_index": 2
  },
  "explanation": "Mild day with rain likely in the afternoon."
}
```

### `POST /feedback`

Submits user feedback on a recommendation.

**Request body**

```json
{
  "recommendation_id": "f3b1c2e4-…",
  "rating": 1,
  "notes": "Was a bit too warm for the jacket"
}
```

`rating` is `-1` (bad), `0` (okay), or `1` (good).

**Response**: `204 No Content`.

### `GET /health`

Returns service health and currently-loaded model version.

```json
{
  "status": "ok",
  "model_version": "2026-04-21-v3",
  "uptime_seconds": 3421
}
```

Full OpenAPI spec is auto-generated and available at `/docs`.

---

## 🗺️ Roadmap

### Current release — Web platform

- [x] Multi-source weather ingestion (Open-Meteo, NOAA)
- [x] Medallion lakehouse on Cloudflare R2
- [x] dbt-duckdb transformation layer
- [x] Data quality test suite
- [x] FastAPI service with rule-based engine
- [x] Astro web app + landing page
- [ ] LightGBM ML engine with MLflow tracking
- [ ] Weekly automated retraining
- [ ] Public Grafana dashboard

### Next — Mobile

- [ ] iOS app (SwiftUI) consuming the same API
- [ ] Push notifications for morning recommendations
- [ ] User authentication via Supabase Auth
- [ ] Wardrobe personalization (own clothing items)

### Later

- [ ] Iceberg table format migration
- [ ] Real-time event streaming for feedback (Bytewax / Redpanda)
- [ ] Multi-language support
- [ ] Wardrobe photo recognition
- [ ] Calendar integration ("you have a meeting at 3pm — plan for the walk")

---

## 👥 Contributors

- [@walid-peach](https://github.com/Walid-peach/) — data, backend
- [@wassim](https://github.com/basssell) — data, backend

_Two data engineers who'd rather build a five-stage pipeline than admit they don't know what to wear._

Pull requests welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 🤖 Built With

Developed with the help of **[Claude Code](https://claude.ai/code)** and **[Codex](https://openai.com/codex)** for pair programming and code generation. All architectural decisions and deployed code were reviewed by the contributors.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
