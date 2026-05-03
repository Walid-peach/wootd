from app.engines.rules import WeatherSnapshot, recommend


def test_recommendation_adds_cold_rain_and_uv_accessories() -> None:
    outfit = recommend(
        WeatherSnapshot(
            temp_min_c=2,
            temp_max_c=8,
            precip_probability=0.8,
            wind_kmh=12,
            uv_index=7,
        )
    )

    assert outfit.top == "heavy sweater"
    assert outfit.outer == "coat"
    assert outfit.accessories == ["umbrella", "sunglasses", "sunscreen"]
    assert "Cold day" in outfit.explanation
