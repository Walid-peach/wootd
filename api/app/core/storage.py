import duckdb

from app.core.config import settings


def get_duckdb() -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection wired to R2 via the S3 extension."""
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"""
        SET s3_endpoint='{settings.r2_endpoint_url.replace("https://", "")}';
        SET s3_access_key_id='{settings.r2_access_key_id}';
        SET s3_secret_access_key='{settings.r2_secret_access_key}';
        SET s3_region='auto';
    """)
    return con


def gold_path(table: str) -> str:
    return f"s3://{settings.r2_bucket_name}/gold/{table}/**/*.parquet"
