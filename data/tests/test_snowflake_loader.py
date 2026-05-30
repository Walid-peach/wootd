from ingestion.snowflake_loader import load_weather_payload_rows


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def execute(self, sql, params=None) -> None:
        self.connection.executed.append((sql, params))


class FakeConnection:
    def __init__(self):
        self.executed = []

    def cursor(self):
        return FakeCursor(self)


def test_load_weather_payload_rows_uses_common_raw_shape() -> None:
    connection = FakeConnection()
    rows = [
        {
            "provider": "open_meteo",
            "city_name": "Paris",
            "country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "ingested_at": "2026-05-30T00:00:00Z",
            "payload": {"daily": {"time": ["2026-05-30"]}},
        }
    ]

    rows_loaded = load_weather_payload_rows(connection, rows)

    assert rows_loaded == 1
    sql, params = connection.executed[0]
    assert "WEATHER_FORECAST_PAYLOADS" in sql
    assert params[:6] == (
        "open_meteo",
        "Paris",
        "FR",
        48.8566,
        2.3522,
        "2026-05-30T00:00:00Z",
    )
