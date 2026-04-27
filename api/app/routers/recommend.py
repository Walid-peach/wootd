import uuid
from datetime import date
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.core.storage import get_duckdb, gold_path
from app.engines.rules import WeatherSnapshot
from app.engines.rules import recommend as rules_recommend

router = APIRouter()


class Engine(StrEnum):
    rules = "rules"
    ml = "ml"


class OutfitOut(BaseModel):
    top: str
    bottom: str
    outer: str | None
    accessories: list[str]


class WeatherSnapshotOut(BaseModel):
    temp_min_c: float
    temp_max_c: float
    precip_probability: float
    wind_kmh: float
    uv_index: float


class RecommendationOut(BaseModel):
    recommendation_id: str
    city: str
    forecast_date: date
    engine: Engine
    model_version: str
    outfit: OutfitOut
    weather_snapshot: WeatherSnapshotOut
    explanation: str


@router.get("/recommend", response_model=RecommendationOut)
def get_recommendation(
    request: Request,
    city: Annotated[str, Query()],
    user_id: Annotated[str | None, Query()] = None,
    engine: Engine = Engine.rules,
    forecast_date: date = None,  # type: ignore[assignment]
) -> RecommendationOut:
    if forecast_date is None:
        forecast_date = date.today()

    con = get_duckdb()
    row = con.execute(
        f"""
        SELECT temp_min_c, temp_max_c, precip_probability, wind_kmh, uv_index
        FROM read_parquet('{gold_path("gold_daily_forecast")}')
        WHERE lower(city_name) = lower(?)
          AND forecast_date = ?
        LIMIT 1
        """,
        [city, forecast_date],
    ).fetchone()

    if row is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"No forecast found for {city} on {forecast_date}",
        )

    weather = WeatherSnapshot(
        temp_min_c=row[0],
        temp_max_c=row[1],
        precip_probability=row[2],
        wind_kmh=row[3],
        uv_index=row[4],
    )

    if engine == Engine.ml:
        outfit = request.app.state.ml_engine.recommend(weather, user_id)
        model_version = request.app.state.ml_engine.model_version
    else:
        outfit = rules_recommend(weather)
        model_version = "rules-v1"

    return RecommendationOut(
        recommendation_id=str(uuid.uuid4()),
        city=city,
        forecast_date=forecast_date,
        engine=engine,
        model_version=model_version,
        outfit=OutfitOut(
            top=outfit.top,
            bottom=outfit.bottom,
            outer=outfit.outer,
            accessories=outfit.accessories,
        ),
        weather_snapshot=WeatherSnapshotOut(
            temp_min_c=weather.temp_min_c,
            temp_max_c=weather.temp_max_c,
            precip_probability=weather.precip_probability,
            wind_kmh=weather.wind_kmh,
            uv_index=weather.uv_index,
        ),
        explanation=outfit.explanation,
    )
