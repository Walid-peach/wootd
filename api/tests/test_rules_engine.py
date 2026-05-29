from app.engines.rules import WeatherSnapshot, recommend


def test_rules_engine_recommends_umbrella_for_likely_rain() -> None:
    outfit = recommend(
        WeatherSnapshot(
            temp_min_c=10,
            temp_max_c=14,
            precip_probability=0.8,
            wind_kmh=12,
            uv_index=2,
        )
    )

    assert outfit.outer == "light jacket"
    assert "umbrella" in outfit.accessories
