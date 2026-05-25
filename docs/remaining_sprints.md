# Remaining Sprints

This roadmap starts after successful raw ingestion validation.

Completed:

```text
Sprint 0 - Architecture validated
Sprint 1 - Local setup completed
Sprint 2 - dbt/Snowflake connection validated
Sprint 3 - Snowflake role validation completed
Sprint 4 - RAW ingestion validated
```

## Sprint 5 - dbt Seed And Model Build

Goal:

```text
Build Snowflake STAGING, INTERMEDIATE, and MARTS models with dbt.
```

Tasks:

1. Run `dbt debug --profiles-dir .`
2. Run `dbt seed --profiles-dir .`
3. Run `dbt run --profiles-dir .`
4. Run `dbt test --profiles-dir .`
5. Inspect created schemas/tables in Snowflake.

Expected result:

```text
RAW.CITIES exists
STAGING models build
INTERMEDIATE models build
MARTS.FCT_DAILY_FORECAST exists
dbt tests pass or produce clear fixes
```

Files involved:

```text
data/dbt/dbt_project.yml
data/dbt/profiles.yml
data/dbt/seeds/cities.csv
data/dbt/models/staging/*
data/dbt/models/intermediate/*
data/dbt/models/marts/*
data/dbt/tests/*
```

Risk:

```text
Medium
```

Reason:

The first dbt run may reveal JSON path issues or Snowflake SQL dialect issues.

## Sprint 6 - API Validation Against Snowflake Marts

Goal:

```text
Validate the FastAPI service reads from MARTS.FCT_DAILY_FORECAST.
```

Tasks:

1. Start the API locally.
2. Call `/health`.
3. Call `/recommend` for a city/date available in the mart.
4. Validate 404 behavior when forecast data is missing.
5. Validate `/feedback` writes to `RAW.USER_FEEDBACK`.

Expected result:

```text
API returns a real outfit recommendation from Snowflake-backed data.
```

Files involved:

```text
api/app/core/storage.py
api/app/routers/recommend.py
api/app/routers/feedback.py
api/app/engines/rules.py
```

Risk:

```text
Medium
```

Reason:

API assumptions must match the final mart column names and data types.

## Sprint 7 - Documentation Cleanup And First Commit

Goal:

```text
Prepare the branch for a clean commit or PR.
```

Tasks:

1. Review all changed files.
2. Remove obsolete wording.
3. Confirm `.env`, dbt local files, logs, and debug scripts are ignored.
4. Run syntax checks.
5. Run dbt validation.
6. Stage and commit.

Expected result:

```text
Clean commit with Snowflake/dbt architecture foundation.
```

Risk:

```text
Low
```

## Sprint 8 - Frontend/API Integration

Goal:

```text
Connect the frontend to the API recommendation endpoint.
```

Tasks:

1. Create a basic city/date input.
2. Call `/recommend`.
3. Display outfit recommendation.
4. Display weather snapshot.
5. Add error/loading states.

Expected result:

```text
User can request an outfit recommendation from the web app.
```

Risk:

```text
Medium
```

## Sprint 9 - Airflow Orchestration

Goal:

```text
Automate the manual pipeline steps.
```

Future DAG:

```text
ingest_open_meteo
  -> ingest_noaa
  -> dbt_seed
  -> dbt_run
  -> dbt_test
```

Tasks:

1. Add Airflow project structure.
2. Define DAG.
3. Add Snowflake/dbt environment handling.
4. Run locally.
5. Document orchestration.

Expected result:

```text
Manual pipeline becomes scheduled/orchestrated.
```

Risk:

```text
Medium to high
```

Reason:

Airflow adds operational complexity and should come only after the manual pipeline is reliable.

## Sprint 10 - Analytics And ML Readiness

Goal:

```text
Prepare data for analytics and future ML.
```

Tasks:

1. Improve `fct_recommendation_features`.
2. Add feedback analytics.
3. Add acceptance-rate marts.
4. Define future training dataset.
5. Document ML path.

Expected result:

```text
The project can explain how user feedback becomes future personalization.
```

Risk:

```text
Medium
```

## Recommended Next Sprint

The immediate next sprint should be:

```text
Sprint 5 - dbt Seed And Model Build
```

Do not start Airflow until dbt and API are validated manually.
