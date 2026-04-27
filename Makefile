.DEFAULT_GOAL := help
.PHONY: help setup dev down test test-api test-data lint fmt ingest dbt-build dbt-test train clean

help: ## List all targets with descriptions
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Bootstrap ─────────────────────────────────────────────────────────────────

setup: ## Install Python deps (uv) and Node deps
	uv sync --all-packages
	cd web && npm install

# ── Local stack ───────────────────────────────────────────────────────────────

dev: ## Start the full local stack (FastAPI + Astro + MLflow)
	docker compose up --build

down: ## Stop the local stack
	docker compose down

# ── Quality ───────────────────────────────────────────────────────────────────

lint: ## Check Python (ruff + mypy) and web (prettier)
	uv run ruff check api/ data/
	cd api && uv run mypy app
	cd data && uv run mypy ingestion ml
	cd web && npx prettier --check src/

fmt: ## Auto-format Python (ruff) and web (prettier)
	uv run ruff format api/ data/
	uv run ruff check --fix api/ data/
	cd web && npx prettier --write src/

# ── Tests ─────────────────────────────────────────────────────────────────────

test: test-api test-data ## Run all tests

test-api: ## Run API tests
	uv run pytest api/tests/ -v

test-data: ## Run data layer tests
	uv run pytest data/tests/ -v

# ── Pipeline stubs (Phase 1+) ─────────────────────────────────────────────────

ingest: ## [Phase 1] Run bronze ingestion against R2
	@echo "Not implemented yet — coming in Phase 1"

dbt-build: ## [Phase 1] Build dbt models
	@echo "Not implemented yet — coming in Phase 1"

dbt-test: ## [Phase 1] Run dbt data quality tests
	@echo "Not implemented yet — coming in Phase 1"

train: ## [Phase 1] Train the LightGBM model
	@echo "Not implemented yet — coming in Phase 1"

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean: ## Remove build artefacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.duckdb" -delete 2>/dev/null || true
