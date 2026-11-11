from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import health, rides
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="RideFlow ride-hailing platform API",
    version="1.0.0",
)

Instrumentator(
    excluded_handlers=["/metrics"],
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    rides.router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "application": "RideFlow",
        "version": "1.0.0",
        "documentation": "/docs",
    }
