import aioredis
from app.core.config import settings

redis = aioredis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    decode_responses=True
)

async def get_cache(key: str):
    return await redis.get(key)

async def set_cache(key: str, value: str, expire: int = settings.redis_expire):
    await redis.set(key, value, ex=expire)
