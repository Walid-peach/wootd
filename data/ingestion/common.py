"""Shared utilities for writing bronze Parquet to R2."""

import os
from datetime import UTC, datetime

import boto3
import pyarrow as pa
import pyarrow.parquet as pq

R2_ENDPOINT = os.environ["R2_ENDPOINT_URL"]
R2_KEY = os.environ["R2_ACCESS_KEY_ID"]
R2_SECRET = os.environ["R2_SECRET_ACCESS_KEY"]
R2_BUCKET = os.environ.get("R2_BUCKET_NAME", "wootd-lakehouse")


def _s3_client() -> boto3.client:  # type: ignore[type-arg]
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_KEY,
        aws_secret_access_key=R2_SECRET,
    )


def write_bronze(provider: str, table: pa.Table, ts: datetime | None = None) -> str:
    """Write a PyArrow table to bronze/<provider>/date=YYYY-MM-DD/hour=HH/data.parquet."""
    ts = ts or datetime.now(UTC)
    key = f"bronze/{provider}/date={ts.strftime('%Y-%m-%d')}/hour={ts.strftime('%H')}/data.parquet"

    buf = pa.BufferOutputStream()
    pq.write_table(table, buf, compression="snappy")

    _s3_client().put_object(
        Bucket=R2_BUCKET,
        Key=key,
        Body=buf.getvalue().to_pybytes(),
        ContentType="application/octet-stream",
    )
    return key
