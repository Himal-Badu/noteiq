from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class SummarizeResponse(BaseModel):
    summary: str


class ActionsResponse(BaseModel):
    action_items: List[str]


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class OutlineResponse(BaseModel):
    outline: List[str]