import redis

from app.core.config import settings

r = redis.StrictRedis(
    host=settings.redis_settings.host,
    port=settings.redis_settings.port,
    # password=settings.redis_settings.password,
    decode_responses=True,
)

