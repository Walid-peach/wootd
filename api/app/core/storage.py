from __future__ import annotations

from datetime import date
from typing import Any, cast

import snowflake.connector
from snowflake.connector import DictCursor

from app.core.config import settings


def get_snowflake_connection() -> Any:
    return snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        role=settings.snowflake_role,
        warehouse=settings.snowflake_warehouse,
        database=settings.snowflake_database,
    )


def qualified_table(schema: str, table: str) -> str:
    return f"{settings.snowflake_database}.{schema}.{table}"


def fetch_daily_forecast(city: str, forecast_date: date) -> dict[str, Any] | None:
    query = f"""
        SELECT
            CITY_NAME,
            FORECAST_DATE,
            TEMP_MIN_C,
            TEMP_MAX_C,
            PRECIP_PROBABILITY,
            WIND_KMH,
            UV_INDEX
        FROM {qualified_table(settings.snowflake_marts_schema, "FCT_DAILY_FORECAST")}
        WHERE LOWER(CITY_NAME) = LOWER(%s)
          AND FORECAST_DATE = %s
        LIMIT 1
    """

    with get_snowflake_connection() as conn, conn.cursor(DictCursor) as cur:
        cur.execute(query, (city, forecast_date))
        return cast(dict[str, Any] | None, cur.fetchone())


def insert_feedback(recommendation_id: str, rating: int, notes: str) -> None:
    query = f"""
        INSERT INTO {qualified_table(settings.snowflake_raw_schema, "USER_FEEDBACK")} (
            RECOMMENDATION_ID,
            RATING,
            NOTES
        )
        VALUES (%s, %s, %s)
    """

    with get_snowflake_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (recommendation_id, rating, notes))
