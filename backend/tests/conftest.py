import os
from urllib.parse import urlparse

import pytest
from redis import Redis
from sqlalchemy import delete

database_url = os.environ.get("DATABASE_URL", "")
redis_url = os.environ.get("REDIS_URL", "")

if urlparse(database_url).path != "/rideflow_test":
    raise RuntimeError(
        "Tests must use the rideflow_test PostgreSQL database."
    )

if urlparse(redis_url).path != "/1":
    raise RuntimeError(
        "Tests must use Redis database 1."
    )

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.ride import Ride


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_test_data():
    redis_client = Redis.from_url(redis_url)

    with SessionLocal() as db:
        db.execute(delete(Ride))
        db.commit()

    redis_client.flushdb()

    yield

    with SessionLocal() as db:
        db.execute(delete(Ride))
        db.commit()

    redis_client.flushdb()
    redis_client.close()
