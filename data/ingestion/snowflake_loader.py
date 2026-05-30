"""Snowflake RAW-layer loader used by ingestion scripts."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from datetime import datetime
from typing import Any

import snowflake.connector
from snowflake.connector import SnowflakeConnection

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str) -> str:
    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(f"Unsafe Snowflake identifier: {value!r}")
    return value.upper()


def raw_schema() -> str:
    return _identifier(os.environ.get("DBT_SNOWFLAKE_SCHEMA", "RAW"))


def connect(schema: str | None = None) -> SnowflakeConnection:
    kwargs = {
        "account": os.environ["DBT_SNOWFLAKE_ACCOUNT"],
        "user": os.environ["DBT_SNOWFLAKE_USER"],
        "password": os.environ["DBT_ENV_SECRET_SNOWFLAKE_PASSWORD"],
        "role": os.environ.get("DBT_SNOWFLAKE_ROLE"),
        "warehouse": os.environ["DBT_SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["DBT_SNOWFLAKE_DATABASE"],
    }
    if schema:
        kwargs["schema"] = schema
    return snowflake.connector.connect(**kwargs)


def ensure_raw_tables(conn: SnowflakeConnection) -> None:
    schema = raw_schema()
    statements = [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.WEATHER_FORECAST_PAYLOADS (
            INGESTION_ID STRING DEFAULT UUID_STRING(),
            PROVIDER STRING NOT NULL,
            CITY_NAME STRING NOT NULL,
            COUNTRY STRING NOT NULL,
            LATITUDE FLOAT,
            LONGITUDE FLOAT,
            INGESTED_AT TIMESTAMP_TZ NOT NULL,
            PAYLOAD VARIANT NOT NULL
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.OPEN_METEO_FORECASTS (
            INGESTION_ID STRING DEFAULT UUID_STRING(),
            PROVIDER STRING NOT NULL,
            CITY_NAME STRING NOT NULL,
            LATITUDE FLOAT,
            LONGITUDE FLOAT,
            INGESTED_AT TIMESTAMP_TZ NOT NULL,
            PAYLOAD VARIANT NOT NULL
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.NOAA_FORECASTS (
            INGESTION_ID STRING DEFAULT UUID_STRING(),
            PROVIDER STRING NOT NULL,
            CITY_NAME STRING NOT NULL,
            INGESTED_AT TIMESTAMP_TZ NOT NULL,
            PAYLOAD VARIANT NOT NULL
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.USER_FEEDBACK (
            FEEDBACK_ID STRING DEFAULT UUID_STRING(),
            RECOMMENDATION_ID STRING NOT NULL,
            RATING INTEGER NOT NULL,
            NOTES STRING,
            CREATED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.INGESTION_RUNS (
            RUN_ID STRING DEFAULT UUID_STRING(),
            PROVIDER STRING NOT NULL,
            RUN_STARTED_AT TIMESTAMP_TZ NOT NULL,
            RUN_FINISHED_AT TIMESTAMP_TZ NOT NULL,
            STATUS STRING NOT NULL,
            ROWS_LOADED INTEGER NOT NULL,
            MESSAGE STRING
        )
        """,
    ]

    with conn.cursor() as cur:
        for statement in statements:
            cur.execute(statement)


def load_weather_payload_rows(conn: SnowflakeConnection, rows: Iterable[dict[str, Any]]) -> int:
    schema = raw_schema()
    rows_loaded = 0
    insert_sql = f"""
        INSERT INTO {schema}.WEATHER_FORECAST_PAYLOADS (
            PROVIDER,
            CITY_NAME,
            COUNTRY,
            LATITUDE,
            LONGITUDE,
            INGESTED_AT,
            PAYLOAD
        )
        SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
    """

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                insert_sql,
                (
                    row["provider"],
                    row["city_name"],
                    row["country"],
                    row["latitude"],
                    row["longitude"],
                    row["ingested_at"],
                    json.dumps(row["payload"]),
                ),
            )
            rows_loaded += 1

    return rows_loaded


def load_open_meteo_rows(conn: SnowflakeConnection, rows: Iterable[dict[str, Any]]) -> int:
    schema = raw_schema()
    rows_loaded = 0
    insert_sql = f"""
        INSERT INTO {schema}.OPEN_METEO_FORECASTS (
            PROVIDER,
            CITY_NAME,
            LATITUDE,
            LONGITUDE,
            INGESTED_AT,
            PAYLOAD
        )
        SELECT %s, %s, %s, %s, %s, PARSE_JSON(%s)
    """

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                insert_sql,
                (
                    "open_meteo",
                    row["city_name"],
                    row["latitude"],
                    row["longitude"],
                    row["ingested_at"],
                    json.dumps(row["payload"]),
                ),
            )
            rows_loaded += 1

    return rows_loaded


def load_noaa_rows(conn: SnowflakeConnection, rows: Iterable[dict[str, Any]]) -> int:
    schema = raw_schema()
    rows_loaded = 0
    insert_sql = f"""
        INSERT INTO {schema}.NOAA_FORECASTS (
            PROVIDER,
            CITY_NAME,
            INGESTED_AT,
            PAYLOAD
        )
        SELECT %s, %s, %s, PARSE_JSON(%s)
    """

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                insert_sql,
                (
                    "noaa",
                    row["city_name"],
                    row["ingested_at"],
                    json.dumps(row["payload"]),
                ),
            )
            rows_loaded += 1

    return rows_loaded


def record_ingestion_run(
    conn: SnowflakeConnection,
    provider: str,
    started_at: datetime,
    finished_at: datetime,
    status: str,
    rows_loaded: int,
    message: str = "",
) -> None:
    schema = raw_schema()
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {schema}.INGESTION_RUNS (
                PROVIDER,
                RUN_STARTED_AT,
                RUN_FINISHED_AT,
                STATUS,
                ROWS_LOADED,
                MESSAGE
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (provider, started_at, finished_at, status, rows_loaded, message),
        )
