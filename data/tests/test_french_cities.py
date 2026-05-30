from ingestion.cities import FRENCH_CITIES, selected_french_cities


def test_french_cities_are_fr_only() -> None:
    assert FRENCH_CITIES
    assert {city["country"] for city in FRENCH_CITIES.values()} == {"FR"}


def test_selected_french_cities_respects_default_cities(monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_CITIES", "Paris, Rennes, Unknown")

    assert [city["name"] for city in selected_french_cities()] == ["Paris", "Rennes"]
