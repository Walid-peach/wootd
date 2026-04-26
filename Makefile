.PHONY: setup dev ingest dbt-build dbt-test train test test-api test-data lint

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -e "api/[dev]" -e "data/[dev]"
	cd web && npm install
	. .venv/bin/activate && cd data/dbt && dbt deps

dev:
	docker compose up --build

ingest:
	. .venv/bin/activate && python -m data.ingestion.open_meteo
	. .venv/bin/activate && python -m data.ingestion.noaa

dbt-build:
	. .venv/bin/activate && cd data/dbt && dbt build

dbt-test:
	. .venv/bin/activate && cd data/dbt && dbt test

train:
	. .venv/bin/activate && python -m data.ml.train

test: test-api test-data

test-api:
	. .venv/bin/activate && pytest api/tests/ -v

test-data:
	. .venv/bin/activate && pytest data/tests/ -v

lint:
	. .venv/bin/activate && ruff check api/ data/
	. .venv/bin/activate && mypy api/ data/
	cd web && npx prettier --check src/
