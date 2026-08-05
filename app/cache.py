import json
import os
import logging

logger = logging.getLogger("cache")

_in_memory_cache = {}

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=1)
        client.ping()
        return client
    except Exception:
        return None

def cache_get(key: str):
    client = get_redis_client()
    if client:
        try:
            val = client.get(key)
            if val:
                return json.loads(val.decode("utf-8"))
        except Exception as e:
            logger.warning(f"Redis get failed for key {key}: {e}")
    
    return _in_memory_cache.get(key)

def cache_set(key: str, value: dict, expire_seconds: int = 300):
    client = get_redis_client()
    if client:
        try:
            client.setex(key, expire_seconds, json.dumps(value))
            return
        except Exception as e:
            logger.warning(f"Redis set failed for key {key}: {e}")
    
    _in_memory_cache[key] = value

def cache_delete(key: str):
    client = get_redis_client()
    if client:
        try:
            client.delete(key)
        except Exception:
            pass
    _in_memory_cache.pop(key, None)
