"""NoteIQ - AI-Powered Notes Application

NoteIQ is an AI-powered notes application that helps you create, organize,
and interact with your notes using artificial intelligence.
"""

__version__ = "1.0.0"
__author__ = "Himal Badu, AI Founder"

from noteiq.models import (
    Note,
    NoteCreate,
    NoteUpdate,
    SummarizeResponse,
    ActionsResponse,
    AskRequest,
    AskResponse,
    OutlineResponse
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
from noteiq.utils import logger, log_info, log_error, log_warning

__all__ = [
    # Models
    "Note",
    "NoteCreate",
    "NoteUpdate",
    "SummarizeResponse",
    "ActionsResponse",
    "AskRequest",
    "AskResponse",
    "OutlineResponse",
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
    # Utils
    "logger",
    "log_info",
    "log_error",
    "log_warning",
]