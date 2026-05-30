import pytest
import requests
from ingestion import open_meteo, weatherapi
from ingestion.cities import FRENCH_CITIES


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


def test_open_meteo_rows_have_common_shape(monkeypatch) -> None:
    monkeypatch.setattr(open_meteo, "selected_cities", lambda: [FRENCH_CITIES["Paris"]])
    monkeypatch.setattr(
        open_meteo.requests,
        "get",
        lambda *args, **kwargs: DummyResponse({"daily": {"time": ["2026-05-30"]}}),
    )

    rows = open_meteo.build_rows()

    assert rows == [
        {
            "provider": "open_meteo",
            "city_name": "Paris",
            "country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "ingested_at": rows[0]["ingested_at"],
            "payload": {"daily": {"time": ["2026-05-30"]}},
        }
    ]


def test_weatherapi_rows_have_common_shape(monkeypatch) -> None:
    monkeypatch.setenv("WEATHERAPI_API_KEY", "test-key")
    monkeypatch.setattr(weatherapi, "selected_cities", lambda: [FRENCH_CITIES["Rennes"]])
    monkeypatch.setattr(
        weatherapi.requests,
        "get",
        lambda *args, **kwargs: DummyResponse({"forecast": {"forecastday": []}}),
    )

    rows = weatherapi.build_rows()

    assert rows == [
        {
            "provider": "weatherapi",
            "city_name": "Rennes",
            "country": "FR",
            "latitude": 48.1173,
            "longitude": -1.6778,
            "ingested_at": rows[0]["ingested_at"],
            "payload": {"forecast": {"forecastday": []}},
        }
    ]


def test_weatherapi_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("WEATHERAPI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="WEATHERAPI_API_KEY is required"):
        weatherapi.build_rows()


def test_weatherapi_skips_failed_city(monkeypatch) -> None:
    monkeypatch.setenv("WEATHERAPI_API_KEY", "test-key")
    monkeypatch.setattr(weatherapi, "selected_cities", lambda: [FRENCH_CITIES["Nice"]])

    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("slow response")

    monkeypatch.setattr(weatherapi.requests, "get", raise_timeout)

    assert weatherapi.build_rows() == []
