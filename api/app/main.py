import time

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.engines.ml import MLEngine
from app.routers import feedback, health, recommend

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.api_env)

app = FastAPI(title="WOOTD API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.start_time = time.time()
app.state.ml_engine = MLEngine()

app.include_router(recommend.router)
app.include_router(feedback.router)
app.include_router(health.router)
