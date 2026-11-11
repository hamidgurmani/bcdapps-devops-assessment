import json
import logging

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


logger = logging.getLogger(__name__)

CACHE_PREFIX = "rideflow:"
CACHE_TTL_SECONDS = 60

redis_client = Redis.from_url(
    get_settings().redis_url,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def get_cached(key: str):
    try:
        value = redis_client.get(f"{CACHE_PREFIX}{key}")

        if value is None:
            return None

        return json.loads(value)

    except (RedisError, json.JSONDecodeError):
        logger.warning("Redis cache read failed for key: %s", key)
        return None


def set_cached(key: str, value) -> None:
    try:
        redis_client.set(
            f"{CACHE_PREFIX}{key}",
            json.dumps(value),
            ex=CACHE_TTL_SECONDS,
        )
    except (RedisError, TypeError):
        logger.warning("Redis cache write failed for key: %s", key)


def invalidate_ride_cache(ride_id: int) -> None:
    try:
        keys = [
            f"{CACHE_PREFIX}ride:{ride_id}",
            *redis_client.scan_iter(
                match=f"{CACHE_PREFIX}rides:list:*",
                count=100,
            ),
        ]

        if keys:
            redis_client.delete(*keys)

    except RedisError:
        logger.warning("Redis cache invalidation failed for ride: %s", ride_id)
