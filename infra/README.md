# Infrastructure

Infrastructure files for the Snowflake-centered WOOTD architecture.

## Snowflake

`snowflake/001_init_warehouse.sql` creates the basic database, schemas, warehouse, and RAW tables used by ingestion and the API.

## Local Services

`docker-compose.yml` starts the local API and web app. Snowflake runs as a managed cloud warehouse and is configured through `.env`.
