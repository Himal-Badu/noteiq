import os
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from noteiq.models import (
    Note, NoteCreate, NoteUpdate, NoteFilter, NoteSort,
    SummarizeResponse, ActionsResponse, AskRequest, AskResponse, OutlineResponse,
    NoteStats, HealthResponse, NoteCategory, NotePriority, BulkOperation, BulkOperationResult
)
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes
from noteiq.exceptions import APIKeyError, AIError, NoteNotFoundError, ValidationError
from noteiq.utils import logger, log_info, log_error
from noteiq.cache import ai_cache
from noteiq.rate_limit import check_ai_rate_limit, check_api_rate_limit


# Initialize storage
storage = NoteStorage()

# Create FastAPI app
app = FastAPI(
    title="NoteIQ API",
    description="AI-Powered Notes API - Create, organize, and interact with notes using AI",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    log_info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    log_info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# Exception handlers
@app.exception_handler(NoteNotFoundError)
async def note_not_found_handler(request: Request, exc: NoteNotFoundError):
    """Handle NoteNotFoundError"""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(AIError)
async def ai_error_handler(request: Request, exc: AIError):
    """Handle AIError"""
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)}
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle ValidationError"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


def get_ai() -> AINotes:
    """Dependency to get AI instance"""
    try:
        # Check rate limit
        if not check_ai_rate_limit():
            raise HTTPException(
                status_code=429,
                detail="AI rate limit exceeded. Please try again later."
            )
        return AINotes()
    except APIKeyError:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable. Please configure OPENAI_API_KEY."
        )


@app.get("/", response_model=dict)
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NoteIQ API",
        "version": "1.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/version", response_model=dict)
