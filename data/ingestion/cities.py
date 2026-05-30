"""Central city configuration for the active French weather providers."""

from __future__ import annotations

from typing import TypedDict

from .common import configured_cities


class CityConfig(TypedDict):
    name: str
    country: str
    lat: float
    lon: float


FRENCH_CITIES: dict[str, CityConfig] = {
    "Paris": {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
    "Rennes": {"name": "Rennes", "country": "FR", "lat": 48.1173, "lon": -1.6778},
    "Lyon": {"name": "Lyon", "country": "FR", "lat": 45.7640, "lon": 4.8357},
    "Marseille": {"name": "Marseille", "country": "FR", "lat": 43.2965, "lon": 5.3698},
    "Toulouse": {"name": "Toulouse", "country": "FR", "lat": 43.6047, "lon": 1.4442},
    "Bordeaux": {"name": "Bordeaux", "country": "FR", "lat": 44.8378, "lon": -0.5792},
    "Lille": {"name": "Lille", "country": "FR", "lat": 50.6292, "lon": 3.0573},
    "Nantes": {"name": "Nantes", "country": "FR", "lat": 47.2184, "lon": -1.5536},
    "Strasbourg": {"name": "Strasbourg", "country": "FR", "lat": 48.5734, "lon": 7.7521},
    "Nice": {"name": "Nice", "country": "FR", "lat": 43.7102, "lon": 7.2620},
    "Montpellier": {"name": "Montpellier", "country": "FR", "lat": 43.6119, "lon": 3.8772},
    "Grenoble": {"name": "Grenoble", "country": "FR", "lat": 45.1885, "lon": 5.7245},
}


def selected_french_cities() -> list[CityConfig]:
    configured = set(configured_cities())
    return [city for name, city in FRENCH_CITIES.items() if name in configured]
