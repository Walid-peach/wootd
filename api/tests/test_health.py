import time

from app.routers.health import router
from fastapi import FastAPI
from fastapi.testclient import TestClient


class StubMLEngine:
    model_version = "test-model"


def test_health_endpoint_returns_model_version_and_uptime() -> None:
    app = FastAPI()
    app.state.ml_engine = StubMLEngine()
    app.state.start_time = time.time() - 5
    app.include_router(router)

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_version"] == "test-model"
    assert body["uptime_seconds"] >= 0
