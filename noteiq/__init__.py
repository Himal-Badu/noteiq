"""NoteIQ - AI-Powered Notes Application

NoteIQ is an AI-powered notes application that helps you create, organize,
and interact with your notes using artificial intelligence.

Built by Himal Badu, AI Founder
"""

__version__ = "1.1.0"
__author__ = "Himal Badu, AI Founder"

from noteiq.models import (
    Note,
    NoteCreate,
    NoteUpdate,
    NoteSearch,
    NoteFilter,
    NoteSort,
    NoteCategory,
    NotePriority,
    SummarizeResponse,
    ActionsResponse,
    AskRequest,
    AskResponse,
    OutlineResponse,
    NoteStats,
    HealthResponse,
    NoteAnalysis,
    BulkOperation,
    BulkOperationResult
)
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes
from noteiq.config import Config, get_config, update_config
from noteiq.exceptions import (
    NoteIQException,
    NoteNotFoundError,
    ValidationError,
    AIError,
    StorageError,
    ConfigurationError,
    APIKeyError
)
from noteiq.validators import NoteValidator, APIKeyValidator
from noteiq.cache import Cache, ai_cache, cache_ai_response, get_ai_response, clear_ai_cache
from noteiq.rate_limit import RateLimiter, RateLimitExceeded, rate_limit, api_rate_limiter, ai_rate_limiter
from noteiq.utils import logger, log_info, log_error, log_warning

__all__ = [
    # Models
    "Note",
    "NoteCreate",
    "NoteUpdate",
    "NoteSearch",
    "NoteFilter",
    "NoteSort",
    "NoteCategory",
    "NotePriority",
    "SummarizeResponse",
    "ActionsResponse",
    "AskRequest",
    "AskResponse",
    "OutlineResponse",
    "NoteStats",
    "HealthResponse",
    "NoteAnalysis",
    "BulkOperation",
    "BulkOperationResult",
    # Storage
    "NoteStorage",
    # AI
    "AINotes",
    # Config
    "Config",
    "get_config",
    "update_config",
    # Exceptions
    "NoteIQException",
    "NoteNotFoundError",
    "ValidationError",
    "AIError",
    "StorageError",
    "ConfigurationError",
    "APIKeyError",
    # Validators
    "NoteValidator",
    "APIKeyValidator",
    # Cache
    "Cache",
    "ai_cache",
    "cache_ai_response",
    "get_ai_response",
    "clear_ai_cache",
    # Rate Limit
    "RateLimiter",
    "RateLimitExceeded",
    "rate_limit",
    "api_rate_limiter",
    "ai_rate_limiter",
    # Utils
    "logger",
    "log_info",
    "log_error",
    "log_warning",
]
