"""
Enhanced Pydantic models for NoteIQ
Includes additional models for advanced features
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class NotePriority(str, Enum):
    """Note priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NoteCategory(str, Enum):
    """Note categories for organization"""
    GENERAL = "general"
    WORK = "work"
    PERSONAL = "personal"
    IDEAS = "ideas"
    PROJECT = "project"
    MEETING = "meeting"
    LEARNING = "learning"
    TODO = "todo"


class Note(BaseModel):
    """Note model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique note identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    category: NoteCategory = Field(default=NoteCategory.GENERAL, description="Note category")
    priority: NotePriority = Field(default=NotePriority.MEDIUM, description="Note priority")
    is_pinned: bool = Field(default=False, description="Whether note is pinned")
    is_archived: bool = Field(default=False, description="Whether note is archived")
    is_favorite: bool = Field(default=False, description="Whether note is favorite")
    color: Optional[str] = Field(default=None, description="Note color hex code")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    due_date: Optional[datetime] = Field(default=None, description="Optional due date")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
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
    
    @field_validator('color', mode='before')
    @classmethod
    def validate_color(cls, v):
        """Validate color format"""
        if v is None:
            return None
        if isinstance(v, str) and v.startswith('#') and len(v) in [4, 7]:
            return v
        return None
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Meeting Notes",
                "content": "Discussed Q1 goals and team expansion",
                "tags": ["work", "meeting"],
                "category": "meeting",
                "priority": "medium",
                "color": "#FF5733"
            }
        }
    )


class NoteCreate(BaseModel):
    """Model for creating a note"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    category: NoteCategory = Field(default=NoteCategory.GENERAL)
    priority: NotePriority = Field(default=NotePriority.MEDIUM)
    color: Optional[str] = None
    due_date: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate and sanitize tags"""
        if v is None:
            return []
        if isinstance(v, str):
            return [t.strip() for t in v.split(',') if t.strip()]
        return [t for t in v if t]
    
    @field_validator('color', mode='before')
    @classmethod
    def validate_color(cls, v):
        """Validate color format"""
        if v is None:
            return None
        if isinstance(v, str) and v.startswith('#') and len(v) in [4, 7]:
            return v
        return None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "New Note",
                "content": "Note content here",
                "tags": ["tag1", "tag2"],
                "category": "work",
                "priority": "high"
            }
        }
    )


class NoteUpdate(BaseModel):
    """Model for updating a note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    category: Optional[NoteCategory] = None
    priority: Optional[NotePriority] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    color: Optional[str] = None
    due_date: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate and sanitize tags"""
        if v is None:
            return None
        if isinstance(v, str):
            return [t.strip() for t in v.split(',') if t.strip()]
        return [t for t in v if t]
    
    @field_validator('color', mode='before')
    @classmethod
    def validate_color(cls, v):
        """Validate color format"""
        if v is None:
            return None
        if isinstance(v, str) and v.startswith('#') and len(v) in [4, 7]:
            return v
        return None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "tags": ["new", "tags"],
                "priority": "high",
                "is_favorite": True
            }
        }
    )


class NoteSearch(BaseModel):
    """Model for searching notes"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[NoteCategory] = None
    priority: Optional[NotePriority] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class NoteFilter(BaseModel):
    """Model for filtering notes"""
    tags: Optional[List[str]] = None
    categories: Optional[List[NoteCategory]] = None
    priorities: Optional[List[NotePriority]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class NoteSort(BaseModel):
    """Model for sorting notes"""
    field: str = Field(default="updated_at")
    order: str = Field(default="desc")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "created_at",
                "order": "desc"
            }
        }
    )


class NoteExport(BaseModel):
    """Model for note export"""
    notes: List[Note]
    export_date: datetime
    export_format: str
    total_count: int


class NoteImport(BaseModel):
    """Model for note import"""
    notes: List[Dict[str, Any]]
    import_date: datetime
    source: str


class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    summary: str
    original_length: Optional[int] = None
    summary_length: Optional[int] = None
    key_points: List[str] = Field(default_factory=list)


class ActionsResponse(BaseModel):
    """Response model for action extraction"""
    action_items: List[str]
    count: int = 0
    completed_count: int = 0
    overdue_count: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action_items": ["Create budget proposal", "Schedule team meeting"],
                "count": 2,
                "completed_count": 0,
                "overdue_count": 0
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
    sources: List[str] = Field(default_factory=list)


class OutlineResponse(BaseModel):
    """Response model for outline generation"""
    outline: List[str]
    sections: int = 0
    depth: int = Field(default=2)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "outline": ["Introduction", "Main Points", "Conclusion"],
                "sections": 3,
                "depth": 2
            }
        }
    )


class NoteStats(BaseModel):
    """Statistics about notes"""
    total_notes: int
    active_notes: int
    pinned_notes: int
    archived_notes: int
    favorite_notes: int
    notes_by_priority: Dict[str, int]
    notes_by_category: Dict[str, int]
    notes_by_tag: Dict[str, int]
    average_content_length: float
    notes_created_today: int
    notes_updated_today: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    storage_status: str
    ai_status: str
    uptime: Optional[float] = None


class NoteAnalysis(BaseModel):
    """Comprehensive note analysis"""
    summary: str
    key_points: List[str]
    action_items: List[str]
    outline: List[str]
    suggested_tags: List[str]
    keywords: List[str]
    sentiment: Optional[str] = None
    reading_time: Optional[int] = None


class BulkOperation(BaseModel):
    """Model for bulk operations"""
    note_ids: List[str]
    operation: str
    params: Optional[Dict[str, Any]] = None


class BulkOperationResult(BaseModel):
    """Result of bulk operation"""
    success: bool
    processed_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)
