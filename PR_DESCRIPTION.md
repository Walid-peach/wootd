## Summary

- Fixed reviewer-reported Ruff issues in Snowflake storage/loader code.
- Fixed mypy typing issues in Open-Meteo and NOAA ingestion modules.
- Split CI Python tests into separate API and data jobs.
- Updated dbt weather deduplication so Open-Meteo is preferred over NOAA before recency is used as a tie-breaker.

## Validation

- `make fmt` / `make lint` / `make test-api` / `make test-data` / `make dbt-debug` / `make dbt-test`: not runnable in this local PowerShell session because `make` is not installed.
- `.venv\Scripts\python.exe -m ruff format --check --no-cache api/ data/`: reports three pre-existing API files would be reformatted; left untouched to keep this PR reviewer-focused.
- `.venv\Scripts\python.exe -m ruff check --no-cache api/ data/`: passed.
- `.venv\Scripts\python.exe -m mypy api/app data/ingestion data/ml`: passed.
- `.venv\Scripts\python.exe -m pytest api/tests/ -v -p no:cacheprovider`: passed.
- `.venv\Scripts\python.exe -m pytest data/tests/ -v -p no:cacheprovider`: passed.
- `npx prettier --check src/`: not runnable locally because web dependencies are not installed and `prettier-plugin-astro` is unavailable.
- `dbt debug --profiles-dir .`: passed with local `.env` loaded and dbt logs redirected to a temp directory.
- `dbt test --profiles-dir .`: connected to Snowflake, but failed because dbt-built STAGING/INTERMEDIATE/MARTS relations do not exist yet. Run `dbt run` before `dbt test` in a prepared warehouse.

## Notes

- GitHub CLI was not available locally, so this file can be used to update the PR description manually.
- No ingestion commands were run.
