.DEFAULT_GOAL := help
.PHONY: help setup dev down api-dev web-dev test test-api test-data lint fmt ingest ingest-weather ingest-open-meteo ingest-weatherapi dbt-debug dbt-seed dbt-run dbt-test dbt-docs clean

help: ## List all targets with descriptions
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## Install Python and Node dependencies
	uv sync --all-packages
	cd web && npm install

dev: ## Start the local API and web services
	docker compose up --build

down: ## Stop the local Docker services
	docker compose down

api-dev: ## Run FastAPI locally without Docker
	cd api && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

web-dev: ## Run Astro locally without Docker
	cd web && npm run dev -- --host

lint: ## Check Python and web formatting
	uv run ruff check api/ data/
	cd api && uv run mypy app
	cd data && uv run mypy ingestion ml
	cd web && npx prettier --check src/

fmt: ## Auto-format Python and web files
	uv run ruff format api/ data/
	uv run ruff check --fix api/ data/
	cd web && npx prettier --write src/

test: test-api test-data ## Run all tests

test-api: ## Run API tests
	uv run pytest api/tests/ -v

test-data: ## Run data layer tests
	uv run pytest data/tests/ -v

ingest: ingest-weather ## Run active French weather provider ingestion

ingest-weather: ## Ingest active French weather providers into Snowflake RAW
	cd data && uv run python -m ingestion.run_weather_ingestion

ingest-open-meteo: ## Ingest Open-Meteo forecasts into Snowflake RAW
	cd data && uv run python -m ingestion.open_meteo

ingest-weatherapi: ## Ingest WeatherAPI.com forecasts into Snowflake RAW
	cd data && uv run python -m ingestion.weatherapi

dbt-debug: ## Validate dbt Snowflake connection
	cd data/dbt && uv run dbt debug --profiles-dir .

dbt-seed: ## Load dbt seeds into Snowflake RAW
	cd data/dbt && uv run dbt seed --profiles-dir .

dbt-run: ## Build Snowflake STAGING, INTERMEDIATE, and MARTS models
	cd data/dbt && uv run dbt run --profiles-dir .

dbt-test: ## Run dbt data quality tests
	cd data/dbt && uv run dbt test --profiles-dir .

dbt-docs: ## Generate dbt documentation
	cd data/dbt && uv run dbt docs generate --profiles-dir .

clean: ## Remove local build artefacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
