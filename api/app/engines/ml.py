"""Placeholder ML engine.

The Snowflake/dbt architecture exposes model-ready features in
MARTS.FCT_RECOMMENDATION_FEATURES. Training and model serving can be added
later without changing the current rule-based API contract.
"""

from app.engines.rules import Outfit, WeatherSnapshot
from app.engines.rules import recommend as rules_recommend


class MLEngine:
    model_version: str = "rules-fallback"

    def recommend(self, weather: WeatherSnapshot, user_id: str | None = None) -> Outfit:
        return rules_recommend(weather)
