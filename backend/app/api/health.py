from fastapi import APIRouter, HTTPException
from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


router = APIRouter(tags=["Health"])


@router.get("/health/live")
def liveness():
    return {"status": "alive"}


@router.get("/health/ready")
def readiness():
    checks = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["postgresql"] = "healthy"
    except Exception:
        checks["postgresql"] = "unavailable"

    try:
        client = Redis.from_url(
            get_settings().redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        client.close()
        checks["redis"] = "healthy"
    except Exception:
        checks["redis"] = "unavailable"

    if any(value != "healthy" for value in checks.values()):
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": checks},
        )

    return {"status": "ready", "checks": checks}
