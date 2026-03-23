"""NoteIQ - AI-Powered Notes Application"""

__version__ = "1.0.0"
__author__ = "Himal Badu, AI Founder"

from noteiq.models import Note, NoteCreate, NoteUpdate
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes

__all__ = ["Note", "NoteCreate", "NoteUpdate", "NoteStorage", "AINotes"]