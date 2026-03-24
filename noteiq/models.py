"""
Pydantic models for NoteIQ
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid


class NotePriority(str, Enum):
    """Note priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Note(BaseModel):
    """Note model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique note identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    priority: NotePriority = Field(default=NotePriority.MEDIUM, description="Note priority")
    is_pinned: bool = Field(default=False, description="Whether note is pinned")
    is_archived: bool = Field(default=False, description="Whether note is archived")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate and sanitize tags"""
        if v is None:
            return []
        if isinstance(v, str):
            return [t.strip() for t in v.split(',') if t.strip()]
        return [t for t in v if t]
    
    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty"""
        if v and isinstance(v, str):
            return v.strip()
        return v
    
    @field_validator('content', mode='before')
    @classmethod
    def validate_content(cls, v):
        """Validate content is not empty"""
        if v and isinstance(v, str):
            return v.strip()
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Meeting Notes",
                "content": "Discussed Q1 goals and team expansion",
                "tags": ["work", "meeting"],
                "priority": "medium"
            }
        }
    )


class NoteCreate(BaseModel):
    """Model for creating a note"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    priority: NotePriority = Field(default=NotePriority.MEDIUM)
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate and sanitize tags"""
        if v is None:
            return []
        if isinstance(v, str):
            return [t.strip() for t in v.split(',') if t.strip()]
        return [t for t in v if t]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "New Note",
                "content": "Note content here",
                "tags": ["tag1", "tag2"],
                "priority": "high"
            }
        }
    )


class NoteUpdate(BaseModel):
    """Model for updating a note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    priority: Optional[NotePriority] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate and sanitize tags"""
        if v is None:
            return None
        if isinstance(v, str):
            return [t.strip() for t in v.split(',') if t.strip()]
        return [t for t in v if t]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "tags": ["new", "tags"]
            }
        }
    )


class NoteSearch(BaseModel):
    """Model for searching notes"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[NotePriority] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    summary: str
    original_length: Optional[int] = None
    summary_length: Optional[int] = None


class ActionsResponse(BaseModel):
    """Response model for action extraction"""
    action_items: List[str]
    count: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action_items": ["Create budget proposal", "Schedule team meeting"],
                "count": 2
            }
        }
    )


class AskRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What were the main topics discussed?"
            }
        }
    )


class AskResponse(BaseModel):
    """Response model for Q&A"""
    answer: str
    question: str
    confidence: Optional[float] = None


class OutlineResponse(BaseModel):
    """Response model for outline generation"""
    outline: List[str]
    sections: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "outline": ["Introduction", "Main Points", "Conclusion"],
                "sections": 3
            }
        }
    )


class NoteStats(BaseModel):
    """Statistics about notes"""
    total_notes: int
    pinned_notes: int
    archived_notes: int
    notes_by_priority: dict
    notes_by_tag: dict
    average_content_length: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    storage_status: str
    ai_status: str