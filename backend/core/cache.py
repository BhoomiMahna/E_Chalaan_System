import hashlib
import json
from functools import wraps
import redis
from core.config import Config
import logging

logger = logging.getLogger(__name__)

# Attempt to connect to Redis; if it fails, provide a fallback dummy cache
try:
    redis_client = redis.from_url(Config.REDIS_URL)
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available ({e}). Caching is disabled.")
    REDIS_AVAILABLE = False


def cache(ttl_seconds=Config.CACHE_TTL_SECONDS):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return func(*args, **kwargs)

            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            
            try:
                cached = redis_client.get(key_hash)
                if cached:
                    return json.loads(cached)
                
                result = func(*args, **kwargs)
                redis_client.setex(key_hash, ttl_seconds, json.dumps(result))
                return result
            except Exception as e:
                logger.error(f"Redis cache error: {e}")
                return func(*args, **kwargs)
        return wrapper
    return decorator