def get_version():
    """Get API version information"""
    return {
        "version": "1.1.0",
        "api_version": "v1",
        "features": {
            "ai_summarization": True,
            "action_extraction": True,
            "qa": True,
            "outline_generation": True,
            "tag_suggestion": True,
            "sentiment_analysis": True,
            "question_generation": True,
            "caching": True,
            "rate_limiting": True
        }
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    # Check storage
    storage_status = "healthy"
    try:
        storage.get_all()
    except Exception:
        storage_status = "unhealthy"
    
    # Check AI
    ai_status = "disabled"
    if os.getenv("OPENAI_API_KEY"):
        ai_status = "enabled"
    
    return HealthResponse(
        status="healthy" if storage_status == "healthy" else "degraded",
        version="1.1.0",
        timestamp=datetime.utcnow(),
        storage_status=storage_status,
        ai_status=ai_status
    )


@app.get("/api/cache/stats")
def cache_stats():
    """Get cache statistics"""
    return {
        "size": ai_cache.size(),
        "keys": ai_cache.keys()[:10],  # First 10 keys
        "default_ttl": ai_cache.default_ttl
    }


@app.post("/api/cache/clear")
def clear_cache():
    """Clear AI cache"""
    ai_cache.clear()
    return {"message": "Cache cleared successfully"}


@app.post("/api/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    """Create a new note."""
    try:
        log_info(f"Creating note: {note.title}")
        
        # Create note
        new_note = Note(
            title=note.title,
            content=note.content,
            tags=note.tags,
            category=note.category,
            priority=note.priority,
            color=note.color,
            due_date=note.due_date
        )
        
        return storage.create(new_note)
        
    except Exception as e:
        log_error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create note")


@app.get("/api/notes", response_model=List[Note])
def list_notes(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    category: Optional[NoteCategory] = Query(None, description="Filter by category"),
    priority: Optional[NotePriority] = Query(None, description="Filter by priority"),
    include_archived: bool = Query(False, description="Include archived notes"),
    favorites: bool = Query(False, description="Show favorites only"),
    limit: int = Query(50, ge=1, le=100, description="Max notes to return"),
    offset: int = Query(0, ge=0, description="Number of notes to skip")
):
    """List all notes, optionally filtered."""
    try:
        notes = storage.get_all(tag=tag, include_archived=include_archived)
        
        # Filter by category
        if category:
            notes = [n for n in notes if n.category == category]
        
        # Filter by priority
        if priority:
            notes = [n for n in notes if n.priority == priority]
        
        # Filter favorites
        if favorites:
            notes = [n for n in notes if n.is_favorite]
        
        # Apply pagination
        return notes[offset:offset + limit]
        
    except Exception as e:
        log_error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list notes")


@app.get("/api/notes/stats", response_model=NoteStats)
def get_stats():
    """Get note statistics"""
    try:
        return storage.get_stats()
    except Exception as e:
        log_error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.get("/api/notes/count", response_model=dict)
def get_note_count():
    """Get total note count"""
    try:
        notes = storage.get_all()
        return {
            "total": len(notes),
            "active": len([n for n in notes if not n.is_archived]),
            "archived": len([n for n in notes if n.is_archived]),
            "pinned": len([n for n in notes if n.is_pinned]),
            "favorites": len([n for n in notes if n.is_favorite])
        }
    except Exception as e:
        log_error(f"Error getting count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get note count")


@app.get("/api/tags", response_model=dict)
def get_all_tags():
    """Get all unique tags"""
    try:
        tags = storage.get_all_tags()
        return {"tags": tags, "count": len(tags)}
    except Exception as e:
        log_error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tags")


@app.get("/api/categories", response_model=dict)
def get_all_categories():
    """Get all note categories"""
    try:
        categories = storage.get_all_categories()
        return {
            "categories": [c.value for c in categories],
            "count": len(categories)
        }
    except Exception as e:
        log_error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@app.get("/api/notes/search", response_model=List[Note])
def search_notes(
    q: str = Query(..., description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    category: Optional[NoteCategory] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search notes by query and filters"""
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        results = storage.search(q, tags=tag_list)
        
        if category:
            results = [n for n in results if n.category == category]
        
        return results[:limit]
    except Exception as e:
        log_error(f"Error searching notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to search notes")


@app.get("/api/notes/filter", response_model=List[Note])
def filter_notes(
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    priorities: Optional[str] = Query(None, description="Comma-separated priorities"),
    is_pinned: Optional[bool] = Query(None, description="Filter by pinned status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archived status"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    limit: int = Query(50, ge=1, le=100)
):
    """Filter notes with advanced options"""
    try:
        filter_params = NoteFilter(
            tags=[t.strip() for t in tags.split(",")] if tags else None,
            categories=[NoteCategory(c.strip()) for c in categories.split(",")] if categories else None,
            priorities=[NotePriority(p.strip()) for p in priorities.split(",")] if priorities else None,
            is_pinned=is_pinned,
            is_archived=is_archived,
            is_favorite=is_favorite
        )
        
        results = storage.filter_notes(filter_params)
        return results[:limit]
    except Exception as e:
        log_error(f"Error filtering notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter notes")


@app.get("/api/notes/favorites", response_model=List[Note])
def get_favorites(limit: int = Query(50, ge=1, le=100)):
    """Get favorite notes"""
    try:
        return storage.get_favorites()[:limit]
    except Exception as e:
        log_error(f"Error getting favorites: {e}")
        raise HTTPException(status_code=500, detail="Failed to get favorites")


@app.get("/api/notes/due", response_model=List[Note])
def get_due_notes(overdue: bool = Query(False, description="Show overdue only")):
    """Get notes with due dates"""
    try:
        if overdue:
            return storage.get_overdue_notes()
        return storage.get_due_notes()
    except Exception as e:
        log_error(f"Error getting due notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get due notes")


@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    """Get a specific note by ID."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error getting note: {e}")
        raise HTTPException(status_code=500, detail="Failed to get note")


@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: str, note_update: NoteUpdate):
    """Update an existing note."""
    try:
        existing = storage.get_by_id(note_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Apply updates
        if note_update.title is not None:
            existing.title = note_update.title
        if note_update.content is not None:
            existing.content = note_update.content
        if note_update.tags is not None:
            existing.tags = note_update.tags
        if note_update.category is not None:
            existing.category = note_update.category
        if note_update.priority is not None:
            existing.priority = note_update.priority
        if note_update.is_pinned is not None:
            existing.is_pinned = note_update.is_pinned
        if note_update.is_archived is not None:
            existing.is_archived = note_update.is_archived
        if note_update.is_favorite is not None:
            existing.is_favorite = note_update.is_favorite
        if note_update.color is not None:
            existing.color = note_update.color
        if note_update.due_date is not None:
            existing.due_date = note_update.due_date
        
        return storage.update(note_id, existing)
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error updating note: {e}")
        raise HTTPException(status_code=500, detail="Failed to update note")


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str):
    """Delete a note."""
    try:
        success = storage.delete(note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note deleted successfully", "note_id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")


@app.post("/api/notes/{note_id}/pin")
def pin_note(note_id: str):
    """Pin a note"""
    try:
        note = storage.pin(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note pinned", "note_id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error pinning note: {e}")
        raise HTTPException(status_code=500, detail="Failed to pin note")


@app.post("/api/notes/{note_id}/unpin")
def unpin_note(note_id: str):
    """Unpin a note"""
    try:
        note = storage.unpin(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note unpinned", "note_id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error unpinning note: {e}")
        raise HTTPException(status_code=500, detail="Failed to unpin note")


@app.post("/api/notes/{note_id}/favorite")
def favorite_note(note_id: str):
    """Toggle favorite status"""
    try:
        note = storage.toggle_favorite(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note favorited", "note_id": note_id, "is_favorite": note.is_favorite}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error favoriting note: {e}")
        raise HTTPException(status_code=500, detail="Failed to favorite note")


@app.post("/api/notes/{note_id}/archive")
def archive_note(note_id: str):
    """Archive a note"""
    try:
        note = storage.archive(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note archived", "note_id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error archiving note: {e}")
        raise HTTPException(status_code=500, detail="Failed to archive note")


@app.post("/api/notes/{note_id}/unarchive")
def unarchive_note(note_id: str):
    """Unarchive a note"""
    try:
        note = storage.unarchive(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note unarchived", "note_id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error unarchiving note: {e}")
        raise HTTPException(status_code=500, detail="Failed to unarchive note")


@app.post("/api/notes/{note_id}/duplicate")
def duplicate_note(note_id: str):
    """Duplicate a note"""
    try:
        new_note = storage.duplicate_note(note_id)
        if not new_note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note duplicated", "original_id": note_id, "new_id": new_note.id}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error duplicating note: {e}")
        raise HTTPException(status_code=500, detail="Failed to duplicate note")


@app.post("/api/notes/{note_id}/summarize", response_model=SummarizeResponse)
def summarize_note(note_id: str, detailed: bool = Query(False, description="Generate detailed summary"), ai: AINotes = Depends(get_ai)):
    """Generate AI summary of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        summary = ai.summarize(note.content, detailed=detailed)
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(note.content),
            summary_length=len(summary)
        )
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error summarizing note: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


@app.post("/api/notes/{note_id}/tldr")
def tldr_note(note_id: str, ai: AINotes = Depends(get_ai)):
    """Generate TL;DR summary of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        tldr = ai.generate_tldr(note.content)
        
        return {"tldr": tldr}
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error generating TL;DR: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate TL;DR")


@app.post("/api/notes/{note_id}/actions", response_model=ActionsResponse)
def extract_actions(note_id: str, ai: AINotes = Depends(get_ai)):
    """Extract action items from a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        actions = ai.extract_actions(note.content)
        
        return ActionsResponse(
            action_items=actions,
            count=len(actions)
        )
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error extracting actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract actions")


@app.post("/api/notes/{note_id}/prioritize")
def prioritize_actions(note_id: str, ai: AINotes = Depends(get_ai)):
    """Prioritize action items from a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        prioritized = ai.prioritize_actions(note.content)
        
        return prioritized
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error prioritizing actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to prioritize actions")


@app.post("/api/notes/{note_id}/ask", response_model=AskResponse)
def ask_note(note_id: str, request: AskRequest, ai: AINotes = Depends(get_ai)):
    """Ask a question about a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        answer = ai.answer_question(note.content, request.question)
        
        return AskResponse(
            answer=answer,
            question=request.question
        )
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail="Failed to answer question")


@app.post("/api/notes/{note_id}/outline", response_model=OutlineResponse)
def generate_outline(note_id: str, detailed: bool = Query(False, description="Generate detailed outline"), ai: AINotes = Depends(get_ai)):
    """Generate an outline from a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        outline = ai.generate_outline(note.content, detailed=detailed)
        
        return OutlineResponse(
            outline=outline,
            sections=len(outline)
        )
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error generating outline: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate outline")


@app.post("/api/notes/{note_id}/suggest-tags", response_model=dict)
def suggest_tags(note_id: str, ai: AINotes = Depends(get_ai)):
    """Suggest tags for a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        tags = ai.suggest_tags(note.content)
        
        return {"suggested_tags": tags}
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error suggesting tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest tags")


@app.post("/api/notes/{note_id}/sentiment")
def analyze_sentiment(note_id: str, ai: AINotes = Depends(get_ai)):
    """Analyze sentiment of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        sentiment = ai.analyze_sentiment(note.content)
        
        return sentiment
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze sentiment")


@app.post("/api/notes/{note_id}/questions")
def generate_questions(note_id: str, ai: AINotes = Depends(get_ai)):
    """Generate questions prompted by a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        questions = ai.generate_questions(note.content)
        
        return {"questions": questions}
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")


@app.post("/api/notes/{note_id}/improve")
def improve_note(note_id: str, ai: AINotes = Depends(get_ai)):
    """Improve note writing."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        improved = ai.improve_note(note.content)
        
        return {"improved_content": improved}
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error improving note: {e}")
        raise HTTPException(status_code=500, detail="Failed to improve note")


@app.post("/api/notes/{note_id}/analyze", response_model=dict)
def analyze_note(note_id: str, ai: AINotes = Depends(get_ai)):
    """Perform comprehensive AI analysis of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        analysis = ai.analyze_note(note.content)
        
        return analysis
        
    except HTTPException:
        raise
    except AIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Error analyzing note: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze note")


@app.post("/api/notes/bulk-delete")
def bulk_delete(operation: BulkOperation):
    """Delete multiple notes at once"""
    try:
        deleted = storage.bulk_delete(operation.note_ids)
        return BulkOperationResult(
            success=True,
            processed_count=len(operation.note_ids),
            failed_count=len(operation.note_ids) - deleted,
            errors=[]
        )
    except Exception as e:
        log_error(f"Error bulk deleting: {e}")
        return BulkOperationResult(
            success=False,
            processed_count=0,
            failed_count=len(operation.note_ids),
            errors=[str(e)]
        )


@app.post("/api/notes/bulk-archive")
def bulk_archive(operation: BulkOperation):
    """Archive multiple notes at once"""
    try:
        archived = storage.bulk_archive(operation.note_ids)
        return {"message": f"Archived {archived} notes", "count": archived}
    except Exception as e:
        log_error(f"Error bulk archiving: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk archive")


@app.post("/api/notes/bulk-pin")
def bulk_pin(operation: BulkOperation):
    """Pin multiple notes at once"""
    try:
        pinned = storage.bulk_pin(operation.note_ids)
        return {"message": f"Pinned {pinned} notes", "count": pinned}
    except Exception as e:
        log_error(f"Error bulk pinning: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk pin")


@app.delete("/api/notes")
def clear_all_notes():
    """Delete all notes (dangerous!)"""
    try:
        count = storage.clear_all()
        return {
            "message": f"Deleted {count} notes",
            "deleted_count": count
        }
    except Exception as e:
        log_error(f"Error clearing notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear notes")


@app.get("/api/export")
def export_notes(format: str = Query("json", description="Export format (json, dict)"), include_archived: bool = Query(False)):
    """Export all notes"""
    try:
        data = storage.export_to_dict(include_archived=include_archived)
        return data
    except Exception as e:
        log_error(f"Error exporting notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to export notes")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
