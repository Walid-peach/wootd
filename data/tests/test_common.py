from datetime import UTC, datetime
from typing import Any

import pyarrow as pa
from ingestion import common


class FakeS3Client:
    def __init__(self) -> None:
        self.put_calls: list[dict[str, Any]] = []

    def put_object(self, **kwargs: Any) -> None:
        self.put_calls.append(kwargs)


def test_write_bronze_uses_expected_partition_path(monkeypatch: Any) -> None:
    fake_s3 = FakeS3Client()
    monkeypatch.setattr(common, "_s3_client", lambda: fake_s3)

    table = pa.table({"city_name": pa.array(["Paris"])})
    key = common.write_bronze(
        "open_meteo",
        table,
        datetime(2026, 4, 27, 9, tzinfo=UTC),
    )

    assert key == "bronze/open_meteo/date=2026-04-27/hour=09/data.parquet"
    assert fake_s3.put_calls[0]["Bucket"] == common.DEFAULT_R2_BUCKET
    assert fake_s3.put_calls[0]["Key"] == key
    assert fake_s3.put_calls[0]["ContentType"] == "application/octet-stream"
