"""
Caching utilities for NoteIQ
Provides in-memory caching for AI responses and frequently accessed data
"""
import time
from typing import Any, Optional, Dict, Callable
from functools import wraps
from threading import Lock


class Cache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = {
                "value": value,
                "expires_at": time.time() + ttl,
                "created_at": time.time()
            }
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def cleanup(self):
        """Remove expired entries"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def size(self) -> int:
        """Get number of cached entries"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> list:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_func: Function to generate cache key from args/kwargs
        
    Returns:
        Decorated function
    """
    _cache = Cache(default_ttl=ttl)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        # Expose cache for manual manipulation
        wrapper.cache = _cache
        return wrapper
    
    return decorator


# Global cache instance for AI responses
ai_cache = Cache(default_ttl=600)  # 10 minutes default for AI


def cache_ai_response(key: str, value: Any, ttl: int = 600):
    """Cache an AI response"""
    ai_cache.set(key, value, ttl)


def get_ai_response(key: str) -> Optional[Any]:
    """Get cached AI response"""
    return ai_cache.get(key)


def clear_ai_cache():
    """Clear all AI cached responses"""
    ai_cache.clear()
