"""Shared utilities for writing bronze Parquet to R2."""

import os
from datetime import UTC, datetime
from typing import Any

import boto3
import pyarrow as pa
import pyarrow.parquet as pq

DEFAULT_R2_BUCKET = "wootd-lakehouse"


def _s3_client() -> Any:
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT_URL"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )


def _r2_bucket() -> str:
    return os.environ.get("R2_BUCKET_NAME", DEFAULT_R2_BUCKET)


def write_bronze(provider: str, table: pa.Table, ts: datetime | None = None) -> str:
    """Write a PyArrow table to bronze/<provider>/date=YYYY-MM-DD/hour=HH/data.parquet."""
    ts = ts or datetime.now(UTC)
    key = f"bronze/{provider}/date={ts.strftime('%Y-%m-%d')}/hour={ts.strftime('%H')}/data.parquet"

    buf = pa.BufferOutputStream()
    pq.write_table(table, buf, compression="snappy")

    _s3_client().put_object(
        Bucket=_r2_bucket(),
        Key=key,
        Body=buf.getvalue().to_pybytes(),
        ContentType="application/octet-stream",
    )
    return key
