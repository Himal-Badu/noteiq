"""
Custom exceptions for NoteIQ
"""


class NoteIQException(Exception):
    """Base exception for NoteIQ"""
    pass


class NoteNotFoundError(NoteIQException):
    """Raised when a note is not found"""
    
    def __init__(self, note_id: str):
        self.note_id = note_id
        super().__init__(f"Note with ID '{note_id}' not found")


class ValidationError(NoteIQException):
    """Raised when validation fails"""
    pass


class AIError(NoteIQException):
    """Raised when AI operation fails"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"AI operation failed: {message}")


class StorageError(NoteIQException):
    """Raised when storage operation fails"""
    pass


class ConfigurationError(NoteIQException):
    """Raised when configuration is invalid"""
    pass


class APIKeyError(NoteIQException):
    """Raised when API key is missing or invalid"""
    
    def __init__(self, service: str = "OpenAI"):
        self.service = service
        super().__init__(f"{service} API key not configured. Please set the API key.")


# Exception handler functions
def handle_note_not_found(note_id: str) -> None:
    """Handle note not found error"""
    from noteiq.utils import log_error
    log_error(f"Note not found: {note_id}")


def handle_validation_error(errors: list) -> None:
    """Handle validation errors"""
    from noteiq.utils import log_error
    for error in errors:
        log_error(f"Validation error: {error}")


def handle_ai_error(error: Exception) -> None:
    """Handle AI errors"""
    from noteiq.utils import log_error
    log_error(f"AI error: {str(error)}", exc_info=True)


def handle_storage_error(error: Exception) -> None:
    """Handle storage errors"""
    from noteiq.utils import log_error
    log_error(f"Storage error: {str(error)}", exc_info=True)