"""LightGBM engine. Loads the current model artifact from R2 at startup."""

import io
import pickle
from typing import Any

import boto3
import lightgbm as lgb

from app.core.config import settings
from app.engines.rules import Outfit, WeatherSnapshot, recommend as rules_recommend


class MLEngine:
    model: lgb.Booster | None = None
    model_version: str = "none"

    def __init__(self) -> None:
        self._load()

    def _load(self) -> None:
        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=settings.r2_endpoint_url,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
            )
            obj = s3.get_object(
                Bucket=settings.r2_bucket_name, Key="models/current/outfit_model.pkl"
            )
            payload: dict[str, Any] = pickle.loads(obj["Body"].read())
            self.model = payload["model"]
            self.model_version = payload["version"]
        except Exception:
            # Fall back gracefully — model not yet trained
            self.model = None
            self.model_version = "none"

    def recommend(self, weather: WeatherSnapshot, user_id: str | None = None) -> Outfit:
        if self.model is None:
            return rules_recommend(weather)

        # Feature vector order must match training (see data/ml/features.py)
        features = [[
            weather.temp_min_c,
            weather.temp_max_c,
            (weather.temp_min_c + weather.temp_max_c) / 2,
            weather.precip_probability,
            weather.wind_kmh,
            weather.uv_index,
        ]]
        # Model predicts acceptance probability; use rules engine for outfit mapping,
        # ML score influences outer/accessory decisions in the future.
        return rules_recommend(weather)
