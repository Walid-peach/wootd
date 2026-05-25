# Tasks Realized

This file records the implementation work done during the Snowflake/dbt architecture reorganization.

## 2026-05-25

1. Created Git branch `codex/snowflake-dbt-architecture`.
2. Replaced R2/DuckDB data dependencies with `snowflake-connector-python` and `dbt-snowflake`.
3. Replaced API R2/DuckDB/Supabase dependencies with Snowflake connector usage.
4. Updated `.env.example` with Snowflake, dbt, API, Sentry, and ingestion variables.
5. Replaced the old R2 Parquet writer with Snowflake RAW ingestion helpers.
6. Updated Open-Meteo ingestion to insert raw payloads into `RAW.OPEN_METEO_FORECASTS`.
7. Updated NOAA ingestion to insert raw payloads into `RAW.NOAA_FORECASTS`.
8. Added Snowflake RAW table creation and ingestion run logging helpers.
9. Reworked dbt from bronze/silver/gold DuckDB folders to Snowflake `STAGING`, `INTERMEDIATE`, and `MARTS` layers.
10. Added dbt sources for Snowflake RAW weather and feedback tables.
11. Added staging models for Open-Meteo, NOAA, and user feedback.
12. Added intermediate models to union, aggregate, and deduplicate weather observations.
13. Added marts models for city dimension, daily forecast facts, and recommendation features.
14. Added dbt tests for nulls, uniqueness, accepted values, precipitation ranges, and temperature sanity.
15. Added a `cities.csv` seed.
16. Replaced API DuckDB reads with Snowflake reads from `MARTS.FCT_DAILY_FORECAST`.
17. Replaced Supabase feedback writes with Snowflake writes to `RAW.USER_FEEDBACK`.
18. Simplified the ML engine into a rules fallback placeholder until Snowflake-based model training is added.
19. Added Snowflake initialization SQL under `infra/snowflake`.
20. Removed MLflow from Docker Compose because it is outside the basic Snowflake/dbt architecture.
21. Updated Makefile commands for Snowflake ingestion, dbt, API, and web workflows.
22. Updated CI Node install commands to avoid requiring a missing `package-lock.json`.
23. Replaced placeholder tests with rule-engine and ingestion-config tests.
24. Updated API, data, infra, and docs README files to describe the new architecture.
25. Updated agent guidance files to prevent stale R2/DuckDB instructions from reappearing.
26. Added architecture, data model, and local development documentation under `docs/`.
27. Cleaned active documentation so Snowflake is described as the only warehouse/storage layer.
28. Ran Python syntax compilation with `python -m compileall api data`.
29. Attempted `uv`-based pytest, ruff, and dbt parse checks; they could not run because `uv` is not installed or not on PATH in the local shell.
30. Ran `git diff --check`; no whitespace errors were reported.
31. Added root `requirements.txt` so the project can be installed with pip without using the Makefile.
32. Updated local development docs and README with direct script-by-script commands for ingestion, dbt, API, and web.
33. Sprint 1 setup check found local Python 3.10.5; docs now explicitly require Python 3.11+.
34. Removed unused `pandas` and `scikit-learn` setup dependencies from the first manual install path.
35. Added `python-dotenv` to the data package dependencies because ingestion scripts import it.
36. Created local ignored `.env` from `.env.example` with blank Snowflake credential values.
37. Validated `.env` is ignored by Git.
38. Updated README setup command to use PowerShell `Copy-Item` for the local Windows workflow.

## Sprint 2 preparation - dbt/Snowflake environment best practices

- Added/updated `.env.example` with safe `DBT_SNOWFLAKE_*` placeholders only.
- Ensured `.env` and `.env.*` are ignored while keeping `.env.example` committable.
- Updated `data/dbt/profiles.yml` to use dbt `env_var()` for Snowflake connection values.
- Updated dbt RAW source configuration to use the same environment variable names.
- Updated Snowflake ingestion connection helpers to read the same local Snowflake variables.
- Added `scripts/load-env.ps1` to load local `.env` values into the current PowerShell session without printing secret values.
- Added `scripts/validate-dbt-snowflake.ps1` for local dbt/Snowflake connection validation.
- Updated README and local development docs with the dbt/Snowflake validation workflow.
- Migrated local ignored `.env` from the older `SNOWFLAKE_*` names to the new `DBT_SNOWFLAKE_*` names without printing secret values.
- Ran dbt/Snowflake validation with `dbt debug --profiles-dir .`; profile and project files were valid, but the Snowflake connection failed with a login endpoint 404, which usually means the local account identifier needs correction.
- Updated the validation script to redact account, user, and Snowflake host details from dbt debug output.
- Added generated dbt `data/dbt/.user.yml` to `.gitignore` and removed the local generated copy.
- Restored `data/dbt/profiles.yml` after it was manually changed back to hardcoded Snowflake credentials.
- Removed obsolete empty dbt `bronze`, `silver`, and `gold` model directories from the working tree.
- Re-ran redacted `dbt debug`; the repo configuration is valid, but Snowflake now reports incorrect username or password.
- Updated ignored local `.env` from the working Python Snowflake connection script without printing secret values.
- Added local `scripts/testsnowcon.py` to `.gitignore` because it is a credential-bearing debug script.
- Re-ran redacted `dbt debug`; Snowflake connection passed successfully.
- Added generated root `logs/` to `.gitignore` and removed the local generated copy.
- No ingestion executed.

## Sprint 4 - raw ingestion validation

- Explained the expected raw Open-Meteo payload shape before ingestion.
- Ran Open-Meteo ingestion into `RAW.OPEN_METEO_FORECASTS`.
- Validated `RAW.OPEN_METEO_FORECASTS` row count and latest `RAW.INGESTION_RUNS` audit entry.
- Explained the expected raw NOAA payload shape.
- Ran NOAA ingestion into `RAW.NOAA_FORECASTS`.
- Validated `RAW.NOAA_FORECASTS` row count, latest audit entry, and presence of `payload:properties:periods`.
- No dbt models were run.

## Sprint 4 documentation - ingestion, architecture, and roadmap

- Added `docs/data_ingested_breakdown.md` explaining current raw data, business value, and future provider candidates.
- Added `docs/project_new_architecture.md` explaining the full project with the Snowflake/dbt architecture.
- Added `docs/remaining_sprints.md` defining the remaining project sprints.
- Updated `docs/README.md` with links to the new documentation files.
- No ingestion or dbt commands were run during this documentation update.
