import time

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthOut(BaseModel):
    status: str
    model_version: str
    uptime_seconds: float


@router.get("/health", response_model=HealthOut)
def health(request: Request) -> HealthOut:
    return HealthOut(
        status="ok",
        model_version=request.app.state.ml_engine.model_version,
        uptime_seconds=round(time.time() - request.app.state.start_time, 1),
    )
