"""
Rate limiting utilities for NoteIQ
Provides rate limiting for API endpoints and AI operations
"""
import time
from typing import Dict, Optional
from threading import Lock
from functools import wraps


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, max_calls: int = 10, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed per period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self._calls: Dict[str, list] = {}
        self._lock = Lock()
    
    def _cleanup_old_calls(self, key: str):
        """Remove calls outside the current period"""
        if key not in self._calls:
            return
        
        current_time = time.time()
        cutoff_time = current_time - self.period
        self._calls[key] = [
            call_time for call_time in self._calls[key]
            if call_time > cutoff_time
        ]
    
    def is_allowed(self, key: str = "default") -> bool:
        """
        Check if a call is allowed.
        
        Args:
            key: Identifier for the rate limit bucket
            
        Returns:
            True if allowed, False if rate limited
        """
        with self._lock:
            self._cleanup_old_calls(key)
            
            if key not in self._calls:
                self._calls[key] = []
            
            if len(self._calls[key]) < self.max_calls:
                self._calls[key].append(time.time())
                return True
            
            return False
    
    def get_remaining(self, key: str = "default") -> int:
        """
        Get remaining calls allowed in current period.
        
        Args:
            key: Identifier for the rate limit bucket
            
        Returns:
            Number of remaining calls
        """
        with self._lock:
            self._cleanup_old_calls(key)
            
            if key not in self._calls:
                return self.max_calls
            
            return max(0, self.max_calls - len(self._calls[key]))
    
    def get_reset_time(self, key: str = "default") -> float:
        """
        Get time until rate limit resets.
        
        Args:
            key: Identifier for the rate limit bucket
            
        Returns:
            Seconds until reset
        """
        with self._lock:
            self._cleanup_old_calls(key)
            
            if key not in self._calls or not self._calls[key]:
                return 0
            
            oldest_call = min(self._calls[key])
            return max(0, (oldest_call + self.period) - time.time())
    
    def reset(self, key: str = "default"):
        """
        Reset rate limit for a key.
        
        Args:
            key: Identifier for the rate limit bucket
        """
        with self._lock:
            if key in self._calls:
                del self._calls[key]
    
    def reset_all(self):
        """Reset all rate limits"""
        with self._lock:
            self._calls.clear()


def rate_limit(max_calls: int = 10, period: int = 60, key_func: Optional[callable] = None):
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        max_calls: Maximum calls allowed per period
        period: Time period in seconds
        key_func: Function to generate rate limit key from args/kwargs
        
    Returns:
        Decorated function
    """
    _limiter = RateLimiter(max_calls=max_calls, period=period)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = func.__name__
            
            # Check rate limit
            if not _limiter.is_allowed(key):
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Max {max_calls} calls per {period} seconds."
                )
            
            return func(*args, **kwargs)
        
        # Expose limiter for configuration
        wrapper.limiter = _limiter
        return wrapper
    
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


# Global rate limiters for different services
api_rate_limiter = RateLimiter(max_calls=100, period=60)  # 100 requests per minute
ai_rate_limiter = RateLimiter(max_calls=20, period=60)  # 20 AI requests per minute


def check_api_rate_limit(client_id: str = "default") -> bool:
    """Check if API request is allowed"""
    return api_rate_limiter.is_allowed(client_id)


def check_ai_rate_limit(client_id: str = "default") -> bool:
    """Check if AI request is allowed"""
    return ai_rate_limiter.is_allowed(client_id)
