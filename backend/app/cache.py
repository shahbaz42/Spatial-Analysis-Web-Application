"""Redis cache manager for the application"""

import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class CacheManager:
    """Redis cache manager with async support"""
    
    _redis_client: Optional[redis.Redis] = None
    
    @classmethod
    async def init_redis(cls):
        """Initialize Redis connection pool"""
        if not settings.REDIS_ENABLED:
            print("Redis caching is disabled")
            return
        
        try:
            cls._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            await cls._redis_client.ping()
            print(f"Redis connected successfully at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            print("Continuing without cache...")
            cls._redis_client = None
    
    @classmethod
    async def close_redis(cls):
        """Close Redis connection"""
        if cls._redis_client:
            await cls._redis_client.close()
            print("Redis connection closed")
    
    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        """Get Redis client instance"""
        return cls._redis_client
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if Redis is enabled and connected"""
        return cls._redis_client is not None and settings.REDIS_ENABLED
    
    @classmethod
    def generate_cache_key(cls, prefix: str, **kwargs) -> str:
        """
        Generate a unique cache key based on prefix and parameters
        
        Args:
            prefix: Key prefix (e.g., 'sites', 'statistics')
            **kwargs: Key-value pairs to include in the key
        
        Returns:
            Unique cache key string
        """
        # Sort kwargs to ensure consistent key generation
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        if not cls.is_enabled():
            return None
        
        try:
            value = await cls._redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    @classmethod
    async def set(cls, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: from settings)
        
        Returns:
            True if successful, False otherwise
        """
        if not cls.is_enabled():
            return False
        
        try:
            ttl = ttl or settings.REDIS_TTL
            serialized_value = json.dumps(value, default=str)
            await cls._redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if successful, False otherwise
        """
        if not cls.is_enabled():
            return False
        
        try:
            await cls._redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., 'sites:*')
        
        Returns:
            Number of keys deleted
        """
        if not cls.is_enabled():
            return 0
        
        try:
            keys = []
            async for key in cls._redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await cls._redis_client.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    @classmethod
    async def clear_all(cls) -> bool:
        """
        Clear all cache entries
        
        Returns:
            True if successful, False otherwise
        """
        if not cls.is_enabled():
            return False
        
        try:
            await cls._redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


def cache_response(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache API response
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (optional)
    
    Usage:
        @cache_response(prefix="sites", ttl=300)
        async def get_sites(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            # Filter out non-serializable arguments like db session
            cacheable_kwargs = {
                k: v for k, v in kwargs.items() 
                if k not in ['db', 'request', 'response'] and v is not None
            }
            
            cache_key = CacheManager.generate_cache_key(prefix, **cacheable_kwargs)
            
            # Try to get from cache
            cached_result = await CacheManager.get(cache_key)
            if cached_result is not None:
                print(f"Cache HIT: {cache_key}")
                return cached_result
            
            # Cache miss - execute function
            print(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await CacheManager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


async def invalidate_cache(prefix: str):
    """
    Invalidate all cache entries with given prefix
    
    Args:
        prefix: Cache key prefix to invalidate
    """
    pattern = f"{prefix}:*"
    deleted = await CacheManager.delete_pattern(pattern)
    print(f"Invalidated {deleted} cache entries with prefix '{prefix}'")
