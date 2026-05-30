from ingestion import noaa, open_meteo, run_weather_ingestion, weatherapi


def test_active_providers_exclude_noaa() -> None:
    assert open_meteo.build_rows in run_weather_ingestion.ACTIVE_PROVIDERS
    assert weatherapi.build_rows in run_weather_ingestion.ACTIVE_PROVIDERS
    assert noaa.build_rows not in run_weather_ingestion.ACTIVE_PROVIDERS


def test_collect_provider_rows_continues_after_provider_failure() -> None:
    def ok_provider():
        return [
            {
                "provider": "open_meteo",
                "city_name": "Paris",
                "country": "FR",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "ingested_at": "2026-05-30T00:00:00Z",
                "payload": {},
            }
        ]

    def failing_provider():
        raise RuntimeError("missing key")

    rows, summaries = run_weather_ingestion.collect_provider_rows(
        [ok_provider, failing_provider]
    )

    assert len(rows) == 1
    assert [summary.status for summary in summaries] == ["success", "failed"]
    assert summaries[1].message == "missing key"
