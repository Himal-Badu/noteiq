import os
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from noteiq.models import (
    Note, NoteCreate, NoteUpdate,
    SummarizeResponse, ActionsResponse, AskRequest, AskResponse, OutlineResponse
)
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes


app = FastAPI(title="NoteIQ API", description="AI-Powered Notes API")
storage = NoteStorage()


@app.get("/")
def root():
    return {"message": "Welcome to NoteIQ API", "version": "1.0.0"}


@app.post("/api/notes", response_model=Note)
def create_note(note: NoteCreate):
    """Create a new note."""
    new_note = Note(
        title=note.title,
        content=note.content,
        tags=note.tags
    )
    return storage.create(new_note)


@app.get("/api/notes", response_model=list[Note])
def list_notes(tag: Optional[str] = Query(None, description="Filter by tag")):
    """List all notes, optionally filtered by tag."""
    return storage.get_all(tag=tag)


@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    """Get a specific note by ID."""
    note = storage.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: str, note_update: NoteUpdate):
    """Update an existing note."""
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
    
    return storage.update(note_id, existing)


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str):
    """Delete a note."""
    success = storage.delete(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}


@app.post("/api/notes/{note_id}/summarize", response_model=SummarizeResponse)
def summarize_note(note_id: str):
    """Generate AI summary of a note."""
    note = storage.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    ai = AINotes()
    summary = ai.summarize(note.content)
    return SummarizeResponse(summary=summary)


@app.post("/api/notes/{note_id}/actions", response_model=ActionsResponse)
def extract_actions(note_id: str):
    """Extract action items from a note."""
    note = storage.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    ai = AINotes()
    actions = ai.extract_actions(note.content)
    return ActionsResponse(action_items=actions)


@app.post("/api/notes/{note_id}/ask", response_model=AskResponse)
def ask_note(note_id: str, request: AskRequest):
    """Ask a question about a note."""
    note = storage.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    ai = AINotes()
    answer = ai.answer_question(note.content, request.question)
    return AskResponse(answer=answer)


@app.post("/api/notes/{note_id}/outline", response_model=OutlineResponse)
def generate_outline(note_id: str):
    """Generate an outline from a note."""
    note = storage.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    ai = AINotes()
    outline = ai.generate_outline(note.content)
    return OutlineResponse(outline=outline)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)