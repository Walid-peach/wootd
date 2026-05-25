from ingestion.common import configured_cities


def test_configured_cities_splits_env_value(monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_CITIES", "Paris, London,,Tokyo ")

    assert configured_cities() == ["Paris", "London", "Tokyo"]
